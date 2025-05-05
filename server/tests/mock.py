import os
import json

from unittest.mock import create_autospec

from superdesk.vocabularies import VocabulariesService
from superdesk.geonames import geonames_request, format_geoname_item
from flask import current_app as app

SEQUENCE_NUMBER = 100

with open(
    os.path.join(os.path.dirname(__file__), "..", "data", "vocabularies.json")
) as f:
    cv_lists = json.load(f)
    cvs = {}
    for cv in cv_lists:
        cvs[cv["_id"]] = cv


def get_cv(req, _id):
    return cvs.get(_id)


def get_rightsinfo(article):
    return {
        "copyrightholder": "copyrightholder",
        "copyrightnotice": "copyrightnotice",
        "usageterms": "usageterms",
    }


def get_place(geoname_id, language="en"):
    assert geoname_id
    params = [
        ("geonameId", geoname_id),
        ("lang", language),
        ("style", app.config.get("GEONAMES_SEARCH_STYLE", "full")),
    ]
    json_data = geonames_request("getJSON", params)
    return format_geoname_item(json_data)


def get_cv_items(_id, is_active):
    cv = cvs.get(_id)
    items = []
    for item in cv["items"]:
        item.setdefault("scheme", _id)
        if item.get("is_active", True) == is_active:
            items.append(item)
    return items


class Resource:
    def __init__(self, service):
        self.service = service


vocabularies_service = create_autospec(VocabulariesService)
vocabularies_service.find_one.side_effect = get_cv
vocabularies_service.get_rightsinfo.side_effect = get_rightsinfo
vocabularies_service.get_items.side_effect = get_cv_items


resources = {"vocabularies": Resource(vocabularies_service)}
