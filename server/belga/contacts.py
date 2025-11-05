import os
from typing import TypedDict
import requests
import logging

import superdesk

from flask import json
from datetime import datetime, timedelta
from urllib.parse import urljoin
from superdesk.utils import ListCursor

logger = logging.getLogger(__name__)

BELGA_CONTACTS_PREFIX = "urn:belga:contact:"


class KeycloakAuth:
    """Handles Keycloak authentication and token management."""

    def __init__(self, endpoint: str, client_id: str, client_secret: str):
        self.endpoint = endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None
        self._token_expiry = None

    def get_token(self) -> str:
        """Get a valid access token"""
        if (
            not self._token
            or not self._token_expiry
            or datetime.now() >= self._token_expiry
        ):
            self._fetch_new_token()

        assert self._token is not None, "Access token was not fetched"
        return self._token

    def _fetch_new_token(self):
        """Fetch new token from Keycloak."""
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.endpoint, data=data, verify=False)
        response.raise_for_status()

        token_data = response.json()
        self._token = token_data["access_token"]
        # Set expiry 5 minutes before actual expiry to be safe
        self._token_expiry = datetime.now() + timedelta(
            seconds=token_data["expires_in"] - 300
        )


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


def format_id(contact_id: str) -> str:
    """Format contact ID."""
    return str(contact_id)


def parse_contact(contact) -> Contact:
    _id = format_id(contact.get("id"))
    updated = contact.get("updateDate") or contact.get("createDate")
    parsed: Contact = {
        "_id": _id,
        "uri": BELGA_CONTACTS_PREFIX + _id,
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

        # Initialize Keycloak auth
        self.auth = KeycloakAuth(
            endpoint=os.environ.get("BELGA_KEYCLOAK_ENDPOINT"),
            client_id=os.environ.get("BELGA_KEYCLOAK_CLIENT_ID"),
            client_secret=os.environ.get("BELGA_KEYCLOAK_CLIENT_SECRET"),
        )

    def _get_headers(self):
        """Get request headers with auth token."""
        return {"Authorization": f"Bearer {self.auth.get_token()}"}

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
            headers=self._get_headers(),
            verify=False,
            timeout=self.timeout,
        )
        res.raise_for_status()

        data = res.json()
        contacts = [parse_contact(c) for c in data.get("contacts", [])]
        return ListCursor(contacts)

    def find_one(self, req, **lookup):
        _id = str(lookup.get("_id"))
        if not _id:
            return None

        contact_id = (
            _id.replace(BELGA_CONTACTS_PREFIX, "")
            if _id.startswith(BELGA_CONTACTS_PREFIX)
            else _id
        )

        res = self.session.get(
            urljoin(self.base, f"contacts/{contact_id}"),
            headers=self._get_headers(),
            verify=False,
            timeout=self.timeout,
        )
        if res.status_code == 500:  # returns 500 on missing contact
            return None
        res.raise_for_status()
        data = res.json()
        return parse_contact(data)

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
                doc["_id"] = format_id(doc["_id"])
            else:
                raise NotImplementedError("Creating new contacts is not supported.")


def init_app(_app):
    if os.environ.get("BELGA_CONTACTS_URL"):
        # Add required environment variables
        required_vars = [
            "BELGA_CONTACTS_URL",
            "BELGA_KEYCLOAK_ENDPOINT",
            "BELGA_KEYCLOAK_CLIENT_ID",
            "BELGA_KEYCLOAK_CLIENT_SECRET",
        ]
        missing = [var for var in required_vars if not os.environ.get(var)]
        if missing:
            logger.warning(
                "External contacts feature disabled. Missing environment variables: %s",
                ", ".join(missing),
            )
            return

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
