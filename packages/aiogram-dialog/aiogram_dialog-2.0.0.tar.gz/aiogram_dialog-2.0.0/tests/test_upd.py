from datetime import datetime

from aiogram import Bot
from aiogram.types import (
    Chat, Message, Update, User,
)
from aiogram_dialog.api.entities.update_event import DialogUpdate


class FakeBot(Bot):
    def __init__(self):
        pass  # do not call super, so it is invalid bot, used only as a stub

    @property
    def id(self):
        return 1

    def __call__(self, *args, **kwargs) -> None:
        raise RuntimeError("Fake bot should not be used to call telegram")
    def __hash__(self) -> int:
        return 1

    def __eq__(self, other) -> bool:
        return self is other


def new_message(
        text: str,
):
    chat = Chat(id=1, type="private")
    user = User(
        id=1, is_bot=False,
        first_name=f"User_1",
    )
    return Message(
        message_id=1,
        date=datetime.fromtimestamp(1234567890),
        chat=chat,
        from_user=user,
        text=text,
    )


def test_upd():
    update = Update(
        update_id=1,
        message=new_message("a"),
        bot=FakeBot(),
    )
    print(update.event_type)

    update = Update(
        update_id=1,
        message=new_message("a"),
        bot=FakeBot(),
    )
    print(update.event_type)
