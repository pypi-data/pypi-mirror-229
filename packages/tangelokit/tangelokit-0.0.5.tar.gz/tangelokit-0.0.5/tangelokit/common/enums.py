from enum import Enum, unique


@unique
class SchemasTypes(Enum):
    """Class for enums of schemas types"""

    DISBURSEMENT = "disbursement_schema"
    CREDIT_LINE = 'credit_line_schema'
    CREDIT_REQUEST = 'credit_request_schema'
    PRODUCT = 'product_schema'
    CONTACT = 'contact_schema'

    @staticmethod
    def values():
        return list(map(lambda e: e.value, SchemasTypes))
