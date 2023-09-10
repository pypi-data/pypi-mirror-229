import typing_extensions

from openapi_client.paths import PathValues
from openapi_client.apis.paths.access_accounts_count import AccessAccountsCount
from openapi_client.apis.paths.access_accounts_id import AccessAccountsId
from openapi_client.apis.paths.access_accounts import AccessAccounts
from openapi_client.apis.paths.access_configs_count import AccessConfigsCount
from openapi_client.apis.paths.access_configs_id import AccessConfigsId
from openapi_client.apis.paths.access_configs import AccessConfigs
from openapi_client.apis.paths.auth_callback import AuthCallback
from openapi_client.apis.paths.auth_login import AuthLogin
from openapi_client.apis.paths.auth_logout import AuthLogout
from openapi_client.apis.paths.beamlines_count import BeamlinesCount
from openapi_client.apis.paths.beamlines_id import BeamlinesId
from openapi_client.apis.paths.beamlines import Beamlines
from openapi_client.apis.paths.datasets_count import DatasetsCount
from openapi_client.apis.paths.datasets_id import DatasetsId
from openapi_client.apis.paths.datasets import Datasets
from openapi_client.apis.paths.devices_count import DevicesCount
from openapi_client.apis.paths.devices_id import DevicesId
from openapi_client.apis.paths.devices import Devices
from openapi_client.apis.paths.events_count import EventsCount
from openapi_client.apis.paths.events_id import EventsId
from openapi_client.apis.paths.events import Events
from openapi_client.apis.paths.experiment_accounts_count import ExperimentAccountsCount
from openapi_client.apis.paths.experiment_accounts_id import ExperimentAccountsId
from openapi_client.apis.paths.experiment_accounts import ExperimentAccounts
from openapi_client.apis.paths.experiments_count import ExperimentsCount
from openapi_client.apis.paths.experiments_id import ExperimentsId
from openapi_client.apis.paths.experiments import Experiments
from openapi_client.apis.paths.functional_accounts_count import FunctionalAccountsCount
from openapi_client.apis.paths.functional_accounts_id import FunctionalAccountsId
from openapi_client.apis.paths.functional_accounts import FunctionalAccounts
from openapi_client.apis.paths.scans_count import ScansCount
from openapi_client.apis.paths.scans_id import ScansId
from openapi_client.apis.paths.scans import Scans
from openapi_client.apis.paths.sessions_count import SessionsCount
from openapi_client.apis.paths.sessions_id import SessionsId
from openapi_client.apis.paths.sessions import Sessions
from openapi_client.apis.paths.users_login import UsersLogin
from openapi_client.apis.paths.users_me import UsersMe
from openapi_client.apis.paths.users_user_id import UsersUserId
from openapi_client.apis.paths.users import Users

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.ACCESSACCOUNTS_COUNT: AccessAccountsCount,
        PathValues.ACCESSACCOUNTS_ID: AccessAccountsId,
        PathValues.ACCESSACCOUNTS: AccessAccounts,
        PathValues.ACCESSCONFIGS_COUNT: AccessConfigsCount,
        PathValues.ACCESSCONFIGS_ID: AccessConfigsId,
        PathValues.ACCESSCONFIGS: AccessConfigs,
        PathValues.AUTH_CALLBACK: AuthCallback,
        PathValues.AUTH_LOGIN: AuthLogin,
        PathValues.AUTH_LOGOUT: AuthLogout,
        PathValues.BEAMLINES_COUNT: BeamlinesCount,
        PathValues.BEAMLINES_ID: BeamlinesId,
        PathValues.BEAMLINES: Beamlines,
        PathValues.DATASETS_COUNT: DatasetsCount,
        PathValues.DATASETS_ID: DatasetsId,
        PathValues.DATASETS: Datasets,
        PathValues.DEVICES_COUNT: DevicesCount,
        PathValues.DEVICES_ID: DevicesId,
        PathValues.DEVICES: Devices,
        PathValues.EVENTS_COUNT: EventsCount,
        PathValues.EVENTS_ID: EventsId,
        PathValues.EVENTS: Events,
        PathValues.EXPERIMENTACCOUNTS_COUNT: ExperimentAccountsCount,
        PathValues.EXPERIMENTACCOUNTS_ID: ExperimentAccountsId,
        PathValues.EXPERIMENTACCOUNTS: ExperimentAccounts,
        PathValues.EXPERIMENTS_COUNT: ExperimentsCount,
        PathValues.EXPERIMENTS_ID: ExperimentsId,
        PathValues.EXPERIMENTS: Experiments,
        PathValues.FUNCTIONALACCOUNTS_COUNT: FunctionalAccountsCount,
        PathValues.FUNCTIONALACCOUNTS_ID: FunctionalAccountsId,
        PathValues.FUNCTIONALACCOUNTS: FunctionalAccounts,
        PathValues.SCANS_COUNT: ScansCount,
        PathValues.SCANS_ID: ScansId,
        PathValues.SCANS: Scans,
        PathValues.SESSIONS_COUNT: SessionsCount,
        PathValues.SESSIONS_ID: SessionsId,
        PathValues.SESSIONS: Sessions,
        PathValues.USERS_LOGIN: UsersLogin,
        PathValues.USERS_ME: UsersMe,
        PathValues.USERS_USER_ID: UsersUserId,
        PathValues.USERS: Users,
    }
)

