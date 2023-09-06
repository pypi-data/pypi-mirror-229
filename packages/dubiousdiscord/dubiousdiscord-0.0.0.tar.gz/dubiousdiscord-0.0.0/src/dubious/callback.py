
import dataclasses as dc
import inspect
import multiprocessing as mp
import re
import traceback as tb
import typing as t

from dubious.discord import api

_option_types = {
    str: api.ApplicationCommandOptionType.STRING,
    int: api.ApplicationCommandOptionType.INTEGER,
    bool: api.ApplicationCommandOptionType.BOOLEAN,
    api.User: api.ApplicationCommandOptionType.USER,
    api.Channel: api.ApplicationCommandOptionType.CHANNEL,
    api.Role: api.ApplicationCommandOptionType.ROLE,
    float: api.ApplicationCommandOptionType.NUMBER,
    api.Attachment: api.ApplicationCommandOptionType.ATTACHMENT,
}
_option_types_strs = {
    k.__name__: v for k, v in _option_types.items()
}

_pat_discord_name = re.compile(r"^[-_a-z]{1,32}$")


def _prepare_option(opt: inspect.Parameter):
    if not _pat_discord_name.search(opt.name):
        # https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-naming
        raise ValueError(f"Option '{opt.name}' has an invalid name.")
    desc = "No description."
    choices = None
    if t.get_origin(opt.annotation) == t.Annotated:
        anns = t.get_args(opt.annotation)
        typ = _option_types[anns[0]]
        if len(anns) > 1:
            if len(anns[1]) > 100:
                raise ValueError(
                    f"The description for option '{opt.name}' is too long. Should be 100 or less; got {len(anns[1])}.")
            desc = anns[1]
        if len(anns) > 2: choices = anns[2]
    else:
        if isinstance(opt.annotation, str):
            # to account for `from __future__ import annotations` making types strings
            wo_namespace = opt.annotation.split(".")[-1]
            typ = _option_types_strs[wo_namespace]
        else:
            typ = _option_types[opt.annotation]

    return api.ApplicationCommandOption(
        typ,
        opt.name,
        desc,
        required=None if not opt.default == inspect.Parameter.empty else True,
        choices=choices
    )


ta_CommandRet = api.InteractionCallbackData | None | t.Iterator[api.InteractionCallbackData | None]
""" A type alias that defines what a function stored in a :class:`Callback` can return. """

ps_CallbackArgs = t.ParamSpec("ps_CallbackArgs")
""" Represents the arguments for a function stored in a :class:`Callback`. """
t_CommandRet = t.TypeVar("t_CommandRet", bound=ta_CommandRet)
""" Represents the return value for a function stored in a :class:`Callback`. """


def do_callback(
    callback: t.Callable[ps_CallbackArgs, t_CommandRet],
    ixn: api.Interaction,
    data: api.InteractionData | api.ApplicationCommandInteractionDataOption | None
) -> t_CommandRet:
    """ Extracts options from an :class:`.api.Interaction`, and uses them as arguments to call a given ``callback`` function.
    
        This is the "optionated" part of DubiousDiscord: The ``callback`` function's signature can define keyword-specific arguments (i.e. arguments that come after ``*,`` in the signature) that :func:`.do_callback` will take from the ``ixn`` :class:`.api.Interaction` object. Take an example ``callback`` function::
        
            from dubious.discord import api
            from dubious import pory

            bot = pory.Pory("app id", "app key", "bot token")

            @bot.on_command
            def whereami(*, channel_id: api.Snowflake | None):
                if not channel_id:
                    return api.ResponseMessage(content="We're nowhere! How's that possible?")
                else:
                    return api.RepsonseMessage(content=f"We're in the <#{channel_id}> channel!")

        The callback function asks for ``channel_id``, which is a field on :class:`.api.Interaction`. :func:`do_callback` will find the :attr:`~.api.Interaction.channel_id` field on the given ``ixn`` argument and give it to the callback function as a coresponding keyword argument.
        
        Note that the :attr:`.api.Interaction.channel_id` field has the type ``Snowflake | None``. There's no way to enforce this, but the callback function should reflect that type in the signature, as shown in the example. (Though, to be pedantic: In this particular example, the ``whereami`` function will *never* be called in response to a Modal Interaction, which is the only case in which :attr:`~.api.Interaction.channel_id` could be ``None``, so making ``channel_id`` in the signature ``None`` -able isn't as big of a deal.)
        """

    fixed_args: dict[str, t.Any] = {}
    for param in inspect.signature(callback).parameters.values():
        match param.kind:
            case inspect.Parameter.POSITIONAL_OR_KEYWORD:
                assert isinstance(data, (api.ApplicationCommandData, api.ApplicationCommandInteractionDataOption))
                assert isinstance(ixn.data, api.ApplicationCommandData)
                if not param.default == inspect.Parameter.empty: continue
                assert data.options

                found = False
                for opt in data.options:
                    if found := opt.name == param.name:
                        if opt.type == api.ApplicationCommandOptionType.CHANNEL:
                            assert ixn.data.resolved
                            assert isinstance(opt.value, (str, int))
                            assert ixn.data.resolved.channels
                            fixed_args[param.name] = ixn.data.resolved.channels[api.Snowflake(opt.value)]
                        elif opt.type == api.ApplicationCommandOptionType.USER:
                            assert ixn.data.resolved
                            assert isinstance(opt.value, (str, int))
                            assert ixn.data.resolved.users
                            fixed_args[param.name] = ixn.data.resolved.users[api.Snowflake(opt.value)]
                        elif opt.type == api.ApplicationCommandOptionType.ROLE:
                            assert ixn.data.resolved
                            assert isinstance(opt.value, (str, int))
                            assert ixn.data.resolved.roles
                            fixed_args[param.name] = ixn.data.resolved.roles[api.Snowflake(opt.value)]
                        elif opt.type == api.ApplicationCommandOptionType.ATTACHMENT:
                            assert ixn.data.resolved
                            assert isinstance(opt.value, (str, int))
                            assert ixn.data.resolved.attachments
                            fixed_args[param.name] = ixn.data.resolved.attachments[api.Snowflake(opt.value)]
                        else:
                            fixed_args[param.name] = opt.value
                        break
                assert found
            case inspect.Parameter.KEYWORD_ONLY:
                if param.name == "ixn":
                    fixed_args[param.name] = ixn
                elif param.name == "data":
                    fixed_args[param.name] = ixn.data
                elif param.name == "user":
                    if not ixn.user:
                        assert ixn.member
                        fixed_args[param.name] = ixn.member.user
                elif hasattr(ixn, param.name):
                    fixed_args[param.name] = getattr(ixn, param.name)
                elif hasattr(ixn.data, param.name):
                    fixed_args[param.name] = getattr(ixn.data, param.name)
                else:
                    raise Exception()
            case _:
                raise Exception()

    return callback(**fixed_args)  # type: ignore


