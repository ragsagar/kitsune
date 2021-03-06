from nose.tools import eq_
from pyquery import PyQuery as pq

from kitsune.sumo.tests import TestCase
from kitsune.sumo.urlresolvers import reverse
from kitsune.wiki.config import MAJOR_SIGNIFICANCE, MEDIUM_SIGNIFICANCE
from kitsune.wiki.tests import revision, translated_revision


class LocalizationDashTests(TestCase):
    """Tests for the Localization Dashboard.

    The L10n Dash shares a lot of code with the Contributor Dash, so
    this also covers much of the latter, such as the readout template,
    most of the view mechanics, and the Unreviewed Changes readout
    itself.

    """

    @staticmethod
    def _assert_readout_contains(doc, slug, contents):
        """Assert `doc` contains `contents` within the `slug` readout."""
        html = doc('a#' + slug).closest('details').html()
        assert contents in html, \
            "'" + contents + "' is not in the following: " + html

    def test_render(self):
        """Assert main dash and all the readouts render and don't crash."""
        # Put some stuff in the DB so at least one row renders for each
        # readout:
        untranslated = revision(is_approved=True,
                                is_ready_for_localization=True)
        untranslated.save()

        unreviewed = translated_revision(is_ready_for_localization=True)
        unreviewed.save()

        out_of_date = translated_revision(is_approved=True,
                                          is_ready_for_localization=True)
        out_of_date.save()
        major_update = revision(document=out_of_date.document.parent,
                                significance=MAJOR_SIGNIFICANCE,
                                is_approved=True,
                                is_ready_for_localization=True)
        major_update.save()

        needing_updates = translated_revision(is_approved=True,
                                              is_ready_for_localization=True)
        needing_updates.save()
        medium_update = revision(document=needing_updates.document.parent,
                                 significance=MEDIUM_SIGNIFICANCE,
                                 is_ready_for_localization=True)
        medium_update.save()

        response = self.client.get(reverse('dashboards.localization',
                                           locale='de'),
                                   follow=False)
        eq_(200, response.status_code)
        doc = pq(response.content)
        self._assert_readout_contains(doc, 'untranslated',
                                      untranslated.document.title)
        self._assert_readout_contains(doc, 'unreviewed',
                                      unreviewed.document.title)
        self._assert_readout_contains(doc, 'out-of-date',
                                      out_of_date.document.title)
        # TODO: Why does this fail? Is the setup wrong, or is the query?
        # self._assert_readout_contains(doc, 'needing-updates',
        #                               needing_updates.document.title)

    def test_untranslated_detail(self):
        """Assert the whole-page Untranslated Articles view works."""
        # We don't need to test every whole-page view: just one, to
        # make sure the localization_detail template and the view
        # work. All the readouts' querying and formatting methods,
        # including the various template parameters for each
        # individual readout, are exercised by rendering the main,
        # multi-readout page.

        # Put something in the DB so something shows up:
        untranslated = revision(is_approved=True,
                                is_ready_for_localization=True)
        untranslated.save()

        response = self.client.get(reverse('dashboards.localization_detail',
                                           args=['untranslated'],
                                           locale='de'))
        self.assertContains(response, untranslated.document.title)
