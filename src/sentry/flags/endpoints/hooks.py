import datetime
from typing import Any, TypedDict

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response

from sentry.api.api_owners import ApiOwner
from sentry.api.api_publish_status import ApiPublishStatus
from sentry.api.authentication import OrgAuthTokenAuthentication
from sentry.api.base import Endpoint, region_silo_endpoint
from sentry.api.bases.organization import OrganizationPermission
from sentry.api.exceptions import ResourceDoesNotExist
from sentry.flags.models import ACTION_MAP, MODIFIED_BY_TYPE_MAP, FlagAuditLogModel
from sentry.models.organization import Organization
from sentry.utils.sdk import bind_organization_context

"""HTTP endpoint.

This endpoint accepts only organization authorization tokens. I've made the conscious
decision to exclude all other forms of authentication. We don't want users accidentally
writing logs or leaked DSNs generating invalid log entries. An organization token is
secret and reasonably restricted and so makes sense for this use case where we have
inter-provider communication.

This endpoint allows writes if any write-level "org" permission was provided.
"""


class OrganizationFlagHookPermission(OrganizationPermission):
    scope_map = {
        "POST": ["org:write", "org:admin"],
    }


@region_silo_endpoint
class OrganizationFlagsHooksEndpoint(Endpoint):
    authentication_classes = (OrgAuthTokenAuthentication,)
    owner = ApiOwner.REPLAY
    permission_classes = (OrganizationFlagHookPermission,)
    publish_status = {
        "POST": ApiPublishStatus.PRIVATE,
    }

    def convert_args(
        self,
        request: Request,
        organization_id_or_slug: int | str,
        *args,
        **kwargs,
    ):
        try:
            if isinstance(organization_id_or_slug, int):
                organization = Organization.objects.get_from_cache(id=organization_id_or_slug)
            else:
                organization = Organization.objects.get_from_cache(slug=organization_id_or_slug)
        except Organization.DoesNotExist:
            raise ResourceDoesNotExist

        self.check_object_permissions(request, organization)
        bind_organization_context(organization)

        kwargs["organization"] = organization
        return args, kwargs

    def post(self, request: Request, organization: Organization, provider: str) -> Response:
        try:
            row_data = handle_provider_event(provider, request.data, organization.id)

            action_int = ACTION_MAP[row_data.pop("action")]
            modified_by_type_int = MODIFIED_BY_TYPE_MAP[row_data.pop("modified_by_type")]

            FlagAuditLogModel.objects.create(
                action=action_int,
                modified_by_type=modified_by_type_int,
                **row_data,
            )
            return Response(status=200)
        except InvalidProvider:
            raise ResourceDoesNotExist
        except DeserializationError as exc:
            return Response(exc.errors, status=400)


"""Provider definitions.

Provider definitions are pure functions. They accept data and return data. Providers do not
initiate any IO operations. Instead they return commands in the form of the return type or
an exception. These commands inform the caller (the endpoint defintion) what IO must be
emitted to satisfy the request. This is done primarily to improve testability and test
performance but secondarily to allow easy extension of the endpoint without knowledge of
the underlying systems.
"""


class FlagAuditLogRow(TypedDict):
    """A complete flag audit log row instance."""

    action: str
    flag: str
    modified_at: datetime.datetime
    modified_by: str
    modified_by_type: str
    organization_id: int
    tags: dict[str, Any]


class DeserializationError(Exception):
    """The request body could not be deserialized."""

    def __init__(self, errors):
        self.errors = errors


class InvalidProvider(Exception):
    """An unsupported provider type was specified."""

    ...


def handle_provider_event(
    provider: str,
    request_data: dict[str, Any],
    organization_id: int,
) -> FlagAuditLogRow:
    if provider == "flag-pole":
        return handle_flag_pole_event(request_data, organization_id)
    else:
        raise InvalidProvider(provider)


"""Flag pole provider definition.

If you are not Sentry you will not ever use this driver. Metadata provider by flag pole is
limited to what we can extract from the git repository on merge.
"""


class FlagPoleSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=("created", "updated"), required=True)
    flag = serializers.CharField(max_length=100, required=True)
    modified_at = serializers.DateTimeField(required=True)
    modified_by = serializers.CharField(required=True)


def handle_flag_pole_event(request_data: dict[str, Any], organization_id: int) -> FlagAuditLogRow:
    serializer = FlagPoleSerializer(data=request_data)
    if not serializer.is_valid():
        raise DeserializationError(serializer.errors)

    validated_data = serializer.validated_data

    return dict(
        action=validated_data["action"],
        flag=validated_data["flag"],
        modified_at=validated_data["modified_at"],
        modified_by=validated_data["modified_by"],
        modified_by_type="email",
        organization_id=organization_id,
        tags={},
    )
