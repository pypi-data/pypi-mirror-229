# ruff: noqa: E402

from atoti_core import get_env_flag
from atoti_query import (
    Auth as Auth,
    BasicAuthentication as BasicAuthentication,
    ClientCertificate as ClientCertificate,
    OAuth2ResourceOwnerPasswordAuthentication as OAuth2ResourceOwnerPasswordAuthentication,
    QueryCube as QueryCube,
    QueryHierarchy as QueryHierarchy,
    QueryLevel as QueryLevel,
    QueryMeasure as QueryMeasure,
    QueryResult as QueryResult,
    QuerySession as QuerySession,
    TokenAuthentication as TokenAuthentication,
)

from . import (
    agg as agg,
    array as array,
    experimental as experimental,
    math as math,
    scope as scope,
    string as string,
)
from ._compose_decorators import compose_decorators
from ._condition_to_json_serializable_dict import *
from ._decorate_api import decorate_api
from ._eula import (  # noqa: N811
    EULA as __license__,  # noqa: F401
    hide_new_eula_message as hide_new_eula_message,
    print_eula_message,
)
from ._external_table_identifier import *
from ._measure_metadata import *
from ._py4j_utils import patch_databricks_py4j
from ._telemetry import telemeter
from ._typecheck import typecheck
from ._user_service_client import UserServiceClient as UserServiceClient
from .aggregate_provider import AggregateProvider as AggregateProvider
from .app_extension import *
from .client_side_encryption_config import *
from .column import *
from .config import *
from .cube import Cube as Cube
from .directquery import *
from .function import *
from .hierarchy import *
from .level import *
from .measure import *
from .order import *
from .scope import *
from .session import Session as Session, _sessions as sessions
from .table import Table as Table
from .type import *

print_eula_message()


def close() -> None:
    """Close all opened sessions."""
    sessions.close()


patch_databricks_py4j()

_api_decorators = []

if __debug__ and not get_env_flag("_ATOTI_DISABLE_TYPECHECKING"):
    _api_decorators.append(typecheck)

_track_call = telemeter()

if _track_call:
    _api_decorators.append(_track_call)

if _api_decorators:
    decorate_api(compose_decorators(*_api_decorators))
