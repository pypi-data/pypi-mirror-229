"""
Programme's Global Settings.

Cannot use logger. That would cause Cyclical Dependency OR double or triple logging of the same message
"""

__all__ = ['GlobalSettingsModelSingleton', 'GlobalSettingsModel']

import logging
from pathlib import Path
from typing import List, Optional, Dict, Set, Any

import yaml
from pydantic import Field, model_validator

from api_compose.core.events.base import EventType
from api_compose.core.settings.yaml_settings import YamlBaseSettings, BaseSettings, SettingsConfigDict
from api_compose.core.utils.dict import merge_dict
from api_compose.services.persistence_service.models.enum import BackendProcessorEnum
from api_compose.services.reporting_service.models.enum import ReportProcessorEnum


class ActionSettings(BaseSettings):
    pass


class BackendSettings(BaseSettings):
    processor: BackendProcessorEnum = BackendProcessorEnum.SimpleBackend


class CliContext(BaseSettings):
    model_config = SettingsConfigDict(extra='allow')


class CliOptions(BaseSettings):
    is_interactive: bool = Field(False,
                                 description='When True, users will be prompted to create assertions dynamically at the end of each Scenario Run')
    cli_context: Dict[str, Any] = Field({}, description='context passed via CLI')

    ## new
    include_manifest_file_paths: List[Path] = Field([], description='List of manifest file paths to include')
    include_tags: Set[str] = Field(set(), description='set of tags to look for in manifest(s) to include')

    exclude_manifest_file_paths: List[Path] = Field([], description='List of manifest file paths to exclude')
    exclude_tags: Set[str] = Field(set(), description='set of tags to look for in manifest(s) to exclude')

    @property
    def is_to_exclude(self) -> bool:
        """When True, it starts from all models and then exclude. When False, it starts from no models and then include"""
        include_num = len(self.include_tags) + len(self.include_manifest_file_paths)

        if include_num > 0:
            return False
        else:
            return True

    @model_validator(mode='after')
    @classmethod
    def validate_not_both_include_and_exclude_are_specifiied(cls, m: 'CliOptions'):
        include_num = len(m.include_tags) + len(m.include_manifest_file_paths)
        exclude_num = len(m.exclude_tags) + len(m.exclude_tags)
        if include_num != 0:
            assert exclude_num == 0, 'You cannot exclude any model when you start from excluding all manifests'

        if exclude_num != 0:
            assert include_num == 0, 'You cannot include any model when you start from including all manifests'
        return m

    @model_validator(mode='before')
    @classmethod
    def validate_tags_and_select_not_set_together(cls, values):
        select = values.get('select')
        tags = values.get('tags')
        if select and tags:
            raise ValueError(f'Tags and Select cannot be set at the same time. Display \n'
                             f'{select=}, {tags=}')
        return values


class DiscoverySettings(BaseSettings):
    manifests_folder_path: Path = Path('manifests')
    functions_folder_path: Path = Path('functions')
    tags: Set[str] = set()


class LoggingSettings(BaseSettings):
    logging_level: int = logging.INFO
    log_file_path: Optional[Path] = Path('log.jsonl')
    event_filters: List[EventType] = []


class EnvFileSettings(BaseSettings):
    base_path: Optional[Path] = Path('envs/base-env.yaml')
    overlay_paths: List[Path] = []


class ReportingSettings(BaseSettings):
    processor: ReportProcessorEnum = ReportProcessorEnum.HtmlReport
    reports_folder: Path = Path('reports')


class GlobalSettingsModel(YamlBaseSettings):
    action: ActionSettings = ActionSettings()
    backend: BackendSettings = BackendSettings()
    build_folder: Path = Path('build')
    cli_options: CliOptions = Field(CliOptions(), exclude=True)
    compiled_folder: Path = Path('compiled')
    discovery: DiscoverySettings = DiscoverySettings()
    logging: LoggingSettings = LoggingSettings()
    env_files: EnvFileSettings = EnvFileSettings()
    reporting: ReportingSettings = ReportingSettings()
    run_folder: Path = Path('run')

    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        yaml_file="config.yaml",
        env_prefix='acp__',
        extra='forbid'
    )

    @property
    def all_env_files(self) -> List[Path]:
        env_file_paths: List[Path] = [self.env_files.base_path] + self.env_files.overlay_paths
        return [env_file_path for env_file_path in env_file_paths if env_file_path.exists() and env_file_path.is_file()]

    @property
    def env_vars(self) -> Dict[str, Any]:
        env_vars = {}
        for env_file_path in self.all_env_files:
            if env_file_path.exists():
                with open(env_file_path, 'r') as f:
                    new_dict = yaml.load(f, Loader=yaml.FullLoader)
            # Merge
            env_vars = merge_dict(env_vars, new_dict)
        return env_vars


class GlobalSettingsModelSingleton():
    _GLOBAL_SETTINGS_MODEL: Optional[GlobalSettingsModel] = None

    @classmethod
    def set(cls):
        cls._GLOBAL_SETTINGS_MODEL = GlobalSettingsModel()

    @classmethod
    def get(cls) -> GlobalSettingsModel:
        if cls._GLOBAL_SETTINGS_MODEL is None:
            raise ValueError('Global Settings Model not yet created!')
        return cls._GLOBAL_SETTINGS_MODEL
