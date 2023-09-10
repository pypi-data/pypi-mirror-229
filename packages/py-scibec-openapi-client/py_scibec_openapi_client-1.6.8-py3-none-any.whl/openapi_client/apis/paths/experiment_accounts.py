from openapi_client.paths.experiment_accounts.get import ApiForget
from openapi_client.paths.experiment_accounts.post import ApiForpost
from openapi_client.paths.experiment_accounts.patch import ApiForpatch


class ExperimentAccounts(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
