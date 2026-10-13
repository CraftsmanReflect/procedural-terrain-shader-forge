"""ShaderStage — the contract every shader stage plugin implements."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ShaderStage(ABC):
    """A GLSL stage pair (vertex + fragment) plus its uniform contract.

    The pipeline compiles `vertex_src` + `fragment_src` with the configured
    GLSL version prepended. `uniform_contract` maps uniform names to
    (type_str, default) so the binder can allocate + validate.
    """

    name: str = "unnamed"

    @property
    @abstractmethod
    def vertex_src(self) -> str: ...

    @property
    @abstractmethod
    def fragment_src(self) -> str: ...

    @property
    def uniform_contract(self) -> dict[str, tuple[str, Any]]:
        """name -> (glsl_type, default_value)."""
        return {}
</｜｜DSML｜｜ parameter>
</invoke>