from __future__ import annotations


import typing as tp

import numpy as np

from jijmodeling import (
    BinaryVar,
    ContinuousVar,
    IntegerVar,
    SemiContinuousVar,
    SemiIntegerVar,
)

DecisionVariable = tp.Union[
    BinaryVar, ContinuousVar, IntegerVar, SemiContinuousVar, SemiIntegerVar
]

NumberValue = tp.Union[int, float]
TensorValue = tp.Union[NumberValue, np.ndarray]
ListValue = tp.List[NumberValue]
NonZeroIndices = tp.Tuple[tp.List[int], ...]
NonZeroValues = tp.Union[tp.List[tp.Union[int, float]], tp.Union[int, float]]
Shape = tp.Tuple[int, ...]
SparseSolution = tp.Tuple[
    NonZeroIndices,
    NonZeroValues,
    Shape,
]
DenseSolution = np.ndarray

ForallIndexType = tp.Dict[str, tp.List[tp.List[int]]]
ForallValuesType = tp.Dict[str, tp.List[float]]
ConstraintExpressionValuesType = tp.Dict[str, tp.Dict[tp.Tuple[int, ...], float]]


VARIABLE_KEY = str
# User interface for values of instance data.
INSTANCE_DATA_INTERFACE = tp.Dict[VARIABLE_KEY, tp.Union[TensorValue, ListValue]]

DECI_VALUES_INTEREFACE = tp.Dict[tp.Union[str, DecisionVariable], TensorValue]
DECISION_VALUES = tp.Dict[DecisionVariable, TensorValue]

# fixed variable
# ex. fix array element : {"x": {(0, 1, 2): 1}} means x[0, 1, 2] = 1
#     fix scalar variable: {"y": {(): 0}} means y = 0
FIXED_VARS_INTERFACE = tp.Dict[
    str,
    tp.Dict[tp.Tuple[int, ...], NumberValue],
]
