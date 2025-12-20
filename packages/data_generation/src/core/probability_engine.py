"""Probability Engine for synthetic data generation.

This module implements a flexible probability system that reads distributions,
correlations, and constraints from configuration files and applies them during
data generation.
"""

import random
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T", str, int, float)


class DistributionType(StrEnum):
    """Supported probability distribution types."""

    CATEGORICAL = "categorical"
    WEIGHTED_RANGES = "weighted_ranges"
    UNIFORM = "uniform"


class RangeConfig(BaseModel):
    """Configuration for a weighted range.

    :ivar range: Min and max values [min, max]
    :vartype range: List[Union[int, float]]
    :ivar weight: Weight for this range
    :vartype weight: float
    """

    model_config = ConfigDict(frozen=False)

    range: List[Union[int, float]] = Field(min_length=2, max_length=2)
    weight: float = Field(default=1.0, gt=0)

    @field_validator("range")
    @classmethod
    def validate_range(cls, v: List[Union[int, float]]) -> List[Union[int, float]]:
        """Validate that min <= max value."""
        if len(v) == 2 and v[0] > v[1]:
            msg = f"Range min ({v[0]})  must be <= max ({v[1]})"
            raise ValueError(msg)
        return v


class DistributionConfig(BaseModel):
    """Configuration for a probability distribution.

    :ivar type: Type of distribution
    :vartype type: DistributionType
    :ivar weights: Category weights (for categorical)
    :vartype weights: Optional[Dict[str, float]]
    :ivar ranges: Range definitions (for weighted_ranges)
    :vartype ranges: Optional[List[RangeConfig]]
    """

    model_config = ConfigDict(frozen=False, use_enum_values=True)

    type: DistributionType
    weights: Optional[Dict[str, float]] = Field(default=None)
    ranges: Optional[List[RangeConfig]] = Field(default=None)

    @field_validator("weights")
    @classmethod
    def validate_weights(
        cls, v: Optional[Dict[str, float]]
    ) -> Optional[Dict[str, float]]:
        """Validate that all weights are positive."""
        if v is not None:
            for key, weight in v.items():
                if weight < 0:
                    msg = f"Weight for '{key}' must be non-negative, got {weight}"
                    raise ValueError(msg)
        return v


class ConditionConfig(BaseModel):
    """Configuration for a single condition.

    :ivar field: Field name to check
    :vartype field: Optional[str]
    :ivar value: Exact value to match
    :vartype value: Optional[Any]
    :ivar range: Range to match [min, max]
    :vartype range: Optional[List[Union[int, float]]]
    :ivar all: List of conditions (AND logic)
    :vartype all: Optional[List['ConditionConfig']]
    :ivar any: List of conditions (OR logic)
    :vartype any: Optional[List['ConditionConfig']]
    """

    model_config = ConfigDict(frozen=False)

    field: Optional[str] = None
    value: Optional[Any] = None
    range: Optional[List[Union[int, float]]] = None
    all: Optional[List["ConditionConfig"]] = None
    any: Optional[List["ConditionConfig"]] = None


class CorrelationConfig(BaseModel):
    """Configuration for conditional probability adjustments.

    :ivar condition: Conditions that trigger this correlation
    :vartype condition: ConditionConfig
    :ivar adjustments: New probability weights when conditions met
    :vartype adjustments: Dict[str, Dict[str, float]]
    """

    model_config = ConfigDict(frozen=False)

    condition: ConditionConfig
    adjustments: Dict[str, Dict[str, float]]


class ConstraintConfig(BaseModel):
    """Configuration for business rule constraints.

    :ivar type: Type of constraint (hard/soft/exclusion)
    :vartype type: str
    :ivar rule: Rule identifier
    :vartype rule: str
    :ivar params: Rule parameters
    :vartype params: Dict[str, Any]
    :ivar error_message: Error message for violations
    :vartype error_message: Optional[str]
    """

    model_config = ConfigDict(frozen=False)

    type: str = Field(pattern="^(hard|soft|exclusion)$")
    rule: str = Field(min_length=1)
    params: Dict[str, Any]
    error_message: Optional[str] = None


