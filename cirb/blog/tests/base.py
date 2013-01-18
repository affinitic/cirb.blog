import transaction
import unittest2 as unittest
from cirb.blog import testing
from zope.event import notify
from zope.traversing.interfaces import BeforeTraverseEvent


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        pass


class IntegrationTestCase(unittest.TestCase):

    layer = testing.INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        # the setup view use workflow which seems to fails in tests env
        # lets do the setup by hand ...
        self.folder.invokeFactory('Blog Entry', 'test-blog-entry')
        self.blogentry = getattr(self.folder, 'test-blog-entry')
        self.blogentry.setTitle('Test blog entry')
        self.blogentry.setText('A super blog entry')
        self.blogentry.reindexObject()
        self.folder.invokeFactory('Collection', 'blog')
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Blog Entry',
        }]
        self.folder.blog.setQuery(query)
        self.folder.blog.setLayout('cirb_blog_view')
        self.folder.setDefaultPage('blog')
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Member'])
        self.request = self.layer['request']

        # setup manually the correct browserlayer, see:
        # https://dev.plone.org/ticket/11673
        notify(BeforeTraverseEvent(self.portal, self.request))

#        workflowTool = self.portal.portal_workflow
#        default = 'simple_publication_workflow'
#        workflowTool.setDefaultChain(default)
#        portal_types = ('Blog Entry', 'Folder', 'Document', 'Collection')
#        workflowTool.setChainForPortalTypes(portal_types, default)


class FunctionalTestCase(IntegrationTestCase):

    layer = testing.FUNCTIONAL

    def setUp(self):
        #we must commit the transaction
        transaction.commit()
