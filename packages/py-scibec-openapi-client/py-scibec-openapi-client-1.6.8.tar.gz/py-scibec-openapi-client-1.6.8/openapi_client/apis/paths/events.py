from openapi_client.paths.events.get import ApiForget
from openapi_client.paths.events.post import ApiForpost
from openapi_client.paths.events.patch import ApiForpatch


class Events(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
