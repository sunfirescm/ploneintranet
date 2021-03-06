# coding=utf-8
import logging
from plone import api

from update_social import UpdateSocialHandler

logger = logging.getLogger(__name__)


class PostWellDoneView(UpdateSocialHandler):
    '''
    Helper view that handles HTTP POST of update-social
    and renders a new update-social + the created post
    for injection back into the calling view.
    '''

    def render_post(self):
        if not self.post:
            return
        return api.content.get_view(
            'post.html',
            self.post,
            self.request
        )()  # __call__()
