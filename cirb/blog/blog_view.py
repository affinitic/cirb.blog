from zope import component
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone import api

from cirb.blog import i18n
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IConversation

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
        self.portal_registry = component.getUtility(IRegistry)
        self.portal_url = api.portal.get().absolute_url()
        self.portal_state = component.getMultiAdapter((self.context,
                                                       self.request),
                                                  name="plone_portal_state")
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

        key = 'cirb.blog.settings.truncate_length'
        if key in self.portal_registry:
            self.truncate_length = self.portal_registry[key]
        else:
            self.truncate_length = '1000'

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

        lang = ""
        if ob.Language():
            lang = ob.Language()
        else:
            lang = self.portal_state.language()

        conversation = IConversation(ob)

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
                'lang': lang,
                'total_comments': conversation.total_comments,
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

    def translated_more_on(self):
        msgid = _(u"Read more on")
        return self.context.translate(msgid)

    def translated_less_on(self):
        msgid = _(u"Hide")
        return self.context.translate(msgid)
