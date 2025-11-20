from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.meta import Base
from service.organizations.models import Department  # noqa


class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("department.id"), nullable=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    parent_name = Column(String)

    photo_link = Column(String)
    phone_number = Column(String)
    pass_salt = Column(String, nullable=False)
    password = Column(String, nullable=False)

    email = Column(String, nullable=False, unique=True)
    active = Column(Boolean, default=False, nullable=False)

    is_internal = Column(Boolean, default=True, server_default="true", nullable=False)

    roles = relationship(
        "Role",
        secondary="user_role",
        back_populates="users",
        lazy="selectin",
    )
    role = relationship(
        "Role",
        secondary="user_role",
        backref="user",
        uselist=False,
        viewonly=True,
        lazy='selectin',
        order_by="desc(UserRole.id)"
    )
    department = relationship("Department", backref='employees', uselist=False)

    all_job_site_creds = relationship(
        "JobSiteCredentials",
        back_populates="user",
        lazy="selectin",
    )


class JobSiteCredentials(Base):

    __tablename__ = "job_site_credentials"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    credentials = Column(JSONB, nullable=False, default={}, server_default="{}")
    platform_type = Column(String, nullable=False)

    user = relationship(
        "User",
        back_populates="all_job_site_creds",
        lazy="joined",
        uselist=False,
        viewonly=True,
    )


class UserAgreement(Base):

    __tablename__ = "user_agreement"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    agreement_type = Column(String, nullable=False)
