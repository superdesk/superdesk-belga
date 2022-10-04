import logging
import superdesk
from .search_providers import BelgaImageSearchProvider
from .search_providers import BelgaCoverageSearchProvider
from .search_providers import Belga360ArchiveSearchProvider
from .search_providers import BelgaPressSearchProvider
from .search_providers import BelgaImageV2SearchProvider
from .search_providers import BelgaCoverageV2SearchProvider


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
