from pathlib import Path
from typing import List, Set

from api_compose import get_logger, DiscoveryEvent
from api_compose.services.common.models.base import BaseModel

logger = get_logger(__name__)


def filter_by_inclusion(
        models: List[BaseModel],
        include_manifest_file_paths: List[Path],
        include_tags: Set[str],
        include_models: List[str],
) -> List[BaseModel]:
    """Assume no models are required"""
    required_models = []
    for model in models:
        is_include = False
        if len(include_manifest_file_paths) > 0:
            if model.manifest_file_path in include_manifest_file_paths:
                is_include = True
            else:
                logger.warning(f'Include Manifest File Path Filter {include_manifest_file_paths} not working', DiscoveryEvent())

        if len(include_tags) > 0:
            for include_tag in include_tags:
                if include_tag in model.tags:
                    is_include = True

            if not is_include:
                logger.warning(f'Include Tags Filter {include_tags} not working', DiscoveryEvent())

        if len(include_models) > 0:
            for include_model in include_models:
                if include_model == model.model_name:
                    is_include = True
            if not is_include:
                logger.warning(f'Include Models Filter {include_models} not working', DiscoveryEvent())

        if is_include:
            required_models.append(model)

    return required_models


def filter_by_exclusion(
        models: List[BaseModel],
        exclude_manifest_file_paths: List[Path],
        exclude_tags: Set[str],
        exclude_models: List[str],
) -> List[BaseModel]:
    required_models = []

    for model in models:
        is_exclude = False

        if len(exclude_manifest_file_paths) > 0:
            if model.manifest_file_path in exclude_manifest_file_paths:
                is_exclude = True
            else:
                logger.warning(f'Exclude Manifest File Path Filter {exclude_manifest_file_paths} not working', DiscoveryEvent())

        if len(exclude_tags) > 0:
            for exclude_tag in exclude_tags:
                if exclude_tag in model.tags:
                    is_exclude = True
            if not is_exclude:
                logger.warning(f'Exclude Tags Filter {exclude_tags} not working', DiscoveryEvent())

        if len(exclude_models) > 0:
            for exclude_model in exclude_models:
                if exclude_model == model.model_name:
                    is_exclude = True
            if not is_exclude:
                logger.warning(f'Exclude Models Filter {exclude_models} not working', DiscoveryEvent())

        if not is_exclude:
            required_models.append(model)

    return required_models



