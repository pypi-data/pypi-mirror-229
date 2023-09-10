from openapi_client.paths.scans.get import ApiForget
from openapi_client.paths.scans.post import ApiForpost
from openapi_client.paths.scans.patch import ApiForpatch


class Scans(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
