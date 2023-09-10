from openapi_client.paths.experiment_accounts_id.get import ApiForget
from openapi_client.paths.experiment_accounts_id.delete import ApiFordelete
from openapi_client.paths.experiment_accounts_id.patch import ApiForpatch


class ExperimentAccountsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
