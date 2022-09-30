import re

from _action import log, talk


class FilterMeta(type):
    name = ""
    regex = b""
    talk = False
    talk_prefix = ""

    def __new__(cls, name, bases, attrs: dict):
        if not attrs.get("name"):
            raise ValueError(f"{name} has invalid name")
        if not attrs.get("regex"):
            raise ValueError(f"{name} has invalid regex")
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def action(cls, m: re.Match[bytes]):
        name = m[1].split(b"\x00")[0].decode("cp932")
        body = m[2].split(b"\x00")[0].decode("cp932")
        log(f"[{cls.name}] {name}: {body}")
        if cls.talk:
            talk(f"{cls.talk_prefix}{name}:{body}")


class Nop(FilterMeta):
    name = "NOP"
    regex = rb"^\x1E\x00\x09\x70\x00\x00"

    @classmethod
    def action(cls, m: re.Match[bytes]):
        return None


class Nop2(FilterMeta):
    name = "NOP"
    regex = rb"^\x06\x00\x00\x10\x00\x00"

    @classmethod
    def action(cls, m: re.Match[bytes]):
        return None


class FieldChat(FilterMeta):
    name = "FIELD"
    regex = rb"\x00\(\x11\x00\x00[\x01|\x02|\x03]\x00\x00\x00.\x00X\x11\x00\x00.\x00\x00\x00([^\x00]+)\x00+([^\x00]+)"
    talk = False


class PartyChat(FilterMeta):
    name = "PARTY"
    regex = rb".\x00\(\x11\x00\x00.\x00\x00\x00(?:.)+\x00\x58\x11\xCC\xCC\xCC..\x80([^\x00]+)\x00+([^\x00]+)"
    talk = True


class GuildChat(FilterMeta):
    name = "GUILD"
    regex = rb"\x00\x58\x11\xCC\xCC\xCC..\x80([^\x00]+)\x00+([^\x00]+)"
    talk = True
    talk_prefix = "じー、"
    # MEMO: 他のチャットより後に処理すること


class ShoutChat(FilterMeta):
    name = "SHOUT"
    regex = rb"\x00\x58\x11\xCC\xCC..\x0c\x81([^\x00]+)\x00+([^\x00]+)"
    talk = False
    talk_prefix = "エコー)"


class WorldChat(FilterMeta):
    name = "WORLD"
    regex = rb"\x00\x58\x11\xCC\xCC\xCC\xCC\x0C\x84([^\x00]+)\x00+([^\x00]+)"


class WhisperFromTo(FilterMeta):
    name = "WHISP_FROMTO"
    regex = rb"\x00\(\x11\x00\x00.\x00\x00\x00\x9A\x00v\x11\x00\x00\x00\x00(.{18})([^\x00]+).*\x00X\x11\xCC\xCC..L\x80"


class WhisperTo(FilterMeta):
    name = "WHISP_TO"
    regex = rb"\x00\(\x11\x00\x00.\x00\x00\x00\x9A\x00v\x11\x00\x00\x00\x00(.{18})([^\x00]+)"


class WhisperFrom(FilterMeta):
    name = "WHISP_FROM"
    regex = rb"\x00\(\x11\x00\x00\x01\x00\x00\x00.\x00X\x11\xCC\xCC..L\x80([^\x00]+)\x00+([^\x00]+)"


FILTERS: list[type[FilterMeta]] = [
    Nop,
    Nop2,
    FieldChat,
    PartyChat,
    GuildChat,
    ShoutChat,
    WorldChat,
    WhisperFromTo,
    WhisperFrom,
    WhisperTo,
]
