"""Publish only a prepared full-domain bundle; do not replace the root with dist."""
from pathlib import Path
import json, subprocess, sys
from prepare_netlify import ROOT, WORK, SITE_ID, CLI, current_site

prepared = json.loads((WORK / 'prepared.json').read_text())
current = current_site()['published_deploy']['id']
if prepared['siteId'] != SITE_ID or current != prepared['baselineDeployId']:
    sys.exit('Production changed since preparation. Run prepare_netlify.py again before publishing.')
production = '--prod' in sys.argv
args = CLI + ['deploy', '--no-build', '--site', SITE_ID, '--dir', str(WORK / 'site'),
              '--message', 'Add AI Agent Chinese handbook at /agent-handbook/', '--json']
if production:
    args.append('--prod')
result = json.loads(subprocess.check_output(args, cwd=ROOT, text=True))
(WORK / ('production.json' if production else 'preview.json')).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
