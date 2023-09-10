from openapi_client.paths.events_id.get import ApiForget
from openapi_client.paths.events_id.put import ApiForput
from openapi_client.paths.events_id.delete import ApiFordelete
from openapi_client.paths.events_id.patch import ApiForpatch


class EventsId(
    ApiForget,
    ApiForput,
    ApiFordelete,
    ApiForpatch,
):
    pass
