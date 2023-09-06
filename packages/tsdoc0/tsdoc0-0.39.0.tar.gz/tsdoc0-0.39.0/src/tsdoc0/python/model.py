from typing import Final, Iterable

from attrs import define, field

from tsdoc0.python.segment import Segment


# This converter wrapper-function is used because of a bug with the mypy-attrs plugin.
# https://github.com/python/mypy/issues/8389
def _tuple(iterable: Iterable[Segment]) -> tuple[Segment, ...]:
    return tuple(iterable)


# This class must be a non-slotted because there are several special attributes on
# model objects created by textX. All special attributes' names start with prefix _tx.
# https://textx.github.io/textX/3.1/model/#special-model-objects-attributes
@define(auto_attribs=True, kw_only=True, slots=False)
class Model:
    segments: Final[tuple[Segment, ...]] = field(converter=_tuple)
