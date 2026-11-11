# //// Neoffice — added file (no upstream equivalent): the screens of Insights read Insights' own catalogue first
# //// (neoffice-maintenance#1195).
"""`get_all_translations` merges every installed app, last one winning. An app
installed after Insights that translates the same English word another way took
the word from Insights' screens: « Open » read « Ouvert » on the template library.
"""

from unittest.mock import patch

import frappe
from frappe.tests import UnitTestCase

from insights.api import translations

EVERY_APP = {"Open": "Ouvert", "Close": "Fermer"}
INSIGHTS = {"Open": "Ouvrir"}
PERSON = {"Close": "Clore"}


def own_catalogue(language, apps=None):
    return INSIGHTS if apps == ["insights"] else EVERY_APP


class TestTranslationsEndpoint(UnitTestCase):
    # create=True: the module before the fix imports neither, and must fail on the words, not on the patch
    def call(self):
        with (
            patch.object(translations, "get_all_translations", return_value=dict(EVERY_APP)),
            patch.object(translations, "get_translations_from_apps", side_effect=own_catalogue, create=True),
            patch.object(translations, "get_user_translations", return_value=dict(PERSON), create=True),
            patch.object(frappe.db, "get_single_value", return_value="fr"),
            patch.object(frappe.db, "get_value", return_value="fr"),
        ):
            return translations.get_translations()

    def test_insights_words_beat_another_apps(self):
        self.assertEqual(self.call()["Open"], "Ouvrir")

    def test_a_word_insights_does_not_have_stays(self):
        self.assertIn("Close", self.call())

    def test_a_translation_written_on_the_site_still_wins(self):
        self.assertEqual(self.call()["Close"], "Clore")