@dc.dataclass
class Callback(t.Generic[ps_CallbackArgs, t_CommandRet]):
    """ This dataclass holds a function along with an associated name.
    
        The name allows it to be identified dynamically, so that it may be matched with e.g. a Discord interaction. """

    name: str
    __func__: t.Callable[ps_CallbackArgs, t_CommandRet]

    def do(
        self,
        ixn: api.Interaction,
        data: api.InteractionData | api.ApplicationCommandInteractionDataOption | None
    ) -> api.InteractionCallbackData | None:
        """ Calls the wrapped function using data from an :class:`.api.Interaction`.
        
            ``ixn`` and ``data`` are separate arguments because the :attr:`.api.Interaction.data` field can be that of a subcommand group, whose :attr:`~.api.ApplicationCommandData.options` field has only one :class:`.api.ApplicationCommandInteractionDataOption` coresponding to the subcommand (or subcommand group) currently being called. :func:`do_callback` needs to have the :class:`.api.ApplicationCommandInteractionDataOption`\\ s that corespond to the wrapped function's arguments. """

        done = do_callback(self.__func__, ixn, data)
        if isinstance(done, t.Iterator):
            initial_return = next(done)
            mp.Process(target=list, args=(done,)).start()
            return initial_return
        return done


@dc.dataclass
class CallbackGroup:
    _options: dict[str, Callback] = dc.field(default_factory=dict, kw_only=True)

    def __call__(self, cb: t.Callable[ps_CallbackArgs, t_CommandRet] | None = None, /, *, name: str | None = None):
        def _(callback: t.Callable[ps_CallbackArgs, t_CommandRet]):
            _name = name if name else callback.__name__
            self._options[_name] = Callback(_name, callback)
            return callback

        if cb:
            return _(cb)
        else:
            return _


