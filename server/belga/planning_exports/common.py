from superdesk.utc import utc_to_local


def get_sort_date(item):
    """Get date used for sorting of the output"""
    return item['dates']['start']


def set_item_title(item, event):
    """Set the item's title

    Prioritise the Event's slugline/name before Planning item's
    """

    item["title"] = (
        event.get("name")
        or item.get("name")
        or event.get("slugline")
        or item.get("slugline")
        or ""
    )


def set_item_description(item, event):
    """Set the item's description

    Prioritise the Event's description before Planning item's
    """

    description = (
        event.get("definition_long")
        or event.get("description_text")
        or event.get("definition_short")
        or ""
    ).rstrip()
    item["description"] = description


def set_item_dates(item, event):
    """Set the item's dates to be used for sorting"""
    item["dates"] = {
        "start": event['dates']['start'],
        "tz": "Europe/Brussels",
    }

    tz = item["dates"].get("tz") or "Europe/Brussels"
    start_local = utc_to_local(tz, item["dates"]["start"])
    start_local_str = start_local.strftime("%Hu%M")

    item["local_time"] = start_local_str
    item["local_date_str"] = start_local.strftime("%Y-%m-%d")


def set_item_location(item, event):
    """Set the location to be used for sorting / displaying"""
    
    item.setdefault("address", {})    
    if len(event.get("location") or []):
        try:
            location = event.get("location", {})[0]
            address = location.get("address") or {}
            item["address"] = {
                "country": address["country"] if address.get("country") else "",
                "city": address["city"] if address.get("city") else "",
                "name": address.get("city") or location.get("name") or ""
            }
        except (IndexError, KeyError):
            pass

def get_language_name(item, language) -> str:
    return ((item.get("translations") or {}).get("name") or {}).get(
        language
    ) or item.get("name")

def get_subject(event, language):
    subjects = event.get("subject")
    filter_subj = []
    if subjects:
        for subj in subjects:
            if subj.get("scheme") == "belga-keywords":
                filter_subj.append(get_language_name(subj, language))
        return filter_subj
    return []
