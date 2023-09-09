from pathlib import Path
from typing import List

from api_compose.services.common.deserialiser.deserialiser import deserialise_manifest_to_model, get_all_template_paths
from api_compose.services.common.models.base import BaseModel


def get_available_models(manifests_folder_path: Path) -> List[BaseModel]:
    """Loop through al manifest templates, render them and deserialise to BaseModels"""
    models = []

    for template_path in get_all_template_paths(manifests_folder_path):
        models.append(
            deserialise_manifest_to_model(
                template_path,
                manifests_folder_path=manifests_folder_path,
                context=None,
            )
        )

    return models


