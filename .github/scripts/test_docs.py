"""Contract tests for the shared documentation check."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("check_docs", Path(__file__).with_name("check_docs.py"))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class AssessmentTests(unittest.TestCase):
    def test_specific_no_impact(self):
        check.validate_impact("Documentation impact: none\nDocumentation details: Internal refactor preserves the documented API and operating procedure.", ["server.py"])

    def test_existing_runbook_counts(self):
        check.validate_impact("Documentation impact: updated\nDocumentation details: infrastructure/README.md now records the changed rollback command.", ["infrastructure/README.md"])

    def test_comments_do_not_count(self):
        with self.assertRaises(ValueError):
            check.validate_impact("<!-- Documentation impact: none\nDocumentation details: This explanatory text is only a template comment. -->", [])

    def test_empty_placeholder_and_duplicate_fail(self):
        for body in ("", "Documentation impact: updated|none\nDocumentation details: <explanation>", "Documentation impact: none\nDocumentation details: TBD with a sufficiently long placeholder", "Documentation impact: none\nDocumentation impact: updated\nDocumentation details: This description has more than twenty characters."):
            with self.subTest(body=body), self.assertRaises(ValueError):
                check.validate_impact(body, [])

    def test_updated_requires_changed_path(self):
        with self.assertRaises(ValueError):
            check.validate_impact("Documentation impact: updated\nDocumentation details: docs/requirements.md explains the new scope.", ["app.py"])

    def test_template_alone_is_not_documentation(self):
        with self.assertRaises(ValueError):
            check.validate_impact("Documentation impact: updated\nDocumentation details: .github/pull_request_template.md was changed for this work.", [".github/pull_request_template.md"])

    def test_document_contract_and_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".github").mkdir()
            docs = {role: f"{role}.md" for role in check.ROLES}
            config = root / ".github/repository-docs.json"
            for path in docs.values():
                (root / path).write_text("# Title\n\n> Purpose: Context.\n\n**Status:** ACTIVE\n", encoding="utf-8")
            config.write_text(json.dumps({"documents": docs}), encoding="utf-8")
            check.validate_documents(root)
            docs["progress"] = "../outside.md"
            config.write_text(json.dumps({"documents": docs}), encoding="utf-8")
            with self.assertRaises(ValueError):
                check.validate_documents(root)


if __name__ == "__main__":
    unittest.main()
