from typing import Final, Iterable, Optional

from attrs import define, field

from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent


# This converter wrapper-function is used because of a bug with the mypy-attrs plugin.
# https://github.com/python/mypy/issues/8389
def _tuple(iterable: Iterable[str]) -> tuple[str, ...]:
    return tuple(iterable)


@define(auto_attribs=True, kw_only=True)
class Keywords(Segment):
    parent: Optional[Model] = field(eq=False, repr=repr_parent)
    indentation: Final[str]
    terms: Final[tuple[str, ...]] = field(converter=_tuple)

    @property
    def callout(self) -> str:
        keywords = " " + ", ".join(self.terms) if self.terms else ""

        return f"Keywords:{keywords}"
