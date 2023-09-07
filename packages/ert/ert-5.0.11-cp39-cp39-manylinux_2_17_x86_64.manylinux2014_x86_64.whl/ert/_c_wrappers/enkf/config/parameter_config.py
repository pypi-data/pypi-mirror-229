from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict

    from ert.storage import EnsembleAccessor, EnsembleReader


class CustomDict(dict):
    """Used for converting types that can not be serialized
    directly to json
    """

    def __init__(self, data):
        for i, (key, value) in enumerate(data):
            if isinstance(value, Path):
                data[i] = (key, str(value))
        super().__init__(data)


@dataclasses.dataclass
class ParameterConfig(ABC):
    name: str
    forward_init: bool

    @abstractmethod
    def load(self, run_path: Path, real_nr: int, ensemble: EnsembleAccessor):
        ...

    @abstractmethod
    def save(self, run_path: Path, real_nr: int, ensemble: EnsembleReader):
        ...

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self, dict_factory=CustomDict)

    def save_experiment_data(
        self,
        experiment_path: Path,
    ):
        pass
