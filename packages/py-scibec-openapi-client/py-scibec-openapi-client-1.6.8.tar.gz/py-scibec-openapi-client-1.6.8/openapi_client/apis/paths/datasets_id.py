from openapi_client.paths.datasets_id.get import ApiForget
from openapi_client.paths.datasets_id.delete import ApiFordelete
from openapi_client.paths.datasets_id.patch import ApiForpatch


class DatasetsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
