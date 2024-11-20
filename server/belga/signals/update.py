from superdesk import get_resource_service
from superdesk.metadata.item import CONTENT_STATE
from superdesk.utc import utcnow
from datetime import timedelta

TEXT = "TEXT"
ALERT = "ALERT"

DISTRIBUTION_ID = "distribution"


def handle_update(sender, item, original, **kwargs):
    profile_service = get_resource_service("content_types")
    alert = profile_service.find_one(req=None, label=ALERT)
    if alert and str(item.get("profile")) == str(alert["_id"]):
        text = profile_service.find_one(req=None, label=TEXT)
        if text:
            item["profile"] = text["_id"]
            item["urgency"] = 3
            item.setdefault("subject", [])
            subject = [
                subj
                for subj in item["subject"]
                if subj.get("scheme") != DISTRIBUTION_ID
            ]
            subject.append(
                {
                    "name": "default",
                    "qcode": "default",
                    "scheme": DISTRIBUTION_ID,
                }
            )
            item["subject"] = subject


def handle_coming_up_field(sender, item, original, **kwargs):
    # Disable and empty date time for coming_up field
    if original.get("extra", {}).get("DueBy"):
        item["extra"]["DueBy"] = None
