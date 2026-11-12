# //// Neoffice — added file (no upstream equivalent)
# A query saved without any operation yet (a new, empty one) has operations NULL. Its builder died on
# « 'NoneType' object is not iterable » each time it was run (neoffice-maintenance#2404): it now builds nothing.
import frappe

from insights.insights.doctype.insights_data_source_v3.ibis_utils import IbisQueryBuilder
from insights.tests.base import InsightsIntegrationTestCase


class TestAQueryWithoutOperations(InsightsIntegrationTestCase):
    def make_query_doc(self, operations):
        return frappe._dict(
            name="Ibis Empty Query Test",
            title="Ibis Empty Query Test",
            use_live_connection=0,
            operations=operations,
        )

    def test_a_query_whose_operations_are_null_builds_nothing(self):
        builder = IbisQueryBuilder(self.make_query_doc(None))
        self.assertEqual(builder.operations, [])
        self.assertIsNone(builder.build())

    def test_a_query_whose_operations_are_an_empty_list_builds_nothing(self):
        self.assertIsNone(IbisQueryBuilder(self.make_query_doc("[]")).build())
