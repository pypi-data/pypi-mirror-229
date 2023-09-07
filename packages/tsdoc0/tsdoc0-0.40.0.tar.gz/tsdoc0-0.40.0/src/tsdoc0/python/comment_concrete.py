from typing import Final, Iterable, Optional

from attrs import define, field

from tsdoc0.python.comment_sentence import CommentSentence
from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent


# This converter wrapper-function is used because of a bug with the mypy-attrs plugin.
# https://github.com/python/mypy/issues/8389
def _tuple(iterable: Iterable[CommentSentence]) -> tuple[CommentSentence, ...]:
    return tuple(iterable)


@define(auto_attribs=True, kw_only=True)
class CommentConcrete(Segment):
    parent: Optional[Model] = field(eq=False, repr=repr_parent)
    indentation: Final[str]
    sentences: Final[tuple[CommentSentence, ...]] = field(converter=_tuple)

    @property
    def code(self) -> str:
        return "\n".join(sentence.code for sentence in self.sentences)
