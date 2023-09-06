from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from jijmodeling import SampleSet
from jijzeptlab.compile import CompiledInstance
from jijzeptlab.utils.baseclass import Option, Result

from typing import List, Literal


class VASamplerOption(Option):
    """Options to create a VASampler.
    This VASampler

    Attributes:
        num_reads (Optional[int]): Number of reads. Defaults to None.
        num_sweeps (Optional[int]): Number of sweeps. Defaults to None.
        beta_range (Optional[list]): Beta range. Defaults to None.
        beta_list (Optional[List[float]]): Beta list. Defaults to None.
        init_spin (Optional[Dict[str, int]]): Initial spin. Defaults to None.
        dense (Optional[bool]): Dense. Defaults to None.
        num_threads (Optional[int]): Number of threads. Defaults to None.
        vector_mode (Optional[Literal["speed", "accuracy"]]): Vector mode. Defaults to None.
        timeout (Optional[int]): Timeout. Defaults to None.
    """

    num_reads: Optional[int] = None
    num_results: Optional[int] = None
    num_sweeps: Optional[int] = None
    beta_range: Optional[list] = None
    beta_list: Optional[List[float]] = None
    init_spin: Optional[Dict[str, int]] = None
    dense: Optional[bool] = None
    num_threads: Optional[int] = None
    vector_mode: Optional[Literal["speed", "accuracy"]] = None
    timeout: Optional[int] = None


@dataclass(frozen=True)
class VAModel:
    """Model for VASampler.

    Attributes:
        compiled_instance (CompiledInstance): CompiledInstance
    """

    compiled_instance: CompiledInstance


@dataclass(frozen=True)
class VAResult(Result):
    """Result of VASampler."""

    sample_set: SampleSet

    def to_sample_set(self) -> SampleSet:
        return self.sample_set


def create_model(compiled_instance: CompiledInstance) -> VAModel:
    """Create a model for VASampler.

    Args:
        compiled_instance (CompiledInstance): CompiledInstance

    Returns:
        VAModel: VAModel
    """
    raise NotImplementedError("VASampler is not implemented yet.")


def sample(
    model: VAModel,
    option: Optional[VASamplerOption] = None,
    needs_square_constraints: dict[str, bool] = {},
) -> VAResult:
    """Sample by VASampler.

    Args:
        model (VAModel): VAModel
        option (Optional[VASamplerOption], optional): Option. Defaults to None.
        needs_square_constraints: (dict[str, bool]): This dictionary object is utilized to determine whether to square the constraint condition while incorporating it into the QUBO/HUBO penalty term. Here, the constraint's name is used as the key. If the value is set to True, the corresponding constraint is squared upon its addition to the QUBO/HUBO penalty term. By default, the value is set to True for linear constraints, and to False for non-linear ones.

    Returns:
        VAResult: VAResult
    """
    raise NotImplementedError("VASampler is not implemented yet.")
