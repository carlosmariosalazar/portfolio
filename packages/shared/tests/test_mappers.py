from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from shared.src.dto.create import CreateGenderDTO, CreatePatientDTO
from shared.src.dto.query import DocumentTypeQueryDTO, GenderQueryDTO, PatientQueryDTO
from shared.src.mappers.base import AutoToDTOMapper, AutoToORMMapper, MapperRegistry
from shared.src.mappers.mappers import (
    DocumentTypeToDTOMapper,
    GenderToDTOMapper,
    GenderToORMMapper,
    PatientToDTOMapper,
    PatientToORMMapper,
)
from shared.src.orm.lookup import Gender, GenderAbbreviation, GenderName
from shared.src.orm.patient import Patient


class TestAutoToORMMapper:
    """Test suite for AutoToORMMapper."""

    def test_map_dto_to_orm(self, create_gender_dto: CreateGenderDTO) -> None:
        """Test that mapper creates a new ORM instance with DTO data."""
        mapper = AutoToORMMapper(CreateGenderDTO, Gender)
        gender_orm = mapper.to_orm(dto= create_gender_dto)

        assert isinstance(gender_orm, Gender)
        assert gender_orm.gender_abb == create_gender_dto.gender_abb
        assert gender_orm.gender_name == create_gender_dto.gender_name

    def test_map_creates_new_instance_every_call(
            self,
            create_gender_dto: CreateGenderDTO
            ) -> None:
        """Test that each call creates a new ORM instance."""
        mapper = AutoToORMMapper(CreateGenderDTO, Gender)

        orm1 = mapper.to_orm(dto= create_gender_dto)
        orm2 = mapper.to_orm(dto= create_gender_dto)

        assert orm1 is not orm2
        assert id(orm1) != id(orm2)

    def test_applies_field_transformers(self) -> None:

        dto = CreateGenderDTO(gender_abb= "f", gender_name= "female")

        transformers = {
            "gender_abb": lambda x: x.upper(),
            "gender_name": lambda x: x.upper()
        }

        mapper = AutoToORMMapper(
            dto_class= CreateGenderDTO,
            orm_class= Gender,
            field_transformers= transformers
            )

        orm = mapper.to_orm(dto)

        assert orm.gender_abb == "F"
        assert orm.gender_name == "FEMALE"


class TestAutoToDtoMapper:
    """Test suite for AutoToDtoMapper."""

    def test_maps_orm_to_dto(self, gender_orm: Gender) -> None:
        """Test that mapper converts ORM to Query DTO."""
        mapper = AutoToDTOMapper(Gender, GenderQueryDTO)
        gender_dto = mapper.to_dto(gender_orm)

        assert isinstance(gender_dto, GenderQueryDTO)
        assert gender_dto.id_gender == gender_orm.id_gender
        assert gender_dto.gender_abb == gender_orm.gender_abb

    def test_uses_pydantic_validation(self) -> None:
        """Test that Pydantic validation is applied during mapping."""
        mapper = AutoToDTOMapper(Gender, GenderQueryDTO)

        invalid_orm = Gender()

        with pytest.raises(ValidationError):
            mapper.to_dto(invalid_orm)

class TestGenderToORMMapper:
    """Test suite for GenderToORMMapper."""

    def test_maps_all_fields_correctly(self) -> None:
        """Test complete field mapping."""
        dto = CreateGenderDTO(
            gender_abb= "M",
            gender_name= "MALE"
        )
        mapper = GenderToORMMapper()
        orm = mapper.to_orm(dto)

        assert isinstance(orm, Gender)
        assert orm.gender_abb == "M"
        assert orm.gender_name == "MALE"

class TestGenderToDTOMapper:
    """Test suite for GenderToDTOMapper."""

    def test_complete_mapping(self, gender_orm: Gender) -> None:
        """Test complete ORM to DTO mapping."""

        mapper = GenderToDTOMapper()
        dto = mapper.to_dto(gender_orm)

        assert dto.id_gender == 1
        assert dto.gender_abb == "M"
        assert dto.gender_name == "MALE"


class TestPatientToORMMapper:
    """Test suite for PatientToORMMapper."""

    def test_maps_create_patient_dto_to_orm(
            self,
            create_patient_dto: CreatePatientDTO
            ) -> None:
        """
        Test Create Patient DTO mapping to ORM.

        :param create_patient_dto: Create Patient DTO
        :type create_patient_dto: CreatePatientDTO
        """
        mapper = PatientToORMMapper()
        patient_orm = mapper.to_orm(create_patient_dto)

        assert isinstance(patient_orm, Patient)
        assert patient_orm.id_gender == create_patient_dto.id_gender
        assert patient_orm.identification == create_patient_dto.identification
        assert patient_orm.id_gender == create_patient_dto.id_gender
        assert patient_orm.date_of_birth == create_patient_dto.date_of_birth
        assert patient_orm.name == create_patient_dto.name


