from typing import Final, Iterable, Optional

from attrs import define, field

from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent
from tsdoc0.python.vocabulary_term import VocabularyTerm


# This converter wrapper-function is used because of a bug with the mypy-attrs plugin.
# https://github.com/python/mypy/issues/8389
def _tuple(iterable: Iterable[VocabularyTerm]) -> tuple[VocabularyTerm, ...]:
    return tuple(iterable)


@define(auto_attribs=True, kw_only=True)
class Vocabulary(Segment):
    parent: Optional[Model] = field(eq=False, repr=repr_parent)
    indentation: Final[str]
    terms: Final[tuple[VocabularyTerm, ...]] = field(converter=_tuple)
