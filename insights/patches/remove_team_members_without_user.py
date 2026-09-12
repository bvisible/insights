# //// Neoffice — added file (no upstream equivalent). Removes Insights Team Member rows
# //// whose User no longer exists, then puts back into the Admin team every holder of
# //// the Insights Admin role that a failed save kept out (neoffice-maintenance#372).
# //// Idempotent.
import frappe
from frappe.core.doctype.role.role import get_users as get_users_with_role


def execute():
    if not frappe.db.table_exists("Insights Team Member"):
        return

    frappe.db.sql(
        """delete m from `tabInsights Team Member` m
        left join `tabUser` u on u.name = m.user
        where u.name is null"""
    )

    if not frappe.db.exists("Insights Team", "Admin"):
        return

    members = set(frappe.get_all("Insights Team Member", filters={"parent": "Admin"}, pluck="user"))
    missing = [user for user in get_users_with_role("Insights Admin") if user not in members]
    if not missing:
        return

    team = frappe.get_doc("Insights Team", "Admin")
    for user in missing:
        team.append("team_members", {"user": user})
    team.save(ignore_permissions=True)
