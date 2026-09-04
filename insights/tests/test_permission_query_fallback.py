"""A document permission is a verdict, never an exception.

_build_permission_query() returns nothing for the team-based doctypes while team
permissions are off, and has_doc_permission() used to call .where() straight on it.
`enable_permissions` is 0 by default, so the every-day path of reading a data source
somebody else owns answered AttributeError — HTTP 500 — instead of yes or no.
"""

import frappe

from insights.permissions import (
    TEAM_BASED_PERMISSION_DOCTYPES,
    InsightsPermissions,
)
from insights.tests.base import InsightsIntegrationTestCase
from insights.tests.factories import DT, as_user, create_user, delete_users

OWNER = "permission_query_owner@test.com"
READER = "permission_query_reader@test.com"


class TestPermissionQueryFallback(InsightsIntegrationTestCase):
    @classmethod
    def before_class(cls):
        create_user(OWNER, first_name="Query", last_name="Owner", roles="Insights User")
        create_user(READER, first_name="Query", last_name="Reader", roles="Insights User")

        cls.data_source = (
            frappe.get_doc(
                {
                    "doctype": DT.DATA_SOURCE,
                    "title": "Permission Query Fallback Source",
                    "database_type": "DuckDB",
                    "database_name": "permission_query_fallback",
                    "owner": OWNER,
                }
            )
            .insert()
            .name
        )
        frappe.db.set_value(DT.DATA_SOURCE, cls.data_source, "owner", OWNER)

    @classmethod
    def after_class(cls):
        frappe.delete_doc(DT.DATA_SOURCE, cls.data_source, force=True, ignore_permissions=True)
        delete_users(OWNER, READER)

    def before_test(self):
        frappe.db.set_single_value(DT.SETTINGS, "enable_permissions", 0)

    def test_a_doctype_with_no_permission_query_answers_instead_of_raising(self):
        permissions = InsightsPermissions(READER)
        self.assertFalse(permissions.team_permissions_enabled)

        doc = frappe.get_doc(DT.DATA_SOURCE, self.data_source)
        self.assertNotEqual(doc.owner, READER, "the reader must not own the source")

        # a data source is team-based, and team permissions are off: every insights
        # user reaches it, which is what get_permission_query_conditions() says too
        self.assertTrue(permissions.has_doc_permission(doc, "read"))
        self.assertIn(doc.doctype, TEAM_BASED_PERMISSION_DOCTYPES)

    def test_reading_a_data_source_someone_else_owns_does_not_raise(self):
        with as_user(READER):
            doc = frappe.get_doc(DT.DATA_SOURCE, self.data_source)
            doc.check_permission("read")

    def test_the_fallback_denies_a_doctype_that_is_not_team_based(self):
        """A doctype listed in PERMISSION_DOCTYPES with no query builder must fail
        closed, not open."""
        import insights.permissions as permissions_module

        permissions = InsightsPermissions(READER)
        doc = frappe.get_doc(DT.DATA_SOURCE, self.data_source)
        doc.doctype = "Insights Query Result"

        previous = permissions_module.PERMISSION_DOCTYPES
        permissions_module.PERMISSION_DOCTYPES = [*previous, "Insights Query Result"]
        try:
            self.assertFalse(permissions.has_doc_permission(doc, "read"))
        finally:
            permissions_module.PERMISSION_DOCTYPES = previous
