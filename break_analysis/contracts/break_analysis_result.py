from pydantic import BaseModel, Field

from edmcs_agent.contracts import InvestigationResult


class BreakAnalysisResult(BaseModel):
    '''Represents the final analysis of a single reconciliation break.'''

    record_id: str = Field(
        description='Unique identifier of the analyzed reconciliation break.'
    )

    is_explained: bool = Field(
        description='Whether the break has been explained by the investigation.'
    )

    explanation: str = Field(
        description='Concise explanation of the identified cause of the break.'
    )

    edmcs_result: InvestigationResult | None = Field(
        default=None,
        description='EDMCS investigation result, when EDMCS validation was performed.'
    )
