# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.namedfile.file import NamedBlobFile
from ploneintranet import api as pi_api
from ploneintranet.async import tasks
from ploneintranet.async.celeryconfig import ASYNC_ENABLED
from ploneintranet.async.testing import FunctionalTestCase
from ploneintranet.async.testing import MustReadFunctionalTestCase

import os
import transaction
import unittest

TEST_MIME_TYPE = 'application/vnd.oasis.opendocument.text'
TEST_FILENAME = u'test.odt'


class TestTasks(FunctionalTestCase):
    """Extra task tests, separate from the async framework tests."""

    @unittest.skip("https://github.com/quaive/ploneintranet/issues/944")
    def test_preview(self):
        """Verify async preview generation"""

        if not ASYNC_ENABLED:
            print("Skipping preview test")
            return

        if not self.redis_running():
            self.fail("requires redis")
            return

        ff = open(os.path.join(os.path.dirname(__file__), TEST_FILENAME), 'r')
        self.filedata = ff.read()
        ff.close()
        # Temporarily enable Async
        self.testfile = api.content.create(
            type='File',
            id='test-file',
            title=u"Test File",
            file=NamedBlobFile(data=self.filedata, filename=TEST_FILENAME),
            container=self.portal)

        context = getattr(self.portal, 'test-file')
        self.assertFalse(pi_api.previews.has_previews(context))

        generator = tasks.GeneratePreview(context, self.request)
        result = generator()
        self.waitfor(result, timeout=15.0)

        # we need to commit in order to see the other transaction
        # now go and check that the preview has been generated
        transaction.commit()
        self.assertTrue(pi_api.previews.has_previews(context))

    def test_reindex(self):
        """Verify object reindexing"""
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        if not self.redis_running():
            self.fail("requires redis")
            return

        # set up a test page
        context = api.content.create(
            type='Document',
            title='Test Document',
            container=self.portal)
        # api.create auto-indexes. modification does not
        context.title = 'Foobar Document'
        # we need to commit to make the object visible for async
        transaction.commit()
        # verify that our change is not indexed yet
        catalog = api.portal.get_tool('portal_catalog')
        self.assertFalse(context.title in [x.Title for x in catalog()])

        result = tasks.ReindexObject(context, self.request)()
        self.waitfor(result)
        # we need to commit in order to see the other transaction
        transaction.commit()
        # check that our modification was indexed
        self.assertTrue(context.title in [x.Title for x in catalog()])


class TestMustreadTask(MustReadFunctionalTestCase):

    def test_mark_read(self):
        """Verify mustread view tracking"""
        if not self.redis_running():
            self.fail("requires redis")
            return

        # we need to commit to make the test page visible for async
        transaction.commit()
        # verify that the document is not read yet
        self.assertEqual(self.db.reads, [])
        # schedule the hit
        result = tasks.MarkRead(self.page, self.request)()
        self.waitfor(result, timeout=15.0)
        # we need to commit in order to see the other transaction
        transaction.commit()
        # check that our view was tracked
        self.assertTrue(self.tracker.has_read(self.page))
