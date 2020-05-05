import logging
from copy import deepcopy

from superdesk.metadata.item import CONTENT_TYPE


logger = logging.getLogger(__name__)


def handle_duplicate(sender, item, original, operation):
    def is_belga_archive(item):
        return item.get('type') == CONTENT_TYPE.TEXT and item.get('extra', {}).get('bcoverage')

    if operation == 'translate':
        # remove all belga archive 360 associations
        for k, v in deepcopy(item.get('associations', {})).items():
            if is_belga_archive(v):
                del item.get('associations', {})[k]
