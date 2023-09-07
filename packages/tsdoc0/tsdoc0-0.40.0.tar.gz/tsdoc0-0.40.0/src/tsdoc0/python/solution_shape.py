from typing import Final, Iterable, Optional

from attrs import define, field

from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.solution_item import SolutionItem
from tsdoc0.python.solution_pseudocode import SolutionPseudocode
from tsdoc0.python.utils import repr_parent


# This converter wrapper-function is used because of a bug with the mypy-attrs plugin.
# https://github.com/python/mypy/issues/8389
#
# The Segment type is used instead of a generic type because of another bug with the
# mypy-attrs plugin.
# https://github.com/python/mypy/issues/8625#issuecomment-632720205
def _tuple(iterable: Iterable[Segment]) -> tuple[Segment, ...]:
    return tuple(iterable)


@define(auto_attribs=True, kw_only=True)
class SolutionShape(Segment):
    parent: Optional[Model] = field(eq=False, repr=repr_parent)
    indentation: Final[str]
    pseudocodes: Final[tuple[SolutionPseudocode, ...]] = field(converter=_tuple)
    items: Final[tuple[SolutionItem, ...]] = field(converter=_tuple)

    @property
    def answer(self) -> str:
        pseudocodes = "\n".join(pseudocode.text for pseudocode in self.pseudocodes)
        items = "\n".join(f"{item.key}: {item.value}" for item in self.items)

        return f"```\n{pseudocodes}\n\n{items}\n```"

    @property
    def callout(self) -> str:
        pseudocodes = "\n".join(pseudocode.text for pseudocode in self.pseudocodes)
        items = "\n".join(f"{item.key}: `{item.value}`" for item in self.items)

        return f"```\n{pseudocodes}\n```\n\n{items}"
