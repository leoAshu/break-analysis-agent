from decimal import Decimal

from pydantic import BaseModel, Field

from edmcs_agent.contracts.segment_validation_result import SegmentValidationResult


class InvestigationResult(BaseModel):
    '''Represents the completed investigation of one reconciliation break.'''

    record_id: str = Field(
        description='Unique identifier of the investigated break record.'
    )
    region_code: str | None = Field(
        default=None,
        description='Region code resolved during the investigation.'
    )

    # Amounts
    pre_fah_balance: Decimal
    gl_balance: Decimal
    difference: Decimal

    # GL Segment Validations
    validations: list[SegmentValidationResult] = Field(
        default_factory=list,
        description='Result for every GL segment that was validated.'
    )

    is_explained: bool = Field(
        description=(
            'Whether the recon break is explained by one or more '
            'invalid EDMCS segment values.'
        )
    )
    invalid_segments: list[str] = Field(
        default_factory=list,
        description='Names of GL segments that failed validation.'
    )
    summary: str = Field(
        description='Human-readable investigation summary.'
    )
