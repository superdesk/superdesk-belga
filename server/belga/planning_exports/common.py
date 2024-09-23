from superdesk.utc import utc_to_local
from flask import current_app as app
from typing import List, Dict, Any, TypedDict
from babel.dates import format_date
from superdesk import get_resource_service


class FormattedContact(TypedDict):
    name: str
    organisation: str
    email: List[str]
    phone: List[str]
    mobile: List[str]
    website: str
    job_title: str


def set_item_title(item: Dict[str, Any], event: Dict[str, Any]):
    """Set the item's title

    Prioritise the Event's slugline/name before Planning item's
    """

    item["title"] = event.get("name") or event.get("slugline") or ""


def set_item_description(item: Dict[str, Any], event: Dict[str, Any]):
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


def set_item_dates(item: Dict[str, Any], event: Dict[str, Any]):
    """Set the item's dates to be used for sorting"""
    item["dates"] = {
        "start": event["dates"]["start"],
        "end": event["dates"]["end"],
        "tz": event.get("dates", {}).get("tz") or app.config.get("DEFAULT_TIMEZONE"),
    }

    tz = item["dates"]["tz"]
    start_local = utc_to_local(tz, item["dates"]["start"])
    item["local_time"] = start_local.strftime("%Hu%M")
    item["local_date_time"] = start_local.strftime("%Y%m%d")


def get_item_location(
    event: Dict[str, Any], locale: str, is_only_city_and_country: bool = False
) -> str:
    """Set the location to be used for sorting / displaying"""
    location = event.get("location")
    if not location:
        return ""

    event_lang = event.get("language") or locale
    location_name = location[0].get("name", "")

    # find location on DB and then extract translation Name
    if location[0].get("qcode") and event_lang:
        location_data = get_resource_service("locations").find_one(
            req=None, guid=location[0].get("qcode")
        )
        if location_data:
            translated_name = (
                location_data.get("translations", {})
                .get("name", {})
                .get(f"name:{event_lang}")
            )
            location_name = translated_name or location_name

    # Build location_items based on is_only_city_and_country flag
    location_items = []
    if not is_only_city_and_country:
        address = location[0].get("address", {})
        address_line = address.get("line", [""])[0]

        # Check if name and address line are identical, and skip address if they are
        if location_name.lower() != address_line.lower():
            location_items.append(reorder_address(location_name))
            location_items.append(reorder_address(address_line))
        else:
            location_items.append(reorder_address(location_name))

        location_items.extend(
            [
                f'{address.get("postal_code", "")} {address.get("city") or address.get("area", "")}',
                address.get("country", ""),
            ]
        )
    else:
        location_items.extend(
            [
                location[0].get("address", {}).get("city")
                or location[0].get("address", {}).get("area"),
                location[0].get("address", {}).get("country"),
            ]
        )

    # Filter and join non-empty location items
    filtered_items = [
        item.strip() for item in location_items if item and not item.isspace()
    ]
    return ", ".join(filtered_items)


def get_language_name(item: Dict[str, Any], language: str):
    return ((item.get("translations") or {}).get("name") or {}).get(
        language
    ) or item.get("name")


def get_subjects(event: Dict[str, Any], language: str):
    subjects = event.get("subject")
    filter_subj = []
    if subjects:
        for subj in subjects:
            if subj.get("scheme") == "belga-keywords":
                filter_subj.append(get_language_name(subj, language))
        return filter_subj
    return []


def format_datetime(event: Dict[str, Any], locale: str, format: str):
    tz = event.get("dates", {}).get("tz") or app.config.get("DEFAULT_TIMEZONE")
    start_time = event.get("dates", {}).get("start")
    return format_date(utc_to_local(tz, start_time), format, locale=locale)


def set_metadata(formatted_event: Dict[str, Any], event: Dict[str, Any], locale: str):
    formatted_event["links"] = event.get("links", "")
    set_item_dates(formatted_event, event)
    set_event_translations_value(event, locale)
    set_item_title(formatted_event, event)
    set_item_description(formatted_event, event)


def get_formatted_contacts(event: Dict[str, Any]) -> List[FormattedContact]:
    contacts = event.get("event_contact_info", [])
    formatted_contacts: List[FormattedContact] = []

    for contact_id in contacts:
        contact_details = get_resource_service("contacts").find_one(
            req=None, _id=contact_id
        )
        if contact_details:
            formatted_contact: FormattedContact = {
                "name": " ".join(
                    [
                        c
                        for c in [
                            contact_details.get("first_name", ""),
                            contact_details.get("last_name", ""),
                        ]
                        if c
                    ]
                ),
                "organisation": contact_details.get("organisation", ""),
                "email": contact_details.get("contact_email", []),
                "phone": [
                    c.get("number", "")
                    for c in contact_details.get("contact_phone", [])
                    if c.get("public")
                ],
                "mobile": [
                    c.get("number", "")
                    for c in contact_details.get("mobile", [])
                    if c.get("public")
                ],
                "website": contact_details.get("website", ""),
                "job_title": contact_details.get("job_title", ""),
            }
            formatted_contacts.append(formatted_contact)

    return formatted_contacts


def get_coverages(event: Dict[str, Any], locale: str):
    formatted_coverages = []
    planning_ids = event.get("planning_ids", [])
    planning_service = get_resource_service("planning")
    for id in planning_ids:
        planning_item = planning_service.find_one(req=None, _id=id)
        for coverage in planning_item.get("coverages", []):
            cov_planning = coverage.get("planning", {})
            cov_type = cov_planning.get("g2_content_type", "").upper()
            cov_status = (
                coverage.get("news_coverage_status", {}).get("label", "").upper()
            )

            if cov_planning.get("language", locale) == locale:
                formatted_coverages.append(f"{cov_type} ({cov_status})")

    return formatted_coverages


def set_event_translations_value(event: Dict[str, Any], locale: str):
    """
    set event translations value based on locale
    """
    translations = event.get("translations")
    translated_value = {}
    if translations is not None:
        translated_value.update(
            {
                entry["field"]: entry["value"]
                for entry in translations or []
                if entry["language"] == locale
            }
        )
        event.update(
            {
                key: val
                for key, val in translated_value.items()
                if key
                in (
                    "description_text",
                    "name",
                    "slugline",
                    "definition_long",
                    "definition_short",
                )
            }
        )


def reorder_address(address: str) -> str:
    """
    Reorder an address string by moving the leading number (if present)
    to the end of the string.
    """
    parts = address.split(" ", 1)
    if parts[0].isdigit() and len(parts) == 2:
        return f"{parts[1]} {parts[0]}"
    return address
