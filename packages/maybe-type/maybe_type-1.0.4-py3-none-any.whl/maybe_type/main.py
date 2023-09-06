import typing
import functools
from dataclasses import dataclass

T = typing.TypeVar('T')

@dataclass(frozen=True)
class Some(typing.Generic[T]):
    """
    Some[T] is a wrapper for a value of type T.
    This allows us to apply the functions bind and map to the value.
    Also allows for fancy pattern matching.
    """
    value: T

    def bind(self, f: typing.Callable[[T], 'Maybe[T]']) -> 'Maybe[T]':
        """Applies a function, that returns a Maybe, to the value, that is wrapped."""
        return f(self.value)
    
    def map(self, f: typing.Callable[[T], T]) -> 'Maybe[T]':
        """Applies a function to the value, that is wrapped."""
        return Some(f(self.value))

    def __repr__(self) -> str:
        return f'Some[{self.value.__class__.__name__}]({self.value})'

Maybe = typing.Union[Some[T], None]
"""A union type to represent a value of type Some[T] or None."""

def with_maybe(f: typing.Callable[..., T]) -> typing.Callable[..., Maybe[T]]:
    """A decorator that wraps a function, that may throw an exception, in a Maybe."""

    @functools.wraps(f)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> Maybe[T]:
        try:
            return Some(f(*args, **kwargs))
        except Exception:
            return None
    return wrapper