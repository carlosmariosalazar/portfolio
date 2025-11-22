"""Lookup tables.

This is a submodule from ORM module, it contains all lookup tables needed
to create a Patient or Study record in database. Each one of the lookup tables
has a One to Many relationship with a Patient/Study.

Gender's table
    It contains information about a patient's gender

Document type's table
    It contains information about the legal document type of a patient, it
    is related with patient age.

Procedure's table
    It contains all procedures performed as well as pricing information, it
    is related to a Study

Physician's table
    It contains information about physicians who performs the ordered procedures, it
    is related to a Study

Referral's table
    It contains information about physicians that ordered a given procedure, it is
    related to a Study

"""

from enum import StrEnum

from shared.src.orm.base import Base
from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class GenderAbbreviation(StrEnum):
    """Enum class for Gender abbreviation."""

    MALE = "M"
    FEMALE = "F"


class GenderName(StrEnum):
    """Enum class for Gender name."""

    MALE = "MALE"
    FEMALE = "FEMALE"


class DocumentTypeAbbreviation(StrEnum):
    """Enum class for Document type abbreviation."""

    REGISTRO_CIVIL = "RC"
    TARJETA_DE_IDENTIDAD = "TI"
    CEDULA_DE_CIUDADANIA = "CC"


class DocumentTypeName(StrEnum):
    """Enum class for Document type name."""

    REGISTRO_CIVIL = "REGISTRO CIVIL"
    TARJETA_DE_IDENTIDAD = "TARJETA DE IDENTIDAD"
    CEDULA_DE_CIUDADANIA = "CEDULA DE CIUDADANIA"


class Gender(Base):
    """Reference table for Genders (Lookup Table).

    This table contains a fix set of genders that a patient may have

    :param id_gender:
        Autoincremental primary key of the table

    :param gender_abb:
        Gender abbreviature `('M', 'F')` constrained by `GenderAbbreviation` Enum
        and unique index

    :param gender_name:
        Gender name `('MALE', 'FEMALE')` constrained by `GenderName` Enum and unique
        index.
    """

    __tablename__ = "genders"

    id_gender: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
    gender_abb: Mapped[str] = mapped_column(Enum(GenderAbbreviation), unique=True)
    gender_name: Mapped[GenderName] = mapped_column(Enum(GenderName), unique=True)


class DocumentType(Base):
    """Reference table for Document types (Lookup Table).

    This table contains all document types that a patient may have

    :param id_document_type:
        Autoincremental primary key of the table

    :param document_type_abb:
        Document type abbreviature `(RC, TI, CC)` constrained
        by `DocumentTypeAbbreviation` Enum and unique index

    :param document_type_name:
        Document type name constrained by `DocumentTypeName` Enum and unique
        index
    """

    __tablename__ = "document_types"

    id_document_type: Mapped[int] = mapped_column(
        primary_key=True, autoincrement="auto"
    )
    document_type_abb: Mapped[DocumentTypeAbbreviation] = mapped_column(
        Enum(DocumentTypeAbbreviation), unique=True
    )
    document_type_name: Mapped[DocumentTypeName] = mapped_column(
        Enum(DocumentTypeName), unique=True
    )


class Procedure(Base):
    """Reference table for Procedures (Lookup Table).

    This table contains procedures performed

    :param id_procedure:
        Autoincremental primary key of the table

    :param cups:
        Six digits nunmeric unique code for each procedure

    :param procedure_name:
        Ultrasound procedure name

    :param procedure_price:
        Procedure pricing

    """

    __tablename__ = "procedures"

    id_procedure: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
    cups: Mapped[str] = mapped_column(String(length=6), unique=True)
    procedure_name: Mapped[str] = mapped_column(String(length=50), unique=True)
    procedure_price: Mapped[int] = mapped_column(Integer())


class Physician(Base):
    """Reference table for Physicians (Lookup Table).

    This table contains physicians that performs procedures

    :param id_physician:
        Autoincremental primary key of the table

    :param physician_rm:
        Four digits numeric code unique for each physician

    :param physician_name:
        Phyisician name
    """

    __tablename__ = "physicians"

    id_physician: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
    physician_rm: Mapped[str] = mapped_column(String(4), unique=True)
    physician_name: Mapped[str] = mapped_column(String(30))


class Referral(Base):
    """Reference table for Referrals (Lookup Table).

    This table contains referring physicians for a given procedure

    :param id_referral:
        Autoincremental primary key of the table

    :param referral_rm:
        Four digits numeric code unique for each referral

    :param referral_name:
        Referral name
    """

    __tablename__ = "referrals"

    id_referral: Mapped[int] = mapped_column(primary_key=True, autoincrement="auto")
    referral_rm: Mapped[str] = mapped_column(String(4), unique=True)
    referral_name: Mapped[str] = mapped_column(String(30))
