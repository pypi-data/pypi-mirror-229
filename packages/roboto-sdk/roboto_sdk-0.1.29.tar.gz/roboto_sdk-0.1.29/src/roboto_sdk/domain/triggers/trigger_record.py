#  Copyright (c) 2023 Roboto Technologies, Inc.
import datetime
import enum
import typing

import pydantic

from ...query import ConditionType
from ..actions import (
    ComputeRequirements,
    ContainerParameters,
)


class TriggerForEachPrimitive(str, enum.Enum):
    Dataset = "dataset"
    DatasetFile = "dataset_file"


class TriggerRecord(pydantic.BaseModel):
    DISALLOWED_FOR_UPDATE: typing.ClassVar[set[str]] = {
        "name",
        "org_id",
        "created",
        "created_by",
        "modified",
        "modified_by",
    }

    name: str  # Sort Key
    org_id: str  # Partition Key
    created: datetime.datetime  # Persisted as ISO 8601 string in UTC
    created_by: str
    modified: datetime.datetime  # Persisted as ISO 8601 string in UTC
    modified_by: str
    action_name: str
    required_inputs: list[str]
    for_each: TriggerForEachPrimitive = TriggerForEachPrimitive.Dataset
    enabled: bool = True
    additional_inputs: typing.Optional[list[str]] = None
    compute_requirement_overrides: typing.Optional[ComputeRequirements] = None
    container_parameter_overrides: typing.Optional[ContainerParameters] = None
    condition: typing.Optional[ConditionType] = None
