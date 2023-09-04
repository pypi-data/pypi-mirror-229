import click
from aura.config_repository import CLIConfig
from aura.error_handler import handle_error
from aura.decorators import pass_config
from aura.logger import get_logger


@click.option("--name", "-n", help="Name for the credentials")
@click.option("--client-id", "-id", help="The client ID")
@click.option("--client-secret", "-s", help="The client secret")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Print verbose output")
@click.command(name="add", help="Add new OAuth client credentials")
@pass_config
def add_credentials(
    config: CLIConfig, name: str, client_id: str, client_secret: str, verbose: bool
):
    """
    Add a new set of credentials
    """
    logger = get_logger("auracli")

    if not name:
        name = click.prompt("Credentials Name")
    if not client_id:
        client_id = click.prompt("Client ID")
    if not client_secret:
        client_secret = click.prompt("Client Secret")

    try:
        config.add_credentials(name, client_id, client_secret)
    except Exception as exception:
        handle_error(exception)

    logger.info(f'Credentials "{name}" successfully saved. Now using "{name}" as credentials.')
    if not config.env["VERBOSE"]:
        print(f'Credentials "{name}" successfully saved. Now using "{name}" as credentials.')

    logger.debug("CLI command completed successfully.")
