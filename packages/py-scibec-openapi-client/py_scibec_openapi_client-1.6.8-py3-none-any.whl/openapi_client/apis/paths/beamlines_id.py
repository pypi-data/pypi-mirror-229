from openapi_client.paths.beamlines_id.get import ApiForget
from openapi_client.paths.beamlines_id.delete import ApiFordelete
from openapi_client.paths.beamlines_id.patch import ApiForpatch


class BeamlinesId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
