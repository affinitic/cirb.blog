import unittest2 as unittest
from zope.interface import alsoProvides
from cirb.blog import testing
from cirb.blog.tests import base
from cirb.blog.tests.utils import FakeContext
from cirb.blog.is_blog import IsBlog
from cirb.blog.interfaces import IBlogContainer


class TestIsBlog(base.UnitTestCase):
    def test_isblog(self):
        context = FakeContext()
        context.portal_type = "Folder"
        isblog = IsBlog(context, {})
        self.assertFalse(isblog())
        alsoProvides(context, IBlogContainer)
        self.assertTrue(isblog())


class IntegrationTestIsBlog(base.IntegrationTestCase):
    def test_isblog(self):
        isblog = self.folder.restrictedTraverse('@@cirb_blog_isblog')
        self.assertFalse(isblog())
        alsoProvides(self.folder, IBlogContainer)
        self.assertTrue(isblog())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
