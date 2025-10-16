import os
from typing import TypedDict
import requests

import superdesk

from flask import json
from datetime import datetime
from urllib.parse import urljoin
from superdesk.utils import ListCursor

BELGA_CONTACTS_PREFIX = "urn:belga:contact:"


class Contact(TypedDict, total=False):
    _id: str
    uri: str
    is_active: bool
    public: bool
    organisation: str
    first_name: str
    last_name: str
    honorific: str
    job_title: str
    fax: str
    website: str
    notes: str
    _created: datetime
    _updated: datetime
    contact_email: list[str]
    mobile: list[dict]
    contact_phone: list[dict]
    twitter: str
    facebook: str
    instagram: str
    city: str
    country: dict[str, str]
    contact_address: list[str]
    postcode: str


def get_uri(contact_id: str) -> str:
    """Format contact ID to a URI."""
    return f"{BELGA_CONTACTS_PREFIX}{contact_id}"


def parse_contact(contact) -> Contact:
    uri = get_uri(contact.get("id"))
    updated = contact.get("updateDate") or contact.get("createDate")
    parsed: Contact = {
        "_id": uri,
        "uri": uri,
        "is_active": bool(contact.get("active")),
        "public": bool(contact.get("publicFlag")),
        "organisation": contact.get("organization") or "",
        "first_name": contact.get("firstName") or "",
        "last_name": contact.get("lastName") or "",
        "honorific": contact.get("honorific") or "",
        "job_title": contact.get("title") or "",
        "fax": contact.get("fax") or "",
        "website": contact.get("website") or "",
        "notes": contact.get("editorialComment") or "",
        "_created": datetime.fromisoformat(contact.get("createDate")),
        "_updated": datetime.fromisoformat(updated),
    }

    infos = contact.get("infos", [])
    for info in infos:
        if info.get("type") == "EMAIL" and info.get("public"):
            parsed.setdefault("contact_email", []).append(info.get("value", ""))
        if info.get("type") == "MOBILE":
            parsed.setdefault("mobile", []).append(
                {
                    "number": info.get("value", ""),
                    "public": info.get("public", False),
                    "usage": info.get("usage", ""),
                }
            )
        if info.get("type") == "PHONE":
            parsed.setdefault("contact_phone", []).append(
                {
                    "number": info.get("value", ""),
                    "public": info.get("public", False),
                    "usage": info.get("usage", ""),
                }
            )

        if info.get("type") == "X":
            parsed["twitter"] = info.get("value", "")
        if info.get("type") == "FACEBOOK":
            parsed["facebook"] = info.get("value", "")
        if info.get("type") == "INSTAGRAM":
            parsed["instagram"] = info.get("value", "")

    for address in contact.get("addresses", []):
        if address.get("city"):
            parsed["city"] = address.get("city")
        if address.get("country"):
            parsed["country"] = {
                "name": address.get("country"),
            }
        if address.get("street"):
            parsed.setdefault("contact_address", []).append(address.get("street", ""))
        if address.get("number"):
            parsed.setdefault("contact_address", []).append(address.get("number", ""))
        if address.get("postalCode"):
            parsed["postcode"] = address.get("postalCode")

    return parsed


class BelgaContactsProxy(superdesk.Service):

    def __init__(self, url):
        self.base = url
        self.count = 50
        self.timeout = 30
        self.session = requests.Session()

    def get(self, req, lookup):
        if req.args.get("source"):
            source = json.loads(req.args.get("source"))
            if (
                source.get("query")
                and source["query"].get("terms")
                and source["query"]["terms"].get("_id")
            ):
                _ids = source["query"]["terms"]["_id"]
                return self.search_ids(_ids)

        size = int(req.args.get("max_results", self.count))
        page = int(req.args.get("page", 1)) - 1

        params = {"searchText": req.args.get("q", ""), "count": size, "offset": page}
        res = self.session.get(
            urljoin(self.base, "contacts"),
            params=params,
            verify=False,
            timeout=self.timeout,
        )
        res.raise_for_status()

        data = res.json()
        contacts = [parse_contact(c) for c in data.get("contacts", [])]
        return ListCursor(contacts)

    def find_one(self, req, **lookup):
        _id = str(lookup.get("_id"))
        if _id and _id.startswith(BELGA_CONTACTS_PREFIX):
            contact_id = _id.replace(BELGA_CONTACTS_PREFIX, "")
            res = self.session.get(
                urljoin(self.base, f"contacts/{contact_id}"),
                verify=False,
                timeout=self.timeout,
            )
            if res.status_code == 500:  # returns 500 on missing contact
                return None
            res.raise_for_status()
            data = res.json()
            return parse_contact(data)
        return None

    def search(self, source):
        try:
            _ids = source["query"]["bool"]["must"]["terms"]["_id"]
        except (KeyError, TypeError):
            _ids = []
        return self.search_ids(_ids)

    def search_ids(self, _ids):
        contacts = []
        for _id in _ids:
            contact = self.find_one(None, _id=_id)
            if contact:
                contacts.append(contact)
        return ListCursor(contacts)

    def post(self, docs, **kwargs):
        for doc in docs:
            if doc.get("_id"):  # linking contacts during ingest
                doc["_id"] = get_uri(doc["_id"])
            else:
                raise NotImplementedError("Creating new contacts is not supported.")


def init_app(_app):
    if os.environ.get("BELGA_CONTACTS_URL"):
        superdesk.resources["contacts"].service = BelgaContactsProxy(
            os.environ["BELGA_CONTACTS_URL"]
        )
        _app.client_config.update(
            {
                "external_contacts": {
                    "create_url": os.environ.get(
                        "BELGA_CONTACTS_CREATE_URL",
                        "http://contact-bos.staging.belga.be/contacts/addContact",
                    ),
                    "edit_url": os.environ.get(
                        "BELGA_CONTACTS_EDIT_URL",
                        "http://contact-bos.staging.belga.be/contacts/editContact",
                    ),
                }
            }
        )
