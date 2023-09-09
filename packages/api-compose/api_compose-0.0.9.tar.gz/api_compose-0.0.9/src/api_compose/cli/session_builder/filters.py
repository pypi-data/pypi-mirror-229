from pathlib import Path
from typing import List, Set

from api_compose.services.common.models.base import BaseModel


def filter_by_inclusion(
        models: List[BaseModel],
        include_manifest_file_paths: List[Path],
        include_tags: Set[str],
) -> List[BaseModel]:
    """Assume no models are required"""
    required_models = []
    for model in models:
        is_include = False
        if model.manifest_file_path in include_manifest_file_paths:
            is_include = True

        for include_tag in include_tags:
            if include_tag in model.tags:
                is_include = True

        if is_include:
            required_models.append(model)

    return required_models


def filter_by_exclusion(
        models: List[BaseModel],
        exclude_manifest_file_paths: List[Path],
        exclude_tags: Set[str],
) -> List[BaseModel]:
    required_models = []

    for model in models:
        is_exclude = False
        if model.manifest_file_path in exclude_manifest_file_paths:
            is_exclude = True

        for exclude_tag in exclude_tags:
            if exclude_tag in model.tags:
                is_exclude = True

        if not is_exclude:
            required_models.append(model)

    return required_models
