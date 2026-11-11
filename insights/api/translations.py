from contextlib import suppress  # //// Neoffice — added import, for get_translations below

import frappe

# //// Neoffice — added imports (get_translations_from_apps, get_user_translations), for get_translations below.
from frappe.translate import get_all_translations, get_translations_from_apps, get_user_translations


# //// Neoffice — the reason on the def line is ours: open to guests, the guard of new web methods asks why (#1195)
@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_translations():  # permission-check: ok the site's catalogue of interface words, the same for every visitor; no record is read
    language = None
    if frappe.session.user != "Guest":
        language = frappe.db.get_value("User", frappe.session.user, "language")
    if not language:
        language = frappe.db.get_single_value("System Settings", "language")
    # //// Neoffice — the screens of Insights read Insights' own catalogue first. `get_all_translations` merges every
    # //// installed app, and an app installed after Insights that gives the same English word another sense wins: the
    # //// « Open » button of the template library read « Ouvert » (an open state) instead of Insights' « Ouvrir »
    # //// (neoffice-maintenance#1195). A translation a person wrote on the site (Translation doctype) still wins.
    translations = dict(get_all_translations(language))
    if not language:
        return translations
    translations.update(get_translations_from_apps(language, apps=["insights"]))
    with suppress(Exception):
        translations.update(get_user_translations(language))
    return translations
