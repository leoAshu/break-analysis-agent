from collections.abc import Sequence
from langchain_core.tools import tool, BaseTool

def create_tools() -> Sequence[BaseTool]:
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
    def validate_entity(entity_code: str, region_code: str) -> str:
        '''Validate whether an entity exists in EDMCS for the supplied region.'''

        valid_entities = {
            'AD': {'505890', '505893'},
            'EMEA': {'505891'},
            'APAC': {'505892'},
        }

        is_valid = entity_code in valid_entities.get(region_code, [])
        message = (
            f'Entity {entity_code} exists in EDMCS for region {region_code}.'
            if is_valid else
            f'Entity {entity_code} was not found in EDMCS for region {region_code}.'
        )

        return message


    @tool
    def validate_department(department_code: str, region_code: str) -> str:
        '''Validate whether a department exists in EDMCS for the supplied region.'''

        valid_departments = {
            'AD': {'A04025', 'A04026'},
            'EMEA': {'A04027'},
            'APAC': {'A04028'},
        }

        is_valid = department_code in valid_departments.get(region_code, [])
        message = (
            f'Department {department_code} exists in EDMCS for region {region_code}.'
            if is_valid else
            f'Department {department_code} was not found in EDMCS for region {region_code}.'
        )

        return message


    @tool
    def validate_branch(branch_code: str, region_code: str) -> str:
        '''Validate whether a branch exists in EDMCS for the supplied region.'''

        valid_branches = {
            'AD': {'000000', '000001'},
            'EMEA': {'000002'},
            'APAC': {'000003'},
        }

        is_valid = branch_code in valid_branches.get(region_code, [])
        message = (
            f'Branch {branch_code} exists in EDMCS for region {region_code}.'
            if is_valid else
            f'Branch {branch_code} was not found in EDMCS for region {region_code}.'
        )

        return message


    @tool
    def validate_account(account_code: str, region_code: str) -> str:
        '''Validate whether an account exists in EDMCS for the supplied region.'''

        valid_accounts = {
            'AD': {'A100', 'A200', 'A300', '198170'},
            'EMEA': {'A400', 'A500'},
            'APAC': {'A600', 'A700'},
        }

        is_valid = account_code in valid_accounts.get(region_code, [])
        message = (
            f'Account {account_code} exists in EDMCS for region {region_code}.'
            if is_valid else
            f'Account {account_code} was not found in EDMCS for region {region_code}.'
        )

        return message


    @tool
    def validate_sub_account(sub_account_code: str, region_code: str) -> str:
        '''Validate whether a sub-account exists in EDMCS for the supplied region.'''

        valid_sub_accounts = {
            'AD': {'S100', 'S200', 'S300', '114110'},
            'EMEA': {'S400', 'S500'},
            'APAC': {'S600', 'S700'},
        }

        is_valid = sub_account_code in valid_sub_accounts.get(region_code, [])
        message = (
            f'Sub-Account {sub_account_code} exists in EDMCS for region {region_code}.'
            if is_valid else
            f'Sub-Account {sub_account_code} was not found in EDMCS for region {region_code}.'
        )

        return message


    @tool
    def validate_affiliate(affiliate_code: str, region_code: str) -> str:
        '''Validate whether an affiliate exists in EDMCS for the supplied region.'''

        valid_affiliates = {
            'AD': {'000000', '000001'},
            'EMEA': {'000002'},
            'APAC': {'000003'},
        }

        is_valid = affiliate_code in valid_affiliates.get(region_code, [])
        message = (
            f'Affiliate {affiliate_code} exists in EDMCS for region {region_code}.'
            if is_valid else
            f'Affiliate {affiliate_code} was not found in EDMCS for region {region_code}.'
        )

        return message


    @tool 
    def validate_book_code(book_code: str, region_code: str) -> str:
        '''Validate whether a book code exists in EDMCS for the supplied region.'''

        valid_book_codes = {
            'AD': {'JGAAP_DELTA', 'JGAAP_ALPHA'},
            'EMEA': {'JGAAP_BETA'},
            'APAC': {'JGAAP_GAMMA'},
        }

        is_valid = book_code in valid_book_codes.get(region_code, [])
        message = (
            f'Book Code {book_code} exists in EDMCS for region {region_code}.'
            if is_valid else
            f'Book Code {book_code} was not found in EDMCS for region {region_code}.'
        )

        return message


    @tool
    def validate_source(source_code: str, region_code: str) -> str:
        '''Validate whether a source exists in EDMCS for the supplied region.'''

        valid_sources = {
            'AD': {'11392:039', '11392:040'},
            'EMEA': {'11392:041'},
            'APAC': {'11392:042'},
        }

        is_valid = source_code in valid_sources.get(region_code, [])
        message = (
            f'Source {source_code} exists in EDMCS for region {region_code}.'
            if is_valid else
            f'Source {source_code} was not found in EDMCS for region {region_code}.'
        )

        return message


    @tool
    def validate_product(product_code: str, region_code: str) -> str:
        '''Validate whether a product exists in EDMCS for the supplied region.'''

        valid_products = {
            'AD': {'100005', '100006'},
            'EMEA': {'100007'},
            'APAC': {'100008'},
        }

        is_valid = product_code in valid_products.get(region_code, [])
        message = (
            f'Product {product_code} exists in EDMCS for region {region_code}.'
            if is_valid else
            f'Product {product_code} was not found in EDMCS for region {region_code}.'
        )

        return message


    @tool
    def validate_project(project_code: str, region_code: str) -> str:
        '''Validate whether a project exists in EDMCS for the supplied region.'''

        valid_projects = {
            'AD': {'BILATERAL', 'MULTILATERAL'},
            'EMEA': {'PROJECT_X'},
            'APAC': {'PROJECT_Y'},
        }

        is_valid = project_code in valid_projects.get(region_code, [])
        message = (
            f'Project {project_code} exists in EDMCS for region {region_code}.'
            if is_valid else
            f'Project {project_code} was not found in EDMCS for region {region_code}.'
        )

        return message


    return [
        get_region_code,
        validate_entity,
        validate_department,
        validate_branch,
        validate_account,
        validate_sub_account,
        validate_affiliate,
        validate_book_code,
        validate_source,
        validate_product,
        validate_project,
    ]
