# //// Neoffice — added file (no upstream equivalent). Creating a dashboard or changing its items asks for a preview
# //// image. Upstream falls back to a third-party service (preview.frappe.cloud) when no `preview_generator_url`
# //// is configured, which receives this site's address and a read key for the dashboard. Nothing is sent there
# //// any more unless a service is configured. Run without a site: Frappe and the network are replaced.
"""The preview of a dashboard is never sent to a service nobody configured."""

import unittest
from unittest.mock import MagicMock, patch

import frappe

from insights.insights.doctype.insights_dashboard_v3 import insights_dashboard_v3 as dashboard_module

URL = "https://shop.example.test/insights/shared/dashboard/D1"
HEADERS = {"X-Insights-Preview-Key": "key-that-reads-one-dashboard"}


class TestNoServiceNoCall(unittest.TestCase):
    def test_nothing_is_posted_without_a_configured_service(self):
        with (
            patch.object(dashboard_module.frappe, "conf", frappe._dict()),
            patch.object(dashboard_module.requests, "post") as post,
        ):
            self.assertIsNone(dashboard_module.get_page_preview_via_service(URL, HEADERS))
        post.assert_not_called()

    def test_a_configured_service_gets_the_page_and_nothing_else_changes(self):
        answer = MagicMock(status_code=200, content=b"jpeg-bytes")
        conf = frappe._dict(preview_generator_url="https://preview.internal.test/render")
        with (
            patch.object(dashboard_module.frappe, "conf", conf),
            patch.object(dashboard_module.requests, "post", return_value=answer) as post,
        ):
            image = dashboard_module.get_page_preview_via_service(URL, HEADERS)
        self.assertEqual(image, b"jpeg-bytes")
        self.assertEqual(post.call_args.args[0], "https://preview.internal.test/render")
        self.assertEqual(post.call_args.kwargs["json"]["url"], URL)

    def test_the_default_address_is_gone_from_the_code(self):
        import ast
        import inspect

        tree = ast.parse(inspect.getsource(dashboard_module.get_page_preview_via_service))
        literals = [
            n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
        ]
        self.assertFalse([text for text in literals if "preview.frappe.cloud" in text])

    def test_a_dashboard_keeps_its_image_when_no_preview_is_made(self):
        document = object.__new__(dashboard_module.InsightsDashboardv3)
        document.name = "D1"
        document.preview_image = "/private/files/D1-preview.jpeg?ab12"
        with (
            patch.object(dashboard_module, "get_page_preview", return_value=None),
            patch.object(dashboard_module, "create_preview_file") as create,
            patch.object(dashboard_module.frappe.utils, "get_url", return_value=URL),
            patch.object(dashboard_module.frappe, "generate_hash", return_value="k"),
            patch.object(dashboard_module.frappe, "cache", MagicMock()),
            patch.object(dashboard_module.frappe, "session", frappe._dict(user="u@example.test")),
        ):
            result = document.generate_dashboard_preview()
        self.assertEqual(result, "/private/files/D1-preview.jpeg?ab12")
        create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