class ConstraintViolation(BaseModel):
    """Represents a constraint validation failure.

    :ivar constraint: The violated constraint
    :vartype constraint: ConstraintConfig
    :ivar entity_data: Data that violated the constraint
    :vartype entity_data: Dict[str, Any]
    :ivar message: Detailed error message
    :vartype message: str
    """

    model_config = ConfigDict(frozen=False)

    constraint: ConstraintConfig
    entity_data: Dict[str, Any]
    message: str


class DistributionStrategy(ABC, Generic[T]):
    """Abstract base class for probability distribution strategies.

    Each distribution type implements its own selection logic.
    """

    @abstractmethod
    def select(self, config: DistributionConfig) -> T:
        """Select a single value from the distribution.

        :param config: Distribution configuration
        :type config: DistributionConfig
        :return: Selected value
        :rtype: T
        """
        ...

    @abstractmethod
    def select_bulk(self, config: DistributionConfig, count: int) -> List[T]:
        """Select multiple values from the distribution efficiently.

        :param config: Distribution configuration
        :type config: DistributionConfig
        :param count: Number of values to select
        :type count: int
        :return: List of selected values
        :rtype: List[T]
        """
        ...


class CategoricalDistribution(DistributionStrategy[str]):
    """Categorical distribution with weighted random selection."""

    def select(self, config: DistributionConfig) -> str:
        """Select category using weighted random choice.

        :param config: Distribution configuration with weights
        :type config: DistributionConfig
        :return: Selected category
        :rtype: str
        :raises ValueError: If weights are not provided or invalid
        """
        if not config.weights:
            msg = "Categorical distribution requires weights"
            raise ValueError(msg)

        active_weights = {k: v for k, v in config.weights.items() if v > 0}

        if not active_weights:
            msg = "No valid categories with positive weights"
            raise ValueError(msg)

        total = sum(active_weights.values())
        normalized_weights = {k: v / total for k, v in active_weights.items()}

        categories = list(normalized_weights.keys())
        probabilities = list(normalized_weights.values())

        return random.choices(categories, weights=probabilities, k=1)[0]

    def select_bulk(self, config: DistributionConfig, count: int) -> List[str]:
        """Select multiple categories efficiently.

        :param config: Distribution configuration
        :type config: DistributionConfig
        :param count: Number of selections
        :type count: int
        :return: List of selected categories
        :rtype: List[str]
        """
        if not config.weights:
            msg = "Categorical distribution requires weights"
            raise ValueError(msg)

        active_weights = {k: v for k, v in config.weights.items() if v > 0}

        if not active_weights:
            msg = "No valid categories with positive weights"
            raise ValueError(msg)

        total = sum(active_weights.values())
        categories = list(active_weights.keys())
        probabilities = [active_weights[c] / total for c in categories]

        return random.choices(categories, weights=probabilities, k=count)


class WeightedRangesDistribution(DistributionStrategy[Union[int, float]]):
    """Distribution over numeric ranges with weights."""

    def select(self, config: DistributionConfig) -> Union[int, float]:
        """Select value from weighted ranges.

        :param config: Distribution configuration with ranges
        :type config: DistributionConfig
        :return: Selected value within a range
        :rtype: Union[int, float]
        :raises ValueError: If ranges are not provided or invalid
        """
        if not config.ranges:
            msg = "Weighted ranges distribution requires ranges"
            raise ValueError(msg)

        weights = [r.weight for r in config.ranges]
        selected_range = random.choices(config.ranges, weights=weights, k=1)[0]

        min_val, max_val = selected_range.range

        if isinstance(min_val, int) and isinstance(max_val, int):
            return random.randint(min_val, max_val)

        return random.uniform(float(min_val), float(max_val))

    def select_bulk(
        self, config: DistributionConfig, count: int
    ) -> List[Union[int, float]]:
        """Select multiple values from ranges efficiently.

        :param config: Distribution configuration
        :type config: DistributionConfig
        :param count: Number of selections
        :type count: int
        :return: List of selected values
        :rtype: List[Union[int, float]]
        """
        if not config.ranges:
            msg = "Weighted ranges distribution requires ranges"
            raise ValueError(msg)

        weights = [r.weight for r in config.ranges]
        selected_ranges = random.choices(config.ranges, weights=weights, k=count)

        results: List[Union[int, float]] = []
        for range_config in selected_ranges:
            min_val, max_val = range_config.range

            if isinstance(min_val, int) and isinstance(max_val, int):
                results.append(random.randint(min_val, max_val))
            else:
                results.append(random.uniform(float(min_val), float(max_val)))

        return results


