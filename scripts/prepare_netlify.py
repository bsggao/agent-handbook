"""Preserve the current static root site and add /agent-handbook/.

Uses the authenticated Netlify CLI without reading or printing its credentials.
Fails on functions/edge functions, hash mismatches, or unexpected configuration.
The baseline deploy ID is checked again immediately before publishing.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib, json, shutil, subprocess, urllib.request, time

ROOT = Path(__file__).resolve().parents[1]
SITE_ID = '23d7fb77-075f-4327-a7c1-bc66012fd37d'
PREFIX = '/agent-handbook/'
CLI = ['npx', '--yes', 'netlify-cli@23.1.3']
WORK = ROOT / '.deploy'


def api(name, data):
    return json.loads(subprocess.check_output(CLI + ['api', name, '--data', json.dumps(data)], cwd=ROOT, text=True))


def current_site():
    site = api('getSite', {'site_id': SITE_ID})
    if site.get('custom_domain') != 'gaogaoai.cn':
        raise ValueError('The site does not own the expected domain')
    deploy = site['published_deploy']
    if deploy.get('available_functions') or deploy.get('edge_functions_present'):
        raise ValueError('The root site has functions: manual preservation review is required')
    return site


def main():
    site = current_site()
    deploy = site['published_deploy']
    # Existing route/CSP rules were compared with this repository's netlify.toml.
    # Stop if a future site introduces a build pipeline we do not control.
    if site.get('build_settings', {}).get('repo_url'):
        raise ValueError('Root site now uses Git deployment; integrate its pipeline before publishing')
    files = api('listSiteFiles', {'site_id': SITE_ID})
    if any(f['deploy_id'] != deploy['id'] for f in files):
        raise ValueError('Production changed while reading the file manifest; prepare again')
    backup = WORK / 'baseline' / deploy['id']
    backup.mkdir(parents=True, exist_ok=True)
    preserved = [f for f in files if not f['path'].startswith(PREFIX) and f['path'] != '/netlify.toml']
    if any(f['path'] in ('/_redirects', '/_headers') for f in preserved):
        raise ValueError('New root routing files require review before merging')

    def download(f):
        relative = f['path'].lstrip('/')
        if '..' in Path(relative).parts:
            raise ValueError('Unsafe baseline path')
        dest = backup / relative
        if dest.exists() and hashlib.sha1(dest.read_bytes()).hexdigest() == f['sha']:
            return
        url = deploy['deploy_ssl_url'] + f['path']
        last_error = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=90) as response:
                    data = response.read()
                if hashlib.sha1(data).hexdigest() != f['sha']:
                    raise ValueError(f'Baseline checksum mismatch: {relative}')
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
                return
            except Exception as error:
                last_error = error
                if attempt < 2:
                    time.sleep(1)
        raise last_error

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(download, preserved))
    output = WORK / 'site'
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    for f in preserved:
        relative = f['path'].lstrip('/')
        dest = output / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(backup / relative, dest)
    html = (ROOT / 'dist/index.html').read_text()
    if PREFIX + 'assets/' not in html or '<script id="check-dark-mode">' in html:
        raise ValueError('Run npm run build:production before preparing the deployment')
    shutil.copytree(ROOT / 'dist', output / PREFIX.strip('/'))
    record = {'siteId': SITE_ID, 'siteName': site['name'], 'domain': site['custom_domain'],
              'baselineDeployId': deploy['id'], 'baselineUrl': deploy['deploy_ssl_url'],
              'base': PREFIX, 'preservedFiles': preserved,
              'omittedConfigFile': '/netlify.toml (deployment settings are maintained in repository root)'}
    (WORK / 'prepared.json').write_text(json.dumps(record, indent=2) + '\n')
    page_count = len(list((ROOT / 'dist').rglob('*.html')))
    print(f'Prepared {len(preserved)} checksum-verified existing files + {page_count} tutorial pages at {PREFIX}')
    print(f'Baseline deploy: {deploy["id"]}')


if __name__ == '__main__':
    main()
