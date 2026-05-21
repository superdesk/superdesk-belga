from superdesk import get_resource_service

TEXT = "TEXT"
ALERT = "ALERT"

DISTRIBUTION_ID = "distribution"


async def handle_update(item, original):
    profile_service = get_resource_service("content_types")
    alert = await profile_service.find_one_async(req=None, label=ALERT)
    if alert and str(item.get("profile")) == str(alert["_id"]):
        text = await profile_service.find_one_async(req=None, label=TEXT)
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
