from openapi_client.paths.sessions.get import ApiForget
from openapi_client.paths.sessions.post import ApiForpost
from openapi_client.paths.sessions.patch import ApiForpatch


class Sessions(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
