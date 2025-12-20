"""Data generation module fixtures."""

import random

import pytest
from data_generation.src.core.probability_engine import (
    DistributionConfig,
    DistributionType,
    ProbabilityEngine,
    RangeConfig,
)


@pytest.fixture(autouse= True)
def seed() -> None:
    """Set seed automatically."""
    random.seed(42)


@pytest.fixture
def engine() -> ProbabilityEngine:
    """Provide a fresh Probability Engine instance.

    :return: ProbabilityEngine instance
    :rtype: ProbabilityEngine
    """
    return ProbabilityEngine()


@pytest.fixture
def gender_distribution() -> DistributionConfig:
    """Provide a gender distribution config.

    :return: Gender distribution
    :rtype: DistributionConfig
    """
    return DistributionConfig(
        type= DistributionType.CATEGORICAL,
        weights= {"female": 0.65, "male": 0.35}
    )


@pytest.fixture
def age_distribution() -> DistributionConfig:
    """Provide an age distribution config.

    :return: Age distribution
    :rtype: DistributionConfig
    """
    return DistributionConfig(
        type=DistributionType.WEIGHTED_RANGES,
        ranges=[
            RangeConfig(range=[0, 18], weight=0.10),
            RangeConfig(range=[19, 35], weight=0.25),
            RangeConfig(range=[36, 55], weight=0.35),
            RangeConfig(range=[56, 75], weight=0.20),
            RangeConfig(range=[76, 100], weight=0.10),
        ]
    )


@pytest.fixture
def procedure_distribution() -> DistributionConfig:
    """Provide a procedure distribution config.

    :return: Procedure distribution
    :rtype: DistributionConfig
    """
    return DistributionConfig(
        type=DistributionType.CATEGORICAL,
        weights={
            "obstetric_ultrasound": 0.30,
            "abdominal_ultrasound": 0.20,
            "cardiac_echo": 0.15,
            "thyroid_ultrasound": 0.15,
            "pelvic_ultrasound": 0.20,
        }
    )
