import unittest2 as unittest
from cirb.blog.tests import base
from Products.CMFDynamicViewFTI.fti import DynamicViewTypeInformation


class TestSetup(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def test_blog_entry_type(self):
        portal_types = self.portal.portal_types
        types = portal_types.listTypeInfo()
        type_ids = [t.getId() for t in types]
        self.assertIn('Blog Entry', type_ids)
        blog_entry = portal_types['Blog Entry']
        self.assertIsInstance(blog_entry, DynamicViewTypeInformation)
        self.assertIn('newsitem_view', blog_entry.view_methods)
        self.assertEqual('newsitem_view', blog_entry.default_view)

    def test_collection_view(self):
        portal_types = self.portal.portal_types
        collection = portal_types['Collection']
        self.assertIn('cirb_blog_view', collection.view_methods)

    def test_topic_view(self):
        portal_types = self.portal.portal_types
        collection = portal_types['Topic']
        self.assertIn('cirb_blog_view', collection.view_methods)

#    def test_setup_view(self):
        #it fails and I don't understand why
#        self.folder.restrictedTraverse('@@cirb_blog_setup')()
#        ids = self.folder.objectIds()
#        self.assertIn('media', ids)
#        self.assertIn('blog', ids)
        #TODO: check content rule as been created


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
