from decimal import Decimal
from pydantic import BaseModel, Field

class BreakRecord(BaseModel):
    '''A reconciliation break record that requires EDMCS investigation.'''

    # Identifier
    record_id: str = Field(
        description='Unique identifier of the recon break.'
    )
    business_dt: str = Field(
        description='Business date of the recon break.'
    )

    # Amounts
    pre_fah_balance: Decimal = Field(
        description='Amount reported by Pre-FAH.'
    )
    gl_balance: Decimal = Field(
        description='Amount reported by GL.'
    )
    difference: Decimal = Field(
        description='Difference between Pre-FAH and GL balances.'
    )

    # Gl Segments
    entity: str = Field(
        description='Entity GL Segment.'
    )
    department: str = Field(
        description='Department GL Segment.'
    )
    branch: str = Field(
        description='Branch GL Segment.'
    )
    account: str = Field(
        description='Account GL Segment.'
    )
    sub_account: str = Field(
        description='Sub-Account GL Segment.'
    )
    affiliate: str = Field(
        description='Affiliate GL Segment.'
    )
    product: str = Field(
        description='Product GL Segment.'
    )
    book_code: str = Field(
        description='Book Code GL Segment.'
    )
    source: str = Field(
        description='Source GL Segment.'
    )
    project: str = Field(
        description='Project GL Segment.'
    )
    future1: str = Field(
        description='Future1 GL Segment.'
    )
    future2: str = Field(
        description='Future2 GL Segment.'
    )

    # SL Segments
    ledger: str = Field(
        description='Ledger segment.'
    )
    currency: str = Field(
        description='Currency segment.'
    )
