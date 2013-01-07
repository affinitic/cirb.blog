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
from Products.CMFCore.interfaces._events import IActionSucceededEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent

logger = logging.getLogger("cirb.blog")


class SetupView(BrowserView):
    """setup the context as blog"""
    def __call__(self):
        if self.context.portal_type != 'Folder':
            raise ValueError("That view must be called from a Folder")
        self.update()
        self.add_media_folder()
        self.add_default_page()
        self.mark()
        self.initialize_archive_rules()
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

    def initialize_archive_rules(self):
        RULE_ID = 'archive-%s' % self.context.getId()
        rule = self._create_rule(RULE_ID,
                                 "Archive %s" % self.context.Title(),
                                 IActionSucceededEvent)

        #add condition & action
        data = {'wf_transitions': ['publish']}
        self._add_rule_condition(rule,
                                 'plone.conditions.WorkflowTransition',
                                 data)

        target = '/'.join(self.context.getPhysicalPath())
        data = {'target_folder': target,
                'folderish_type': 'Folder',
                'transitions': ["publish"]}
        self._add_rule_action(rule,
                              'collective.contentrules.yearmonth.actions.Move',
                              data)

        #activate it on context
        self._activate_rule(RULE_ID)

    def _add_rule_condition(self, rule, condition_id, data):
        condition = getUtility(IRuleCondition, name=condition_id)
        adding = getMultiAdapter((rule, self.request), name='+condition')
        addview = getMultiAdapter((adding, self.request),
                                  name=condition.addview)
        addview.createAndAdd(data=data)

    def _add_rule_action(self, rule, action_id, data):
        action = getUtility(IRuleAction, name=action_id)
        adding = getMultiAdapter((rule, self.request), name='+action')
        addview = getMultiAdapter((adding, self.request),
                                  name=action.addview)
        addview.createAndAdd(data=data)

    def _create_rule(self, rule_id, title, event):
        storage = getUtility(IRuleStorage)
        if rule_id not in storage:
            storage[rule_id] = Rule()
        rule = storage.get(rule_id)
        rule.title = title
        rule.enabled = True
        # Clear out conditions and actions since we're expecting new ones
        del rule.conditions[:]
        del rule.actions[:]
        rule.event = event
        rule = rule.__of__(self.portal)
        return rule

    def _activate_rule(self, rule_id, context=None):
        if context is None:
            context = self.context
        storage = getUtility(IRuleStorage)
        rule = storage.get(rule_id)
        assignable = IRuleAssignmentManager(context)
        assignment = assignable.get(rule_id, None)
        if not assignment:
            assignment = assignable[rule_id] = RuleAssignment(rule_id)
        assignment.enabled = True
        get_assignments(rule).insert('/'.join(self.context.getPhysicalPath()))
