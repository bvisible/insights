# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# //// Neoffice — was `from urllib.parse import quote_plus`: quoting the whole DSN
# //// broke it, so only its user-info part is escaped now (see quote_dsn_credentials).
# //// (drop once upstream PR from bvisible/insights branch
# //// upstream/security-hardening-2026-09 is merged into frappe/insights)
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import ibis


# //// Neoffice — added helpers, upstream defect (frappe/insights): upstream ran
# //// quote_plus() over the WHOLE DSN, which percent-encodes "://", "@" and "/" too.
# //// "postgresql%3A%2F%2Fuser..." is no longer a URL, so ibis.connect() failed on
# //// every connection string — the field was unusable. Only the user-info part of
# //// the URL can hold characters that need escaping, so escape that part alone and
# //// leave the scheme, host, port and database untouched. quote(unquote(x)) keeps
# //// the operation idempotent: a DSN that is already correctly escaped ("p%40ss")
# //// is not escaped twice into "p%2540ss".
# //// (drop once upstream PR the upstream PR from bvisible/insights branch
# //// upstream/security-hardening-2026-09 is merged into frappe/insights)
def quote_userinfo_part(part: str) -> str:
    return quote(unquote(part), safe="")


def quote_dsn_credentials(connection_string: str) -> str:
    parts = urlsplit(connection_string)
    if "@" not in parts.netloc:
        return connection_string

    userinfo, _, hostinfo = parts.netloc.rpartition("@")
    username, separator, password = userinfo.partition(":")
    userinfo = quote_userinfo_part(username) + separator + quote_userinfo_part(password)

    return urlunsplit(parts._replace(netloc=f"{userinfo}@{hostinfo}"))


def get_postgres_connection(data_source):
    if data_source.connection_string:
        # //// Neoffice — read through get_password(): `connection_string` is now a
        # //// Password field (it carries the database user and its password, and any
        # //// Insights User could read it from the table). get_password() returns the
        # //// in-memory value for an unsaved document, so "Test connection" on a data
        # //// source being created still works.
        # //// (drop once upstream PR the upstream PR from bvisible/insights branch
# //// upstream/security-hardening-2026-09 is merged into frappe/insights)
        conn_string = quote_dsn_credentials(
            data_source.get_password("connection_string", raise_exception=False)
        )
        return ibis.connect(conn_string)
    else:
        password = data_source.get_password(raise_exception=False)
        data_source.port = int(data_source.port or 5432)
        return ibis.postgres.connect(
            host=data_source.host,
            port=data_source.port,
            user=data_source.username,
            password=password,
            database=data_source.database_name,
            schema=data_source.schema,
            sslmode="require" if data_source.use_ssl else None,
        )
