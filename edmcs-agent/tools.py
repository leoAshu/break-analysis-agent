from langchain_core.tools import tool

@tool
def get_region_code(entity: str) -> str:
    '''Return the EDMCS region code for the given entity.'''

    region_by_entity = {
        '505890': 'AD',
        '505891': 'EMEA',
        '505892': 'APAC'
    }

    region_code = region_by_entity.get(entity)

    if region_code is None:
        return f'No region code found for entity {entity}.'

    return region_code
