from openapi_client.paths.access_accounts.get import ApiForget
from openapi_client.paths.access_accounts.post import ApiForpost
from openapi_client.paths.access_accounts.patch import ApiForpatch


class AccessAccounts(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
