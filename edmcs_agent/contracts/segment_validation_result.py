from typing import Any

from pydantic import BaseModel, Field


class SegmentValidationResult(BaseModel):
    '''Represents the EDMCS validation result for one GL segment.'''

    segment_name: str = Field(
        description='Business name of the validated GL segment.'
    )
    segment_value: str = Field(
        description='Value from the break record that was validated.'
    )
    is_valid: bool = Field(
        description='Whether the segment value is valid in EDMCS.'
    )
    reason: str | None = Field(
        default=None,
        description='Explanation of the validation result.'
    )
    reference_data: dict[str, Any] | None = Field(
        default=None,
        description='Optional supporting data returned by the validator.'
    )