class UniformDistribution(DistributionStrategy[str]):
    """Uniform distribution (all categories equally likely)."""

    def select(self, config: DistributionConfig) -> str:
        """Select uniformly from categories.

        :param config: Distribution configuration
        :type config: DistributionConfig
        :return: Selected category
        :rtype: str
        :raises ValueError: If weights are not provided
        """
        if not config.weights:
            msg = "Uniform distribution requires categories"
            raise ValueError(msg)

        # Filter out zero-weight categories
        active_categories = [k for k, v in config.weights.items() if v > 0]

        if not active_categories:
            msg = "No valid categories"
            raise ValueError(msg)

        return random.choice(active_categories)

    def select_bulk(self, config: DistributionConfig, count: int) -> List[str]:
        """Select uniformly in bulk.

        :param config: Distribution configuration
        :type config: DistributionConfig
        :param count: Number of selections
        :type count: int
        :return: List of selected categories
        :rtype: List[str]
        """
        if not config.weights:
            msg = "Uniform distribution requires categories"
            raise ValueError(msg)

        active_categories = [k for k, v in config.weights.items() if v > 0]

        if not active_categories:
            msg = "No valid categories"
            raise ValueError(msg)

        return random.choices(active_categories, k=count)


class ConstraintPreventer(ABC):
    """Abstract base class for preventive constraint strategies.

    Adjusts probability distributions to prevent constraint violations
    rather than validating after generation.
    """

    @abstractmethod
    def apply_prevention(
        self,
        constraint: ConstraintConfig,
        distribution_name: str,
        config: DistributionConfig,
        context: Dict[str, Any],
    ) -> DistributionConfig:
        """Apply preventive adjustments to distribution config.

        :param constraint: Constraint to prevent
        :type constraint: ConstraintConfig
        :param distribution_name: Name of distribution being adjusted
        :type distribution_name: str
        :param config: Current distribution configuration
        :type config: DistributionConfig
        :param context: Current entity context
        :type context: Dict[str, Any]
        :return: Adjusted distribution configuration
        :rtype: DistributionConfig
        """
        ...


class ProcedureGenderPreventer(ConstraintPreventer):
    """Prevents procedure-gender constraint violations."""

    def apply_prevention(
        self,
        constraint: ConstraintConfig,
        distribution_name: str,
        config: DistributionConfig,
        context: Dict[str, Any],
    ) -> DistributionConfig:
        """Prevent procedure selection that violates gender constraints.

        Example: If gender is male, set obstetric_ultrasound weight to 0.

        :param constraint: Constraint with procedure and required_gender
        :type constraint: ConstraintConfig
        :param distribution_name: Distribution being adjusted
        :type distribution_name: str
        :param config: Current distribution config
        :type config: DistributionConfig
        :param context: Context with 'gender' field
        :type context: Dict[str, Any]
        :return: Adjusted config with prevented procedures
        :rtype: DistributionConfig
        """
        if distribution_name != "procedures" or not config.weights:
            return config

        gender = context.get("gender")
        required_procedure = constraint.params.get("procedure")
        required_gender = constraint.params.get("required_gender")

        if gender and gender != required_gender and required_procedure:
            adjusted_config = config.model_copy(deep=True)
            if (
                adjusted_config.weights
                and required_procedure in adjusted_config.weights
            ):
                adjusted_config.weights[required_procedure] = 0.0
            return adjusted_config

        return config


