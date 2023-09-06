from typing import TYPE_CHECKING, Final, Optional

from attrs import define, field

from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent

# Conditional import used because there would be a circular dependency
# https://mypy.readthedocs.io/en/latest/common_issues.html#import-cycles
if TYPE_CHECKING:
    from tsdoc0.python.activity_header import ActivityHeader  # noqa: F401


@define(auto_attribs=True, kw_only=True)
class ActivityPart(Segment):
    # Forward reference used because there would be a circular dependency
    # https://mypy.readthedocs.io/en/latest/kinds_of_types.html#class-name-forward-references
    parent: Optional["ActivityHeader"] = field(eq=False, repr=repr_parent)
    number: Final[str]

    @property
    def code(self) -> str:
        return f"Part {self.number}: "
