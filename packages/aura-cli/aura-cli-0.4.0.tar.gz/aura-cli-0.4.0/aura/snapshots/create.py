import click
from aura.api_command import api_command
from aura.api_repository import make_api_call
from aura.util.get_instance_id import get_instance_id


@api_command(name="create", help_text="Create a new snapshot")
@click.option("--instance-id", "-id", help="The instance ID")
@click.option("--instance-name", "-n", help="The instance name")
def create_snapshot(instance_id: str, instance_name: str):
    """
    Create a new snapshot of an instance.

    Makes "POST /instances/:instanceId/snapshots" API request.
    """

    instance_id = get_instance_id(instance_id, instance_name)

    path = f"/instances/{instance_id}/snapshots"

    return make_api_call("POST", path)
