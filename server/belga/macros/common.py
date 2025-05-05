from superdesk import get_resource_service
from typing import Optional


def get_cv_by_qcode(scheme: str, field: Optional[str] = None) -> dict:
    """
    Retrieve cv items by qcode for a given scheme.
    """
    cvs = get_resource_service("vocabularies").find_one(req=None, _id=scheme)
    if not cvs:
        return {}

    return {
        item.get("qcode"): (
            {**item, "scheme": scheme} if field is None else item.get(field)
        )
        for item in cvs.get("items") or []
        if item.get("is_active", True)
    }
