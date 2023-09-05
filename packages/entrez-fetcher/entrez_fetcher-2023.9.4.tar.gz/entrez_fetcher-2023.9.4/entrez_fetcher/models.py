""" Models for entrez_fetcher

This module contains the dataclasses used to represent the data returned by the
NCBI Entrez API.
"""

from __future__ import annotations
from dataclasses import fields
from enum import Enum

import re
from datetime import datetime
from typing import Iterable, List, Optional

from pydantic import validator
from pydantic.fields import ModelField
from pydantic.dataclasses import dataclass

_SNAKE_CASE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def pascal2snake(name: str) -> str:
    return _SNAKE_CASE_PATTERN.sub("_", name).lower()


class DB(Enum):
    bioproject = "bioproject"
    biosample = "biosample"
    biosystems = "biosystems"
    books = "books"
    cdd = "cdd"
    gap = "gap"
    dbvar = "dbvar"
    epigenomics = "epigenomics"
    nucest = "nucest"
    gene = "gene"
    genome = "genome"
    gds = "gds"
    geoprofiles = "geoprofiles"
    nucgss = "nucgss"
    homologene = "homologene"
    mesh = "mesh"
    toolkit = "toolkit"
    ncbisearch = "ncbisearch"
    nlmcatalog = "nlmcatalog"
    nuccore = "nuccore"
    omia = "omia"
    popset = "popset"
    probe = "probe"
    protein = "protein"
    proteinclusters = "proteinclusters"
    pcassay = "pcassay"
    pccompound = "pccompound"
    pcsubstance = "pcsubstance"
    pubmed = "pubmed"
    pmc = "pmc"
    snp = "snp"
    sra = "sra"
    structure = "structure"
    taxonomy = "taxonomy"
    unigene = "unigene"
    unists = "unists"


@dataclass
class Docsum:
    id: Optional[int] = None
    caption: Optional[str] = None
    title: Optional[str] = None
    extra: Optional[str] = None
    gi: Optional[int] = None
    create_date: Optional[str] = None
    update_date: Optional[str] = None
    flags: Optional[int] = None
    tax_id: int = 0
    length: Optional[int] = None
    status: Optional[str] = None
    replaced_by: Optional[str] = None
    comment: Optional[str] = None
    accession_version: Optional[str] = None

    @classmethod
    def get_fields_name(cls) -> List[str]:
        return [field.name for field in fields(cls)]

    @validator("create_date", "update_date", pre=True)
    def _parse_date(cls, v):
        if v is None:
            return v
        try:
            return datetime.strptime(v, "%Y/%m/%d").date().isoformat()
        except ValueError:
            pass
        return v

    @validator("*")
    def _force_stdtype(cls, v, field: ModelField):
        if v is None:
            return v
        if field.type_ in [str, int, dict]:
            return field.type_(v)
        return v

    @classmethod
    def from_dict(cls, d):
        return cls(
            **{
                fkey: value
                for key, value in d.items()
                if (fkey := pascal2snake(key)) in cls.get_fields_name()
            }
        )


@dataclass
class GeneticCode:
    id: int
    name: str

    @classmethod
    def get_fields_name(cls) -> List[str]:
        return [field.name for field in fields(cls)]

    @validator("*")
    def _force_stdtype(cls, v, field: ModelField):
        if field.type_ in [str, int, dict]:
            return field.type_(v)
        return v


@dataclass
class LineageEx:
    tax_id: int
    scientific_name: str
    rank: str

    @classmethod
    def get_fields_name(cls) -> List[str]:
        return [field.name for field in fields(cls)]

    @validator("*")
    def _force_stdtype(cls, v, field: ModelField):
        if field.type_ in [str, int, dict]:
            return field.type_(v)
        return v

    @classmethod
    def from_dict(cls, d):
        return cls(
            **{
                fkey: value
                for key, value in d.items()
                if (fkey := pascal2snake(key)) in cls.get_fields_name()
            }
        )


@dataclass
class Taxonomy:
    tax_id: int
    scientific_name: Optional[str] = None
    rank: Optional[str] = None
    division: Optional[str] = None
    parent_tax_id: Optional[int] = None
    genetic_code: Optional[GeneticCode] = None
    mito_genetic_code: Optional[GeneticCode] = None
    lineage: Optional[List[str]] = None
    lineage_ex: Optional[List[LineageEx]] = None
    create_date: Optional[str] = None
    update_date: Optional[str] = None
    pub_date: Optional[str] = None

    @classmethod
    def get_fields_name(cls) -> List[str]:
        return [field.name for field in fields(cls)]

    @classmethod
    def from_dict(cls, d):
        return cls(
            **{
                fkey: value
                for key, value in d.items()
                if (fkey := pascal2snake(key)) in cls.get_fields_name()
            }
        )

    @validator("*")
    def _force_stdtype(cls, v, field: ModelField):
        if v is None:
            return v
        if field.type_ in [str, int, dict]:
            return field.type_(v)
        return v

    @validator("genetic_code", pre=True)
    def _parse_gcode(cls, v):
        if v is None:
            return v
        return GeneticCode(id=v["GCId"], name=v["GCName"])

    @validator("mito_genetic_code", pre=True)
    def _parse_mgcode(cls, v):
        if v is None:
            return v
        return GeneticCode(id=v["MGCId"], name=v["MGCName"])

    @validator("create_date", "update_date", "pub_date", pre=True)
    def _parse_date(cls, v):
        if v is None:
            return v
        try:
            return datetime.strptime(v, "%Y/%m/%d %H:%M:%S").isoformat()
        except ValueError:
            pass
        return v

    @validator("lineage", pre=True)
    def _parse_lineage(cls, v):
        if v is None:
            return v
        return v.split("; ")

    @validator("lineage_ex", pre=True)
    def _parse_lineage_ex(cls, v):
        if v is None:
            return v
        return list(map(LineageEx.from_dict, v))
