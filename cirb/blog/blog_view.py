from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone import api

from cirb.blog import i18n

_ = i18n._


class BlogView(BrowserView):
    """CIRB Blog View class"""

    index = ViewPageTemplateFile("templates/blog_view.pt")

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        self.users = {}
        self.articles = []
        self.portal_url = api.portal.get().absolute_url()
        brains = None
        if self.context.portal_type not in ('Topic', 'Collection'):
            catalog = getToolByName(self.context, 'portal_catalog')
            query = {'portal_type': 'Blog Entry',
                     'review_state': 'published'}
            brains = catalog(**query)
        else:
            brains = self.context.queryCatalog()
        if brains and not self.articles:
            self.articles = map(self._map_article_to_dic, brains)

    def get_articles(self):
        return self.articles

    def _map_article_to_dic(self, brain):
        ob = brain.getObject()
        user = self.get_user(brain.Creator)
        effdate = ob.getEffectiveDate()
        localized_dt = api.portal.get_localized_time(datetime=effdate)

        image_tag = ""
        image_field = ob.getField("image")
        if image_field.get_size(ob) != 0:
            scale = "thumb"  # 128:128
            image_tag = image_field.tag(ob, scale=scale)

        return {'url': brain.getURL(),
                'id': brain.UID,
                'class': 'post-X tag-X',
                'title': brain.Title,
                'description': brain.Description,
                'body': ob.getText(),
                'author': user,
                'datetime': brain.EffectiveDate,
                'datetime_human': localized_dt,
                'tags': brain.Subject,
                'categories': [],
                'image_tag': image_tag,
                'image_alt': ob.getImageCaption(),
                }

    def get_user(self, username):
        if username not in self.users:
            user = api.user.get(username=username)
            fullname = user.fullname
            if not fullname:
                fullname = username
            user_info = {'fullname': fullname,
                         'email': user.email,
                         'username': username,
                         'url': '%s/author/%s' % (self.portal_url,
                                                  username)}
            self.users[username] = user_info
        return self.users[username]

    def translated_view_by(self):
        msgid = _(u"View all posts from")
        return self.context.translate(msgid)
