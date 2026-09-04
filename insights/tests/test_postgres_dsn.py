"""Only the credentials of a connection string are escaped.

quote_plus() ran over the whole DSN, encoding "://", "@" and "/" as well, so
ibis.connect() was handed something that is not a URL and the connection string
field could never work.
"""

from insights.insights.doctype.insights_data_source_v3.connectors.postgresql import (
    quote_dsn_credentials,
)
from insights.tests.base import InsightsIntegrationTestCase


class TestPostgresDSN(InsightsIntegrationTestCase):
    def test_a_password_holding_an_at_sign_is_escaped(self):
        self.assertEqual(
            quote_dsn_credentials("postgresql://user:p@ss@db.example.com:5432/mydb"),
            "postgresql://user:p%40ss@db.example.com:5432/mydb",
        )

    def test_an_already_escaped_password_is_not_escaped_twice(self):
        self.assertEqual(
            quote_dsn_credentials("postgresql://user:p%40ss@db.example.com:5432/mydb"),
            "postgresql://user:p%40ss@db.example.com:5432/mydb",
        )

    def test_a_lone_percent_sign_is_escaped(self):
        self.assertEqual(
            quote_dsn_credentials("postgresql://user:100%@localhost/db"),
            "postgresql://user:100%25@localhost/db",
        )

    def test_a_dsn_with_nothing_to_escape_comes_back_untouched(self):
        for dsn in (
            "postgresql://localhost/db",
            "postgresql://user@host/db",
            "postgresql://user:simple@localhost:5432/db?sslmode=require",
        ):
            self.assertEqual(quote_dsn_credentials(dsn), dsn)

    def test_the_rest_of_the_url_is_never_touched(self):
        dsn = "postgresql://user:p@ss@db.example.com:5432/mydb?sslmode=require"
        quoted = quote_dsn_credentials(dsn)

        self.assertTrue(quoted.startswith("postgresql://"))
        self.assertTrue(quoted.endswith("@db.example.com:5432/mydb?sslmode=require"))
