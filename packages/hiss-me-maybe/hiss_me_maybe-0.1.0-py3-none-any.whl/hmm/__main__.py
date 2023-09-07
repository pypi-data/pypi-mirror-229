import base64
import dataclasses
import datetime
import sys
from typing import NamedTuple

import click
import requests

BASE_ENCODING = "ASCII"
SEPARATOR = ":"

PushoverCreds = NamedTuple("PushoverCreds", [("user_key", str), ("app_key", str)])
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"


@dataclasses.dataclass
class MessagePacket:
    title: str
    message: str


def pushover_parse(basic_key: str) -> PushoverCreds:
    user_key, app_key = (
        base64.b64decode(basic_key).decode(BASE_ENCODING).split(SEPARATOR)
    )
    return PushoverCreds(user_key=user_key, app_key=app_key)


def pushover_send(creds: PushoverCreds, packet: MessagePacket) -> None:
    user_key, app_key = creds

    with requests.post(
        PUSHOVER_URL,
        data={
            "token": app_key,
            "user": user_key,
            "message": packet.message,
            "title": packet.title,
        },
    ) as rq:
        if rq.status_code != 200:
            raise ValueError("Failed to send message :(")


@click.group()
def _cli() -> None:
    ...


def read_stdin() -> str:
    stdin_ = ""
    while c := sys.stdin.readline():
        stdin_ += c
    return stdin_


@_cli.command("pushover")
@click.argument("credentials")
def pushover(credentials: str) -> None:
    creds = pushover_parse(credentials)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    packet = MessagePacket(title=now, message=read_stdin())

    pushover_send(creds, packet)


def _main() -> None:
    _cli()


if __name__ == "__main__":
    _main()
