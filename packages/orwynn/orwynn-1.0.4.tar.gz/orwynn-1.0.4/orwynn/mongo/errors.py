from typing import TYPE_CHECKING, Any

from pymongo.errors import DuplicateKeyError as PymongoDuplicateKeyError

if TYPE_CHECKING:
    pass


class DuplicateKeyError(Exception):
    def __init__(
        self,
        message: str = "",
        original_error: PymongoDuplicateKeyError | None = None
    ) -> None:
        if not message and original_error:
            message = "; ".join([str(x) for x in original_error.args])
        super().__init__(message)


class DocumentUpdateError(Exception):
    pass


class UnsupportedQueryTypeError(Exception):
    """
    Type of given query is unsupported.
    """
    def __init__(
        self,
        *,
        key: str,
        unsupported_value: Any
    ) -> None:
        message: str = \
            f"query for key <{key}> has an unsupported value" \
            f" <{unsupported_value}>"
        super().__init__(message)
