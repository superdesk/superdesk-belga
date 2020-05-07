from copy import deepcopy

from superdesk.metadata.item import CONTENT_TYPE


def handle_duplicate(sender, item, original, operation):

    def is_belga_archive(item):
        return item.get('type') == CONTENT_TYPE.TEXT and item.get('extra', {}).get('bcoverage')

    def is_video(item):
        return item.get('type') == CONTENT_TYPE.VIDEO

    if operation == 'translate':
        # remove all belga-archive-360/video associations
        for k, v in deepcopy(item.get('associations', {})).items():
            if is_belga_archive(v) or is_video(v):
                del item.get('associations', {})[k]
