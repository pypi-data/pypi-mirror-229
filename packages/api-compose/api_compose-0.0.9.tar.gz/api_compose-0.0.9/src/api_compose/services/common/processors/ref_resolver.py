from pathlib import Path

from api_compose import GlobalSettingsModelSingleton
from api_compose.core.utils.dict import merge_dict
from api_compose.services.common.deserialiser.deserialiser import deserialise_manifest_to_model
from api_compose.services.common.models.base import BaseModel
from api_compose.services.common.models.ref_resolver import RefResolverModel
from api_compose.services.common.processors.base import BaseProcessor
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorType, ProcessorCategory


@ProcessorRegistry.set(
    processor_type=ProcessorType.Builtin,
    processor_category=ProcessorCategory.Ref,
    models=[
        RefResolverModel(
            id='some_ref',
            description='',
            ref='actions/action_one.yaml',
            context=dict(
                execution_id='action_one_exec_one',
                url='http://abc.com',
                limit='12',
            ),
        ),
    ]
)
class RefResolver(BaseProcessor):
    """Resolve the reference"""

    def __init__(
            self,
            ref_resolver_model: RefResolverModel,
    ):
        super().__init__()
        self.ref_resolver_model = ref_resolver_model

    def resolve(
            self,
            manifests_folder_path: Path,
    ) -> BaseModel:
        merged_context = merge_dict(GlobalSettingsModelSingleton.get().env_vars, self.ref_resolver_model.context)
        merged_context = merge_dict(merged_context, GlobalSettingsModelSingleton.get().cli_options.cli_context)

        model: BaseModel = deserialise_manifest_to_model(
            manifest_file_path=self.ref_resolver_model.ref,
            manifests_folder_path=manifests_folder_path,
            context=merged_context,
        )

        model.manifest_file_path = None
        return model
