from typing import TYPE_CHECKING, Final, Optional

from attrs import define, field

from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent

# Conditional import used because there would be a circular dependency
# https://mypy.readthedocs.io/en/latest/common_issues.html#import-cycles
if TYPE_CHECKING:
    from tsdoc0.python.solution_shape import SolutionShape  # noqa: F401


@define(auto_attribs=True, kw_only=True)
class SolutionItem(Segment):
    # Forward reference used because there would be a circular dependency
    # https://mypy.readthedocs.io/en/latest/kinds_of_types.html#class-name-forward-references
    parent: Optional["SolutionShape"] = field(eq=False, repr=repr_parent)
    indentation: Final[str]
    key: Final[str]
    value: Final[str]
