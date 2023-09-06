import dataclasses
import typing as typ

import jijmodeling as jm
import jijmodeling_transpiler as jmt
from jijzeptlab.utils.jijmodeling import INSTANCE_DATA_INTERFACE, FIXED_VARS_INTERFACE

from jijzeptlab.jijzeptlab import (
    FixedVariables as FixedVariables,
    InstanceData as InstanceData,
)
from jijzeptlab.utils.baseclass import Option as Option


class CompileOption(Option):
    """Compile option

    Attributes:
        needs_normalize (bool): Whether to normalize the problem. Defaults to False.
    """

    needs_normalize: bool = False


class CompiledInstance:
    """Compiled instance

    Attributes:
        compile_option (CompileOption): Compile option
        problem (jm.Problem): Problem
        instance_data (InstanceData): Instance data
        fixed_variables (FixedVariables): Fixed variables
    """

    compile_option: CompileOption
    problem: jm.Problem
    instance_data: InstanceData
    fixed_variables: FixedVariables

    def __init__(
        self,
        engine_instance,
        compile_option: CompileOption,
        problem: jm.Problem,
        instance_data: InstanceData,
        fixed_variables: FixedVariables,
    ) -> None:
        self._instance = engine_instance
        self.compile_option = compile_option
        self.problem = problem
        self.instance_data = instance_data
        self.fixed_variables = fixed_variables

    def append_constraint(
        self,
        constraint: jm.Constraint,
        instance_data: typ.Union[InstanceData, INSTANCE_DATA_INTERFACE],
    ):
        """Append a constraint to the problem.
        Note that instance data attribute is updated.
        Args:
            constraint (jm.Constraint): Constraint to append.
            instance_data (InstanceData | INSTANCE_DATA_INTERFACE): Instance data.
        """
        raise NotImplementedError("append_constraint is not implemented.")

    def set_default_parameters(
        self,
        multipliers: dict[str, typ.Union[tuple[float, float], float]],
        needs_square_dict: dict[str, bool] = {},
    ):
        """Set default multipliers to the compiled instance.
        Suppose we have the following problem with objectives and constraints:
        min_x f(x) s.t. g_k(x) <= 0, k=1,...,K,
        The augumented Lagrangian is given by
        L(x, lambda) = f(x) + sum_{k=1}^K lambda_k g_k(x) + sum_{k=1}^K mu_k g_k(x)^2.
        This function sets the default multipliers lambda and mu to the compiled instance.
        For instance, if the multipliers are given by
        ```python
        multipliers = {"constraint_name": (1.0, 3.0)}
        ```
        where "constraint_name" is the name of the constraint, then the default multipliers are set as
        lambda_k = 1.0, mu_k = 3.0 for k=1,...,K.
        if the constraint name is not specified, then the default multipliers are set as
        lambda_k = 0.0, mu_k = 1.0 for k=1,...,K if the constraint is equality constraint, and
        lambda_k = 1.0, mu_k = 1.0 for k=1,...,K if the constraint is inequality constraint.
        Args:
            multipliers (dict[str, Union[tuple[float, float], float]]): Multipliers to be set.
            needs_square_dict (dict[str, bool]): If True, the corresponding constraint is squared. Defaults to True for linear constraints and False for nonlinear constraints.
        """
        raise NotImplementedError("set_default_parameter is not implemented.")

    def get_parameters(self) -> dict:
        """Get the parameters of the compiled instance.
        Returns:
            dict: Parameters.
        """
        raise NotImplementedError("get_parameters is not implemented.")

    def set_linear_parameter(self, label: str, indices: list[int], value: float):
        """Set the linear parameter of the compiled instance.
        Args:
            label (str): Label of the constraint.
            indices (list[int]): Indices of the constraint.
            value (float): Value of the parameter.
        """
        raise NotImplementedError("set_linear_parameter is not implemented.")

    def set_quad_parameter(self, label: str, indices: list[int], value: float):
        """Set the quadratic parameter of the compiled instance.
        Args:
            label (str): Label of the constraint.
            indices (list[int]): Indices of the constraint.
            value (float): Value of the parameter.
        """
        raise NotImplementedError("set_quad_parameter is not implemented.")

    def set_penalty_parameter(self, label: str, indices: list[int], value: float):
        """Set the penalty parameter of the compiled instance.
        Args:
            label (str): Label of the constraint.
            indices (list[int]): Indices of the constraint.
            value (float): Value of the parameter.
        """
        raise NotImplementedError("set_penalty_parameter is not implemented.")


def compile_model(
    problem: jm.Problem,
    instance_data: typ.Union[InstanceData, INSTANCE_DATA_INTERFACE],
    fixed_variables: typ.Optional[
        typ.Union[FixedVariables, FIXED_VARS_INTERFACE]
    ] = None,
    option: typ.Optional[CompileOption] = None,
) -> CompiledInstance:
    """Compile a problem

    Args:
        problem (jm.Problem): Problem to be compiled
        instance_data (InstanceData): Instance data
        fixed_variables (FixedVariables, optional): Fixed variables. Defaults to None.
        option (CompileOption, optional): Compile option. Defaults to None.

    Returns:
        CompiledInstance: Compiled instance
    """

    from jijzeptlab.process.process import BackendProcess

    _option: CompileOption
    if option is not None:
        _option = option
    else:
        _option = CompileOption()

    _fixed_vars: FixedVariables
    if fixed_variables is None:
        _fixed_vars = FixedVariables()
    elif isinstance(fixed_variables, dict):  # FIXED_VARS_INTERFACE
        _fixed_vars = FixedVariables.from_dict(fixed_variables)
    else:
        _fixed_vars = fixed_variables

    _instance_data: InstanceData
    if isinstance(instance_data, dict):  # INSTANCE_DATA_INTERFACE
        _instance_data = InstanceData.from_dict(instance_data)
    else:
        _instance_data = instance_data

    return BackendProcess.compile_model(problem, _instance_data, _fixed_vars, _option)
