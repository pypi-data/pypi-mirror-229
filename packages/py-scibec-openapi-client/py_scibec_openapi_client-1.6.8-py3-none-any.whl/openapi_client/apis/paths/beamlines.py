from openapi_client.paths.beamlines.get import ApiForget
from openapi_client.paths.beamlines.post import ApiForpost
from openapi_client.paths.beamlines.patch import ApiForpatch


class Beamlines(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
