from collections import Counter
from typing import List, Union

import pytest
from data_generation.src.core.probability_engine import (
    CategoricalDistribution,
    ConditionConfig,
    ConstraintConfig,
    CorrelationConfig,
    DistributionConfig,
    DistributionType,
    ProbabilityEngine,
    ProcedureAgeRangePreventer,
    ProcedureGenderPreventer,
    RangeConfig,
    WeightedRangesDistribution,
)
from pydantic import ValidationError


class TestRangeConfig:
    """Test suite for RangeConfig."""

    @pytest.mark.parametrize(
            argnames= ("_range"),
            argvalues= [
                [],
                [1.0],
                [1.0, 2.0, 3.0],
                ]
        )
    def test_range_field_lenght(self, _range: List[Union[int,float]]) -> None:
        """Test that invalid range array lenght raise ValidationError"""

        with pytest.raises(ValidationError) as _:
            RangeConfig(range = _range, weight= 0.5)

    def test_weight_field_greater_than_zero(self) -> None:
        """Test that negative weights raise ValidationError"""

        with pytest.raises(ValidationError) as _:
            RangeConfig(range= [1.0, 2.0], weight= -0.1)

    def test_range_field_validator(self) -> None:
        """Test that min value grater than max value raise ValueError"""

        with pytest.raises(ValueError, match= "Range min") as _:
            RangeConfig(range = [2.0, 1.0], weight= 0.5)

class TestDistributionConfig:
    """Test suite for DistributionConfig."""

    def test_distribution_config_negative_weights(self) -> None:
        """Test that negative weights raise ValidationError."""

        weights = {"a": -0.1, "b": 0.1}

        with pytest.raises(ValueError, match= "must be non-negative") as _:
            DistributionConfig(type= DistributionType.CATEGORICAL, weights= weights)

class TestCategoricalDistribution:
    """Test suite for CategoricalDistribution."""

    def test_select_respects_weights(self) -> None:
        """Test that selecion respects probability weights."""

        config = DistributionConfig(
            type= DistributionType.CATEGORICAL,
            weights= {"a": 0.9, "b": 0.05, "c": 0.05}
        )
        distribution = CategoricalDistribution()
        selection = distribution.select(config)

        assert selection in config.weights # type: ignore
        assert selection == "a"

    def test_select_bulk_respects_weights(self) -> None:
        """Test select bulk method respects weights."""

        config = DistributionConfig(
            type= DistributionType.CATEGORICAL,
            weights= {"a": 0.9, "b": 0.05, "c": 0.05}
        )
        distribution = CategoricalDistribution()
        selections = distribution.select_bulk(config, count= 50)

        counts = Counter(selections)

        assert counts["a"] > counts["b"]
        assert counts["a"] > counts["c"]


    def test_select_weights_not_loaded(self) -> None:
        """Test missing weights raises ValueError."""

        distribution = CategoricalDistribution()
        config = DistributionConfig(
            type= DistributionType.CATEGORICAL,
        )
        with pytest.raises(ValueError, match= "requires weights") as _:
            distribution.select(config)

    def test_select_negative_weights(self) -> None:
        """Test error when weights are negative values in select method."""

        distribution = CategoricalDistribution()
        config = DistributionConfig(
            type= DistributionType.CATEGORICAL,
        )
        config.weights = {"a": -0.1, "b": -0.2}

        with pytest.raises(ValueError, match= "No valid categories") as _:
            distribution.select(config)

