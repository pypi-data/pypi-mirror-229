from openapi_client.paths.devices.get import ApiForget
from openapi_client.paths.devices.post import ApiForpost
from openapi_client.paths.devices.patch import ApiForpatch


class Devices(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
