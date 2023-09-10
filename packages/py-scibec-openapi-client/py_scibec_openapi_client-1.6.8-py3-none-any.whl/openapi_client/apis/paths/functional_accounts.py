from openapi_client.paths.functional_accounts.get import ApiForget
from openapi_client.paths.functional_accounts.post import ApiForpost
from openapi_client.paths.functional_accounts.patch import ApiForpatch


class FunctionalAccounts(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
