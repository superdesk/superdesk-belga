import os
import json

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


vocabularies_service = create_autospec(VocabulariesService)
vocabularies_service.find_one.side_effect = get_cv

resources = {"vocabularies": Resource(vocabularies_service)}