@dc.dataclass
class Command(api.ApplicationCommandOption, Callback[ps_CallbackArgs, t_CommandRet]):
    """ This class contains a callback function to be matched against a Discord Interaction. It subclasses :class:`.ApplicationCommandOption` to vaguely match the structure of incoming commands.
        
        Generally, this class isn't meant to be instantiated manually. Instead, the right way to create an instance is to use a :class:`CommandGroup` as a decorator around a callback function. """

    __func__: t.Callable[ps_CallbackArgs, t_CommandRet]

    default_member_permissions: str | None = None
    """ Defines the permissions required to use the command. This field comes from the :class:`.api.ApplicationCommand` class.
    
        The API documentation marks it as a string, even though it's mean to be a bitfield of :class:`.api.Permission` bits. """
    
    _options: dict[str, api.ApplicationCommandOption] = dc.field(default_factory=dict, kw_only=True)

    guild_id: api.Snowflake | None = None
    """ Defining this can specify a guild in which to register the command to Discord. """

    early_response: t_CommandRet | None = None

    @property
    def options(self):
        return list(self._options.values()) if self._options else None

    @options.setter
    def options(self, _: list[api.ApplicationCommandOption] | None):
        # only needed to appease dataclass default __init__
        pass

    def __post_init__(self):
        assert _pat_discord_name.search(self.name), f"Command '{self.name}' has an invalid name."
        assert len(
            self.description) <= 100, f"The description on command '{self.name}' is too long. Should be 100 or less; got {len(self.description)}."

        for opt in inspect.signature(self.__func__).parameters.values():
            if opt.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                try:
                    self._options[opt.name] = _prepare_option(opt)
                except Exception as e:
                    raise ValueError(f"In command '{self.name}': {''.join(tb.format_exception(e))}")
        if len(self._options) > 25: raise ValueError(
            f"There are too many options for command \"{self.name}\". Should be 25 or less; got {len(self._options)}.")

    def _compare_with(self, registered: api.ApplicationCommand):
        return (
            self.guild_id == registered.guild_id and
            self.default_member_permissions == registered.default_member_permissions and
            self._compare_with_as_option(registered)
        )

    def _compare_with_as_option(self, registered: api.ApplicationCommand | api.ApplicationCommandOption):
        return (
            self.name == registered.name and
            self.name_localizations == registered.name_localizations and
            self.description == registered.description and
            self.description_localizations == registered.description_localizations and
            all(
                this_opt._compare_with_as_option(that_opt)
                if isinstance(this_opt, Command) else
                this_opt == that_opt
                for this_opt, that_opt in zip(self.options, registered.options)
            ) if self.options and registered.options else self.options == registered.options
        )

    def __call__(self, *args: ps_CallbackArgs.args, **kwargs: ps_CallbackArgs.kwargs):
        """ Redefines what calling an instance of this class does to be the same as calling the wrapped function. """

        return self.__func__(*args, **kwargs)


@dc.dataclass
class CommandGroup(CallbackGroup, Command[[], None]):
    _options: dict[str, Command] = dc.field(default_factory=dict, kw_only=True)

    def get_commands(self, *, as_type: api.ApplicationCommandType | None = None):
        prepared_commands: dict[str, Command] = {}
        for opt in self._options.values():
            prepared = opt
            if as_type:
                # below should type error but dc.replace doesn't care
                # api.ApplicationCommandOption.type field can't be type api.ApplicationCommandType
                prepared = dc.replace(prepared, type=as_type)
            if isinstance(prepared, CommandGroup):
                prepared = dc.replace(prepared, _options=prepared.get_commands())
            prepared_commands[opt.name] = prepared
        return prepared_commands

    @classmethod
    def new(cls):
        return cls(
            "_",
            lambda: None,
            api.ApplicationCommandOptionType.SUB_COMMAND_GROUP,
            "_",
        )

    def __call__(self, cb: t.Callable[ps_CallbackArgs, t_CommandRet] | None = None, /, *,
                 name: str | None = None,
                 desc: str | None = None,
                 perms: list[api.Permission] | None = None,
                 guild: api.Snowflake | None = None,
                 ):
        def _wrap(callback: t.Callable[ps_CallbackArgs, t_CommandRet]) -> t.Callable[ps_CallbackArgs, t_CommandRet]:
            _name = name if name else callback.__name__
            _desc = desc if desc else callback.__doc__ if (not desc) and callback.__doc__ else "No description provided."
            _perms = 0
            for perm in perms if perms else []:
                _perms |= perm
            self._options[_name] = Command(
                _name,
                callback,
                api.ApplicationCommandOptionType.SUB_COMMAND,
                _desc.strip(),
                str(_perms) if perms else None,
                guild,
            )
            return callback

        return _wrap(cb) if cb else _wrap

    def group(self,
              name: str,
              desc: str,
              perms: t.Collection[api.Permission] | None = None,
              guild: api.Snowflake | None = None
              ):
        """ Adds a subcommand :class:`CommandGroup` to this :class:`CommandGroup`'s options and returns it. """

        _perms = 0
        if perms:
            for perm in perms:
                _perms |= perm
        group = self.__class__(
            name,
            lambda: None,
            api.ApplicationCommandOptionType.SUB_COMMAND_GROUP,
            desc,
            str(_perms) if perms else None,
            guild
        )
        self._options[name] = group
        return group
    
    def do(self, ixn: api.Interaction, data: api.ApplicationCommandData | api.ApplicationCommandInteractionDataOption) -> api.InteractionCallbackData | None:
        """ Propagates an :class:`.api.Interaction` down to the subcommand callback it's meant for.
        
            In other words, this function extracts the appropriate subcommand :class:`Command` object and calls the subcommand's :meth:`Callback.do`. If the subcommand is a :class:`CommandGroup`, this function recurses by calling the subcommand's :meth:`CommandGroup.do`. """

        assert data.options
        # data.options is always guaranteed to have a length of 1 as long as the data belongs to a subcommand group
        option, = data.options
        subcommand = self._options[option.name]
        return subcommand.do(ixn, option)
