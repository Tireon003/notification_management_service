from typing import Callable, Optional, Tuple, Dict, Any, Union, Awaitable
from fastapi import Request, Response


def key_builder_by_url_method(
    func: Callable[..., Any],
    namespace: str = "",
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> Union[str, Awaitable[str]]:
    if request is None:
        raise ValueError("Request object is required for this key builder")

    return ":".join(
        [
            namespace,
            request.method.lower(),
            request.url.path,
        ]
    )
