# //// Neoffice — added file (no upstream equivalent). Pins the property added to
# //// IbisQueryBuilder at the 2026-09-24 merge: a site whose data store is off reads
# //// its sources live, whatever use_live_connection a query was saved with.
import frappe
from frappe.tests.utils import FrappeTestCase

from insights.insights.doctype.insights_data_source_v3.ibis_utils import IbisQueryBuilder


def saved_query(use_live_connection: int):
    """A query as the assistant tools save it: no editor sets the flag for them."""
    return frappe._dict(
        name="probe-query",
        title="probe",
        operations="[]",
        use_live_connection=use_live_connection,
    )


class TestDataStoreOffReadsLive(FrappeTestCase):
    def setUp(self):
        self.previous = frappe.db.get_single_value("Insights Settings", "enable_data_store")

    def tearDown(self):
        frappe.db.set_single_value("Insights Settings", "enable_data_store", self.previous)

    def test_a_site_without_data_store_reads_live(self):
        """58 native queries saved with the default 0 broke on osiris: they were sent to
        a data store the site had never enabled, transpiled to DuckDB."""
        frappe.db.set_single_value("Insights Settings", "enable_data_store", 0)
        self.assertTrue(IbisQueryBuilder(saved_query(0)).use_live_connection)

    def test_a_site_with_data_store_keeps_the_query_choice(self):
        frappe.db.set_single_value("Insights Settings", "enable_data_store", 1)
        self.assertFalse(IbisQueryBuilder(saved_query(0)).use_live_connection)
        self.assertTrue(IbisQueryBuilder(saved_query(1)).use_live_connection)

    def test_the_build_override_still_applies(self):
        """InsightsQueryv3.build() assigns the attribute: the setter must keep it."""
        frappe.db.set_single_value("Insights Settings", "enable_data_store", 1)
        builder = IbisQueryBuilder(saved_query(1))
        builder.use_live_connection = False
        self.assertFalse(builder.use_live_connection)
