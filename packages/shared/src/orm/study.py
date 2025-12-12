"""Study table.

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
from datetime import date

from shared.src.orm.base import Base
from shared.src.orm.lookup import Physician, Procedure, Referral
from shared.src.orm.patient import Patient
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Study(Base):
    """Studies table.

    This table stores study information listed below

    :param id_study:
        Autoincremental primary key of the table

    :param id_patient:
        Foreing key from `Patient` table

    :param study_date:
        Date when procedure performed in `YYYY-MM-DD` format

    :param id_procedure:
        Foreign key from `Procedure` table

    :param id_physician:
        Foreign key from `Physician` table

    :param id_referral:
        Foreign key from `Referral` table


    """

    id_study: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_patient: Mapped[int] = mapped_column(ForeignKey("patients.id_patient"))
    study_date: Mapped[date]
    id_procedure: Mapped[int] = mapped_column(ForeignKey("procedures.id_procedure"))
    id_physician: Mapped[int] = mapped_column(ForeignKey("physicians.id_physician"))
    id_referral: Mapped[int] = mapped_column(ForeignKey("referrals.id_referral"))

    study_patient: Mapped[Patient] = relationship()
    study_procedure: Mapped[Procedure] = relationship()
    study_physician: Mapped[Physician] = relationship()
    study_referral: Mapped[Referral] = relationship()
