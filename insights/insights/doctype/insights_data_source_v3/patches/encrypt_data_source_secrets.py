# //// Neoffice — added file (no upstream equivalent). Ships with the security fix
# //// that turned `Insights Data Source v3.connection_string`,
# //// `.bigquery_service_account_key` and `Insights Data Source.connection_string`
# //// into Password fields at permlevel 1: changing the fieldtype only protects
# //// values written AFTER the change, the ones already in the table stay in clear
# //// until the row is saved again. This patch moves them into `__Auth` (encrypted)
# //// and leaves the usual mask in the column, so an install that has been running
# //// for months ends up in the same state as a fresh one. It also repairs the
# //// permission level on the instances that carry Custom DocPerm rows for these
# //// doctypes — see grant_permlevel_access below. Idempotent: a value that is
# //// already a mask is skipped, and a permission that exists is not added twice.
# //// (drop once upstream PR bvisible/insights:security-hardening-2026-09 is merged)
import frappe
from frappe.utils.password import set_encrypted_password

SECRET_FIELDS = {
    "Insights Data Source v3": ("connection_string", "bigquery_service_account_key"),
    "Insights Data Source": ("connection_string",),
}

# who may read and write the fields now sitting at permlevel 1 — the same role the
# DocType JSON grants, so both halves say the same thing
PERMLEVEL_ROLE = {
    "Insights Data Source v3": "Insights Admin",
    "Insights Data Source": "System Manager",
}
PERMLEVEL = 1


def execute():
    """encrypt_data_source_secrets"""

    for doctype, fieldnames in SECRET_FIELDS.items():
        if not frappe.db.table_exists(doctype):
            continue

        for fieldname in fieldnames:
            if not frappe.db.has_column(doctype, fieldname):
                continue
            encrypt_column(doctype, fieldname)

        grant_permlevel_access(doctype, PERMLEVEL_ROLE[doctype])


def encrypt_column(doctype: str, fieldname: str):
    rows = frappe.db.sql(
        """
        select `name`, `{fieldname}` as `value`
        from `tab{doctype}`
        where `{fieldname}` is not null and `{fieldname}` != ''
        """.format(doctype=doctype, fieldname=fieldname),
        as_dict=True,
    )

    encrypted = 0
    for row in rows:
        if is_masked(row.value):
            continue
        set_encrypted_password(doctype, row.name, row.value, fieldname)
        frappe.db.set_value(
            doctype,
            row.name,
            fieldname,
            "*" * len(row.value),
            update_modified=False,
        )
        encrypted += 1

    if encrypted:
        print(f"insights: encrypted {encrypted} {doctype}.{fieldname} value(s)")


def grant_permlevel_access(doctype: str, role: str):
    """Give `role` permlevel 1 on an instance whose permissions were customised.

    A DocType that carries any Custom DocPerm row ignores its shipped DocPerms
    entirely (frappe.permissions.get_valid_perms), so the permlevel 1 row added to
    the DocType JSON never reaches such an instance: the two fields would end up
    readable and writable by nobody but Administrator, and an Insights Admin could
    no longer configure a connection string. Only instances that already hold
    Custom DocPerms are touched — creating the first one would freeze the doctype
    on its current permissions and make every later upstream change inert.
    """
    if not frappe.db.exists("Custom DocPerm", {"parent": doctype}):
        return

    if frappe.db.exists(
        "Custom DocPerm", {"parent": doctype, "role": role, "permlevel": PERMLEVEL}
    ):
        return

    frappe.get_doc(
        {
            "doctype": "Custom DocPerm",
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "permlevel": PERMLEVEL,
            "read": 1,
            "write": 1,
        }
    ).insert(ignore_permissions=True)

    frappe.clear_cache(doctype=doctype)
    print(f"insights: granted {role} permlevel {PERMLEVEL} on {doctype}")


def is_masked(value: str) -> bool:
    return bool(value) and value == "*" * len(value)
