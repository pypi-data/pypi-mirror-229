
from __future__ import annotations

import abc
import dataclasses as dc
import enum
import math
import time
import types
import typing as t

from requests import request


class Snowflake(str):
    """ Represents a `Discord Snowflake <https://discord.com/developers/docs/reference#snowflakes>`_.
    
        :mod:`dubious.discord.api` imports this. It's acceptable to ``from dubious.discord import api`` and use ``api.Snowflake`` instead of ``disc.Snowflake``. """

    def __init__(self, r: str|int):
        self.id = int(r) if isinstance(r, str) else r
        self.timestamp = (self.id >> 22) + 1420070400000
        self.workerID = (self.id & 0x3E0000) >> 17
        self.processID = (self.id & 0x1F000) >> 12
        self.increment = self.id & 0xFFF

    def __repr__(self):
        return str(self.id)

    def __str__(self) -> str:
        return repr(self)

    def __hash__(self):
        return self.id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            try:
                return int(o) == self.id # type: ignore
            except TypeError:
                return False
        return o.id == self.id

    def __ne__(self, o: object) -> bool:
        return not self == o

@dc.dataclass
class Disc:
    """ Root class for all Discord objects. Exists in case there's some functionality to be implemented across every Discord data structure. """

t_Cast = t.TypeVar("t_Cast")
""" Represents the return type of :func:`.cast`."""
def cast(t_to: type[t_Cast], raw: t.Any) -> t_Cast:
    """ Casts ``raw`` data of any shape to the given type, ``t_to``.  """

    if raw is None: return raw

    if dc.is_dataclass(raw):
        raw = dc.asdict(raw)
    if dc.is_dataclass(t_to):
        fixedraw = {}

        fieldtypes: dict[str, type] = t.get_type_hints(t_to)
        fixedraw = {
            field.name: cast(
                fieldtypes[field.name], raw[field.name] if field.name in raw else None
            ) for field in dc.fields(t_to)
        }
        return t_to(**fixedraw)

    t_root = t.get_origin(t_to)

    if t_root:
        if issubclass(t_root, list):
            t_list, *_ = t.get_args(t_to)
            return [
                cast(t_list, rawitem) for rawitem in raw
            ] # type: ignore
        elif issubclass(t_root, dict):
            t_key, t_val, *_ = t.get_args(t_to)
            return {
                cast(t_key, key): cast(t_val, val)
                    for key, val in raw.items()
            } # type: ignore
        elif issubclass(t_root, types.UnionType):
            t_optionals = [
                t for t in t.get_args(t_to)
                    if t != type(None)
            ]
            best_score = 0
            best_len = math.inf
            best_opt = None
            for t_opt in t_optionals:
                if dc.is_dataclass(t_opt):
                    fields = [field.name for field in dc.fields(t_opt)]
                    score = sum(name in fields for name in raw)
                    if (
                        score > best_score or (
                            score == best_score and 
                            len(fields) < best_len
                        )
                    ):
                        best_score = score
                        best_len = len(fields)
                        best_opt = t_opt
                else:
                    try:
                        return cast(t_opt, raw)
                    except ValueError:
                        continue
            return cast(best_opt, raw) #type: ignore

    try:
        return t_to(raw)
    except ValueError:
        return raw

def uncast(raw: t.Any):
    """ Transforms an object to a json-compatible object. """

    if dc.is_dataclass(raw):
        return dc.asdict(raw)
    elif isinstance(raw, dict):
        return {uncast(k): uncast(v) for k, v in raw.items()}
    elif isinstance(raw, list):
        return [uncast(v) for v in raw]
    else:
        return raw

ROOT = "https://discord.com/api"

class Http(str, enum.Enum):
    """ Enum for each potential type of request to make to the Discord API. """

    GET = "GET"
    PUT = "PUT"
    PATCH = "PATCH"
    POST = "POST"
    DELETE = "DELETE"

t_Ret = t.TypeVar("t_Ret")
""" Represents the type that an :class:`HttpReq` will return upon success. """
class HttpReq(abc.ABC, t.Generic[t_Ret]):
    """ A class that holds information about a request to make to the Discord API.
     
        Subclasses should define within themselves a class for the :attr:`.query` attribute and/or the :attr:`.form` attribute, if either exist, and appropriately set the type hints of either. """
    
    query: Disc | None = None
    """ An object to give to the request. Acts as a query string in the URL; is given to :func:`requests.request` as the ``params`` kwarg. """
    form: Disc | None = None
    """ An object to give to the request. Acts as a json string in the request's body; is given to :func:`requests.request` as the ``json`` kwarg. """

    method: t.ClassVar[Http]
    """ The HTTP method with which to make the request. Given to :func:`requests.request` as the ``method`` argument. """
    endpoint: str
    """ The URL at which the request should be made. Given to :func:`requests.request` as the ``url`` argument. This field is set dynamically in a subclass's ``__post_init__`` in order to allow for per-guild/per-channel/etc. requests. """

    @abc.abstractmethod
    def cast(self, data: t.Any) -> t_Ret:
        ...

    def do_with(self, token: str) -> t_Ret:
        """ Perform this Discord API request with :func:`requests.request`. Requires authentication using a bot token - this is usually :attr:`dubious.pory.Pory.token`.
        
            When a rate limit is encountered, wait the response's given time and retry (by calling recursively). """

        res = request(self.method, ROOT + self.endpoint,
            headers={
                "Authorization": f"Bot {token}"
            },
            params=dc.asdict(self.query) if self.query else None,
            json=dc.asdict(self.form) if self.form else None
        )
        if not res.status_code in range(200, 300):
            error = res.json()
            if error.get("retry_after"):
                wait = error["retry_after"]/1000
                print(f"rate limited, waiting {wait} seconds")
                time.sleep(wait)
                return self.do_with(token)
            raise Exception(f"{res.status_code}: {str(error)}")
        return self.cast(res.json() if res.text else None)