class TestWeightedRangesDistribution:
    """Test WeightedRangesDistribution strategy."""

    def test_select_integer_range(self) -> None:
        """Test selecting from integer range."""
        config = DistributionConfig(
            type=DistributionType.WEIGHTED_RANGES,
            ranges=[RangeConfig(range=[10, 20], weight=1.0)]
        )
        strategy = WeightedRangesDistribution()

        result = strategy.select(config)

        assert isinstance(result, int)
        assert 10 <= result <= 20

    def test_select_float_range(self) -> None:
        """Test selecting from float range."""
        config = DistributionConfig(
            type=DistributionType.WEIGHTED_RANGES,
            ranges=[RangeConfig(range=[10.5, 20.5], weight=1.0)]
        )
        strategy = WeightedRangesDistribution()

        result = strategy.select(config)

        assert isinstance(result, float)
        assert 10.5 <= result <= 20.5

    def test_select_respects_range_weights(self) -> None:
        """Test that selection respects range weights."""
        config = DistributionConfig(
            type=DistributionType.WEIGHTED_RANGES,
            ranges=[
                RangeConfig(range=[0, 10], weight=0.9),
                RangeConfig(range=[90, 100], weight=0.1),
            ]
        )
        strategy = WeightedRangesDistribution()

        samples = [strategy.select(config) for _ in range(1000)]

        # Most should be in [0, 10] range
        in_first_range = sum(1 for s in samples if 0 <= s <= 10)
        assert in_first_range > 800

    def test_select_bulk(self) -> None:
        """Test bulk selection from ranges."""
        config = DistributionConfig(
            type=DistributionType.WEIGHTED_RANGES,
            ranges=[RangeConfig(range=[0, 100], weight=1.0)]
        )
        strategy = WeightedRangesDistribution()

        results = strategy.select_bulk(config, count=50)

        assert len(results) == 50
        assert all(0 <= r <= 100 for r in results)

