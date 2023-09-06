from typing import Final, Optional

from attrs import define, field

from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent


@define(auto_attribs=True, kw_only=True)
class CommentParagraph(Segment):
    parent: Optional[Model] = field(eq=False, repr=repr_parent)
    indentation: Final[str]
    text: Final[str]

    @property
    def code(self) -> str:
        return f"{self.indentation}## -- {self.text} -- ##"

    @property
    def callout(self) -> str:
        return self.code
