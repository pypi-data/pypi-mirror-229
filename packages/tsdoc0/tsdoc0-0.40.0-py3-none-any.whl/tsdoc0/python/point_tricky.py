from typing import Final, Optional

from attr import define, field

from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent


@define(auto_attribs=True, kw_only=True)
class PointTricky(Segment):
    parent: Optional[Model] = field(eq=False, repr=repr_parent)
    indentation: Final[str]
    point: Final[str]
    explanation: Final[str]
