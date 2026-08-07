from pydantic import BaseModel


class RegionResolutionResult(BaseModel):
    '''Result of resolving the EDMCS region for a break record.'''

    region_code: str
    region_name: str | None = None
