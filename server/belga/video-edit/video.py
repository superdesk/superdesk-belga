from urllib.parse import urljoin

import requests


class VideoEditorProvider():
    """Base class for Video Editor
    """

    label = 'unknown'

    def __init__(self, provider):
        self.provider = provider

    def get(self, project_id):
        """Get single project

        :param project_id:
        """
        raise NotImplementedError

    def get_paginate(self, offset):
        """Get list of projects

        :param offset:
        """
        raise NotImplementedError

    def post_project(self, filestream):
        """Create new project

        :param filestream:
        """
        raise NotImplementedError

    def post(self, project_id, updates):
        """Edit video. This method creates a new project

        :param project_id:
        :param updates: changes apply to the video
        """
        raise NotImplementedError

    def put(self, project_id, updates):
        """Edit video. This method does not create a new project

        :param project_id:
        :param updates: changes apply to the video
        """
        raise NotImplementedError

    def delete(self, project_id):
        """Delete video

        :param project_id:
        """
        raise NotImplementedError

    def get_thumbnail(self, project_id, amount):
        """Get video thumbnails

        :param project_id:
        :param amount: number of thumbnails to generate/get
        """
        raise NotImplementedError

    def post_preview_thumbnail(self, project_id, post_type, time=None, base64_data=None):
        """Post video preview thumbnail, capture image from video or from user upload

        :param project_id:
        :param post_type: Post preview thumbnail type, either capture or upload
        :param time: time to capture
        :param base64_data: base64 image data if type is upload
        """
        raise NotImplementedError


class BelgaVideoEditorProvider(VideoEditorProvider):

    label = 'Belga Video Editor'
    base_url = 'http://localhost:5050/projects/'

    def __init__(self, ):
        self.session = requests.Session()

    def url(self, resource, *args):
        return urljoin(self.base_url, resource, *args)

    def get(self, project_id):
        resp = self.session.get(self.url(project_id))
        if resp.status_code != 200:
            resp.raise_for_status()

        data = resp.json()
        return data

    def get_paginate(self, offset):
        resp = self.session.get(self.base_url, params={'offset': offset})
        if resp.status_code != 200:
            resp.raise_for_status()

        data = resp.json()
        return data

    def post_project(self, file_storage):
        video_file = {'file': (file_storage.filename, file_storage.read())}
        resp = self.session.post(self.base_url, files=video_file)
        if resp.status_code != 200:
            resp.raise_for_status()

        data = resp.json()
        return data

    def post(self, project_id, updates):
        resp = self.session.post(self.url(project_id), data=updates)
        if resp.status_code != 201:
            resp.raise_for_status()

        data = resp.json()
        return data

    def put(self, project_id, updates):
        resp = self.session.put(self.url(project_id), data=updates)
        if resp.status_code != 200:
            resp.raise_for_status()

        data = resp.json()
        return data

    def delete(self, project_id):
        resp = self.session.delete(self.url(project_id))
        if resp.status_code != 204:
            resp.raise_for_status()

        return True

    def get_thumbnail(self, project_id, amount):
        resp = self.session.get(self.url(project_id, 'thumbnails'), params={'amount': amount})
        if resp.status_code != 200:
            resp.raise_for_status()

        data = resp.json()
        return data

    def post_preview_thumbnail(self, project_id, post_type, time=None, base64_data=None):
        payloads = {
            'type': post_type,
            'time': time,
            'data': base64_data,
        }
        resp = self.session.post(self.url(project_id, 'preview_thumbnail'), data=payloads)
        if resp.status_code != 200:
            resp.raise_for_status()

        data = resp.json()
        return data
