from datetime import datetime, timezone

import pytest
from django.urls import reverse

from sentry.flags.endpoints.hooks import (
    DeserializationError,
    FlagAuditLogModel,
    InvalidProvider,
    handle_flag_pole_event,
    handle_provider_event,
)
from sentry.testutils.cases import APITestCase


def test_handle_provider_event():
    result = handle_provider_event(
        "flag-pole",
        {
            "action": "created",
            "flag": "test",
            "modified_at": "2024-01-01T00:00:00",
            "modified_by": "colton.allen@sentry.io",
        },
        1,
    )

    assert result["action"] == "created"
    assert result["flag"] == "test"
    assert result["modified_at"] == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert result["modified_by"] == "colton.allen@sentry.io"
    assert result["modified_by_type"] == "email"
    assert result["organization_id"] == 1


def test_handle_provider_event_invalid_provider():
    with pytest.raises(InvalidProvider):
        handle_provider_event("other", {}, 1)


def test_handle_flag_pole_event():
    result = handle_flag_pole_event(
        {
            "action": "created",
            "flag": "test",
            "modified_at": "2024-01-01T00:00:00",
            "modified_by": "colton.allen@sentry.io",
        },
        1,
    )

    assert result["action"] == "created"
    assert result["flag"] == "test"
    assert result["modified_at"] == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert result["modified_by"] == "colton.allen@sentry.io"
    assert result["modified_by_type"] == "email"
    assert result["organization_id"] == 1


def test_handle_flag_pole_event_bad_request():
    try:
        handle_flag_pole_event({}, 1)
    except DeserializationError as exc:
        assert exc.errors["action"][0].code == "required"
        assert exc.errors["flag"][0].code == "required"
        assert exc.errors["modified_at"][0].code == "required"
        assert exc.errors["modified_by"][0].code == "required"
    else:
        assert False, "Expected deserialization error"


class OrganizationFlagsHooksEndpointTestCase(APITestCase):
    endpoint = "sentry-api-0-organization-flag-hooks"

    def setUp(self):
        super().setUp()
        self.url = reverse(self.endpoint, args=(self.organization.slug, "flag-pole"))

    def test_post(self):
        # TODO: Use org token auth!
        response = self.client.post(
            self.url,
            data={
                "action": "created",
                "flag": "test",
                "modified_at": "2024-01-01T00:00:00",
                "modified_by": "colton.allen@sentry.io",
            },
        )
        assert response.status_code == 200

        assert FlagAuditLogModel.objects.count() == 1
        flag = FlagAuditLogModel.objects.first()
        assert flag.action == "created"
        assert flag.flag == "test"
        assert flag.modified_at == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert flag.modified_by == "colton.allen@sentry.io"
        assert flag.modified_by_type == "email"
        assert flag.organization_id == self.organization.id

    def test_post_unauthorized(self):
        response = self.client.post(self.url, data={})
        assert response.status_code == 401