path_to_api = PathToApi(
    {
        PathValues.ACCESSACCOUNTS_COUNT: AccessAccountsCount,
        PathValues.ACCESSACCOUNTS_ID: AccessAccountsId,
        PathValues.ACCESSACCOUNTS: AccessAccounts,
        PathValues.ACCESSCONFIGS_COUNT: AccessConfigsCount,
        PathValues.ACCESSCONFIGS_ID: AccessConfigsId,
        PathValues.ACCESSCONFIGS: AccessConfigs,
        PathValues.AUTH_CALLBACK: AuthCallback,
        PathValues.AUTH_LOGIN: AuthLogin,
        PathValues.AUTH_LOGOUT: AuthLogout,
        PathValues.BEAMLINES_COUNT: BeamlinesCount,
        PathValues.BEAMLINES_ID: BeamlinesId,
        PathValues.BEAMLINES: Beamlines,
        PathValues.DATASETS_COUNT: DatasetsCount,
        PathValues.DATASETS_ID: DatasetsId,
        PathValues.DATASETS: Datasets,
        PathValues.DEVICES_COUNT: DevicesCount,
        PathValues.DEVICES_ID: DevicesId,
        PathValues.DEVICES: Devices,
        PathValues.EVENTS_COUNT: EventsCount,
        PathValues.EVENTS_ID: EventsId,
        PathValues.EVENTS: Events,
        PathValues.EXPERIMENTACCOUNTS_COUNT: ExperimentAccountsCount,
        PathValues.EXPERIMENTACCOUNTS_ID: ExperimentAccountsId,
        PathValues.EXPERIMENTACCOUNTS: ExperimentAccounts,
        PathValues.EXPERIMENTS_COUNT: ExperimentsCount,
        PathValues.EXPERIMENTS_ID: ExperimentsId,
        PathValues.EXPERIMENTS: Experiments,
        PathValues.FUNCTIONALACCOUNTS_COUNT: FunctionalAccountsCount,
        PathValues.FUNCTIONALACCOUNTS_ID: FunctionalAccountsId,
        PathValues.FUNCTIONALACCOUNTS: FunctionalAccounts,
        PathValues.SCANS_COUNT: ScansCount,
        PathValues.SCANS_ID: ScansId,
        PathValues.SCANS: Scans,
        PathValues.SESSIONS_COUNT: SessionsCount,
        PathValues.SESSIONS_ID: SessionsId,
        PathValues.SESSIONS: Sessions,
        PathValues.USERS_LOGIN: UsersLogin,
        PathValues.USERS_ME: UsersMe,
        PathValues.USERS_USER_ID: UsersUserId,
        PathValues.USERS: Users,
    }
)
