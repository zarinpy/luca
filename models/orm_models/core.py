# Base declarative class for all models
import datetime
import uuid

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
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


# 1. mitre_collections
class Collection(Base):
    """Stores metadata about each collection (table) in the system.

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
    """Defines fields/columns for each collection.

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
    """Captures relations between two collections (one-to-many, many-to-many).

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
        comment="Collection on the 'many' side",
    )
    one_collection: Mapped[str] = mapped_column(
        String,
        ForeignKey("mitre_collections.collection"),
        nullable=False,
        index=True,
        comment="Collection on the 'one' side",
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
    """Supports draft and versioning of collection records.

    Useful for content moderation workflows and undo/history.
    """

    __tablename__ = "mitre_revisions"

    collection: Mapped[str] = mapped_column(
        String,
        ForeignKey("mitre_collections.collection"),
        nullable=False,
        index=True,
        comment="Collection the revision belongs to",
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
    """Defines navigational structure (menus, links).

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
