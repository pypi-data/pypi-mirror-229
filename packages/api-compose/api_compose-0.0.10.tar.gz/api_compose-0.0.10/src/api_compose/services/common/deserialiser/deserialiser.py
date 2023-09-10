__all__ = ['deserialise_manifest_to_model']

from pathlib import Path
from typing import Dict, Optional, Union, List

import yaml

from api_compose.services.common.env import get_env_vars
from api_compose.core.jinja.core.context import BaseJinjaContext
from api_compose.core.logging import get_logger
from api_compose.core.settings.settings import GlobalSettingsModelSingleton
from api_compose.core.utils.dict import merge_dict
from api_compose.core.utils.files import get_file_paths_relative_to
from api_compose.services.common.exceptions import ManifestIdNonUniqueException, ManifestIdNotFoundException, \
    ManifestDeserialisationException
from api_compose.services.common.events.deserialisation import DeserialisationEvent
from api_compose.services.common.jinja import build_compile_time_jinja_engine
from api_compose.services.common.models.base import BaseModel
from api_compose.services.common.registry.processor_registry import ProcessorRegistry

logger = get_logger(__name__)


def deserialise_manifest_to_model(
        manifest_file_path: Path,
        manifests_folder_path: Path,
        context: Dict = None,
) -> Optional[Union[BaseModel, str]]:
    """
    Given relative path to a manifest file, deserialise it to a model based on the field `model_name` in the file.

    Parameters
    ----------
    manifest_file_path: Path to Manifest relative to MANIFESTS_FOLDER_PATH
    manifests_folder_path: Path to Manifests Folder
    context: user-defined additional contexts

    Returns
    -------

    """
    dict_ = deserialise_manifest_to_dict(
        manifest_file_path=manifest_file_path,
        manifests_folder_path=manifests_folder_path,
        context=context,
    )

    model_name = dict_.get('model_name')
    return ProcessorRegistry.create_model_by_name(model_name, dict_)


def deserialise_manifest_to_dict(
        manifest_file_path: Path,
        manifests_folder_path: Path,
        context: Dict = None,
) -> Dict:
    if context is None:
        context = {}

    # Precendence - CLI Env Var >> Manifest-specific Env Var >> .env file env var
    context_merged = merge_dict(overlayed_dict=get_env_vars(), overlaying_dict=context)
    context_merged = merge_dict(overlayed_dict=context_merged,
                                overlaying_dict=dict(GlobalSettingsModelSingleton.get().cli_options.cli_context))

    # Letting know what context is passed is important only when rendering is strict
    logger.debug(f'Deserialising {manifest_file_path=} relative to {manifests_folder_path=}. \n' f'{context_merged=}',
                 DeserialisationEvent())

    # Read + Render
    jinja_engine = build_compile_time_jinja_engine(manifests_folder_path)
    relative_manifest_path = get_manifest_relative_path(manifests_folder_path, manifest_file_path)

    str_, is_success, exec = jinja_engine.set_template_by_file_path(template_file_path=str(relative_manifest_path),
                                                                    can_strip=True).render_to_str(
        jinja_context=BaseJinjaContext(**context_merged))

    if not is_success:
        raise ManifestDeserialisationException(
            manifest_file_path=manifests_folder_path.joinpath(relative_manifest_path),
            context=context_merged,
        ) from exec

    dict_ = yaml.safe_load(str_)
    if dict_.get('id'):
        logger.warning(f'Id field is already set in the file. Will be overridden by the file name {id=}',
                       DeserialisationEvent())

    dict_['id'] = relative_manifest_path.stem
    dict_['manifest_file_path'] = relative_manifest_path
    return dict_


def get_manifest_relative_path(
        manifests_folder_path: Path,
        manifest_file_path: Path,
) -> Path:
    stem: str = Path(manifest_file_path).stem
    relative_paths = get_file_paths_relative_to(manifests_folder_path, stem)
    if len(relative_paths) == 0:
        raise ManifestIdNotFoundException(manifests_folder_path, stem)
    elif len(relative_paths) > 1:
        raise ManifestIdNonUniqueException(manifests_folder_path)
    else:
        return relative_paths[0]


def get_all_template_paths(manifest_folder_path: Path) -> List[Path]:
    jinja_engine = build_compile_time_jinja_engine(manifests_folder_path=manifest_folder_path)
    return jinja_engine.get_available_templates()
