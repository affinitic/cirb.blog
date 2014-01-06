# -*- coding: utf-8 -*-
from zope import component
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone import api

from cirb.blog import i18n
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IConversation
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

_ = i18n._


class BlogView(BrowserView):
    """CIRB Blog View class"""

    index = ViewPageTemplateFile("templates/blog_view.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.users = {}
        self.articles = []
        self.portal_url = None
        self.navigation_root_url = None
        self.portal_registry = None
        self.portal_state = None
        self.truncate_length = None
        self.has_api = None
        self.context_url = None

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        if self.context_url is None:
            self.context_url = self.context.absolute_url()
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
        if self.navigation_root_url is None:
            self.navigation_root_url = self.portal_state.navigation_root_url()
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
        if self.has_api and datetime:
            return api.portal.get_localized_time(datetime=datetime)

    def _map_article_to_dic(self, brain):
        ob = brain.getObject()
        user = self.get_user(brain.Creator)
        effdate = ob.getEffectiveDate()
        localized_dt = self.get_localized_time(datetime=effdate)

        image_tag = ""
        image_field = ob.getField("image")
        if image_field and image_field.get_size(ob) != 0:
            image_caption = ob.getImageCaption()
            image_tag = ob.tag(
                css_class="image-left",
                scale="thumb",  # 128:128
                alt=image_caption,
                title=image_caption,
            )

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
            fullname = user.getProperty('fullname')
            if not fullname:
                fullname = username
            user_info = {'fullname': fullname,
                         'email': user.getProperty('email'),
                         'username': username,
                         'url': '%s/authorwp/%s' % (self.navigation_root_url,
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


class BlogItemView(BrowserView):
    template = ViewPageTemplateFile("templates/blogitem_view.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.effdate = self.context.getEffectiveDate()
        self.portal_state = component.getMultiAdapter((self.context,
                                                          self.request),
                                                  name="plone_portal_state")
        self.navigation_root_url = self.portal_state.navigation_root_url()

    def __call__(self):
        return self.template()

    def get_author_name(self):
        username = self.context.Creator()
        user = api.user.get(username=username)
        name = user.getProperty('fullname')
        return name

    def get_author_url(self):
        username = self.context.Creator()
        return "{}/authorwp/{}".format(self.navigation_root_url, username)

    def get_datetime_human(self):
        if self.effdate:
            return api.portal.get_localized_time(datetime=self.effdate)
        else:
            return False

    def translated_view_by(self):
        msgid = _(u"View all posts from")
        return self.context.translate(msgid)


class AuthorWpView(BrowserView):
    implements(IPublishTraverse)
    template = ViewPageTemplateFile("templates/authorwp_view.pt")

    def __call__(self):
        return self.template()

    def publishTraverse(self, request, name):
        request.PARENTS.pop()
        request.set("author", name)
        return self()

    def list_of_articles(self):
        author = self.request.author
        articles = []
        portal_catalog = self.context.portal_catalog
        brains = portal_catalog.searchResults({
            'Creator': author,
            'portal_type': 'Blog Entry',
            'Language': All,
            })
        for brain in brains:
            articles.append(brain.getObject())
        return articles
