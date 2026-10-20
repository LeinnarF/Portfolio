import tempfile
import unittest
from pathlib import Path

from src.builder import build


class TestBuilder(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent
        self.content_dir = self.root / "content"
        self.templates_dir = self.root / "templates"
        self.assets_dir = self.root / "assets"

    def test_build_generates_pages_and_nojekyll(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            projects = build(
                content_dir=self.content_dir,
                templates_dir=self.templates_dir,
                assets_dir=self.assets_dir,
                output_dir=out_dir,
                base_url="/Portfolio",
                strict=True,
            )
            self.assertGreater(len(projects), 0)
            self.assertTrue((out_dir / "index.html").is_file())
            self.assertTrue((out_dir / "404.html").is_file())
            self.assertTrue((out_dir / "sitemap.xml").is_file())
            self.assertTrue((out_dir / ".nojekyll").is_file())

            # Check that base_url is prefixed
            index_content = (out_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="/Portfolio/"', index_content)
            self.assertIn('href="/Portfolio/assets/css/style.css"', index_content)
            self.assertIn('src="/Portfolio/assets/js/main.js"', index_content)

            # Check sitemap
            sitemap_content = (out_dir / "sitemap.xml").read_text(encoding="utf-8")
            self.assertIn("/Portfolio/", sitemap_content)

    def test_build_root_base_url(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            build(
                content_dir=self.content_dir,
                templates_dir=self.templates_dir,
                assets_dir=self.assets_dir,
                output_dir=out_dir,
                base_url="",
                strict=True,
            )
            index_content = (out_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="/"', index_content)
            self.assertIn('href="/assets/css/style.css"', index_content)
            self.assertIn('src="/assets/js/main.js"', index_content)
            self.assertTrue((out_dir / ".nojekyll").is_file())


if __name__ == "__main__":
    unittest.main()
