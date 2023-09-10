from openapi_client.paths.experiments.get import ApiForget
from openapi_client.paths.experiments.post import ApiForpost
from openapi_client.paths.experiments.patch import ApiForpatch


class Experiments(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