class ProcedureAgeRangePreventer(ConstraintPreventer):
    """Prevents procedure-age range constraint violations."""

    def apply_prevention(
        self,
        constraint: ConstraintConfig,
        distribution_name: str,
        config: DistributionConfig,
        context: Dict[str, Any],
    ) -> DistributionConfig:
        """Prevent procedure selection that violates age constraints.

        Example: If age is 60, set obstetric_ultrasound weight to 0.

        :param constraint: Constraint with procedure, min_age, max_age
        :type constraint: ConstraintConfig
        :param distribution_name: Distribution being adjusted
        :type distribution_name: str
        :param config: Current distribution config
        :type config: DistributionConfig
        :param context: Context with `age` field
        :type context: Dict[str, Any]
        :return: Adjusted config with prevented procedures
        :rtype: DistributionConfig
        """
        # Only apply to procedure distributions
        if distribution_name != "procedures" or not config.weights:
            return config

        age = context.get("age")
        required_procedure = constraint.params.get("procedure")
        min_age = constraint.params.get("min_age")
        max_age = constraint.params.get("max_age")

        # If age is outside range, zero out the procedure
        if age is not None and required_procedure and (age < min_age or age > max_age):
            adjusted_config = config.model_copy(deep=True)
            if (
                adjusted_config.weights
                and required_procedure in adjusted_config.weights
            ):
                adjusted_config.weights[required_procedure] = 0.0
            return adjusted_config

        return config


