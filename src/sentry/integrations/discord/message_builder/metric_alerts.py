from __future__ import annotations

import time
from datetime import datetime
from typing import Optional

from sentry.incidents.models import AlertRule, Incident, IncidentStatus
from sentry.integrations.discord.message_builder import INCIDENT_COLOR_MAPPING, LEVEL_TO_COLOR
from sentry.integrations.discord.message_builder.base.base import DiscordMessageBuilder
from sentry.integrations.discord.message_builder.base.embed.base import DiscordMessageEmbed
from sentry.integrations.discord.message_builder.base.embed.image import DiscordMessageEmbedImage
from sentry.integrations.metric_alerts import metric_alert_attachment_info
from sentry.integrations.slack.utils.escape import escape_slack_text


class DiscordMetricAlertMessageBuilder(DiscordMessageBuilder):
    def __init__(
        self,
        alert_rule: AlertRule,
        incident: Optional[Incident] = None,
        new_status: Optional[IncidentStatus] = None,
        metric_value: Optional[int] = None,
        chart_url: Optional[str] = None,
    ) -> None:
        self.alert_rule = alert_rule
        self.incident = incident
        self.metric_value = metric_value
        self.new_status = new_status
        self.chart_url = chart_url

    def build(self, notification_uuid: str | None = None) -> dict[str, object]:
        data = metric_alert_attachment_info(
            self.alert_rule, self.incident, self.new_status, self.metric_value
        )

        embeds = [
            DiscordMessageEmbed(
                title=data["title"],
                url=f"{data['title_link']}&referrer=discord",
                description=f"<{data['title_link']}|*{escape_slack_text(data['title'])}*>  \n{data['text']}",
                color=LEVEL_TO_COLOR[INCIDENT_COLOR_MAPPING.get(data["status"], "")],
                image=DiscordMessageEmbedImage(self.chart_url) if self.chart_url else None,
            )
        ]

        return self._build(embeds=embeds)


def get_started_at(timestamp: datetime) -> str:
    unix_timestamp = int(time.mktime(timestamp.timetuple()))
    return f"Started <t:{unix_timestamp}:R>"
