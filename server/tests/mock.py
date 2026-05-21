import os
import json
import re

from aioresponses import aioresponses

from unittest.mock import create_autospec

from superdesk.vocabularies import VocabulariesService


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


class Resource:
    def __init__(self, service):
        self.service = service


def fixture(filename, as_json=False):
    filename = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(filename) as _file:
        return _file.read() if not as_json else json.load(_file)


def http(
    http_mock: aioresponses,
    url: str | re.Pattern[str] | None = None,
    method: str = "get",
    status: int = 200,
    payload: dict | bytes | str | None = None,
):
    func = getattr(http_mock, method)
    url_match = url or re.compile(".*")
    func(url_match, status=status, payload=payload or {}, repeat=True)


vocabularies_service = create_autospec(VocabulariesService)
vocabularies_service.find_one.side_effect = get_cv
vocabularies_service.find_one_async.side_effect = get_cv

resources = {"vocabularies": Resource(vocabularies_service)}