class TestProbabilityEngineBasics:
    """Test basic ProbabilityEngine operations."""

    def test_register_and_select_distribution(
        self,
        engine: ProbabilityEngine,
        gender_distribution: DistributionConfig
    ) -> None:
        """Test registering and selecting from distribution."""
        engine.register_distribution("gender", gender_distribution)

        result = engine.select_from_distribution("gender")

        assert result in ["female", "male"]

    def test_select_nonexistent_distribution_raises_error(
        self,
        engine: ProbabilityEngine
    ) -> None:
        """Test selecting from unregistered distribution raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            engine.select_from_distribution("nonexistent")

        assert "not registered" in str(exc_info.value)

    def test_bulk_selection_without_contexts(
        self,
        engine: ProbabilityEngine,
        gender_distribution: DistributionConfig
    ) -> None:
        """Test bulk selection without contexts."""
        engine.register_distribution("gender", gender_distribution)

        results = engine.select_bulk("gender", count=100)

        assert len(results) == 100
        assert all(r in ["female", "male"] for r in results)

    def test_bulk_selection_with_contexts(
        self,
        engine: ProbabilityEngine,
        procedure_distribution: DistributionConfig
    ) -> None:
        """Test bulk selection with contexts."""
        engine.register_distribution("procedures", procedure_distribution)

        contexts = [{"gender": "female"} for _ in range(10)]
        results = engine.select_bulk("procedures", count=10, contexts=contexts)

        assert len(results) == 10

    def test_bulk_selection_contexts_length_mismatch_raises_error(
        self,
        engine: ProbabilityEngine,
        gender_distribution: DistributionConfig
    ) -> None:
        """Test that mismatched contexts length raises ValueError."""
        engine.register_distribution("gender", gender_distribution)

        contexts = [{"test": "value"}] * 5

        with pytest.raises(ValueError, match= "must match count") as _:
            engine.select_bulk("gender", count=10, contexts=contexts)

class TestCorrelations:
    """Test correlation functionality."""

    def test_correlation_adjusts_probabilities(
        self,
        engine: ProbabilityEngine,
        procedure_distribution: DistributionConfig
    ) -> None:
        """Test that correlations adjust distribution probabilities."""
        engine.register_distribution("procedures", procedure_distribution)

        # Register correlation: females more likely to get obstetric
        correlation = CorrelationConfig(
            condition= ConditionConfig(field="gender", value="female"),
            adjustments= {
                "procedures": {"obstetric_ultrasound": 1.5}
            }
        )
        engine.register_correlation(correlation)

        # Generate with female context
        context = {"gender": "female"}
        samples = [
            engine.select_from_distribution("procedures", context)
            for _ in range(100)
        ]

        counter = Counter(samples)
        obstetric_count = counter.get("obstetric_ultrasound", 0)

        # Should be high due to correlation
        assert obstetric_count > 60

    def test_correlation_with_range_condition(
        self,
        engine: ProbabilityEngine,
        procedure_distribution: DistributionConfig
    ) -> None:
        """Test correlation with age range condition."""
        engine.register_distribution("procedures", procedure_distribution)

        # Young age → more obstetric
        correlation = CorrelationConfig(
            condition=ConditionConfig(field="age", range=[20, 40]),
            adjustments={
                "procedures": {"obstetric_ultrasound": 0.95}
            }
        )
        engine.register_correlation(correlation)

        # Test with age 30 (in range)
        context = {"age": 30}
        samples = [
            engine.select_from_distribution("procedures", context)
            for _ in range(100)
        ]

        counter = Counter(samples)
        assert counter["obstetric_ultrasound"] > 60

    def test_multiple_correlations_stack(
        self,
        engine: ProbabilityEngine,
        procedure_distribution: DistributionConfig
    ) -> None:
        """Test that multiple correlations can stack."""
        engine.register_distribution("procedures", procedure_distribution)

        # Correlation 1: Female
        corr1 = CorrelationConfig(
            condition=ConditionConfig(field="gender", value="female"),
            adjustments={"procedures": {"pelvic_ultrasound": 0.60}}
        )
        engine.register_correlation(corr1)

        # Correlation 2: Age range
        corr2 = CorrelationConfig(
            condition=ConditionConfig(field="age", range=[30, 50]),
            adjustments={"procedures": {"pelvic_ultrasound": 0.70}}
        )
        engine.register_correlation(corr2)

        # Both conditions met
        context = {"gender": "female", "age": 35}
        samples = [
            engine.select_from_distribution("procedures", context)
            for _ in range(500)
        ]

        counter = Counter(samples)
        # Last correlation wins (0.50)
        assert counter["pelvic_ultrasound"] > 200

class TestConstraintPreventers:

    def test_procedure_gender_preventer(
            self,
            engine: ProbabilityEngine,
            procedure_distribution: DistributionConfig
        ) -> None:
        """Test procedure-gender prevention."""

        constraint = ConstraintConfig(
            rule= "procedure_requires_gender",
            params= {
                "procedure": "obstetric_ultrasound",
                "required_gender": "female"
                }
            )

        engine.register_distribution("procedures", procedure_distribution)
        engine.register_constraint(config= constraint)

        engine.register_constraint_preventer(
            rule_name= "procedure_requires_gender",
            preventer= ProcedureGenderPreventer()
            )

        context = {"gender": "male"}

        samples = [
            engine.select_from_distribution("procedures", context)
            for _ in range(100)
            ]

        counter = Counter(samples)

        assert "obstetric_ultrasound" not in counter

    def test_age_range_preventer(
            self,
            engine: ProbabilityEngine,
            procedure_distribution: DistributionConfig,
            age_distribution: DistributionConfig
        ) -> None:
        """Test procedure-age prevention."""

        engine.register_distribution("procedures", procedure_distribution)
        engine.register_distribution("age", age_distribution)

        config = ConstraintConfig(
            rule= "procedure_requires_age_range",
            params= {
                "procedure": "obstetric_ultrasound",
                "min_age": 15,
                "max_age": 50
                }
            )
        engine.register_constraint(config)

        engine.register_constraint_preventer(
            rule_name= "procedure_requires_age_range",
            preventer= ProcedureAgeRangePreventer()
        )

        context_list = [
            {"age": engine.select_from_distribution("age")} for _ in range(100)
            ]

        samples = [
            engine.select_from_distribution("procedures",context)
            for context in context_list
            ]

        procedure_ages = [
            context["age"]
            for procedure, context in zip(samples, context_list)
            if procedure == "obstetric_ultrasound"
            and isinstance(context["age"], (int, float))
            ]

        assert all(15 <= age <= 50 for age in procedure_ages)

