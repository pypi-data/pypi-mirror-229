import jsonschema
from .schemas import SCHEMAS


def schema_validator(schema: str, data: dict) -> list:
    """_summary_

    Args:
        data (dict): _description_
        schema (str): _description_

    Returns:
        list:[] or ["error1",...]
    """
    errors = []
    schema_info = SCHEMAS.get(schema, {})
    if not schema_info:
        errors.append(f"schema {schema} not found")
        return errors

    validator = jsonschema.Draft7Validator(schema_info)
    for error in validator.iter_errors(data):
        errors.append(error.message)

    return {schema: errors} if errors else []


def validate_parameters(func, validate=True):
    def wrapper(self, *args, **kwargs):
        if any(arg is None for arg in args):
            raise ValueError("All parameters must have data")
        return func(self, *args, **kwargs)
    return wrapper
