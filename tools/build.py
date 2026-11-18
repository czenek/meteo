"""Sestaví index.html: vloží data/geo.json do src/template.html (placeholder /*GEO*/)."""
from pathlib import Path
root = Path(__file__).resolve().parent.parent
tpl = (root / "src" / "template.html").read_text(encoding="utf-8")
geo = (root / "data" / "geo.json").read_text(encoding="utf-8")
assert "/*GEO*/" in tpl
(root / "index.html").write_text(tpl.replace("/*GEO*/", geo), encoding="utf-8")
print("index.html sestaven")
