#  Copyright (c) 2023 Roboto Technologies, Inc.
from typing import Any, Optional

import pydantic

from ...query import ConditionType
from ..actions import (
    ComputeRequirements,
    ContainerParameters,
)
from .trigger_record import (
    TriggerForEachPrimitive,
)


class CreateTriggerRequest(pydantic.BaseModel):
    # Required
    name: str = pydantic.Field(regex=r"[\w\-]{1,256}")
    action_name: str
    required_inputs: list[str]
    for_each: TriggerForEachPrimitive
    compute_requirement_overrides: Optional[ComputeRequirements] = None
    container_parameter_overrides: Optional[ContainerParameters] = None
    condition: Optional[ConditionType] = None


class QueryTriggersRequest(pydantic.BaseModel):
    filters: dict[str, Any] = pydantic.Field(default_factory=dict)

    class Config:
        extra = "forbid"
