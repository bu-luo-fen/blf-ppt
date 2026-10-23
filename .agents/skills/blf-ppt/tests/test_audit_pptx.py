"""Structural tests using small synthetic OOXML packages, not rendered decks."""

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_pptx.py"
spec = importlib.util.spec_from_file_location("audit_pptx", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"


def make_pptx(path, text="研究方法", x=10, include_slide=True):
    presentation = (f'<p:presentation xmlns:p="{P}" xmlns:r="{R}">'
                    '<p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst>'
                    '<p:sldSz cx="1000" cy="600"/></p:presentation>')
    rels = (f'<Relationships xmlns="{PR}">'
            '<Relationship Id="rId1" Target="slides/slide1.xml"/>'
            '</Relationships>')
    slide = (f'<p:sld xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree><p:sp>'
             f'<p:spPr><a:xfrm><a:off x="{x}" y="10"/><a:ext cx="100" cy="100"/>'
             f'</a:xfrm></p:spPr><p:txBody><a:p><a:r><a:t>{text}</a:t>'
             '</a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("ppt/presentation.xml", presentation)
        z.writestr("ppt/_rels/presentation.xml.rels", rels)
        if include_slide:
            z.writestr("ppt/slides/slide1.xml", slide)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "fixture.pptx"

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_structure(self):
        make_pptx(self.path)
        count, findings, invalid = audit.inspect(self.path)
        self.assertEqual((count, findings, invalid), (1, [], False))

    def test_placeholder_and_overflow_are_warnings(self):
        make_pptx(self.path, text="TODO", x=1100)
        count, findings, invalid = audit.inspect(self.path)
        self.assertEqual(count, 1)
        self.assertFalse(invalid)
        self.assertEqual([f[0] for f in findings], ["警告", "警告"])

    def test_missing_slide_is_problem(self):
        make_pptx(self.path, include_slide=False)
        _, findings, invalid = audit.inspect(self.path)
        self.assertFalse(invalid)
        self.assertTrue(any(f[0] == "问题" for f in findings))

    def test_corrupt_zip_is_invalid(self):
        self.path.write_bytes(b"not a zip")
        _, findings, invalid = audit.inspect(self.path)
        self.assertTrue(invalid)
        self.assertTrue(any(f[0] == "问题" for f in findings))


if __name__ == "__main__":
    unittest.main()
