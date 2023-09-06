
from __future__ import annotations
import abc
import dataclasses as dc
import enum
from pprint import pprint
import re
import typing as t

eval_name = re.compile(r"\w")

ta_MatchResults = dict[str, "str | list[str] | ta_MatchResults"]
ta_Process = t.Callable[[str, "Trick"], ta_MatchResults]
ta_Instructions = dict[str, list[ta_Process]]

@dc.dataclass
class Step:
    name: str | None = None
    ops: list[str] = dc.field(default_factory=list)
    opname: str | None = None
    inner: str = ""
    nest: int = 0
    done: bool = False

@dc.dataclass
class Trick:
    template: str
    instructions: ta_Instructions = dc.field(default_factory=dict)
    pattern: str = dc.field(init=False, default="")

    def __post_init__(self):
        print(f"trick: {self.template}")
        step = Step()
        for char in self.template:
            print(char)
            match char, step:
                case "$", Step(name=None):
                    print("var start")
                    step.name = ""
                case _, Step(name=None):
                    print("adding to pattern")
                    self.pattern += char
                case _, Step(name=str(some), opname=None, nest=0) if re.match(r"\w", char):
                    print("adding to var name")
                    step.name = some + char
                case ".", Step(name=str(_), opname=None, nest=0):
                    print("op start")
                    step.opname = ""
                case _, Step(name=str(some), opname=None, nest=0) if not re.match(r"\w", char):
                    print("var end")
                    self.create_group(some, [])
                    step.name = None
                case _, Step(name=str(_), opname=str(some), nest=0) if re.match(r"\w", char):
                    print("adding to op")
                    step.opname = some + char
                case "{", Step(name=str(_), opname=str(some), nest=0):
                    print("up nest (new op)")
                    step.ops.append(some)
                    step.opname = None
                    step.nest += 1
                case "{", Step(name=str(_), nest=int(some)) if some > 0:
                    print("up nest")
                    step.nest += 1
                case "}", Step(name=str(name), nest=int(some)) if some > 0:
                    print("down nest")
                    step.nest -= 1
                    if step.nest == 0:
                        #self.create_group(name, [op_by_char[opname] for opname in step.ops], step.inner)
                        step.name = None
                case _, Step(name=str(_), nest=int(some)) if some > 0:
                    print("adding to inner")
                    step.inner += char
                case _:
                    raise Exception()
        print(f"trick [[{self.pattern}]] done")

    def create_group(self, name: str, instructions: list[ta_Process], inner: str=""):
        self.pattern += r"(?P<"+name+r">[\w\W]+?)"
        #self.instructions[name] = Trick(inner, instructions) if inner else instructions

    def match(self, on: str):
        match = re.match(self.pattern, on)
        if not match: return
        groups = match.groupdict()
        results: ta_MatchResults = {}
        for group in groups:
            inner = self.instructions[group]
            got = groups[group]
            if not inner:
                results[group] = got
            # else:
            #     results[group] = inner.match(got)

"""
Goal:
    Create a way to store human-readable enumerable information in Discord messages, and create a way to parse that information back out of those messages.
    Examples:
        "Query: `$query_tokens.sep{, }`"
        - "Query: `":
            Literal; doesn't store information.
        - "$query_tokens":
            This will be replaced with a variable called "query_tokens", given when serializing.
            The intent is for this variable to be a list of strings.
        - ".sep{, }":
            This modifier, appended to the query_tokens variable, will separate the variable's items by commas.
        - "`":
            Literal.
        
        "$allowed_users.empty?.lit{Anyone}.else.sep{, }.fmt{<@{}>} can use this query."
        - "$allowed_users":
            Use a variable named "allowed_users".
        - ".empty?":
            This modifier, appended to the allowed_users variable, will only include the modifiers following it up until the ".else" modifier if the given value for the variable is empty.
        - ".lit{Anyone}":
            This modifier will evaluate to the literal string "Anyone".
        - ".else":
            This modifier ends the modifiers for a conditional modifier and begins the modifiers for the alternative.
        - ".sep{, }":
            Separates the variable's items by commas.
        - ".fmt{<@{}>}":
            Surrounds each of the variable's items with <@ and >, replacing the {} with the item itself.
        - " can use this query.":
            Literal.
    
    Can't use regular expressions to parse the rules - the final character of a variable and its modifiers is whitespace, but there can be whitespace inside of curly brackets without ending the modifiers.
    Conditional modifiers can't be nested - modifiers can't be nested inside of other modifiers.
"""

class States(enum.Enum):
    Root = 0
    Variable = 1
    Modifier = 2
    ModifierArg = 3
    EndingVariable = 4

@dc.dataclass
class Modifier:
    name: str = ""
    arg: str = ""

@dc.dataclass
class Variable:
    name: str = ""
    modifiers: str = ""

def parse_modifiers(text: str):
    modifiers: list[Modifier] = []
    state = States.Root
    nest_level = 0
    for char in text:
        match state, char:
            case States.Root | States.Modifier | States.EndingVariable, ".":
                state = States.Modifier
                modifiers.append(Modifier())
            case States.Modifier, "{":
                state = States.ModifierArg
                nest_level += 1
            case States.Modifier, char:
                modifiers[-1].name += char

            case States.ModifierArg, char:
                if char == "{":
                    nest_level += 1
                elif char == "}":
                    nest_level -= 1
                if nest_level == 0:
                    state = States.EndingVariable
                else:
                    modifiers[-1].arg += char
    return [modifier_methods[modifier.name](modifier.arg) for modifier in modifiers]

