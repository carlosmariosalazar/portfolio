"""Shared module test fixtures."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml
from shared.src.dto.create import (
    CreateDocumentTypeDTO,
    CreateGenderDTO,
    CreatePatientDTO,
)
from shared.src.dto.query import (
    DocumentTypeQueryDTO,
    GenderQueryDTO,
    PatientQueryDTO,
)
from shared.src.mappers.base import MapperRegistry
from shared.src.mappers.mappers import (
    DocumentTypeToDTOMapper,
    DocumentTypeToORMMapper,
    GenderToDTOMapper,
    GenderToORMMapper,
    PatientToDTOMapper,
    PatientToORMMapper,
)
from shared.src.orm.lookup import (
    DocumentType,
    DocumentTypeAbbreviation,
    DocumentTypeName,
    Gender,
    GenderAbbreviation,
    GenderName,
)
from shared.src.orm.patient import Patient
from shared.src.utils.config_manager import ConfigManager


@pytest.fixture
def tmp_path() -> Path:
    """Create a temporal path for storing test config files.

    :return: Temporal path
    :rtype: Path
    """
    path = Path(__file__).parent / "tmp"
    path.mkdir(parents=False, exist_ok=True)
    return path


@pytest.fixture
def valid_db_config_data() -> Dict[str, Any]:
    """Provide a valid test configuration data.

    :return: Valid config dictionary
    :rtype: Dict[str,Any]
    """
    return {
        "host": "localhost",
        "port": 4321,
        "database": "testdb",
        "username": "admin",
        "password": "123",
    }


@pytest.fixture
def valid_app_config_data() -> Dict[str, Any]:
    """Provide a valid test application configuration data.

    :return: Valid config dictionary
    :rtype: Dict[str, Any]
    """
    return {"app_name": "app", "debug": True, "log_level": "DEBUG"}


@pytest.fixture
def invalid_config_data() -> Dict[str, Any]:
    """Provide invalid configurationd data.

    :return: Invalid config dictionary with missing fields
    :rtype: Dict[str, Any]
    """
    return {
        "host": "localhost",
        "port": "invalid_port",
        "database": "testdb",
    }


@pytest.fixture
def tmp_json_config(tmp_path: Path, valid_db_config_data: Dict[str, Any]) -> Path:
    """Write a valid JSON config in a temporary path.

    :param tmp_path: Temporary path for testing
    :type tmp_path: Path
    :param valid_db_config_data: Valid config dictionary
    :type valid_db_config_data: Dict[str, Any]
    """
    config_file_path = tmp_path / "config.json"

    with config_file_path.open(mode="w", encoding="utf-8") as f:
        json.dump(valid_db_config_data, f, indent=4)
    return config_file_path


@pytest.fixture
def tmp_yaml_config(tmp_path: Path, valid_app_config_data: Dict[str, Any]) -> Path:
    """Create a temporary YAML config file.

    :param tmp_path: Temporary path for testing
    :type tmp_path: Path
    :param valid_app_config_data: Valid config data
    :type valid_app_config_data: Dict[str, Any]
    :return: Path to temporary YAML file
    :rtype: Path
    """
    config_file = tmp_path / "config.yaml"
    with config_file.open("w", encoding="utf-8") as f:
        yaml.dump(valid_app_config_data, f)
    return config_file


@pytest.fixture
def tmp_invalid_json_config(
    tmp_path: Path, invalid_config_data: Dict[str, Any]
) -> Path:
    """Write an invalid JSON config in a temporary path.

    :param tmp_path: Temporary path
    :type tmp_path: Path
    :param invalid_db_config_data: Invalid config dictionary
    :type invalid_db_config_data: Dict[str, Any]
    """
    config_file_path = tmp_path / "invalid_config.json"

    with config_file_path.open(mode="w", encoding="utf-8") as f:
        json.dump(invalid_config_data, f, indent=4)
    return config_file_path


@pytest.fixture
def tmp_invalid_json(tmp_path: Path) -> Path:
    """Create a temporary invalid JSON file.

    :param tmp_path: Pytest's temporary directory fixture
    :type tmp_path: Path
    :return: Path to temporary invalid JSON file
    :rtype: Path
    """
    config_file = tmp_path / "invalid.json"

    with config_file.open("w", encoding="utf-8") as f:
        f.write("{invalid json content")
    return config_file


@pytest.fixture
def config_manager() -> ConfigManager:
    """Provide a `ConfigManager` instance.

    :return: `ConfigManager` instance
    :rtype: ConfigManager
    """
    return ConfigManager()


# --- Mapper fixtures ---

@pytest.fixture
def create_gender_dto() ->  CreateGenderDTO:
    """Provide a valid Gender create DTO.

    :return: Create gender DTO
    :rtype: GenderQueryDTO
    """
    return CreateGenderDTO(
        gender_abb= "M",
        gender_name= "MALE"
        )

@pytest.fixture
def gender_orm() -> Gender:
    """Provide a valid Gender ORM instance.

    :return: Gender ORM instance
    :rtype: Gender
    """
    gender = Gender()
    gender.id_gender = 1
    gender.gender_abb = GenderAbbreviation.MALE
    gender.gender_name = GenderName.MALE
    return gender

@pytest.fixture
def document_type_orm() -> DocumentType:
    """Provide a valid Document type ORM instance.

    :return: Document type ORM instance
    :rtype: DocumentType
    """
    document_type = DocumentType()
    document_type.id_document_type = 1
    document_type.document_type_abb = DocumentTypeAbbreviation.CEDULA_DE_CIUDADANIA
    document_type.document_type_name = DocumentTypeName.CEDULA_DE_CIUDADANIA
    return document_type

@pytest.fixture
def create_patient_dto() -> CreatePatientDTO:
    """Provide a valid Patient create DTO.

    :return: Patient create DTO
    :rtype: CreatePatientDTO

    """
    return CreatePatientDTO(
        id_document_type= 1,
        identification= "123",
        id_gender= 1,
        date_of_birth= datetime.now(tz= timezone.utc).date(),
        name= "TEST PATIENT"
    )

@pytest.fixture
def patient_orm(gender_orm: Gender, document_type_orm: DocumentType) -> Patient:
    """Provide a valid Patient ORM instance.

    :return: Patient ORM instance
    :rtype: Patient
    """
    patient = Patient()
    patient.id_patient = 1
    patient.id_document_type = 1
    patient.identification = "123"
    patient.id_gender = 1
    patient.date_of_birth = datetime.now(tz= timezone.utc).date()
    patient.name = "TEST PATIENT"

    patient.patient_gender = gender_orm
    patient.patient_document_type = document_type_orm

    return patient

@pytest.fixture
def mapper_registry() -> MapperRegistry:
    """Provide a fresh Mapper Registry with all mappers registered.

    :return: Configured Mapper registry
    :rtype: MapperRegistry
    """
    registry = MapperRegistry()

    gender_to_dto = GenderToDTOMapper()
    document_type_to_dto = DocumentTypeToDTOMapper()

    registry.register_to_dto(Gender, GenderQueryDTO, gender_to_dto)
    registry.register_to_dto(
        DocumentType,
        DocumentTypeQueryDTO,
        DocumentTypeToDTOMapper()
        )
    registry.register_to_dto(
        Patient,
        PatientQueryDTO,
        PatientToDTOMapper(gender_to_dto, document_type_to_dto)
        )

    registry.register_to_orm(CreateGenderDTO, Gender, GenderToORMMapper())
    registry.register_to_orm(
        CreateDocumentTypeDTO,
        DocumentType,
        DocumentTypeToORMMapper()
        )
    registry.register_to_orm(CreatePatientDTO, Patient, PatientToORMMapper())

    return registry
