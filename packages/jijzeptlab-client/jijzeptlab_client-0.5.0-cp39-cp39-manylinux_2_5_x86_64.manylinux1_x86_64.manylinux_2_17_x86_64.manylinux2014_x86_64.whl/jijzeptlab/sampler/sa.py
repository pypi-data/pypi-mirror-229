from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from jijmodeling import SampleSet
from jijzeptlab.compile import CompiledInstance
from jijzeptlab.utils.baseclass import Option, Result


class SASamplerOption(Option):
    """Options to create a SASampler.

    Attributes:
        beta_min (float, optional): Minimum beta. Defaults to None.
        beta_max (float, optional): Maximum beta. Defaults to None.
        num_sweeps (int, optional): Number of sweeps. Defaults to None.
        num_reads (int, optional): Number of reads. Defaults to None.
        initial_state (list | dict, optional): Initial state. Defaults to None.
        updater (str, optional): Updater. Defaults to None.
        sparse (bool, optional): Sparse. Defaults to None.
        reinitialize_state (bool, optional): Reinitialize state. Defaults to None.
        seed (int, optional): Seed. Defaults to None.
    """

    beta_min: Optional[float] = None
    beta_max: Optional[float] = None
    num_sweeps: Optional[int] = None
    num_reads: Optional[int] = None
    initial_state: Optional[Union[list, dict]] = None
    updater: Optional[str] = None
    sparse: Optional[bool] = None
    reinitialize_state: Optional[bool] = None
    seed: Optional[int] = None


@dataclass(frozen=True)
class SAModel:
    """Model for SASampler.

    Attributes:
        compiled_instance (CompiledInstance): CompiledInstance
    """

    compiled_instance: CompiledInstance


@dataclass(frozen=True)
class SAResult(Result):
    """Result of SASampler."""

    sample_set: SampleSet

    def to_sample_set(self) -> SampleSet:
        return self.sample_set


def create_model(compiled_instance: CompiledInstance) -> SAModel:
    """Create a model for SASampler.

    Args:
        compiled_instance (CompiledInstance): CompiledInstance

    Returns:
        SAModel: SAModel
    """
    raise NotImplementedError("SASampler is not implemented yet.")


def sample(
    model: SAModel,
    option: Optional[SASamplerOption] = None,
    needs_square_constraints: dict[str, bool] = {},
) -> SAResult:
    """Sample by SASampler.

    Args:
        model (SAModel): SAModel
        option (Optional[SASamplerOption], optional): Option. Defaults to None.
        needs_square_constraints: (dict[str, bool]): This dictionary object is utilized to determine whether to square the constraint condition while incorporating it into the QUBO/HUBO penalty term. Here, the constraint's name is used as the key. If the value is set to True, the corresponding constraint is squared upon its addition to the QUBO/HUBO penalty term. By default, the value is set to True for linear constraints, and to False for non-linear ones.

    Returns:
        SAResult: SAResult
    """
    raise NotImplementedError("SASampler is not implemented yet.")
