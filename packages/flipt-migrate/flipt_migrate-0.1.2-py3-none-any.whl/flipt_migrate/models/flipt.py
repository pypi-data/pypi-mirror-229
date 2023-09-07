from enum import Enum
from pydantic import BaseModel


class Variant(BaseModel):
    key: str
    name: str | None
    description: str | None


class Distribution(BaseModel):
    variant: str
    rollout: float


class Rule(BaseModel):
    segment: str
    rank: int | None
    distributions: list[Distribution]


class FlagType(Enum):
    variant = "VARIANT_FLAG_TYPE"
    boolean = "BOOLEAN_FLAG_TYPE"


class Flag(BaseModel):
    key: str
    name: str
    description: str | None
    enabled: bool
    type: FlagType = FlagType.variant
    variants: list[Variant] | None
    rules: list[Rule] | None


class ConstraintComparisonType(Enum):
    string = "STRING_COMPARISON_TYPE"
    number = "NUMBER_COMPARISON_TYPE"
    boolean = "BOOLEAN_COMPARISON_TYPE"
    datetime = "DATETIME_COMPARISON_TYPE"


class ConstraintOperator(Enum):
    equals = "eq"
    not_equals = "neq"
    less_than = "lt"
    less_than_or_equal = "lte"
    greater_than = "gt"
    greater_than_or_equal = "gte"
    empty = "empty"
    not_empty = "notempty"
    prefix = "prefix"
    suffix = "suffix"
    present = "present"
    not_present = "notpresent"
    true = "true"
    false = "false"


class Constraint(BaseModel):
    property: str
    operator: ConstraintOperator = ConstraintOperator.equals
    value: str
    type: ConstraintComparisonType = ConstraintComparisonType.string


class SegmentMatchType(Enum):
    all = "ALL_MATCH_TYPE"
    any = "ANY_MATCH_TYPE"


class Segment(BaseModel):
    key: str
    name: str | None
    description: str | None
    match_type: SegmentMatchType = SegmentMatchType.all
    constraints: list[Constraint] | None


class Document(BaseModel):
    flags: list[Flag] | None
    segments: list[Segment] | None


class Collection(BaseModel):
    namespaces: dict[str, Document] | None
