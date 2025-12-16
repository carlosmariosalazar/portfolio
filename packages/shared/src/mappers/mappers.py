"""Implemenation of AutoToORMMappers and ManualToDTOMapper."""

from shared.src.dto.create import (
    CreateDocumentTypeDTO,
    CreateGenderDTO,
    CreatePatientDTO,
    CreatePhysicianDTO,
    CreateProcedureDTO,
    CreateReferralDTO,
    CreateStudyDTO,
)
from shared.src.dto.query import (
    DocumentTypeQueryDTO,
    GenderQueryDTO,
    PatientQueryDTO,
    PhysicianQueryDTO,
    ProcedureQueryDTO,
    ReferralQueryDTO,
    StudyQueryDTO,
)
from shared.src.mappers.base import (
    AutoToDTOMapper,
    AutoToORMMapper,
    ManualToDTOMapper,
    ToDTOMapper,
)
from shared.src.orm.lookup import DocumentType, Gender, Physician, Procedure, Referral
from shared.src.orm.patient import Patient
from shared.src.orm.study import Study


class GenderToORMMapper(AutoToORMMapper[CreateGenderDTO, Gender]):
    """Simple auto mapper for Gender creation."""

    def __init__(self) -> None:
        """Initialize Gender to ORM mapper."""
        super().__init__(CreateGenderDTO, Gender)

class GenderToDTOMapper(AutoToDTOMapper[Gender, GenderQueryDTO]):
    """Simple auto mapper for Gender queries."""

    def __init__(self) -> None:
        """Initialize Gender DTO mapper."""
        super().__init__(Gender, GenderQueryDTO)

class DocumentTypeToORMMapper(AutoToORMMapper[CreateDocumentTypeDTO, DocumentType]):
    """Simple auto mapper for Document Type creation."""

    def __init__(self) -> None:
        """Initialize Document Type ORM mapper."""
        super().__init__(CreateDocumentTypeDTO, DocumentType)

class DocumentTypeToDTOMapper(AutoToDTOMapper[DocumentType, DocumentTypeQueryDTO]):
    """Simple auto mapper for Document Type queries."""

    def __init__(self) -> None:
        """Initialize Document Type DTO mapper."""
        super().__init__(DocumentType, DocumentTypeQueryDTO)

class ProcedureToORMMapper(AutoToORMMapper[CreateProcedureDTO, Procedure]):
    """Simple auto mapper for Procedure creation."""

    def __init__(self) -> None:
        """Initialize Procedure ORM mapper."""
        super().__init__(CreateProcedureDTO, Procedure)

class ProcedureToDTOMapper(AutoToDTOMapper[Procedure, ProcedureQueryDTO]):
    """Simple auto mapper for Procedure queries."""

    def __init__(self) -> None:
        """Initialize Procedure DTO mapper."""
        super().__init__(Procedure, ProcedureQueryDTO)

class PhysicianToORMMapper(AutoToORMMapper[CreatePhysicianDTO, Physician]):
    """Simple auto mapper for Physician creation."""

    def __init__(self) -> None:
        """Initialize Physician ORM mapper."""
        super().__init__(CreatePhysicianDTO, Physician)

class PhysicianToDTOMapper(AutoToDTOMapper[Physician, PhysicianQueryDTO]):
    """Simple auto mapper for Physician queries."""

    def __init__(self) -> None:
        """Initialize Physician DTO mapper."""
        super().__init__(Physician, PhysicianQueryDTO)

class ReferralToORMMapper(AutoToORMMapper[CreateReferralDTO, Referral]):
    """Simple auto mapper for Referral creation."""

    def __init__(self) -> None:
        """Initialize Referral ORM mapper."""
        super().__init__(CreateReferralDTO, Referral)

class ReferralToDTOMapper(AutoToDTOMapper[Referral, ReferralQueryDTO]):
    """Simple auto mapper for Referral queries."""

    def __init__(self) -> None:
        """Initialize Referral DTO mapper."""
        super().__init__(Referral, ReferralQueryDTO)

