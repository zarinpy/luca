# Base declarative class for all models

import datetime
import uuid
from typing import Optional

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.orm_models.crud import CRUD

__all__ = [
    "User",
    "RefreshToken",
    "Relation",
    "Revision",
    "Taxonomy",
    "Translation",
    "Collection",
    "Content",
    "OAuthIdentity",
    "Navigation",
    "Field",
]


class Base(DeclarativeBase, CRUD):
    """Root base class using SQLAlchemy 2.0 DeclarativeBase.

    All models inherit from this to share metadata and conventions.
    Provides a common 'id' primary key column (UUID) for all tables.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Universal primary key UUID",
    )


# Main User table
class User(Base):
    """
    Represents a user in the CMS, supporting multiple authentication methods.

    Stores core user data, credentials for username/password login, and metadata.
    Indexes on email and username optimize login and lookup operations.
    """

    __tablename__ = "mitre_users"

    # Core user fields
    email: Mapped[str] = mapped_column(
        String(254),    # RFC 5321
        unique=True,
        nullable=False,
        index=True,
        comment="Unique email address for login and notifications",
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
        comment="Optional unique username for login",
    )
    hashed_password: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Hashed password for username/password login (null for OAuth-only users)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the user account is active",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the user has admin privileges",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="Account creation timestamp",
    )
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Timestamp of last successful login",
    )

    __table_args__ = (
        Index("idx_mitre_users_email", "email"),
        Index("idx_mitre_users_username", "username"),
    )


# OAuth Identity table for external providers
class OAuthIdentity(Base):
    """
    Stores OAuth2 identities linked to a user.

    Supports multiple OAuth providers (e.g., Google, GitHub).
    Indexes on provider and provider_user_id optimize lookups during login.
    """

    __tablename__ = "mitre_oauth_identities"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mitre_users.id"),
        nullable=False,
        index=True,
        comment="FK to the associated user",
    )
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="OAuth provider (e.g., google, github)",
    )
    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Unique user ID from the OAuth provider",
    )
    access_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="OAuth access token (if stored)",
    )
    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="OAuth refresh token (if stored)",
    )
    token_expiry: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Expiry timestamp for access token",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="Identity creation timestamp",
    )

    __table_args__ = (
        Index(
            "idx_mitre_oauth_identities_provider_user_id",
            "provider",
            "provider_user_id",
        ),
    )


# Refresh Token table for JWT authentication
class RefreshToken(Base):
    """
    Stores refresh tokens for JWT-based authentication.

    Supports token rotation and revocation.
    Indexes on token optimize validation and revocation checks.
    """

    __tablename__ = "mitre_refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mitre_users.id"),
        nullable=False,
        index=True,
        comment="FK to the associated user",
    )
    token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        index=True,
        comment="Refresh token string",
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Token expiry timestamp",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="Token creation timestamp",
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the token is revoked",
    )

    __table_args__ = (
        Index("idx_mitre_refresh_tokens_token", "token"),
    )


# 1. mitre_collections
class Collection(Base):
    """
    Stores metadata about each collection (table) in the system.

    Indexed on 'hidden' for fast filtering of visible vs. hidden collections.
    """

    __tablename__ = "mitre_collections"
    collection: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        comment="Unique collection name/key",
    )
    hidden: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether hidden in the UI",
    )
    singleton: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True if only one record allowed",
    )
    icon: Mapped[JSON] = mapped_column(
        JSON,
        nullable=True,
        comment="UI icon metadata",
    )
    note: Mapped[JSON] = mapped_column(
        JSON,
        nullable=True,
        comment="Arbitrary notes/metadata",
    )
    translations: Mapped[JSON] = mapped_column(
        JSON,
        nullable=True,
        comment="Multilanguage labels",
    )

    __table_args__ = (
        Index("idx_mitre_collections_hidden", "hidden"),
    )


# 2. mitre_fields
class Field(Base):
    """
    Defines fields/columns for each collection.

    Composite index on (collection, field)
    speeds lookups for specific field definitions.
    Indexes on collection, field, and type support common filters.
    """

    __tablename__ = "mitre_fields"
    collection: Mapped[str] = mapped_column(
        String,
        ForeignKey("mitre_collections.collection"),
        nullable=False,
        index=True,
        comment="FK to collection this field belongs to",
    )
    field: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
        unique=True,
        comment="Field/column name in the collection",
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
        comment="Data type (string, integer, etc.)",
    )
    schema: Mapped[JSON] = mapped_column(
        JSON,
        nullable=True,
        comment="Raw column definition JSON",
    )
    interface: Mapped[JSON] = mapped_column(
        JSON,
        nullable=True,
        comment="UI interface settings",
    )
    options: Mapped[JSON] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional UI options",
    )

    __table_args__ = (
        Index(
            "idx_mitre_fields_collection_field",
            "collection", "field",
        ),
    )


# 3. mitre_relations
class Relation(Base):
    """
    Captures relations between two collections (one-to-many, many-to-many).

    Indexes on FK columns optimize joins and relation lookups.
    Composite index on (many_collection, one_collection)
     aids discovery of relation pairs.
    """

    __tablename__ = "mitre_relations"

    many_collection: Mapped[str] = mapped_column(
        String,
        ForeignKey("mitre_collections.collection"),
        nullable=False,
        index=True,
        comment="CreateCollection on the 'many' side",
    )
    one_collection: Mapped[str] = mapped_column(
        String,
        ForeignKey("mitre_collections.collection"),
        nullable=False,
        index=True,
        comment="CreateCollection on the 'one' side",
    )
    field_many: Mapped[str] = mapped_column(
        String,
        ForeignKey("mitre_fields.field"),
        nullable=False,
        index=True,
        comment="Field in many_collection",
    )
    field_one: Mapped[str] = mapped_column(
        String,
        ForeignKey("mitre_fields.field"),
        nullable=False,
        index=True,
        comment="Field in one_collection",
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Relation type: m2o, o2m, m2m",
    )
    junction: Mapped[str] = mapped_column(
        String,
        nullable=True,
        comment="Junction table for m2m relations",
    )

    __table_args__ = (
        Index("idx_mitre_relations_many_one", "many_collection",
              "one_collection"),
    )


# Revisions / Drafts support
class Revision(Base):
    """
    Supports draft and versioning of collection records.

    Useful for content moderation workflows and undo/history.
    """

    __tablename__ = "mitre_revisions"

    collection: Mapped[str] = mapped_column(
        String,
        ForeignKey("mitre_collections.collection"),
        nullable=False,
        index=True,
        comment="CreateCollection the revision belongs to",
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Original item ID this revision represents",
    )
    data: Mapped[JSON] = mapped_column(
        JSON,
        nullable=False,
        comment="Snapshot of item data",
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="draft",
        index=True,
        comment="Revision status: draft, published, archived",
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mitre_users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.now,
    )


# Navigation menu system
class Navigation(Base):
    """
    Defines navigational structure (menus, links).

    Useful for building UI menus dynamically.
    """

    __tablename__ = "mitre_navigation"

    label: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mitre_navigation.id"),
        nullable=True,
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    visible: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


# Taxonomy system
class Taxonomy(Base):
    """Defines vocabularies and taxonomy terms."""

    __tablename__ = "mitre_taxonomy"

    vocabulary: Mapped[str] = mapped_column(String, nullable=False, index=True)
    term: Mapped[str] = mapped_column(String, nullable=False, index=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mitre_taxonomy.id"),
        nullable=True,
    )


# Multilingual content translation table
class Translation(Base):
    """Stores field-level translations for multilingual support."""

    __tablename__ = "mitre_translations"

    collection: Mapped[str] = mapped_column(
        String,
        ForeignKey("mitre_collections.collection"),
        nullable=False,
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    field: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=True)


class Content(Base):
    """
    Stores content records for collections in the CMS.

    Each record is tied to a collection and user, with flexible JSON data.
    Supports draft/published status and versioning via revisions.
    Indexes on collection, status, and created_by optimize common queries.
    """

    __tablename__ = "mitre_content"

    collection: Mapped[str] = mapped_column(
        String,
        ForeignKey("mitre_collections.collection"),
        nullable=False,
        index=True,
        comment="FK to the collection this content belongs to",
    )
    data: Mapped[JSON] = mapped_column(
        JSON,
        nullable=False,
        comment="JSON data for the content record",
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="draft",
        index=True,
        comment="Content status: draft, published, archived",
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mitre_users.id"),
        nullable=False,
        index=True,
        comment="FK to the user who created the content",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="Content creation timestamp",
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Content last update timestamp",
    )
    published_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Content publication timestamp",
    )
    is_draft: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether the content is a draft",
    )

    __table_args__ = (
        Index("idx_mitre_content_collection_status", "collection", "status"),
        Index("idx_mitre_content_created_by", "created_by"),
    )
