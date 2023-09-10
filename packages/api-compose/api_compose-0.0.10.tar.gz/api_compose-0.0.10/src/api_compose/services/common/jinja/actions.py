""" Jinja Globals """

from typing import List

import jinja2
from jinja2 import Environment

from api_compose.services.common.registry.jinja_function_registry import JinjaFunctionsRegistry
from api_compose.services.common.models.text_field.templated_text_field import BaseTemplatedTextField
from api_compose.services.common.registry.jinja_function_registry import JinjaFunctionType
from api_compose.services.composition_service.models.actions.actions.base_action import ReservedExecutionId
from api_compose.services.composition_service.models.actions.filters import _get_action_attr_from_action, \
    _get_action_attr_from_actions


@JinjaFunctionsRegistry.set(name='acp.actions.config_headers', type=JinjaFunctionType.Global)
@jinja2.pass_context
def get_action_config_headers(context: jinja2.runtime.Context, execution_id: str):
    """
    Example Usage in Jinja: {{ acp.actions.config_method('execution_id') }}
    """
    templated_text_field: BaseTemplatedTextField = _get_action_attr(execution_id, context, ['config', 'headers'], '$')
    return _render_templated_text_field(context, templated_text_field=templated_text_field)


@JinjaFunctionsRegistry.set(name='acp.actions.config_method', type=JinjaFunctionType.Global)
@jinja2.pass_context
def get_action_config_method(context: jinja2.runtime.Context, execution_id: str):
    """
    Example Usage in Jinja: {{ acp.actions.config_method('execution_id') }}
    """
    templated_text_field: BaseTemplatedTextField = _get_action_attr(execution_id, context, ['config', 'method'], '$')
    return _render_templated_text_field(context, templated_text_field=templated_text_field)


@JinjaFunctionsRegistry.set(name='acp.actions.config_params', type=JinjaFunctionType.Global)
@jinja2.pass_context
def get_action_config_params(context: jinja2.runtime.Context, execution_id: str):
    """
    Example Usage in Jinja: {{ acp.actions.config_params('execution_id') }}
    """
    templated_text_field: BaseTemplatedTextField = _get_action_attr(execution_id, context, ['config', 'params'], '$')
    return _render_templated_text_field(context, templated_text_field=templated_text_field)


@JinjaFunctionsRegistry.set(name='acp.actions.config_body', type=JinjaFunctionType.Global)
@jinja2.pass_context
def get_action_config_body(context: jinja2.runtime.Context, execution_id: str):
    """
    Example Usage in Jinja: {{ config('execution_id') }}
    """
    templated_text_field: BaseTemplatedTextField = _get_action_attr(execution_id, context, ['config', 'body'], '$')
    return _render_templated_text_field(context, templated_text_field=templated_text_field)


@JinjaFunctionsRegistry.set(name='acp.actions.input_url', type=JinjaFunctionType.Global)
@jinja2.pass_context
def get_action_input_url(context: jinja2.runtime.Context, execution_id: str):
    """
    Example Usage in Jinja: {{ acp.actions.input_body('execution_id', '$.some_field') }}
    """
    return _get_action_attr(execution_id, context, ['input', 'url'], '$')


@JinjaFunctionsRegistry.set(name='acp.actions.input_body', type=JinjaFunctionType.Global)
@jinja2.pass_context
def get_action_input_body(context: jinja2.runtime.Context, execution_id: str, json_path: str, get_all_matches: bool = False):
    """
    Example Usage in Jinja: {{ acp.actions.input_body('execution_id', '$.some_field') }}
    """
    return _get_action_attr(execution_id, context, ['input', 'body'], json_path, get_all_matches)


@JinjaFunctionsRegistry.set(name='acp.actions.output_body', type=JinjaFunctionType.Global)
@jinja2.pass_context
def get_action_output_body(context: jinja2.runtime.Context, execution_id: str, json_path: str, get_all_matches=False):
    """
    Example Usage in Jinja: {{ acp.actions.output_body('execution_id', '$.some_field') }}
    """
    return _get_action_attr(execution_id, context, ['output', 'body'], json_path, get_all_matches)


@JinjaFunctionsRegistry.set(name='acp.actions.output_headers', type=JinjaFunctionType.Global)
@jinja2.pass_context
def get_action_output_headers(context: jinja2.runtime.Context, execution_id: str, json_path: str, get_all_matches: bool = False):
    """
    Example Usage in Jinja: {{ acp.actions.output_headers('execution_id', '$.some_field') }}
    """
    return _get_action_attr(execution_id, context, ['output', 'headers'], json_path, get_all_matches)


@JinjaFunctionsRegistry.set(name='acp.actions.output_status_code', type=JinjaFunctionType.Global)
@jinja2.pass_context
def get_action_output_status_code(context: jinja2.runtime.Context, execution_id: str):
    """
    Example Usage in Jinja: {{ acp.actions.output_status_code('execution_id', '$.some_field') }}
    """
    return _get_action_attr(execution_id, context, ['output', 'status_code'])


def _get_action_attr(
        execution_id: str,
        context: jinja2.runtime.Context,
        action_attrs: List[str],
        json_path: str = "",
        get_all: bool = False,
):
    if execution_id == ReservedExecutionId.Self.value:
        return _get_action_attr_from_action(
            dict(context).get('current_action_model'),
            action_attrs,
            json_path,
            get_all,
        )
    else:
        return _get_action_attr_from_actions(
            execution_id,
            dict(context).get('action_models'),
            action_attrs,
            json_path,
            get_all
        )


def _render_templated_text_field(
        context: jinja2.runtime.Context,
        templated_text_field: BaseTemplatedTextField,
):
    """
    """
    # Context has all the global functions already
    str_ = Environment().from_string(templated_text_field.template).render(context)
    return templated_text_field.serde.deserialise(str_)
