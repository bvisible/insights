# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import ibis


def get_bigquery_connection(data_source):
    project_id = data_source.bigquery_project_id
    dataset_id = data_source.bigquery_dataset_id
    #//// Neoffice — read through get_password(): the service-account key is now a
    #//// Password field (it is a private key, and any Insights User could read it
    #//// from the table). get_password() returns the in-memory value for an unsaved
    #//// document, so "Test connection" still works while creating the source.
    #//// (drop once upstream PR the upstream PR from bvisible/insights branch
#//// upstream/security-hardening-2026-09 is merged into frappe/insights)
    credentials = data_source.get_password("bigquery_service_account_key", raise_exception=False)

    try:
        from google.oauth2 import service_account
    except ImportError:
        raise ImportError("Please install google-auth to use BigQuery as a data source")

    credentials = service_account.Credentials.from_service_account_info(
        frappe.parse_json(credentials)
    )

    return ibis.bigquery.connect(
        project_id=project_id,
        dataset_id=dataset_id,
        credentials=credentials,
    )
