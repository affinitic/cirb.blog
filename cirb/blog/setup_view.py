import logging

from zope import interface
from zope.component import getUtility, getMultiAdapter
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone import api

from cirb.blog.interfaces import IBlogContainer
from plone.contentrules.rule.interfaces import IRuleAction, IRuleCondition
from plone.contentrules.engine.interfaces import IRuleStorage,\
    IRuleAssignmentManager
from plone.app.contentrules.rule import Rule, get_assignments
from plone.contentrules.engine.assignments import RuleAssignment

logger = logging.getLogger("cirb.blog")
YEARMONTH_RULE = 'collective.contentrules.yearmonth.actions.Move'
CONDITION1 = 'plone.conditions.WorkflowTransition'


class SetupView(BrowserView):
    """setup the context as blog"""
    def __call__(self):
        if self.context.portal_type != 'Folder':
            raise ValueError("That view must be called from a Folder")
        self.update()
        self.add_media_folder()
        self.add_default_page()
        self.mark()
        self.initialize_archive_rule()
        self.request.response.redirect(self.context.absolute_url())

    def update(self):
        self.portal = api.portal.get()

    def add_default_page(self):
        collection = None
        folder = self.context
        default_page = folder.getDefaultPage()
        if "blog" not in folder.objectIds():
            collection = self.create_collection()
        else:
            collection = self.context["blog"]

        if default_page != "blog":
            folder.setDefaultPage("blog")

        if collection.getLayout() != "cirb_blog_view":
            collection.setLayout("cirb_blog_view")

    def log_error(self, message):
        IStatusMessage(self.request).add(message, type=u"error")
        logger.error(message)

    def add_media_folder(self):
        folder = self.context
        if 'media' in folder.objectIds():
            return
        media = api.content.create(type='Folder',
                                   title='Media',
                                   id="media",
                                   container=folder)
        api.content.transition(obj=media, transition='publish')

    def create_collection(self):
        collection = api.content.create(type='Collection',
                                  title='Blog',
                                  id="blog",
                                  container=self.context)
        api.content.transition(obj=collection, transition='publish')
        return collection

    def mark(self):
        if not IBlogContainer.providedBy(self.context):
            interface.directlyProvides(self.context, IBlogContainer)

    def initialize_archive_rule(self):
        #create the rule
        storage = getUtility(IRuleStorage)
        if 'archive' not in storage:
            storage['archive'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++archive')

        #add action
        action = getUtility(IRuleAction, name=YEARMONTH_RULE)
        adding = getMultiAdapter((rule, self.request), name='+action')
        addview = getMultiAdapter((adding, self.request),
                                  name=action.addview)
        target = '/'.join(self.context.getPhysicalPath())
        addview.createAndAdd(data={'target_folder': target})

        #add condition
        condition = getUtility(IRuleCondition, name=CONDITION1)
        adding = getMultiAdapter((rule, self.request), name='+condition')
        addview = getMultiAdapter((adding, self.request),
                                  name=condition.addview)
        addview.createAndAdd(data={'wf_transitions': ['publish']})

        #activate "archive" rule on context
        assignable = IRuleAssignmentManager(self.context)
        if 'archive' not in assignable:
            assignable['archive'] = RuleAssignment('archive')
        get_assignments(storage['archive']).insert(target)
