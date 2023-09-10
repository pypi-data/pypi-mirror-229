from openapi_client.paths.functional_accounts_id.get import ApiForget
from openapi_client.paths.functional_accounts_id.delete import ApiFordelete
from openapi_client.paths.functional_accounts_id.patch import ApiForpatch


class FunctionalAccountsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
