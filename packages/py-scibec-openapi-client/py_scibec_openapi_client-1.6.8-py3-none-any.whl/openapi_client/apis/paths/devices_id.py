from openapi_client.paths.devices_id.get import ApiForget
from openapi_client.paths.devices_id.delete import ApiFordelete
from openapi_client.paths.devices_id.patch import ApiForpatch


class DevicesId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
