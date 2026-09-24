# //// Neoffice — added file (no upstream equivalent). One test per guard added by
# //// the 2026-09-04 security pass on this fork; every test names the defect it
# //// pins so a merge that loses the guard fails here instead of in production.
# //// At the 2026-09-24 merge of upstream version-3, F3 and F4 are upstream's own fixes
# //// (check_referenced_query_access, check_stored_document): their tests stay here
# //// as regression guards on the merged code. The others pin guards upstream
# //// still lacks.
import json

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils.password import get_decrypted_password

from insights.api import check_stored_document, run_doc_method
from insights.insights.doctype.insights_data_source_v3 import ibis_utils
from insights.insights.doctype.insights_data_source_v3.connectors.postgresql import (
    quote_dsn_credentials,
)
from insights.insights.doctype.insights_team import insights_team
from insights.permissions import InsightsPermissions

TEST_USER = "_test_insights_security@yopmail.com"
OTHER_USER = "_test_insights_security_other@yopmail.com"


def make_insights_user(email: str, roles: tuple[str, ...] = ("Insights User",)):
    if not frappe.db.exists("User", email):
        user = frappe.new_doc("User")
        user.email = email
        user.first_name = "Insights Security Probe"
        user.send_welcome_email = 0
        user.insert(ignore_permissions=True)

    user = frappe.get_doc("User", email)
    held = {row.role for row in user.roles}
    for role in roles:
        if role not in held:
            user.append("roles", {"role": role})
    user.save(ignore_permissions=True)
    return user


