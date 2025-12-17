"""Patient table.

This is a submodule from ORM module, it contains the patients table, it is
required by Studies table to create a study.

"""
from datetime import date

from shared.src.orm.base import Base
from shared.src.orm.lookup import DocumentType, Gender
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Patient(Base):
    """Patient's table.

    This table stores patient's demographic information listed below

    :param id_patient:
        Autoincremental primary key of the table
    :type id_patient:
        int

    :param id_document_type:
        Foreing key from `DocumentType` table
    :type id_document_type:
        int

    :param identification:
        Patient unique identification number
    :type identification:
        str

    :param name:
        Patient name
    :type name:
        str

    :param id_gender:
        Foreign key from `Gender` table
    :type id_gender:
        int

    :param date_of_birth:
        Patient date of birth in `datetime.date` format
    :type date_of_birth:
        datetime.date

    """

    __tablename__ = "patients"

    id_patient: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_document_type: Mapped[int] = mapped_column(
        ForeignKey("document_types.id_document_type")
    )
    identification: Mapped[str] = mapped_column(String(10), unique=True)
    name: Mapped[str] = mapped_column(String(30))
    id_gender: Mapped[int] = mapped_column(ForeignKey("genders.id_gender"))
    date_of_birth: Mapped[date]

    patient_document_type: Mapped[DocumentType] = relationship()
    patient_gender: Mapped[Gender] = relationship()
