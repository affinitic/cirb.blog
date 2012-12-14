import logging

from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone import api

logger = logging.getLogger("cirb.blog")


class SetupView(BrowserView):
    """setup the context as blog"""
    def __call__(self):
        self.update()
        self.add_media_folder()
        self.add_default_page()

    def update(self):
        pass

    def add_default_page(self):
        collection = None
        if self.context.portal_type == 'Folder':
            collection = self.create_collection()
        elif self.context.portal_type in ('Topic', 'Collection'):
            collection = self.context

        if collection is not None:
            collection.setLayout('cirb_blog_view')
        else:
            self.add_message('no way to create default page')

    def log_error(self, message):
        IStatusMessage(self.request).add(message, type=u"error")
        logger.error(message)

    def add_media_folder(self):
        if 'media' in self.context.objectIds():
            return
        media = api.content.create(type='Folder',
                                   title='Media',
                                   container=self.context)
        api.content.transition(obj=media, transition='publish')

    def create_collection(self):
        return api.content.create(type='Collection',
                                  title='Media',
                                  container=self.context)
