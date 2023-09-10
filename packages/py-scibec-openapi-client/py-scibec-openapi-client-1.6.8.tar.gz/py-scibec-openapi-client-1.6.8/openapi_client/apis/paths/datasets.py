from openapi_client.paths.datasets.get import ApiForget
from openapi_client.paths.datasets.post import ApiForpost
from openapi_client.paths.datasets.patch import ApiForpatch


class Datasets(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
