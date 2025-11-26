"""Query Data Transfer Objects (DTO).

This submodule contains all Query DTOs for each Database entity (table).
Query DTOs are intended to be used in a data presentation layer.

"""

from datetime import date

from pydantic import BaseModel


class GenderQueryDTO(BaseModel):
    """Query Data Transfer Object (DTO) for the `Gender` entity.

    Represents the data structure of a patient's gender
    for presentation purposes as a query result

    :param id_gender:
        Gender unique identifier

    :param gender_abb:
        Gender standarized abbreviation `('M', 'F')`

    :param gender_name:
        Gender name or description `(MALE, FEMALE)`
    """

    id_gender: int
    gender_abb: str
    gender_name: str


class DocumentTypeQueryDTO(BaseModel):
    """Query Data Transfer Object (DTO) for the `DocumentType` entity.

    Represents the data structure of a patient's document type
    for presentation purposes as a query result

    :param id_document_type:
        DocumentType unique identifier

    :param document_type_abb:
        DocumentType standarized abbreviation `(RC, TI, CC)`

    :param document_type_name:
        Document type name or description e.g. `(REGISTRO CIVIL, TARJETA DE IDENTIDAD,
        CEDULA DE CIUDADANIA)`
    """

    id_document_type: int
    document_type_abb: str
    document_type_name: str


class ProcedureQueryDTO(BaseModel):
    """Query Data Transfer Object (DTO) for the `Procedure` entity.

    Represents the data structure of a procedure for presentation purposes
    as a query result

    :param id_procedure:
        Procedure unique identifier

    :param cups:
        Procedure legal unique code (e.g. `881302`)

    :param procedure_name:
        Procedure name or description (e.g. `ECOGRAFIA DE ABDOMEN TOTAL`)

    :param procedure_price:
        Procedure price ($`300.000` COP)
    """

    id_procedure: int
    cups: str
    procedure_name: str
    procedure_price: int


class PhysicianQueryDTO(BaseModel):
    """Query Data Transfer Object (DTO) for the `Physician` entity.

    Represents the data structure of a Physician for presentation purposes
    as a query result

    :param id_physician:
        Physician unique identifier

    :param physician_rm:
        Physician medical license identifier (e.g. `12345`)

    :param physician_name:
        Physician full name (e.g. `PHYSICIAN TEST A`)

    """

    id_physician: int
    physician_rm: str
    physician_name: str


class ReferralQueryDTO(BaseModel):
    """Query Data Transfer Object (DTO) for the `Referral` entity.

    Represents the data structure of a Referral for presentation purposes
    as a query result

    :param id_referral:
        Referral unique identifier

    :param referral_rm:
        Referral medical license identifier (e.g. `54321`)

    :param referral_name:
        Referral full name (e.g. `TEST REFERRAL A`)

    """

    id_referral: int
    referral_rm: str
    referral_name: str


class PatientQueryDTO(BaseModel):
    """Query Data Transfer Object (DTO) for the `Patient` entity.

    Represents the full patient record, used for API responses. This schema
    expands Foreign Keys into nested DTO objects for comprehensive data delivery.

    :param id_patient:
        The unique identifier of the patient

    :param patient_document_type:
        The full Document type lookup entity (`DocumentTypeQueryDTO`) associated
        with this patient.

    :param identification:
        Patient legal identification number

    :param patient_gender:
        The full Gender lookup entity (`GenderQueryDTO`) associated with this patient.

    :param date_of_birth:
        Patient date of birth as `datetime.date` object

    :param name:
        The full legal name of the patient
    """

    id_patient: int
    patient_document_type: DocumentTypeQueryDTO
    identification: str
    patient_gender: GenderQueryDTO
    date_of_birth: date
    name: str


class StudyQueryDTO(BaseModel):
    """Query Data Transfer Object (DTO) for the `Study` entity.

    Represents the data structure of a Study for presentation purposes
    as a query result

    :param id_study:
        Study unique identifier

    :param study_patient:
        The Patient entity (`PatientQueryDTO`) associated with this study

    :param study_date:
        Study performed date as `datetime.date` object

    :param study_procedure:
        The Procedure lookup entity (`ProcedureQueryDTO`) associated with this study

    :param study_physician:
        The Physician lookup entity (`PhysicianQueryDTO`) associated with this study

    :param study_referral:
        The Referral lookup entity (`ReferralQueryDTO`) associated with this study
    """

    id_study: int
    study_patient: PatientQueryDTO
    study_date: date
    study_procedure: ProcedureQueryDTO
    study_physician: PhysicianQueryDTO
    study_referral: ReferralQueryDTO
