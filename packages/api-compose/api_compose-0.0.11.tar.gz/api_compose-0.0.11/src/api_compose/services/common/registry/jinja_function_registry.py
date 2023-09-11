from enum import Enum
from typing import Callable, List

from pydantic import Field, BaseModel as _BaseModel

from api_compose.core.logging import get_logger
from api_compose.services.common.events.jinja_function_registration import JinjaFunctionRegistrationEvent

logger = get_logger(__name__)


class JinjaFunctionType(Enum):
    Global: str = 'Global'
    Filter: str = 'Filter'
    Test: str = 'Test'


class JinjaFunctionModel(_BaseModel):
    name: str = Field(description='dot-separated name. Dot indicates Namespace')
    type: JinjaFunctionType
    func: Callable


class JinjaFunctionsRegistry:
    """
    - Use Decorator to Register Jinja Functions

    Lazy evaluation of Calculated Field.
    Only evaluate when `render()` is called
    """

    _registry: List[JinjaFunctionModel] = []

    @classmethod
    def set(cls, name: str, type: JinjaFunctionType = JinjaFunctionType.Global):
        """
        Parameters
        ----------
        name: How the jinja function is accessed in the template
        type
        Returns
        -------

        """
        assert name not in [model.name for model in cls._registry], f'Jinja Function Name {name} is already taken!!!'

        if type != JinjaFunctionType.Global:
            assert '.' not in name, f"Type {type} does not support namespacing! Please update {name=}"

        def decorator(func: Callable):
            cls._registry.append(
                JinjaFunctionModel(
                    name=name,
                    type=type,
                    func=func
                )
            )
            logger.info("Registering Jinja Function %s of type %s " % (name, type.value),
                        JinjaFunctionRegistrationEvent())
            return func

        return decorator