class TestInsightsSecurity(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # //// Neoffice — setUpClass now forces Administrator before creating test users
        # //// Neoffice — (40b0b50d "test: drop three dead v2 test modules, harden the security suite setup"):
        # //// Neoffice — a failing test after frappe.set_user() used to leak a rolled-back user into the run
        # A test that fails after frappe.set_user() leaks that user into the whole
        # run; the users below must be created by Administrator whatever ran before.
        frappe.set_user("Administrator")
        make_insights_user(TEST_USER)
        make_insights_user(OTHER_USER)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    # ------------------------------------------------------------------ F6
    def test_doc_permission_survives_a_missing_permission_query(self):
        """F6 - has_doc_permission() used to call .where() on the None that
        _build_permission_query() returns when team permissions are off, which
        answered HTTP 500 instead of a verdict."""
        frappe.db.set_single_value("Insights Settings", "enable_permissions", 0)

        permissions = InsightsPermissions(TEST_USER)
        self.assertFalse(permissions.team_permissions_enabled)

        source = frappe.get_doc("Insights Data Source v3", "Site DB")
        self.assertNotEqual(source.owner, TEST_USER, "the probe must not own the source")

        # no exception, and a verdict: team-based doctypes are open to every
        # insights user while team permissions are disabled
        self.assertTrue(permissions.has_doc_permission(source, "read"))

    def test_doc_permission_denies_a_doctype_without_a_permission_query(self):
        """F6 - the same guard must fail closed for a doctype that is declared in
        PERMISSION_DOCTYPES but has no query builder."""
        frappe.db.set_single_value("Insights Settings", "enable_permissions", 0)

        permissions = InsightsPermissions(TEST_USER)
        stranger = frappe.get_doc(
            {"doctype": "Insights Workbook", "name": "does-not-matter", "owner": OTHER_USER}
        )
        stranger.doctype = "Insights Query Result"  # not in TEAM_BASED_PERMISSION_DOCTYPES

        with self.patch_permission_doctypes("Insights Query Result"):
            self.assertFalse(permissions.has_doc_permission(stranger, "read"))

    def patch_permission_doctypes(self, doctype):
        import insights.permissions as module

        class _Patch:
            def __enter__(_self):
                _self.previous = module.PERMISSION_DOCTYPES
                module.PERMISSION_DOCTYPES = [*module.PERMISSION_DOCTYPES, doctype]

            def __exit__(_self, *exc):
                module.PERMISSION_DOCTYPES = _self.previous

        return _Patch()

    # ------------------------------------------------------------------ F4
    def make_query_of(self, owner: str, title: str):
        workbook = frappe.get_doc({"doctype": "Insights Workbook", "title": f"{title} workbook"})
        workbook.insert(ignore_permissions=True)
        frappe.db.set_value("Insights Workbook", workbook.name, "owner", owner)

        query = frappe.get_doc(
            {
                "doctype": "Insights Query v3",
                "title": title,
                "workbook": workbook.name,
                "operations": json.dumps([]),
            }
        )
        query.insert(ignore_permissions=True)
        frappe.db.set_value("Insights Query v3", query.name, "owner", owner)
        return query

    def test_run_doc_method_ignores_the_owner_in_the_payload(self):
        """F4 - the document was built from the request body and the permission
        was checked on it, so putting your own e-mail in `owner` made you the
        owner of every document you could name. Access is now decided on the
        stored row (upstream check_stored_document, which replaced ours)."""
        query = self.make_query_of(OTHER_USER, "owned by someone else")
        forged = {
            "doctype": "Insights Query v3",
            "name": query.name,
            "owner": TEST_USER,
            "title": "forged",
            "operations": json.dumps([{"type": "limit", "limit": 1}]),
        }

        frappe.set_user(TEST_USER)
        with self.assertRaises(frappe.PermissionError):
            run_doc_method("execute", json.dumps(forged))

    def test_run_doc_method_keeps_unsaved_documents_working(self):
        """F4 - the editor previews UNSAVED queries through this endpoint; a name
        with no row behind it discloses nothing and must not be refused."""
        frappe.set_user(TEST_USER)
        self.assertIsNone(check_stored_document("Insights Query v3", "new-query-does-not-exist"))

    # ------------------------------------------------------------------ F3
    def test_export_refuses_linked_queries_the_caller_cannot_read(self):
        """F3 - export() loaded every linked query with no permission check, so
        exporting your own query handed you the definition of someone else's.
        Upstream's fix (check_referenced_query_access) refuses the export where
        ours skipped the dependency; either way the definition stays private."""
        workbook = frappe.get_doc({"doctype": "Insights Workbook", "title": "Export probe"})
        workbook.insert(ignore_permissions=True)

        other_workbook = frappe.get_doc({"doctype": "Insights Workbook", "title": "Someone else's workbook"})
        other_workbook.insert(ignore_permissions=True)
        frappe.db.set_value("Insights Workbook", other_workbook.name, "owner", OTHER_USER)

        secret = frappe.get_doc(
            {
                "doctype": "Insights Query v3",
                "title": "someone else's query",
                "workbook": other_workbook.name,
                "operations": json.dumps([]),
            }
        )
        secret.insert(ignore_permissions=True)
        frappe.db.set_value("Insights Query v3", secret.name, "owner", OTHER_USER)

        mine = frappe.get_doc(
            {
                "doctype": "Insights Query v3",
                "title": "mine",
                "workbook": workbook.name,
                "operations": json.dumps([]),
            }
        )
        mine.insert(ignore_permissions=True)
        frappe.db.set_value("Insights Query v3", mine.name, "owner", TEST_USER)
        frappe.db.set_value("Insights Query v3", mine.name, "linked_queries", json.dumps([secret.name]))
        frappe.db.set_value("Insights Workbook", workbook.name, "owner", TEST_USER)

        frappe.set_user(TEST_USER)
        with self.assertRaises(frappe.PermissionError):
            frappe.get_doc("Insights Query v3", mine.name).export()

    # ------------------------------------------------------------------ F7a
    def restrict_tables(self, *restricted: str):
        """Pretend `restricted` are Insights tables carrying a restriction, and
        record every table check_table_permission() is asked about."""
        checked = []
        test = self

        class _Patch:
            def __enter__(_self):
                _self.saved = (
                    ibis_utils.is_insights_table,
                    ibis_utils.get_restricted_table_sql,
                    insights_team.check_table_permission,
                )
                ibis_utils.is_insights_table = lambda ds, name: name in restricted
                ibis_utils.get_restricted_table_sql = lambda ds, name, dialect: (
                    f"SELECT * FROM `{name}` WHERE `owner` = 'x'" if name in restricted else None
                )
                insights_team.check_table_permission = lambda ds, name, **kw: checked.append(name)
                return checked

            def __exit__(_self, *exc):
                (
                    ibis_utils.is_insights_table,
                    ibis_utils.get_restricted_table_sql,
                    insights_team.check_table_permission,
                ) = _self.saved

        test.addCleanup(lambda: None)
        return _Patch()

    def test_upstream_still_drops_tables_named_like_a_cte(self):
        """F7a canary - the reason check_cte_shadowing() exists. When this fails,
        upstream resolves CTE names itself: drop the guard and these tests."""
        from insights.insights.query_utils import extract_sql_table_refs

        refs = extract_sql_table_refs(
            "WITH tabUser AS (SELECT * FROM tabUser) SELECT * FROM tabUser", dialect="mysql"
        )
        self.assertEqual(refs, [], "upstream now sees the shadowed table")

    def test_raw_sql_checks_permission_on_a_table_a_cte_is_named_after(self):
        """F7a - a CTE named after a table hid that table from the permission
        check: the table set was empty, so nothing was checked."""
        with self.restrict_tables("tabUser") as checked:
            ibis_utils.is_insights_table = lambda ds, name: name == "tabUser"
            ibis_utils.get_restricted_table_sql = lambda ds, name, dialect: None
            ibis_utils.check_cte_shadowing(
                "Site DB", "WITH tabUser AS (SELECT * FROM tabUser) SELECT * FROM tabUser", "mysql"
            )

        self.assertEqual(checked, ["tabUser"], "the shadowed table must still be checked")

    def test_raw_sql_refuses_a_cte_shadowing_a_restricted_table(self):
        """F7a - `WITH tabUser AS (SELECT * FROM tabUser) SELECT * FROM tabUser`
        left no table to bind, so no restriction was applied: the raw SQL reached
        the backend untouched."""
        with self.restrict_tables("tabUser") as checked:
            with self.assertRaises(frappe.PermissionError):
                ibis_utils.check_cte_shadowing(
                    "Site DB",
                    "WITH tabUser AS (SELECT * FROM tabUser) SELECT * FROM tabUser",
                    "mysql",
                )

        self.assertEqual(checked, ["tabUser"], "the shadowed table must still be checked")

    def test_raw_sql_allows_a_cte_that_shadows_nothing(self):
        """F7a - the guard must not cost a legitimate CTE its name: a CTE named
        after no table passes, and the table it reads is left to the bindings."""
        with self.restrict_tables("tabUser") as checked:
            ibis_utils.check_cte_shadowing(
                "Site DB", "WITH helper AS (SELECT * FROM tabUser) SELECT * FROM helper", "mysql"
            )

        self.assertEqual(checked, [], "nothing is shadowed, so the guard has nothing to check")

    # ------------------------------------------------------------------ F1
    def test_data_source_secrets_are_password_fields(self):
        """F1 - `connection_string` and `bigquery_service_account_key` were plain
        Text/JSON columns, readable by any Insights User through
        frappe.client.get_list."""
        meta = frappe.get_meta("Insights Data Source v3")
        for fieldname in ("connection_string", "bigquery_service_account_key"):
            field = meta.get_field(fieldname)
            self.assertEqual(field.fieldtype, "Password", f"{fieldname} must be a Password field")
            self.assertEqual(field.permlevel, 1, f"{fieldname} must sit above permlevel 0")

        v2 = frappe.get_meta("Insights Data Source")
        self.assertEqual(v2.get_field("connection_string").fieldtype, "Password")
        self.assertEqual(v2.get_field("connection_string").permlevel, 1)

    def test_saving_a_data_source_encrypts_its_connection_string(self):
        """F1 - the value must leave the table: `__Auth` holds it encrypted and the
        column keeps a mask, so a list query can no longer read it."""
        dsn = "postgresql://probe:s3cr3t@db.example.invalid:5432/probe"

        source = frappe.get_doc(
            {
                "doctype": "Insights Data Source v3",
                "title": "Security probe source",
                "type": "Database",
                "database_type": "PostgreSQL",
                "connection_string": dsn,
                "status": "Inactive",
            }
        )
        source.flags.ignore_validate = True
        source.insert(ignore_permissions=True)

        stored = frappe.db.get_value("Insights Data Source v3", source.name, "connection_string")
        self.assertNotEqual(stored, dsn, "the DSN must not stay in the table")
        self.assertEqual(stored, "*" * len(dsn))
        self.assertEqual(
            get_decrypted_password("Insights Data Source v3", source.name, "connection_string"),
            dsn,
        )

    def test_encrypt_patch_is_idempotent(self):
        """F1 - the migration that moves existing values must be safe to re-run:
        a value that is already a mask is left alone."""
        from insights.insights.doctype.insights_data_source_v3.patches import (
            encrypt_data_source_secrets as patch,
        )

        dsn = "postgresql://legacy:cleartext@db.example.invalid:5432/legacy"
        source = frappe.get_doc(
            {
                "doctype": "Insights Data Source v3",
                "title": "Legacy probe source",
                "type": "Database",
                "database_type": "PostgreSQL",
                "status": "Inactive",
            }
        )
        source.flags.ignore_validate = True
        source.insert(ignore_permissions=True)
        # simulate a row written before the fieldtype change
        frappe.db.set_value(
            "Insights Data Source v3", source.name, "connection_string", dsn, update_modified=False
        )

        patch.execute()
        self.assertEqual(
            frappe.db.get_value("Insights Data Source v3", source.name, "connection_string"),
            "*" * len(dsn),
        )
        self.assertEqual(
            get_decrypted_password("Insights Data Source v3", source.name, "connection_string"),
            dsn,
        )

        patch.execute()  # second pass must change nothing
        self.assertEqual(
            get_decrypted_password("Insights Data Source v3", source.name, "connection_string"),
            dsn,
        )

    # ------------------------------------------------------- PostgreSQL DSN
    def test_only_the_credentials_of_a_dsn_are_quoted(self):
        """quote_plus() over the whole DSN encoded "://" and "@" too, so
        ibis.connect() could never parse a connection string."""
        self.assertEqual(
            quote_dsn_credentials("postgresql://user:p@ss@db.example.com:5432/mydb"),
            "postgresql://user:p%40ss@db.example.com:5432/mydb",
        )
        # already-escaped input must not be escaped twice
        self.assertEqual(
            quote_dsn_credentials("postgresql://user:p%40ss@db.example.com:5432/mydb"),
            "postgresql://user:p%40ss@db.example.com:5432/mydb",
        )
        # nothing to quote: the DSN comes back untouched
        for dsn in (
            "postgresql://localhost/db",
            "postgresql://user@host/db",
            "postgresql://user:simple@localhost:5432/db?sslmode=require",
        ):
            self.assertEqual(quote_dsn_credentials(dsn), dsn)
