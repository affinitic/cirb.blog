import unittest2 as unittest
from cirb.blog import testing
from cirb.blog.tests import base, utils
from cirb.blog.blog_view import BlogView


class TestBlogView(base.UnitTestCase):
    def setUp(self):
        super(TestBlogView, self).setUp()
        self.context = utils.FakeContext()
        self.request = {}
        self.blogview = BlogView(self.context, self.request)
        self.blogview.has_api = False
        registry = {'cirb.blog.settings.truncate_length': '1001'}
        self.blogview.portal_registry = registry
        self.blogview.portal_url = 'http://nohost.com/plone'
        self.blogview.portal_state = utils.FakePortalState(self.context,
                                                           self.request)
        user = utils.FakeUser()
        user.fullname = "JeanMichel FRANCOIS"
        user.email = "toutpt@gmail.com"
        self.blogview.users['myself'] = user

    def test_update(self):
        #check update can be called multiple time
        self.blogview.update()
        self.blogview.update()
        self.assertEqual(self.blogview.truncate_length, '1001')


class IntegrationTestBlogView(base.IntegrationTestCase):
    def test_isblog(self):
        pass


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
