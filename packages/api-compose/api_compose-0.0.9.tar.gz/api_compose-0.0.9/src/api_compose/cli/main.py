from pathlib import Path
from typing import Annotated, List, Optional

import click

from api_compose import get_logger
from api_compose.cli.commands import config
from api_compose.cli.session_builder import build_session
from api_compose.cli.utils.yaml_dumper import dump_dict_to_single_yaml_file, dump_collection_to_multiple_yaml_files
from api_compose.core.settings import GlobalSettingsModelSingleton
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
        include_manifest_file_paths: Annotated[Optional[List[Path]], typer.Option("--include-file", "-f",
                                                                                  help='Relative Path to Manifests to include')] = None,

        include_tags: Annotated[
            Optional[List[str]], typer.Option("--tag", "-t", help="Tag in manifest to look for to include")] = None,

        exclude_manifest_file_paths: Annotated[Optional[List[Path]], typer.Option("--exclude-file", "-F",
                                                                                  help='Relative Path to Manifests to exclude')] = None,

        exclude_tags: Annotated[Optional[List[str]], typer.Option("--exclude-tag", "-T",
                                                                  help="Tag in manifest to look for to exclude")] = None,

        is_interactive: Annotated[bool, typer.Option("--interactive/--no-interactive", "-i/-I",
                                                     help='Start interactive shell or not')] = False,
        ctx: Annotated[Optional[List[str]], typer.Option()] = None,
) -> None:
    """
    Compile and output model
    Usage:
    acp render --ctx key1=val1 --ctx key2=val2
    """
    session_model = build_session(
        include_manifest_file_paths=include_manifest_file_paths,
        include_tags=set(include_tags),
        exclude_manifest_file_paths=exclude_manifest_file_paths,
        exclude_tags=set(exclude_tags),
        is_interactive=is_interactive,
        ctx=ctx,
    )

    folder_path = COMPILED_FOLDER_PATH.joinpath(session_model.id)
    dump_collection_to_multiple_yaml_files(collection=session_model.model_dump(),
                                           folder_path=folder_path,
                                           key_to_path='manifest_file_path')
    dump_dict_to_single_yaml_file(session_model.model_dump(),
                                  folder_path.joinpath('session.yaml'))


@app.command(help=f"Compile, run and dump manifests as session to Path {RUN_FOLDER_PATH}")
def run(
        include_manifest_file_paths: Annotated[Optional[List[Path]], typer.Option("--include-file", "-f",
                                                                                  help='Relative Path to Manifests to include')] = None,

        include_tags: Annotated[
            Optional[List[str]], typer.Option("--tag", "-t", help="Tag in manifest to look for to include")] = None,

        exclude_manifest_file_paths: Annotated[Optional[List[Path]], typer.Option("--exclude-file", "-F",
                                                                                  help='Relative Path to Manifests to exclude')] = None,

        exclude_tags: Annotated[Optional[List[str]], typer.Option("--exclude-tag", "-T",
                                                                  help="Tag in manifest to look for to exclude")] = None,

        is_interactive: Annotated[bool, typer.Option("--interactive/--no-interactive", "-i/-I",
                                                     help='Start interactive shell or not')] = False,
        ctx: Annotated[Optional[List[str]], typer.Option()] = None
):
    """
    Compile, run and output model
    acp run --ctx key1=val1 --ctx key2=val2
    """
    session_model = build_session(
        include_manifest_file_paths=include_manifest_file_paths,
        include_tags=set(include_tags),
        exclude_manifest_file_paths=exclude_manifest_file_paths,
        exclude_tags=set(exclude_tags),
        is_interactive=is_interactive,
        ctx=ctx,
    )
    session_model = run_session_model(session_model)

    folder_path = RUN_FOLDER_PATH.joinpath(session_model.id)
    dump_collection_to_multiple_yaml_files(collection=session_model.model_dump(),
                                           folder_path=folder_path,
                                           key_to_path='manifest_file_path')
    dump_dict_to_single_yaml_file(session_model.model_dump(),
                                  folder_path.joinpath('session.yaml'))
