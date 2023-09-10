"""
Programme's Global Settings.

Cannot use logger. That would cause Cyclical Dependency OR double or triple logging of the same message
"""

__all__ = ['GlobalSettingsModelSingleton', 'GlobalSettingsModel']

import logging
from pathlib import Path
from typing import List, Optional, Dict, Set, Any

from pydantic import Field, model_validator

from api_compose.core.events.base import EventType
from api_compose.core.settings.exceptions import IncludeExcludeBothSetException
from api_compose.core.settings.yaml_settings import YamlBaseSettings, BaseSettings, SettingsConfigDict
from api_compose.services.persistence_service.models.enum import BackendProcessorEnum
from api_compose.services.reporting_service.models.enum import ReportProcessorEnum


class ActionSettings(BaseSettings):
    pass


class BackendSettings(BaseSettings):
    processor: BackendProcessorEnum = BackendProcessorEnum.SimpleBackend


class CliOptions(BaseSettings):
    is_interactive: bool = Field(False,
                                 description='When True, users will be prompted to create assertions dynamically at the end of each Scenario Run')
    cli_context: Dict[str, Any] = Field({}, description='context passed via CLI')

    include_manifest_file_paths: List[Path] = Field([], description='List of manifest file paths to include')
    include_tags: Set[str] = Field(set(), description='set of tags to look for in manifest(s) to include')
    include_models: List[str] = Field([], description='list of models to look for in manifest(s) to include')

    exclude_manifest_file_paths: List[Path] = Field([], description='List of manifest file paths to exclude')
    exclude_tags: Set[str] = Field(set(), description='set of tags to look for in manifest(s) to exclude')
    exclude_models: List[str] = Field([], description='list of models to look for in manifest(s) to exclude')

    @model_validator(mode='after')
    @classmethod
    def validate_not_both_include_and_exclude_are_specified(cls, m: 'CliOptions'):
        include_num = len(m.include_tags) + len(m.include_manifest_file_paths) + len(m.include_models)
        exclude_num = len(m.exclude_tags) + len(m.exclude_tags) + len(m.exclude_models)

        if include_num > 0 and exclude_num > 0:
            raise IncludeExcludeBothSetException()

        return m


class DiscoverySettings(BaseSettings):
    manifests_folder_path: Path = Path('manifests')
    functions_folder_path: Path = Path('functions')
    tags: Set[str] = set()


class LoggingSettings(BaseSettings):
    logging_level: int = logging.INFO
    log_file_path: Optional[Path] = Path('log.jsonl')
    event_filters: List[EventType] = []


class EnvFileSettings(BaseSettings):
    current_pack: str = Field(
        'base',
        description='Pack of env files to use in current session',
    )
    packs: Dict[str, List[Path]] = Field(
        {'base': [Path('envs/base-env.yaml')],
         'uat': [Path('envs/base-env.yaml'), Path('envs/uat-env.yaml')],
         'prod': [Path('envs/base-env.yaml'), Path('envs/prod-env.yaml')]
         },
        description='Mapping of pack to a list of env files'
    )


class ReportingSettings(BaseSettings):
    processor: ReportProcessorEnum = ReportProcessorEnum.HtmlReport
    reports_folder: Path = Path('reports')


class GlobalSettingsModel(YamlBaseSettings):
    action: ActionSettings = ActionSettings()
    backend: BackendSettings = BackendSettings()
    build_folder: Path = Path('build')
    cli_options: CliOptions = Field(CliOptions())
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
        env_file_paths: List[Path] = self.env_files.packs.get(self.env_files.current_pack, [])
        env_file_paths = [
            env_file_path for env_file_path in env_file_paths if
            env_file_path.exists() and env_file_path.is_file()
        ]

        if len(env_file_paths) == 0:
            print(f'WARNING: No Env Files found in pack {self.env_files.current_pack=}')

        return env_file_paths


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
