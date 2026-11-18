"""Sestaví index.html: vloží data/geo.json (placeholder /*GEO*/) a src/i18n.js (placeholder /*I18N*/) do src/template.html."""
from pathlib import Path
root = Path(__file__).resolve().parent.parent
tpl = (root / "src" / "template.html").read_text(encoding="utf-8")
geo = (root / "data" / "geo.json").read_text(encoding="utf-8")
i18n = (root / "src" / "i18n.js").read_text(encoding="utf-8")
assert "/*GEO*/" in tpl and "/*I18N*/" in tpl
(root / "index.html").write_text(tpl.replace("/*GEO*/", geo).replace("/*I18N*/", i18n), encoding="utf-8")
print("index.html sestaven")
