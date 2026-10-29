"""Exercise the installed native PF updater in a private disposable workplace."""
from __future__ import annotations
import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
import yaml
from release import ROOT, PACKAGE_ID, MANIFEST_URL, build, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pf-root', required=True, type=Path)
    parser.add_argument('--remote', action='store_true')
    args = parser.parse_args()
    pf = args.pf_root.resolve() / 'bin/pf.py'
    scratch = ROOT / '.pf/tmp/initial-release'
    scratch.mkdir(parents=True, exist_ok=True)
    # Retain this exact fixture and command transcripts as local delivery evidence.
    workplace = Path(tempfile.mkdtemp(prefix='native-remote-' if args.remote else 'native-local-', dir=scratch))
    log = []
    env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8'}

    def run(*parts, ok=True):
        result = subprocess.run([sys.executable, str(pf), *parts], cwd=args.pf_root,
                                env=env, encoding='utf-8', stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=120)
        log.append({'arguments': list(parts), 'exit_code': result.returncode, 'output': result.stdout})
        (workplace / 'commands.json').write_text(json.dumps(log, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if ok and result.returncode:
            raise AssertionError(result.stdout)
        return result

    def write_yaml(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding='utf-8')

    artifact = build(workplace / 'mirror')
    source_manifest = json.loads((ROOT / 'updates/joomla-toolkit.json').read_text(encoding='utf-8'))
    version = (ROOT / 'VERSION').read_text().strip()
    package = yaml.safe_load((ROOT / 'package.yaml').read_text(encoding='utf-8'))
    install_path = f'vendor/knowledge/{PACKAGE_ID}'
    installed = workplace / install_path
    installed.mkdir(parents=True)
    with zipfile.ZipFile(artifact) as archive:
        archive.extractall(installed)
    baseline = copy.deepcopy(package)
    baseline['version'] = '1.0.0'
    baseline['resources'][0]['version'] = '1.0.0'
    baseline.pop('update_sites')
    write_yaml(installed / 'package.yaml', baseline)
    if args.remote:
        manifest_url = MANIFEST_URL
    else:
        entry, = [v for v in source_manifest['channels']['stable']['versions'] if v['version'] == version]
        entry['download_url'] = artifact.as_uri()
        entry['changelog_url'] = (ROOT / 'CHANGELOG.md').as_uri()
        (workplace / 'mirror/manifest.json').write_text(json.dumps(source_manifest), encoding='utf-8')
        manifest_url = (workplace / 'mirror/manifest.json').as_uri()
    source = copy.deepcopy(package['update_sites'][0])
    source['subjects'] = [{'type':'knowledge_package','ids':[PACKAGE_ID]}]
    source['manifest_url'] = manifest_url
    source['trust']['require_https'] = args.remote
    write_yaml(workplace / 'workplace.yaml', {
        'schema_version':1,'workplace':{'id':'joomla-toolkit-updater-fixture','name':'Updater fixture','type':'workstation','os':sys.platform},
        'process_forge':{'version_constraint':'^1.0','install_mode':'linked'},
        'paths':{'root':'.','registries':'registries'},
        'registries':{'package_roots':'registries/package-roots.yaml','knowledge_packages':'registries/knowledge-packages.yaml',
                      'installed_subjects':'registries/installed-subjects.yaml','update_sources':'registries/update-sources.yaml'}})
    write_yaml(workplace / 'registries/package-roots.yaml', {'schema_version':1,'package_roots':[{'id':'global','path':'vendor/knowledge','scope':'workplace','status':'available'}]})
    write_yaml(workplace / 'registries/knowledge-packages.yaml', {'schema_version':1,'packages':[{'id':PACKAGE_ID,'name':'Joomla Toolkit','kind':'documentation','package_root':'global','manifest_path_ref':f'{PACKAGE_ID}/package.yaml','resource_count':1}]})
    write_yaml(workplace / 'registries/installed-subjects.yaml', {'schema_version':1,'subjects':[{'id':PACKAGE_ID,'type':'knowledge_package','scope':'global','version':'1.0.0','install_path':install_path,'update_policy':{'allow_stage':True,'allow_apply':True,'install_path':install_path,'backup_before_apply':True}}]})
    write_yaml(workplace / 'registries/update-sources.yaml', {'schema_version':1,'product':'processforge','defaults':{'channel':'stable','require_https':args.remote,'require_sha256_for_download':True,'require_sha256_for_install':True},'sources':[source]})
    run('update','entity-sources','rebuild','--workplace',str(workplace))
    run('update','candidates','refresh','--workplace',str(workplace))
    no_sites = json.loads((workplace / 'runtime/update/candidates.json').read_text(encoding='utf-8'))
    assert no_sites['candidates'] == [], 'Old package unexpectedly has a source'
    # Current PF candidate discovery uses installed entity update_sites, not the
    # global bootstrap-source registry. Add only update metadata to the old package.
    baseline['update_sites'] = [copy.deepcopy(package['update_sites'][0])]
    baseline['update_sites'][0]['manifest_url'] = manifest_url
    baseline['update_sites'][0]['trust']['require_https'] = args.remote
    write_yaml(installed / 'package.yaml', baseline)
    initial_manifest = (installed / 'package.yaml').read_bytes()
    run('update','candidates','refresh','--workplace',str(workplace))
    candidates = json.loads((workplace / 'runtime/update/candidates.json').read_text(encoding='utf-8'))['candidates']
    candidates = [c for c in candidates if c.get('subject',{}).get('id') == PACKAGE_ID]
    assert len(candidates) == 1, candidates
    candidate = candidates[0]
    candidate_id = candidate['id']
    run('update','stage','--workplace',str(workplace),'--candidate',candidate_id)
    run('update','verify','--workplace',str(workplace),'--candidate',candidate_id)
    staged = [p for p in (workplace / 'runtime/update/staged').rglob('*.zip')]
    assert len(staged) == 1, staged
    intact = staged[0].read_bytes()
    assert digest(intact) == digest(artifact.read_bytes()), 'Remote/local artifact bytes differ'
    staged[0].write_bytes(intact+b'tamper')
    denied = run('update','verify','--workplace',str(workplace),'--candidate',candidate_id,ok=False)
    assert denied.returncode != 0 and ('sha256' in denied.stdout.lower() or 'checksum' in denied.stdout.lower()), denied.stdout
    staged[0].write_bytes(intact)
    run('update','verify','--workplace',str(workplace),'--candidate',candidate_id)
    denied = run('update','apply','--workplace',str(workplace),'--candidate',candidate_id,ok=False)
    assert denied.returncode != 0 and '--confirm' in denied.stdout, denied.stdout
    assert (installed/'package.yaml').read_bytes() == initial_manifest
    run('update','apply','--workplace',str(workplace),'--candidate',candidate_id,'--confirm')
    assert (installed/'package.yaml').read_bytes() == (ROOT/'package.yaml').read_bytes()
    for path in (ROOT/'resources').rglob('*.md'):
        assert (installed/path.relative_to(ROOT)).read_bytes() == path.read_bytes()
    assert not (workplace/'packages'/PACKAGE_ID).exists(), 'Receiving install path was ignored'
    run('knowledge-package-doctor','--workplace',str(workplace),'--package',PACKAGE_ID,'--package-root','global')
    # Native resource-index regeneration is checked, while keeping the shipped archive immutable.
    run('knowledge-index-refresh','--workplace',str(workplace),'--package',PACKAGE_ID,'--package-root','global','--apply')
    run('knowledge-package-doctor','--workplace',str(workplace),'--package',PACKAGE_ID,'--package-root','global')
    write_yaml(workplace/'registries/update-sources.yaml', {'schema_version':1,'product':'processforge','sources':[]})
    run('update','entity-sources','rebuild','--workplace',str(workplace))
    discovered = '\n'.join(p.read_text(encoding='utf-8') for p in (workplace/'runtime/update').glob('*sites*') if p.is_file())
    assert MANIFEST_URL in discovered, 'Installed package update site was not rediscovered'
    run('update','rollback','--workplace',str(workplace),'--candidate',candidate_id)
    assert (installed/'package.yaml').read_bytes() == initial_manifest
    # Some PF versions restore files but retain the new installed-subject version.
    state = yaml.safe_load((workplace/'registries/installed-subjects.yaml').read_text(encoding='utf-8'))
    rollback_registry_version = next(x['version'] for x in state['subjects'] if x['id']==PACKAGE_ID)
    if rollback_registry_version != '1.0.0':
        next(x for x in state['subjects'] if x['id']==PACKAGE_ID)['version'] = '1.0.0'
        write_yaml(workplace/'registries/installed-subjects.yaml', state)
    summary = {'status':'passed','transport':'public-https' if args.remote else 'local-file','package':PACKAGE_ID,
               'from_version':'1.0.0','to_version':version,'candidate_id':candidate_id,
               'checks':['no candidate before old package URL registration','discovery after URL registration','stage','SHA-256 verify','tamper rejection','confirm enforcement',
                         'apply','custom receiving install path','exact installed payload','package doctor','native index refresh',
                         'installed package URL rediscovery','rollback files'],
               'rollback_registry_version':rollback_registry_version,'fixture_registry_reconciled':True,
               'shared_workplace_modified':False}
    out=ROOT/'.pf/artifacts/initial-release'/('native-remote.json' if args.remote else 'native-local.json')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))

if __name__ == '__main__':
    main()
