"""Check package identity, provenance, portability and release archive contents."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import tempfile
import zipfile
import yaml
from release import ROOT, PACKAGE_ID, MANIFEST_URL, build, payload_files, digest

def check(pf_root=None):
    package = yaml.safe_load((ROOT / 'package.yaml').read_text(encoding='utf-8'))
    version = (ROOT / 'VERSION').read_text().strip()
    assert package['id'] == PACKAGE_ID and package['version'] == version
    assert package['type'] == 'knowledge_package'
    assert package['update_sites'][0]['manifest_url'] == MANIFEST_URL
    assert package['update_sites'][0]['policy']['auto_apply'] is False
    assert package['update_sites'][0]['trust']['require_https'] is True
    assert package['update_sites'][0]['trust']['require_sha256'] is True
    resource, = package['resources']
    assert resource['id'] == 'joomla-toolkit' and resource['version'] == version
    assert resource['path_ref'] == {'package': PACKAGE_ID, 'relative_path': 'resources/joomla-toolkit'}
    index = yaml.safe_load((ROOT / 'indexes/resource-index.yaml').read_text(encoding='utf-8'))
    assert index['package']['id'] == PACKAGE_ID and index['package']['version'] == version
    assert index['resources'] == [{**resource, 'package': PACKAGE_ID}]
    provenance = json.loads((ROOT / 'docs/source-provenance.json').read_text(encoding='utf-8'))
    assert len(provenance['files']) == 4
    assert sum(x['private_reference_replacements'] for x in provenance['files']) == 5
    for item in provenance['files']:
        actual = digest((ROOT / 'resources/joomla-toolkit' / item['path']).read_bytes())
        # The initial provenance captures only the extraction baseline.
        if version == '1.0.1':
            assert actual == item['published_sha256']
            if not item['private_reference_replacements']:
                assert actual == item['source_sha256']
    for path in payload_files():
        text = path.read_text(encoding='utf-8-sig')
        assert not re.search(r'(?<![A-Za-z0-9])[A-Za-z]:[\\/]', text), path
        assert not re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN .*PRIVATE KEY-----', text), path
    if pf_root:
        import sys
        sys.path.insert(0, str(pf_root / 'src'))
        from processforge_core.maintenance.schema_checks import UpdateSchemaChecks
        schema = json.loads((pf_root / 'schemas/package-manifest.schema.json').read_text(encoding='utf-8'))
        errors = UpdateSchemaChecks(pf_root).validate(package, schema, schema, 'package')
        assert not errors, errors
    scratch = ROOT / '.pf/tmp/initial-release'
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='check-', dir=scratch) as raw:
        artifact = build(Path(raw))
        with zipfile.ZipFile(artifact) as archive:
            expected = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in payload_files()}
            assert set(archive.namelist()) == set(expected)
            assert all(archive.read(name) == data for name, data in expected.items())
            zipped = yaml.safe_load(archive.read('package.yaml'))
            assert zipped['update_sites'][0]['manifest_url'] == MANIFEST_URL
        manifest = json.loads((ROOT / 'updates/joomla-toolkit.json').read_text())
        entry, = [x for x in manifest['channels']['stable']['versions'] if x['version'] == version]
        assert entry['sha256'] == digest(artifact.read_bytes())
        assert 'install_path' not in entry.get('update_policy', {})
    print('PASS: identity, resource index, provenance, portability, immutable release hash and exact ZIP payload')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pf-root', type=Path)
    check(parser.parse_args().pf_root)
