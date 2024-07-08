import logging
import superdesk
from .search_providers import BelgaImageSearchProvider
from .search_providers import BelgaCoverageSearchProvider
from .search_providers import Belga360ArchiveSearchProvider
from .search_providers import BelgaPressSearchProvider
from .search_providers import BelgaImageV2SearchProvider
from .search_providers import BelgaCoverageV2SearchProvider
from flask_babel import _, lazy_gettext


# set logging level for belga logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# register search provider
superdesk.register_search_provider(
    "belga_image", provider_class=BelgaImageSearchProvider
)
superdesk.register_search_provider(
    "belga_coverage", provider_class=BelgaCoverageSearchProvider
)
superdesk.register_search_provider(
    "belga_360archive", provider_class=Belga360ArchiveSearchProvider
)
superdesk.register_search_provider(
    "belga_press", provider_class=BelgaPressSearchProvider
)
superdesk.register_search_provider(
    "belga_image_v2", provider_class=BelgaImageV2SearchProvider
)
superdesk.register_search_provider(
    "belga_coverage_v2", provider_class=BelgaCoverageV2SearchProvider
)

superdesk.register_default_user_preference(
    "assignment:notification",
    {
        "type": "bool",
        "enabled": True,
        "default": True,
    },
    label=lazy_gettext("Send Assignment notifications via email"),
    category=lazy_gettext("notifications"),
)

superdesk.register_default_user_preference(
    "mark_for_user:notification",
    {
        "type": "bool",
        "enabled": True,
        "default": True,
    },
    label=lazy_gettext("Send Mark for User notifications via email"),
    category=lazy_gettext("notifications"),
)