class PatientToORMMapper(AutoToORMMapper[CreatePatientDTO, Patient]):
    """Simple auto mapper for Patient creation."""

    def __init__(self) -> None:
        """Initialize Patient ORM mapper."""
        super().__init__(CreatePatientDTO, Patient)

class PatientToDTOMapper(ManualToDTOMapper[Patient, PatientQueryDTO]):
    """Manual mapper for Patient queries (handle nested DTOs)."""

    def __init__(
            self,
            gender_mapper: ToDTOMapper[Gender, GenderQueryDTO],
            document_type_mapper: ToDTOMapper[DocumentType, DocumentTypeQueryDTO]
            ) -> None:
        """Initialize Patient to DTO mapper.

        :param document_type_mapper: Mapper for nested `DocumentTypeDTO`
        :type document_type_mapper: ToDTOMapper[DocumentType, DocumentTypeQueryDTO]
        :param gender_mapper: Mapper for nested `GenderDTO`
        :type gender_mapper: ToDTOMapper[Gender, GenderQueryDTO]
        """
        self._gender_mapper = gender_mapper
        self._document_type_mapper = document_type_mapper

        def map_patient(orm: Patient) -> PatientQueryDTO:

            document_type_dto = self._document_type_mapper.to_dto(
                orm.patient_document_type
                )

            gender_dto = self._gender_mapper.to_dto(orm.patient_gender)

            return PatientQueryDTO(
                id_patient= orm.id_patient,
                patient_document_type= document_type_dto,
                identification= orm.identification,
                patient_gender= gender_dto,
                date_of_birth= orm.date_of_birth,
                name= orm.name
            )

        super().__init__(Patient, PatientQueryDTO, map_patient)

class StudyToORMMapper(AutoToORMMapper[CreateStudyDTO, Study]):
    """Simple auto mapper for Study creation."""

    def __init__(self) -> None:
        """Initialize Study ORM mapper."""
        super().__init__(CreateStudyDTO, Study)

class StudyToDTOMapper(ManualToDTOMapper[Study, StudyQueryDTO]):
    """Manual mapper for Study queries (handle nested DTOs)."""

    def __init__(
            self,
            patient_mapper: ToDTOMapper[Patient, PatientQueryDTO],
            procedure_mapper: ToDTOMapper[Procedure, ProcedureQueryDTO],
            physician_mapper: ToDTOMapper[Physician, PhysicianQueryDTO],
            referral_mapper: ToDTOMapper[Referral, ReferralQueryDTO]
            ) -> None:
        """Initialize Study to DTO mapper.

        :param patient_mapper: Mapper for nested `PatientQueryDTO`
        :type patient_mapper: ToDTOMapper[Patient, PatientQueryDTO]
        :param procedure_mapper: Mapper for nested `ProcedureQueryDTO`
        :type procedure_mapper: ToDTOMapper[Procedure, ProcedureQueryDTO]
        :param physician_mapper: Mapper for nested `PhysicianQueryDTO`
        :type physician_mapper: ToDTOMapper[Physician, PhysicianQueryDTO]
        :param referral_mapper: Mapper for nested `ReferralQueryDTO`
        :type referral_mapper: ToDTOMapper[Referral, ReferralQueryDTO]

        """
        self._patient_mapper = patient_mapper
        self._procedure_mapper = procedure_mapper
        self._physician_mapper = physician_mapper
        self._referral_mapper = referral_mapper

        def map_study(orm: Study) -> StudyQueryDTO:

            patient_dto = self._patient_mapper.to_dto(orm.study_patient)
            procedure_dto = self._procedure_mapper.to_dto(orm.study_procedure)
            physician_dto = self._physician_mapper.to_dto(orm.study_physician)
            referral_dto = self._referral_mapper.to_dto(orm.study_referral)

            return StudyQueryDTO(
                id_study= orm.id_study,
                study_date= orm.study_date,
                study_patient= patient_dto,
                study_procedure= procedure_dto,
                study_physician= physician_dto,
                study_referral= referral_dto
            )

        super().__init__(Study, StudyQueryDTO, map_study)
