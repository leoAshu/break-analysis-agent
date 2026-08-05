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

@tool
def validate_account(account: str, region_code: str) -> str:
    '''Validate whether an account exists in EDMCS for the supplied region.'''

    valid_accounts_by_region = {
        'AD': {'A100', 'A200', 'A300', '198170'},
        'EMEA': {'A400', 'A500'},
        'APAC': {'A600', 'A700'},
    }

    valid_accounts = valid_accounts_by_region.get(region_code)

    if valid_accounts is None:
        return f'Unknown region code: {region_code}.'

    if account in valid_accounts:
        return (
            f'Account {account} is valid in EDMCS '
            f'for region {region_code}.'
        )

    return (
        f'Account {account} is not valid in EDMCS '
        f'for region {region_code}.'
    )
