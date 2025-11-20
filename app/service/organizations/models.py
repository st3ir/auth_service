from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.meta import Base


class Organization(Base):

    __tablename__ = "organization"

    id = Column(Integer, primary_key=True)

    full_name = Column(String, nullable=False, unique=True)
    short_name = Column(String, nullable=False, unique=True)

    corp_email = Column(String)
    corp_phone = Column(String)

    departments = relationship("Department", back_populates="organization")
    job_sites_policy = relationship(
        "JobSitePolicy",
        back_populates="organization",
    )


class Department(Base):

    __tablename__ = "department"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)

    external_id = Column(String)
    external_type = Column(String)

    full_name = Column(String, nullable=False)
    short_name = Column(String, nullable=False)

    organization = relationship(
        "Organization",
        back_populates="departments",
        uselist=False
    )


class JobSitePolicy(Base):

    __tablename__ = "job_site_policy"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)

    billing_info = Column(JSONB, nullable=False, default={}, server_default="{}")
    platform_type = Column(String, nullable=False)

    organization = relationship(
        "Organization",
        back_populates="job_sites_policy",
        uselist=False,
        viewonly=True,
    )
