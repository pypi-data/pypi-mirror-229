from api_compose import JinjaFunctionsRegistry, JinjaFunctionType


@JinjaFunctionsRegistry.set(name='double_quote', type=JinjaFunctionType.Filter)
def add_quote(value):
    """
    Example Usage in Jinja: {{ value | double_quote }}
    """
    return f'"{value}"'
