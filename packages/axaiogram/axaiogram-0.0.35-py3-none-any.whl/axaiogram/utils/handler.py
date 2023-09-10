from functools import wraps
from typing import Any, Callable, TypeVar, Union, Protocol
from aiogram import F, Router, types

from axaiogram.utils.types import CallbackDataQuery 


class PaginatAbleHandler(Protocol):
    async def __call__(self, *args: Any, message: types.Message, **kwds: Any) -> Any:
        raise NotImplementedError


def _extract_and_get_event_replaceable(
    args: list, 
    kwargs: dict
) -> Union[types.Message, CallbackDataQuery]:
    event_type = (types.Message, types.CallbackQuery)

    for i in range(len(args)):
        if type(args[i]) in event_type:
            return args.pop(i)
        
    for key, value in kwargs.items():
        if type(value) in event_type:
            return kwargs.pop(key)

    raise NotImplementedError


TPaginatAbleHandler = TypeVar('TPaginatAbleHandler', bound=Callable)  #, bound=PaginatAbleHandler)


def extract_paginate_page(
    separator: str = "_page:", 
    loading_msg: str = '...', 
    only_start_loading: bool = True,
    default_page=1,
):
    def inner(f: TPaginatAbleHandler) -> TPaginatAbleHandler:
        @wraps(f)
        async def wrapper(*args_, **kwargs_):
            args = list(args_)
            kwargs = dict(kwargs_)
            event= _extract_and_get_event_replaceable(args, kwargs)
            
            if not isinstance(event, types.CallbackQuery):
                msg = await event.answer(loading_msg)
                return await f(message=event, *args, page=default_page, loading=msg, **kwargs)
            
            _, page = event.data.split(separator)
            page = int(page) if page.strip().isdigit() else default_page

            if not only_start_loading:
                msg = await event.message.edit_text(loading_msg)
            else:
                msg = event.message

            return await f(message=event, *args, loading=msg, page=page, **kwargs)

        return wrapper  # type: ignore
    return inner


def register_as_paginated_handler(
    router: Router,
    handler: Callable,
    command_filter: str,
    *filters,
) -> Router:

    router.callback_query(F.text.startswith(command_filter), *filters)(handler)
    router.message(F.text.startswith(command_filter), *filters)(handler)

    return router

