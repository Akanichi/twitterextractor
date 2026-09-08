from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SecurityConfigurationTests(unittest.TestCase):
    def test_runtime_does_not_enable_debug_mode(self):
        source = (ROOT / "app.py").read_text()
        self.assertNotIn("debug=True", source)

    def test_cors_is_not_unrestricted(self):
        source = (ROOT / "app.py").read_text()
        self.assertNotIn("CORS(app)", source)
        self.assertIn("ALLOWED_ORIGINS", source)

    def test_fixed_dependency_versions_are_present(self):
        requirements = (ROOT / "requirements.txt").read_text()
        self.assertIn("requests==2.33.0", requirements)
        self.assertIn("python-dotenv==1.2.2", requirements)


if __name__ == "__main__":
    unittest.main()
