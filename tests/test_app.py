import importlib.util
import os
import re
import tempfile
import unittest

APP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"
)


def load_app(db_path):
    os.environ["COCOBUTTON_DB_PATH"] = db_path
    spec = importlib.util.spec_from_file_location("cocobutton_app", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CocobuttonTest(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.unlink(self.db_path)
        self.mod = load_app(self.db_path)
        self.client = self.mod.app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_index_ok(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("Cocoa Button", body)
        self.assertIn("ココアを呼ぶ", body)

    def test_lines_variety(self):
        with open(APP_PATH, encoding="utf-8") as f:
            source = f.read()
        match = re.search(r"const lines=\[(.*?)\];", source, re.S)
        self.assertIsNotNone(match)
        lines = re.findall(r'"([^"]+)"', match.group(1))
        self.assertGreaterEqual(len(lines), 20)
        self.assertEqual(len(lines), len(set(lines)))

    def test_count_increments(self):
        self.assertEqual(self.mod.db_counts(), (0, 0))
        res = self.client.post("/count")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {"total": 1, "today": 1})
        res = self.client.post("/count")
        self.assertEqual(res.get_json(), {"total": 2, "today": 2})
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn('<span id="totalCount">2</span>', body)

    def test_count_get_not_allowed(self):
        res = self.client.get("/count")
        self.assertEqual(res.status_code, 405)


if __name__ == "__main__":
    unittest.main()
