# //// Neoffice — added file (no upstream equivalent): an account without an Insights role reads no Insights content,
# //// a workbook shared with the organisation included (neoffice-maintenance#1195).
"""A share « with everyone » is frappe's own, and frappe lets it reach every staff
account after the controller has said no. Insights shares a workbook with the
organisation that way, so an account without any Insights role listed it and
opened it. The organisation is the people who use Insights.
"""

import frappe

from insights.tests.base import InsightsIntegrationTestCase
from insights.tests.factories import (
    DT,
    as_user,
    create_test_workbook,
    create_user,
    delete_users,
    delete_workbooks,
)
from insights.utils import DocShare

OWNER = "role_gate_owner@test.com"
READER = "role_gate_reader@test.com"
STAFF = "role_gate_staff@test.com"
TITLE = "Role Gate Test Workbook"


class TestInsightsRoleGate(InsightsIntegrationTestCase):
    @classmethod
    def before_class(cls):
        cls.cleanup()
        create_user(OWNER, first_name="Gate", last_name="Owner", roles="Insights User")
        create_user(READER, first_name="Gate", last_name="Reader", roles="Insights User")
        # a desk account of the company that does not use Insights
        create_user(STAFF, first_name="Gate", last_name="Staff", roles="Blogger")
        cls.workbook = create_test_workbook(OWNER, title=TITLE).name

        share = DocShare.get_or_create_doc(share_doctype=DT.WORKBOOK, share_name=cls.workbook, everyone=1)
        share.read = 1
        share.write = 0
        share.notify_by_email = 0
        share.flags.ignore_share_permission = True
        share.save(ignore_permissions=True)

    @classmethod
    def after_class(cls):
        cls.cleanup()

    @classmethod
    def cleanup(cls):
        for name in frappe.get_all(DT.WORKBOOK, filters={"title": ["like", f"{TITLE}%"]}, pluck="name"):
            frappe.db.delete("DocShare", {"share_doctype": DT.WORKBOOK, "share_name": name})
        delete_workbooks(title_prefix=TITLE)
        delete_users(OWNER, READER, STAFF)

    def test_the_staff_account_is_a_desk_account(self):
        # the case is a desk account: frappe keeps a share with everyone from the portal accounts on its own
        self.assertEqual(frappe.db.get_value("User", STAFF, "user_type"), "System User")

    def test_an_insights_user_reads_the_organisation_workbook(self):
        with as_user(READER):
            self.assertIn(self.workbook, frappe.get_list(DT.WORKBOOK, pluck="name"))
            frappe.get_doc(DT.WORKBOOK, self.workbook).check_permission("read")

    def test_an_account_without_an_insights_role_does_not_list_it(self):
        with as_user(STAFF):
            names = frappe.get_list(DT.WORKBOOK, pluck="name")
        self.assertNotIn(self.workbook, names)

    def test_an_account_without_an_insights_role_does_not_open_it(self):
        with as_user(STAFF), self.assertRaises(frappe.PermissionError):
            frappe.get_doc(DT.WORKBOOK, self.workbook).check_permission("read")

    def test_the_api_read_is_refused_too(self):
        from frappe.client import get

        with as_user(STAFF), self.assertRaises(frappe.PermissionError):
            get(DT.WORKBOOK, self.workbook)
