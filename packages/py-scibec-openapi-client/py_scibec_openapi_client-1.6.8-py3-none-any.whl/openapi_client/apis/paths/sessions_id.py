from openapi_client.paths.sessions_id.get import ApiForget
from openapi_client.paths.sessions_id.delete import ApiFordelete
from openapi_client.paths.sessions_id.patch import ApiForpatch


class SessionsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