def parse_variables(text: str):
    state = States.Root
    variables: list[Variable] = []
    regex = ""
    nest_level = 0
    for char in text:
        match state, char:
            case States.Root, "$":
                variables.append(Variable())
                state = States.Variable
            case States.Root, char:
                regex += char
            case States.Variable | States.Modifier | States.EndingVariable, ".":
                if state == States.Variable:
                    regex += r"(?P<"+variables[-1].name+r">[\w\W]+?)"
                variables[-1].modifiers += char
                state = States.Modifier
            case States.Variable, char:
                variables[-1].name += char
            case States.Modifier, char:
                variables[-1].modifiers += char
                if char == "{":
                    nest_level += 1
                elif char == "}":
                    nest_level -= 1
                    if nest_level == 0:
                        state = States.EndingVariable
            case States.EndingVariable, char:
                regex += char
                state = States.Root
    return variables, regex

def decode(modifiers: list[ModifierMethods], using: str):
    decoded: list[str] | str = using
    for mod in reversed(modifiers):
        decoded = mod.dec(decoded)
    if not isinstance(decoded, list):
        raise Exception(f"When processing decoding modifiers, the final modifier returned a single string instead of a list.")
    return decoded

def encode(modifiers: list[ModifierMethods], using: list[str]):
    encoded: list[str] | str = [*using]
    for mod in modifiers:
        encoded = mod.enc(encoded)
    if not isinstance(encoded, str):
        raise Exception(f"When processing encoding modifiers, the final modifier returned a list instead of a single string.")
    return encoded

@dc.dataclass
class Rules:
    variable_modifiers: dict[str, list[ModifierMethods]] = dc.field(init=False, default_factory=dict)
    regex: re.Pattern = dc.field(init=False)
    raw: str = dc.field(init=False)

    rules_text: dc.InitVar[str]

    def __post_init__(self, rules_text: str):
        variables, regex = parse_variables(rules_text)
        print(variables, regex)
        
        for variable in variables:
            self.variable_modifiers[variable.name] = parse_modifiers(variable.modifiers)

        self.regex = re.compile(regex)
        self.raw = regex
    
    def decode(self, against: str):
        match = self.regex.match(against)
        if not match: return {}
        groups = match.groupdict()
        modified: dict[str, list[str]] = {}
        for var_name, encoded in groups.items():
            modified[var_name] = decode(self.variable_modifiers[var_name], encoded)
        return modified
    
    def encode(self, **variables: list[str]):
        template = self.raw
        modified: dict[str, str] = {}
        for variable_name in variables:
            modified[variable_name] = encode(self.variable_modifiers[variable_name], variables[variable_name])
        for modified_var_name, encoded in modified.items():
            template = template.replace(r"(?P<"+modified_var_name+r">[\w\W]+?)", encoded)
        return template

modifier_methods: dict[str, t.Type[ModifierMethods]] = {}
def modifier(name: str):
    def _(cls: t.Type[ModifierMethods]):
        modifier_methods[name] = cls
    return _

@dc.dataclass
class ModifierMethods(abc.ABC):
    arg: str

    @abc.abstractmethod
    def enc(self, to_encode: str | list[str]) -> str | list[str]: ...

    @abc.abstractmethod
    def dec(self, to_decode: str | list[str]) -> str | list[str]: ...

@modifier("sep")
@dc.dataclass
class Separate(ModifierMethods):
    def enc(self, to_encode: list[str]):
        return self.arg.join(to_encode)
    def dec(self, to_decode: str):
        return to_decode.split(self.arg)

@modifier("fmt")
@dc.dataclass
class Format(ModifierMethods):
    def enc(self, to_encode: list[str]):
        return [re.sub(r"{}", item, self.arg) for item in to_encode]
    def dec(self, to_decode: list[str]):
        lstrip, rstrip = self.arg.split(r"{}")
        return [item.lstrip(lstrip).rstrip(rstrip) for item in to_decode]

@modifier("empty?")
@dc.dataclass
class Empty(ModifierMethods):
    literal: str = dc.field(init=False)
    further_modifiers: list[ModifierMethods] = dc.field(init=False)
    def __post_init__(self):
        self.literal, further_modifiers = self.arg.split(",", 1)
        self.further_modifiers = parse_modifiers(further_modifiers)

    def enc(self, to_encode: list[str]):
        return self.literal if not len(to_encode) else encode(self.further_modifiers, to_encode)
    def dec(self, to_decode: str):
        return [] if to_decode == self.literal else decode(self.further_modifiers, to_decode)

if __name__ == "__main__":
    trick1 = Rules(r"Query: `$query_tokens.sep{, }`")
    trick2 = Rules(r"$allowed_users.empty?{Anyone, .fmt{<@{}>}.sep{, }} can use this query.")
    pprint(trick1)
    pprint(trick2)
    t1_dec = trick1.decode("Query: `1, 2, 3, 4`")
    t2_dec = trick2.decode("Anyone can use this query.")
    t2_dec2 = trick2.decode("<@lapras#0594> can use this query.")
    print(t1_dec, t2_dec, t2_dec2)
    t1_enc = trick1.encode(**t1_dec)
    t2_enc = trick2.encode(**t2_dec)
    t2_enc2 = trick2.encode(**t2_dec2)
    print(t1_enc, t2_enc, t2_enc2)
