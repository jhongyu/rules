import html
import json
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

PUBLIC.mkdir(exist_ok=True)

for path in PUBLIC.glob("*"):
    if path.is_file():
        path.unlink()

generated_files = []

for yaml_file in sorted(ROOT.glob("*.yaml")):
    data = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or {}
    payload = data.get("payload", [])

    domains = []
    domain_suffixes = []

    for item in payload:
        if not isinstance(item, str):
            continue

        if item.startswith("+."):
            domain_suffixes.append(item[2:])
        elif item.startswith("."):
            domain_suffixes.append(item[1:])
        else:
            domains.append(item)

    rule = {}

    if domains:
        rule["domain"] = domains

    if domain_suffixes:
        rule["domain_suffix"] = domain_suffixes

    rule_set = {
        "version": 2,
        "rules": [rule] if rule else [],
    }

    yaml_output = PUBLIC / yaml_file.name
    shutil.copy2(yaml_file, yaml_output)
    generated_files.append(yaml_file.name)

    json_file_name = f"{yaml_file.stem}.json"
    json_file = PUBLIC / json_file_name
    json_file.write_text(
        json.dumps(rule_set, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    generated_files.append(json_file_name)

links = "\n".join(
    f'    <li><a href="/{html.escape(file_name)}">{html.escape(file_name)}</a></li>'
    for file_name in sorted(generated_files)
)

(PUBLIC / "index.html").write_text(
    f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Rules</title>
</head>
<body>
  <h1>Rules</h1>
  <ul>
{links}
  </ul>
</body>
</html>
""",
    encoding="utf-8",
)