class TestPatientToDTOMapper:
    """Test suite for PatientToDTOMapper."""

    def test_maps_patient_orm_to_query_dto(
        self,
        patient_orm: Patient
    ) -> None:
        """Test Patient ORM mapping to Query DTO with nested Gender & Document Type."""

        gender_mapper = GenderToDTOMapper()
        document_type_mapper = DocumentTypeToDTOMapper()

        mapper = PatientToDTOMapper(gender_mapper, document_type_mapper)

        patient_dto = mapper.to_dto(patient_orm)

        assert isinstance(patient_dto, PatientQueryDTO)
        assert patient_dto.id_patient == 1
        assert patient_dto.identification == "123"
        assert patient_dto.name == "TEST PATIENT"
        assert patient_dto.date_of_birth == datetime.now(tz= timezone.utc).date()

        assert isinstance(patient_dto.patient_gender, GenderQueryDTO)
        assert patient_dto.patient_gender.id_gender == 1
        assert patient_dto.patient_gender.gender_abb == "M"
        assert patient_dto.patient_gender.gender_name == "MALE"

        assert isinstance(patient_dto.patient_document_type, DocumentTypeQueryDTO)
        assert patient_dto.patient_document_type.id_document_type == 1
        assert patient_dto.patient_document_type.document_type_abb  == "CC"
        assert patient_dto.patient_document_type.document_type_name == "CEDULA DE CIUDADANIA"  # noqa: E501


    def test_raises_error_when_gender_not_loaded(self) -> None:
        """Test that error is raised when relationship is not loaded."""
        patient_orm = Patient()
        patient_orm.id_patient = 1
        patient_orm.identification = "123"
        patient_orm.name = "TEST PATIENT"

        gender_mapper = GenderToDTOMapper()
        document_type_mapper = DocumentTypeToDTOMapper()
        mapper = PatientToDTOMapper(gender_mapper, document_type_mapper)

        with pytest.raises(ValidationError) as _:
            mapper.to_dto(patient_orm)

class TestMapperRegistry:
    """Test suite for MapperRegistry."""

    def test_register_and_retrieve_to_orm_mapper(self) -> None:
        """Test registering and using a to_orm mapper."""
        registry = MapperRegistry()
        mapper = GenderToORMMapper()

        registry.register_to_orm(CreateGenderDTO, Gender, mapper)

        dto = CreateGenderDTO(gender_abb= "F", gender_name= "FEMALE")
        orm = registry.to_orm(dto, Gender)

        assert isinstance(orm, Gender)
        assert orm.gender_abb == "F"
        assert orm.gender_name == "FEMALE"

    def test_register_and_retrieve_to_dto_mapper(self, gender_orm: Gender) -> None:
        """Test registering and using a to_dto mapper."""
        registry = MapperRegistry()
        mapper = GenderToDTOMapper()

        registry.register_to_dto(Gender, GenderQueryDTO, mapper)

        dto = registry.to_dto(gender_orm, GenderQueryDTO)

        assert isinstance(dto, GenderQueryDTO)
        assert dto.id_gender == gender_orm.id_gender
        assert dto.gender_abb == gender_orm.gender_abb
        assert dto.gender_name == gender_orm.gender_name

    def test_raises_error_for_unregistered_to_orm_mapper(self) -> None:
        """Test error when trying to use unregistered to_orm mapper."""
        registry = MapperRegistry()
        dto = CreateGenderDTO(gender_abb= "F", gender_name= "FEMALE")

        with pytest.raises(KeyError) as exc_info:
            registry.to_orm(dto, Gender)

        assert "No to_orm mapper registered" in str(exc_info.value)
        assert "CreateGenderDTO" in str(exc_info.value)
        assert "Gender" in str(exc_info.value)

    def test_raises_error_for_unregistered_to_dto_mapper(
            self,
            gender_orm: Gender
            ) -> None:
        """Test error when trying to use unregistered to_dto mapper."""
        registry = MapperRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.to_dto(gender_orm, GenderQueryDTO)

        assert "No to_dto mapper registered" in str(exc_info.value)

    def test_to_dto_list_maps_multiple_orms(
            self,
            mapper_registry: MapperRegistry
            ) -> None:
        """Test mapping a list of ORM instances to DTOs."""

        orm1 = Gender()
        orm1.id_gender = 1
        orm1.gender_abb = GenderAbbreviation.MALE
        orm1.gender_name = GenderName.MALE

        orm2 = Gender()
        orm2.id_gender = 2
        orm2.gender_abb = GenderAbbreviation.FEMALE
        orm2.gender_name = GenderName.FEMALE

        dto_list = mapper_registry.to_dto_list([orm1, orm2], GenderQueryDTO)

        assert len(dto_list) == 2
        assert all(isinstance(dto, GenderQueryDTO) for dto in dto_list)
        assert dto_list[0].gender_name == "MALE"
        assert dto_list[1].gender_name == "FEMALE"

    def test_to_orm_list_maps_multiple_dtos(
            self,
            mapper_registry: MapperRegistry
            ) -> None:
        """Test mapping a list of DTO instances to ORM."""

        dto1 = CreateGenderDTO(
            gender_abb= "M",
            gender_name= "MALE"
        )

        dto2 = CreateGenderDTO(
            gender_abb= "F",
            gender_name= "FEMALE"
        )

        orm_list = mapper_registry.to_orm_list([dto1, dto2], Gender)

        assert len(orm_list) == 2
        assert all(isinstance(orm, Gender) for orm in orm_list)
        assert orm_list[0].gender_name == "MALE"
        assert orm_list[1].gender_name == "FEMALE"
