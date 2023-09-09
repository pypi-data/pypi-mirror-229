
from pathlib import Path
from typing import List, Set

from api_compose.cli.common import get_available_models
from api_compose.cli.session_builder.filters import filter_by_exclusion, filter_by_inclusion
from api_compose.cli.utils.parser import parse_context
from api_compose.core.logging import get_logger
from api_compose.core.settings import CliOptions
from api_compose.core.settings import GlobalSettingsModelSingleton
from api_compose.root import SessionModel
from api_compose.root.models.scenario import ScenarioModel
from api_compose.root.models.specification import SpecificationModel
from api_compose.services.common.deserialiser.deserialiser import get_manifest_relative_path
from api_compose.services.common.models.base import BaseModel
from api_compose.services.composition_service.models.actions.actions.base_action import BaseActionModel

logger = get_logger(__name__)


def build_session(
        include_manifest_file_paths: List[Path],
        include_tags: Set[str],
        exclude_manifest_file_paths: List[Path],
        exclude_tags: Set[str],
        is_interactive: bool,
        ctx: List[str],

) -> SessionModel:
    manifests_folder_path = GlobalSettingsModelSingleton.get().discovery.manifests_folder_path

    # Step 1: Set config
    include_manifest_file_paths = [get_manifest_relative_path(manifests_folder_path, include_path) for include_path
                                   in include_manifest_file_paths]
    exclude_manifest_file_paths = [get_manifest_relative_path(manifests_folder_path, exclude_path) for exclude_path
                                   in exclude_manifest_file_paths]

    GlobalSettingsModelSingleton.get().cli_options = CliOptions(
        cli_context=parse_context(ctx),
        is_interactive=is_interactive,

        include_manifest_file_paths=include_manifest_file_paths,
        include_tags=include_tags,
        exclude_manifest_file_paths=exclude_manifest_file_paths,
        exclude_tags=exclude_tags,
    )

    # Step 2: Get Available Models
    available_models = get_available_models(manifests_folder_path)

    # Step 3: Get Required Models
    if GlobalSettingsModelSingleton.get().cli_options.is_to_exclude:
        required_models = filter_by_exclusion(available_models, exclude_manifest_file_paths, exclude_tags)
    else:
        required_models = filter_by_inclusion(available_models, include_manifest_file_paths, include_tags)

    # Step 4: Build Session
    session = convert_models_to_session(required_models)

    return session


def convert_models_to_session(models: List[BaseModel]) -> SessionModel:
    """
    Build SessionModel from any given BaseModel

    Parameters
    ----------
    models

    Returns
    -------

    """
    default_id = 'default_id'
    default_description = 'default description'
    specification_models: List[SpecificationModel] = []
    for model in models:
        if isinstance(model, BaseActionModel):
            scenario_model = ScenarioModel(id=default_id, description=default_description, actions=[model])
            specification_model = SpecificationModel(id=default_id, description=default_description,
                                                     scenarios=[scenario_model])
            specification_models.append(specification_model)
        elif isinstance(model, ScenarioModel):
            specification_model = SpecificationModel(id=default_id, description=default_description, scenarios=[model])
            specification_models.append(specification_model)
        elif isinstance(model, SpecificationModel):
            specification_models.append(model)
        else:
            raise ValueError(f'Unhandled model type {type(model)}')

    session_model = SessionModel(specifications=specification_models)

    return session_model
