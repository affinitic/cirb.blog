from Products.Five.browser import BrowserView
from cirb.blog.interfaces import IBlogContainer


class IsBlog(BrowserView):
    """check if current folder implements IBlogContainer"""
    def __call__(self):
        context = self.context
        if context.portal_type not in ('Plone Site', 'Folder'):
            context = self.context.aq_inner.aq_parent
        return IBlogContainer.providedBy(context)
