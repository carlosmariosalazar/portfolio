# Ultrasound Clinic Data Generator

A sophisticated synthetic data generation system for ultrasound clinics that creates realistic patient and study data following real-world patterns, correlations, and business constraints.

## 🎯 Project Overview

This project generates synthetic medical data for ultrasound clinics using probabilistic models, temporal patterns, and preventive constraints. The system creates realistic patient demographics, study records, physician assignments, and referral sources while maintaining statistical accuracy and business rule compliance.

### Key Features

- **Probabilistic Data Generation**: Uses weighted distributions and correlations to model real-world patterns
- **Preventive Constraints**: Hard and soft constraints ensure data validity without rejection sampling
- **Temporal Patterns**: Models day-of-week, day-of-month, and seasonal variations
- **Growth Trends**: Simulates linear clinic growth over time with configurable noise
- **Bulk Generation**: Efficient batch processing for large-scale data seeding
- **Static & Dynamic Modes**: Historical data seeding and real-time generation
- **Type-Safe**: Full type annotations with Pydantic models
- **SOLID Architecture**: Clean, extensible design following best practices

## 🏗️ Architecture

### Core Components

1. **Probability Engine** (`probability_engine.py`)
   - Distribution strategies (Categorical, Weighted Ranges, Uniform)
   - Correlation management for conditional probabilities
   - Preventive constraint system (hard/soft enforcement)
   - Bulk selection with context-aware adjustments

2. **Config Management** (`config_manager.py`)
   - YAML/JSON config file parsing
   - Pydantic model validation
   - Type-safe configuration loading

3. **DTO-ORM Mappers** (`mappers.py`)
   - Unidirectional mapping system
   - CreateDTO → ORM (for database inserts)
   - ORM → QueryDTO (for API responses)

4. **Temporal Calculator** (planned)
   - Date-based volume calculation
   - Temporal weight application
   - Growth model implementation

5. **Entity Generators** (planned)
   - Patient generator
   - Study generator with relationships
   - Data orchestrator

## 🚀 Tech Stack

- **Python 3.10+**
- **Pydantic 2.x**: Data validation and settings management
- **PyYAML**: Configuration file parsing
- **Faker**: Realistic fake data generation
- **SQLAlchemy**: ORM for database persistence
- **Pytest**: Testing framework