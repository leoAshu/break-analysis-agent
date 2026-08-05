from pydantic import BaseModel

class BreakRecord(BaseModel):
    '''A reconciliation break record that requires EDMCS investigation.'''

    record_id: str

    entity: str
    dept: str
    branch: str
    account: str
    sub_account: str

    pre_fah_balance: float
    gl_balance: float
    difference: float