class ProbabilityEngine:
    """Core probability engine with preventive constraints and bulk selection.

    Manages distributions, correlations, and preventive constraints for
    synthetic data generation.
    """

    def __init__(self) -> None:
        """Initialize the probability engine."""
        self._distributions: Dict[str, DistributionConfig] = {}
        self._correlations: List[CorrelationConfig] = []
        self._constraints: List[ConstraintConfig] = []

        # Strategy registries
        self._distribution_strategies: Dict[DistributionType, DistributionStrategy] = {
            DistributionType.CATEGORICAL: CategoricalDistribution(),
            DistributionType.WEIGHTED_RANGES: WeightedRangesDistribution(),
            DistributionType.UNIFORM: UniformDistribution(),
        }

        self._constraint_preventers: Dict[str, ConstraintPreventer] = {
            "if_procedure_then_gender": ProcedureGenderPreventer(),
            "if_procedure_then_age_range": ProcedureAgeRangePreventer(),
        }

    def register_distribution(self, name: str, config: DistributionConfig) -> None:
        """Register a probability distribution.

        :param name: Distribution identifier (e.g. "gender", "procedures")
        :type name: str
        :param config: Distribution configuration
        :type config: DistributionConfig
        """
        self._distributions[name] = config

    def register_correlation(self, config: CorrelationConfig) -> None:
        """Register a conditional probability correlation.

        :param config: Correlation configuration
        :type config: CorrelationConfig
        """
        self._correlations.append(config)

    def register_constraint(self, config: ConstraintConfig) -> None:
        """Register a preventive business rule constraint.

        :param config: Constraint configuration
        :type config: ConstraintConfig
        """
        self._constraints.append(config)

    def register_distribution_strategy(
        self, dist_type: DistributionType, strategy: DistributionStrategy
    ) -> None:
        """Register custom distribution strategy.

        :param dist_type: Distribution type identifier
        :type dist_type: DistributionType
        :param strategy: Strategy implementation
        :type strategy: DistributionStrategy
        """
        self._distribution_strategies[dist_type] = strategy

    def register_constraint_preventer(
        self, rule_name: str, preventer: ConstraintPreventer
    ) -> None:
        """Register custom constraint preventer.

        :param rule_name: Rule identifier
        :type rule_name: str
        :param preventer: Preventer implementation
        :type preventer: ConstraintPreventer
        """
        self._constraint_preventers[rule_name] = preventer

    def select_from_distribution(
        self, distribution_name: str, context: Optional[Dict[str, Any]] = None
    ) -> Union[str, int, float]:
        """Select single value from distribution with preventive constraints.

        :param distribution_name: Name of the distribution
        :type distribution_name: str
        :param context: Current entity context for correlations/constraints
        :type context: Optional[Dict[str, Any]]
        :return: Selected value
        :rtype: Union[str, int, float]
        :raises KeyError: If distribution not found
        """
        config = self._get_adjusted_config(distribution_name, context or {})
        strategy = self._get_strategy(config)
        return strategy.select(config)

    def select_bulk(
        self,
        distribution_name: str,
        count: int,
        contexts: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Union[str, int, float]]:
        """Select multiple values efficiently with optional per-item contexts.

        :param distribution_name: Name of the distribution
        :type distribution_name: str
        :param count: Number of values to select
        :type count: int
        :param contexts: Per-item contexts (must be length=count if provided)
        :type contexts: Optional[List[Dict[str, Any]]]
        :return: List of selected values
        :rtype: List[Union[str, int, float]]
        :raises ValueError: If contexts length doesn't match count
        """
        if contexts is not None and len(contexts) != count:
            msg= f"Contexts length ({len(contexts)}) must match count ({count})"
            raise ValueError(msg)

        # If no contexts, use bulk selection on base config
        if contexts is None:
            config = self._get_adjusted_config(distribution_name, {})
            strategy = self._get_strategy(config)
            return strategy.select_bulk(config, count)

        # With contexts, apply per-item adjustments
        results: List[Union[str, int, float]] = []
        for context in contexts:
            config = self._get_adjusted_config(distribution_name, context)
            strategy = self._get_strategy(config)
            results.append(strategy.select(config))

        return results

    def _get_adjusted_config(
        self, distribution_name: str, context: Dict[str, Any]
    ) -> DistributionConfig:
        """Get distribution config with correlations and preventive constraints applied.

        :param distribution_name: Distribution name
        :type distribution_name: str
        :param context: Current context
        :type context: Dict[str, Any]
        :return: Adjusted distribution config
        :rtype: DistributionConfig
        :raises KeyError: If distribution not found
        """
        if distribution_name not in self._distributions:
            msg = f"Distribution '{distribution_name}' not registered"
            raise KeyError(msg)

        # Start with base config
        config = self._distributions[distribution_name].model_copy(deep=True)

        # Apply correlations
        for correlation in self._correlations:
            if self._matches_conditions(correlation.condition, context):
                adjustments = correlation.adjustments.get(distribution_name, {})
                if adjustments and config.weights:
                    config.weights.update(adjustments)

        # Apply preventive constraints
        for constraint in self._constraints:
            if constraint.type != "hard":
                continue

            preventer = self._constraint_preventers.get(constraint.rule)
            if preventer:
                config = preventer.apply_prevention(
                    constraint, distribution_name, config, context
                )

        return config

    def _matches_conditions(
        self,
        condition: ConditionConfig,
        context: Dict[str, Any]
        ) -> bool:
        """Check if context matches correlation conditions.

        :param condition: Condition specification
        :type condition: ConditionConfig
        :param context: Current entity context
        :type context: Dict[str, Any]
        :return: True if conditions match
        :rtype: bool
        """
        # Handle 'all' conditions (AND logic)
        if condition.all:
            return all(
                self._matches_conditions(cond, context) for cond in condition.all
            )

        # Handle 'any' conditions (OR logic)
        if condition.any:
            return any(
                self._matches_conditions(cond, context) for cond in condition.any
            )

        # Handle single condition
        return self._matches_single_condition(condition, context)

    def _matches_single_condition(
        self,
        condition: ConditionConfig,
        context: Dict[str, Any]
        ) -> bool:
        """Check if context matches a single condition.

        :param condition: Condition specification
        :type condition: ConditionConfig
        :param context: Current entity context
        :type context: Dict[str, Any]
        :return: True if condition matches
        :rtype: bool
        """
        if not condition.field or condition.field not in context:
            return False

        context_value = context[condition.field]

        # Exact value match
        if condition.value is not None:
            return context_value == condition.value

        # Range match
        if condition.range:
            min_val, max_val = condition.range
            return min_val <= context_value <= max_val

        return False

    def _get_strategy(self, config: DistributionConfig) -> DistributionStrategy:
        """Get distribution strategy for config type.

        :param config: Distribution config
        :type config: DistributionConfig
        :return: Strategy instance
        :rtype: DistributionStrategy
        :raises ValueError: If strategy not found
        """
        strategy = self._distribution_strategies.get(config.type)
        if not strategy:
            msg = f"No strategy for distribution type: {config.type}"
            raise ValueError(msg)
        return strategy
