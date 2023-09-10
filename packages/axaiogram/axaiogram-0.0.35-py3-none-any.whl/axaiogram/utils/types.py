from aiogram.types import CallbackQuery as _CallbackQuery, Message


class CallbackQuery(_CallbackQuery):
    message: Message


class CallbackDataQuery(CallbackQuery):
    data: str

