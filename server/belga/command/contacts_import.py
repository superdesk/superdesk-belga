import superdesk
import json

from superdesk import get_resource_service
import logging

logger = logging.getLogger(__name__)


def import_contacts_via_json_file(path_file):
    """
    Get info contacts in file and add to database
    :param path_file:
    :param unit_test:
    :return:
    """
    with open(path_file, "rt", encoding="utf-8") as contacts_data:
        json_data = json.load(contacts_data)
        contact_service = get_resource_service("contacts")
        docs = []
        count_items = len(json_data)
        count_import = 0
        for item in json_data:
            # Validate data contacts
            # contact is not name and email, not import
            if (
                not item.get("email")
                and not item.get("personalEmail")
                and not item.get("firstName")
                and not item.get("lastName")
                and not item.get("company")
            ):
                logger.info(
                    "contact (id:%s) is not name, company and email, not import."
                    % str(item.get("contactId"))
                )
                continue
            else:
                # contact same name, email, phone, not import
                query = {
                    "first_name": item.get("firstName", ""),
                    "last_name": item.get("lastName", ""),
                }
                # if first and last name is empty, check company
                if not item.get("firstName") and not item.get("lastName"):
                    query = {"organisation": item.get("company", "")}
                and_query = []
                if item.get("email"):
                    and_query.append({"contact_email": item.get("email")})
                if item.get("personalEmail"):
                    and_query.append({"contact_email": item.get("personalEmail")})
                if item.get("directPhone1"):
                    and_query.append({"contact_phone.number": item.get("directPhone1")})
                if item.get("directPhone2"):
                    and_query.append({"contact_phone.number": item.get("directPhone2")})
                if item.get("phoneGeneral"):
                    and_query.append({"contact_phone.number": item.get("phoneGeneral")})
                if item.get("personalPhone"):
                    and_query.append(
                        {"contact_phone.number": item.get("personalPhone")}
                    )
                if and_query:
                    query.update({"$and": and_query})

                contacts = contact_service.find(query)

                if len(list(contacts)):
                    logger.info(
                        "contact (id:%s) is exist, same name(%s %s), email(%s, %s), phone(%s, %s), not import"
                        % (
                            str(item.get("contactId")),
                            item.get("firstName"),
                            item.get("lastName"),
                            item.get("email", ""),
                            item.get("personalEmail", ""),
                            item.get("directPhone1", ""),
                            item.get("directPhone2", ""),
                        )
                    )
                    continue
            doc = {}
            logger.info(
                "contact (id:%s) is insert successfully:" % str(item.get("contactId"))
            )
            # mapping data
            doc.setdefault("schema", {}).update(
                {"is_active": True, "public": item.get("belgaPublic", True)}
            )
            doc["organisation"] = item.get("company", "")
            doc["first_name"] = item.get("firstName", "")
            doc["last_name"] = item.get("lastName", "")
            if item.get("function"):
                doc["job_title"] = item.get("function")
            if item.get("mobile247"):
                doc.setdefault("mobile", []).append(
                    {
                        "number": item.get("mobile247"),
                        "usage": "Business",
                        "public": True,
                    }
                )
            if item.get("personalMobile"):
                doc.setdefault("mobile", []).append(
                    {
                        "number": item.get("personalMobile"),
                        "usage": "Confidential",
                        "public": True,
                    }
                )
            if item.get("phoneGeneral"):
                doc.setdefault("contact_phone", []).append(
                    {
                        "number": item.get("phoneGeneral"),
                        "usage": "Business",
                        "public": True,
                    }
                )
            if item.get("directPhone1"):
                doc.setdefault("contact_phone", []).append(
                    {
                        "number": item.get("directPhone1"),
                        "usage": "Business",
                        "public": True,
                    }
                )
            if item.get("directPhone2"):
                doc.setdefault("contact_phone", []).append(
                    {
                        "number": item.get("directPhone2"),
                        "usage": "Business",
                        "public": True,
                    }
                )
            if item.get("personalPhone"):
                doc.setdefault("contact_phone", []).append(
                    {
                        "number": item.get("personalPhone"),
                        "usage": "Confidential",
                        "public": True,
                    }
                )
            doc["fax"] = ""
            if item.get("email"):
                doc.setdefault("contact_email", []).append(item.get("email"))
            if item.get("personalEmail"):
                doc.setdefault("contact_email", []).append(item.get("personalEmail"))
            if item.get("twitter"):
                doc["twitter"] = item.get("twitter")
            if item.get("personalTwitter"):
                doc["twitter_personal"] = item.get("personalTwitter")
            if item.get("facebook"):
                doc["facebook"] = item.get("facebook")
            if item.get("personalFacebook"):
                doc["facebook_personal"] = item.get("personalFacebook")
            if item.get("url"):
                doc["website"] = item.get("url")
            if item.get("professionalAddress"):
                doc.setdefault("contact_address", []).append(
                    item.get("professionalAddress")
                )
            if item.get("professionalAddress"):
                doc.setdefault("contact_address", []).append(
                    item.get("personalAddress")
                )
            if item.get("Comment1"):
                doc["notes"] = item.get("Comment1", "")
            if item.get("keywords"):
                doc["keywords"] = item.get("keywords")
            # use original_id check and sync the contact from the belga.
            doc["original_id"] = str(item.get("contactId"))
            count_import += 1
            contact_service.post([doc])
            docs.append(doc)
        logger.info(
            "number item: "
            + str(count_items)
            + ", number imported item: "
            + str(count_import)
        )
        return docs


class ContactImportCommand(superdesk.Command):
    """Import contact from belga to Superdesk.
    This command use for inserting a large number contact from Belga to Superdesk.
    Only support for format json file.
    """

    option_list = [
        superdesk.Option(
            "--file", "-f", dest="contacts_file_path", default="contacts.json"
        )
    ]

    def run(self, contacts_file_path):
        logger.info("import file: " + contacts_file_path)
        import_contacts_via_json_file(contacts_file_path)


superdesk.command("contact:import", ContactImportCommand())
