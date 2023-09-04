import click
from aura.api_command import api_command
from aura.api_repository import make_api_call
from aura.util.get_instance_id import get_instance_id


@api_command(name="pause", help_text="Pause an instance")
@click.option("--instance-id", "-id", help="The instance ID")
@click.option("--name", "-n", help="The instance name")
def pause_instance(instance_id: str, name: str):
    """
    Pause an instance.

    Makes a "POST /instances/:instanceId/pause" API request.
    """

    instance_id = get_instance_id(instance_id, name)

    path = f"/instances/{instance_id}/pause"

    return make_api_call("POST", path)
