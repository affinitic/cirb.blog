from zope import component
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone import api

from cirb.blog import i18n
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IConversation
from zope.component.interfaces import ComponentLookupError

_ = i18n._


class BlogView(BrowserView):
    """CIRB Blog View class"""

    index = ViewPageTemplateFile("templates/blog_view.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.users = {}
        self.articles = []
        self.portal_registry = None
        self.portal_state = None
        self.truncate_length = None
        self.has_api = None

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        if self.has_api is None:
            self.has_api = True
        if self.portal_registry is None:
            self.portal_registry = component.getUtility(IRegistry)
        if self.portal_url is None:
            self.portal_url = api.portal.get().absolute_url()
        if self.portal_state is None:
            self.portal_state = component.getMultiAdapter((self.context,
                                                          self.request),
                                                  name="plone_portal_state")
        if not self.articles:
            brains = None
            if self.context.portal_type not in ('Topic', 'Collection'):
                catalog = getToolByName(self.context, 'portal_catalog')
                query = {'portal_type': 'Blog Entry',
                         'review_state': 'published'}
                brains = catalog(**query)
            else:
                brains = self.context.queryCatalog()
            if brains:
                self.articles = map(self._map_article_to_dic, brains)

        if self.truncate_length is None:
            key = 'cirb.blog.settings.truncate_length'
            if key in self.portal_registry:
                self.truncate_length = self.portal_registry[key]
            else:
                self.truncate_length = '1000'

    def get_articles(self):
        return self.articles

    def get_localized_time(self, datetime=None):
        if self.has_api:
            return api.portal.get_localized_time(datetime=datetime)

    def _map_article_to_dic(self, brain):
        ob = brain.getObject()
        user = self.get_user(brain.Creator)
        effdate = ob.getEffectiveDate()
        localized_dt = self.get_localized_time(datetime=effdate)

        image_tag = ""
        image_field = ob.getField("image")
        if image_field and image_field.get_size(ob) != 0:
            scale = "thumb"  # 128:128
            image_tag = image_field.tag(ob, scale=scale)

        lang = ""
        if ob.Language():
            lang = ob.Language()
        else:
            lang = self.portal_state.language()

        total_comments = self.get_total_comments(ob)

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
                'total_comments': total_comments,
                }

    def get_user(self, username):
        if username not in self.users and username:
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

    def get_total_comments(self, context):
        try:
            conversation = IConversation(context)
            return conversation.total_comments
        except TypeError:
            return 0
