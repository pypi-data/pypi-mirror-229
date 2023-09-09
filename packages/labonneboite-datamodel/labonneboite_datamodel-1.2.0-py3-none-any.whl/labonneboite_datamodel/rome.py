from sqlmodel import Field
from typing import Optional
from .base import BaseMixin


class Rome(BaseMixin, table=True):
    """This table hosts ROME definitions

    Attributes:
        id:
        rome:
        domain:
        granddomain:
        appellation: Real searchable name for the rome (multiple lines)
        label_granddomain:
        label_domain:
        label_rome:

    """
    id: Optional[int] = Field(
        default=None, primary_key=True, nullable=False)

    rome: str = Field(regex=r"^\D\d{4}")
    domain: Optional[str] = Field(default=None, nullable=False)
    granddomain: Optional[str] = Field(default=None, nullable=False)

    label_rome: str
    label_domain: Optional[str] = Field(default=None, nullable=False)
    label_granddomain: Optional[str] = Field(default=None, nullable=False)

    designation: str


class RomeNaf(BaseMixin, table=True):
    """This table hosts the mapping between ROME and NAF to be able to make a ROME search correspond to a SIRET

    Attributes:
        id:
        rome:
        naf:
        ratio: Percentage of rome contribution in current naf

    """
    id: Optional[int] = Field(
        default=None, primary_key=True, nullable=False)
    rome: str = Field(regex=r"^\D\d{4}")
    naf: str = Field(regex=r"^\d{4}\D$")
    ratio: float = Field(ge=0, le=100)
