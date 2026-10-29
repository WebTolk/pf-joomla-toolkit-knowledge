"""Build immutable PF knowledge-package assets for GitHub Releases."""
from __future__ import annotations
import argparse
import hashlib
import io
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'https://github.com/WebTolk/pf-joomla-toolkit-knowledge'
PACKAGE_ID = 'joomla.toolkit.documentation'
MANIFEST_URL = REPOSITORY + '/releases/latest/download/joomla-toolkit.json'
PAYLOAD_FILES = ['package.yaml', 'README.md', 'CHANGELOG.md', 'NOTICE.md',
                 'indexes/resource-index.yaml', 'docs/source-provenance.json',
                 'docs/upstream-package-1.0.0.yaml']

def payload_files():
    return sorted([ROOT / p for p in PAYLOAD_FILES] + list((ROOT / 'resources').rglob('*.md')),
                  key=lambda p: p.relative_to(ROOT).as_posix())

def digest(data):
    return hashlib.sha256(data).hexdigest()

def build(output: Path):
    package = yaml.safe_load((ROOT / 'package.yaml').read_text(encoding='utf-8'))
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version) or package['version'] != version:
        raise ValueError('VERSION and package.yaml must contain the same stable SemVer')
    if package['id'] != PACKAGE_ID or package['update_sites'][0]['manifest_url'] != MANIFEST_URL:
        raise ValueError('Package identity or stable update URL changed')
    output.mkdir(parents=True, exist_ok=True)
    artifact = output / f'{PACKAGE_ID}-{version}.zip'
    # STORED plus fixed headers keeps asset bytes identical on Windows and Linux.
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_STORED) as archive:
        for path in payload_files():
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    artifact_bytes = buffer.getvalue()
    sha = digest(artifact_bytes)
    manifest_path = ROOT / 'updates/joomla-toolkit.json'
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else None
    versions = previous['channels']['stable']['versions'] if previous else []
    same = [v for v in versions if v['version'] == version]
    if same and same[0]['sha256'] != sha:
        raise ValueError('Refusing to change an already recorded version; bump the version first')
    if artifact.exists() and artifact.read_bytes() != artifact_bytes:
        raise ValueError('Refusing to replace an existing archive with different bytes')
    artifact.write_bytes(artifact_bytes)
    if not same:
        versions.append({'version': version, 'released_at': '2026-10-29T00:00:00Z' if version == '1.0.1' else datetime.now(timezone.utc).isoformat(),
                         'download_url': f'{REPOSITORY}/releases/download/v{version}/{artifact.name}',
                         'sha256': sha, 'changelog_url': f'{REPOSITORY}/releases/download/v{version}/CHANGELOG.md',
                         'breaking': False, 'migration_required': False})
    manifest = {'schema_version': 1, 'kind': 'processforge.update_manifest',
                'subject': {'id': PACKAGE_ID, 'type': 'knowledge_package', 'name': 'Joomla Toolkit'},
                'channels': {'stable': {'latest': version, 'versions': versions}}}
    data = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(data)
    (output / 'joomla-toolkit.json').write_bytes(data)
    (output / 'CHANGELOG.md').write_bytes((ROOT / 'CHANGELOG.md').read_bytes())
    assets = [artifact, output / 'joomla-toolkit.json', output / 'CHANGELOG.md']
    (output / 'SHA256SUMS').write_text(''.join(f'{digest(p.read_bytes())}  {p.name}\n' for p in assets), encoding='utf-8', newline='\n')
    return artifact

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.pf/tmp/initial-release/dist')
    args = parser.parse_args()
    artifact = build(args.output.resolve())
    print(f'Built {artifact.name}: {digest(artifact.read_bytes())}')
