from openapi_client.paths.experiments_id.get import ApiForget
from openapi_client.paths.experiments_id.delete import ApiFordelete
from openapi_client.paths.experiments_id.patch import ApiForpatch


class ExperimentsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
