from pathlib import Path
from typing import Annotated, List, Optional

import click

from api_compose.cli.commands import config
from api_compose.cli.session_builder import parse_models, convert_models_to_session
from api_compose.cli.utils.yaml_dumper import dump_dict_to_single_yaml_file
from api_compose.core.logging import get_logger
from api_compose.core.settings.settings import GlobalSettingsModelSingleton
from api_compose.root import run_session_model
from api_compose.version import __version__

logger = get_logger(__name__)

import typer
from typer.core import TyperGroup as TyperGroupBase

DOCUMENTATION_URL = ""
EPILOG_TXT = f"Doc: {DOCUMENTATION_URL}"
HELP_TXT = "Declaratively Compose, Test and Report your API Calls"
COMPILED_FOLDER_PATH = GlobalSettingsModelSingleton.get().build_folder.joinpath(
    GlobalSettingsModelSingleton.get().compiled_folder
)
RUN_FOLDER_PATH = GlobalSettingsModelSingleton.get().build_folder.joinpath(
    GlobalSettingsModelSingleton.get().run_folder
)


class TyperGroup(TyperGroupBase):
    """Custom TyperGroup class."""

    def get_usage(self, ctx: click.Context) -> str:
        """Override get_usage."""
        usage = super().get_usage(ctx)
        message = (
                usage
                + f'\nVersion: {__version__}'
        )
        return message


app = typer.Typer(
    help=HELP_TXT,
    short_help=HELP_TXT,
    epilog=EPILOG_TXT,
    no_args_is_help=True,
    cls=TyperGroup
)

app.add_typer(config.app, name='cfg', help="Configuration")


@app.command(help="Print CLI Version")
def version() -> None:
    typer.echo(__version__)


@app.command(help="Scaffold a Sample Project Structure")
## TODO: Do a network call and git clone the example folder in the github repo instead
## TODO: Let users choose which example to clone
def scaffold(project_name: str) -> None:
    root = Path(project_name).absolute()
    if root.exists():
        raise ValueError(f'File/Folder {root} already exists!')

    root.mkdir(parents=True)
    for source in Path(__file__).parent.joinpath('scaffold_data').glob('**/*'):
        if source.is_file():
            relative_path = Path(*source.relative_to(Path(__file__).parent).parts[1:])
            dest = root.joinpath(relative_path)
            dest.parent.mkdir(exist_ok=True, parents=True)
            dest.write_bytes(source.read_bytes())
    typer.echo(f'Project {project_name} is created!')


@app.command(help=f"Compile and dump manifests as session to Path {COMPILED_FOLDER_PATH}")
def compile(
        include_manifest_file_paths: Annotated[
            Optional[List[Path]],
            typer.Option("--file", "-f", help='Relative Path to Manifests to include')
        ] = None,

        include_tags: Annotated[
            Optional[List[str]],
            typer.Option("--tag", "-t", help="Tag in manifest to look for to include")
        ] = None,

        include_models: Annotated[
            Optional[List[str]],
            typer.Option("--model", "-m", help="Models to include")
        ] = None,

        exclude_manifest_file_paths: Annotated[
            Optional[List[Path]],
            typer.Option("--no-file", "-F", help='Relative Path to Manifests to exclude')
        ] = None,

        exclude_tags: Annotated[
            Optional[List[str]],
            typer.Option("--no-tag", "-T", help="Tag in manifest to look for to exclude")
        ] = None,

        exclude_models: Annotated[
            Optional[List[str]],
            typer.Option("--no-model", "-M", help="Models to exclude")
        ] = None,

        is_interactive: Annotated[
            bool,
            typer.Option("--interactive/--no-interactive", "-i/-I", help='Start interactive shell or not')
        ] = False,

        ctx: Annotated[Optional[List[str]], typer.Option()] = None
) -> None:
    """
    Compile and output model
    Usage:
    acp render --ctx key1=val1 --ctx key2=val2
    """
    required_models = parse_models(
        include_manifest_file_paths=include_manifest_file_paths,
        include_tags=set(include_tags),
        include_models=include_models,
        exclude_manifest_file_paths=exclude_manifest_file_paths,
        exclude_tags=set(exclude_tags),
        exclude_models=exclude_models,
        is_interactive=is_interactive,
        ctx=ctx,
        manifests_folder_path=GlobalSettingsModelSingleton.get().discovery.manifests_folder_path,
    )

    session_model = convert_models_to_session(required_models)
    folder_path = COMPILED_FOLDER_PATH.joinpath(session_model.id)

    # Dump individual file
    for model in required_models:
        dump_dict_to_single_yaml_file(model.model_dump(),
                                      folder_path.joinpath(model.manifest_file_path))
    # Dump Session
    dump_dict_to_single_yaml_file(session_model.model_dump(),
                                  folder_path.joinpath('session.yaml'))


@app.command(help=f"Compile, run and dump manifests as session to Path {RUN_FOLDER_PATH}")
def run(
        include_manifest_file_paths: Annotated[
            Optional[List[Path]],
            typer.Option("--file", "-f", help='Relative Path to Manifests to include')
        ] = None,

        include_tags: Annotated[
            Optional[List[str]],
            typer.Option("--tag", "-t", help="Tag in manifest to look for to include")
        ] = None,

        include_models: Annotated[
            Optional[List[str]],
            typer.Option("--model", "-m", help="Models to include")
        ] = None,

        exclude_manifest_file_paths: Annotated[
            Optional[List[Path]],
            typer.Option("--no-file", "-F", help='Relative Path to Manifests to exclude')
        ] = None,

        exclude_tags: Annotated[
            Optional[List[str]],
            typer.Option("--no-tag", "-T", help="Tag in manifest to look for to exclude")
        ] = None,

        exclude_models: Annotated[
            Optional[List[str]],
            typer.Option("--no-model", "-M", help="Models to exclude")
        ] = None,

        is_interactive: Annotated[
            bool,
            typer.Option("--interactive/--no-interactive", "-i/-I", help='Start interactive shell or not')
        ] = False,

        ctx: Annotated[Optional[List[str]], typer.Option()] = None
):
    """
    Compile, run and output model
    acp run --ctx key1=val1 --ctx key2=val2
    """
    required_models = parse_models(
        include_manifest_file_paths=include_manifest_file_paths,
        include_tags=set(include_tags),
        include_models=include_models,
        exclude_manifest_file_paths=exclude_manifest_file_paths,
        exclude_tags=set(exclude_tags),
        exclude_models=exclude_models,
        is_interactive=is_interactive,
        ctx=ctx,
        manifests_folder_path=GlobalSettingsModelSingleton.get().discovery.manifests_folder_path,
    )
    session_model = convert_models_to_session(required_models)
    session_model = run_session_model(session_model)

    folder_path = RUN_FOLDER_PATH.joinpath(session_model.id)

    # Dump individual file
    for model in required_models:
        dump_dict_to_single_yaml_file(model.model_dump(),
                                      folder_path.joinpath(model.manifest_file_path))

    dump_dict_to_single_yaml_file(session_model.model_dump(),
                                  folder_path.joinpath('session.yaml'))


print('herllo')
