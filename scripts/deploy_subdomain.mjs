// Reuse the pinned CLI's normal authentication; never print or persist credentials.
// Buffer uploads provide Content-Length, with bounded retries for unreliable networks.
import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'

const cliEntry = fs.realpathSync(process.argv[2])
const cliRoot = path.dirname(path.dirname(cliEntry))
const cliPackage = JSON.parse(fs.readFileSync(path.join(cliRoot, 'package.json'), 'utf8'))
if (cliPackage.name !== 'netlify-cli' || cliPackage.version !== '23.1.3') throw new Error('Expected netlify-cli 23.1.3')
const require = createRequire(cliEntry)
const { NetlifyAPI } = await import(pathToFileURL(require.resolve('@netlify/api')).href)
const { getToken } = await import(pathToFileURL(path.join(cliRoot, 'dist/utils/command-helpers.js')).href)
const [token] = await getToken()
if (!token) throw new Error('Run netlify login first')
const api = new NetlifyAPI(token)
const siteId = '8d299a49-c6e9-48f5-880f-4ce6fdd2096d'
const domain = 'agent-handbook.gaogaoai.cn'
const site = await api.getSite({ siteId }, { signal: AbortSignal.timeout(30000) })
if (site.custom_domain !== domain) throw new Error('Unexpected domain binding; stopped')
const root = path.resolve('dist')
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8')
if (!html.includes('src="/assets/bootstrap.') || html.includes('src="/agent-handbook/assets/')) throw new Error('Run npm run build:subdomain first')
if (!fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8').includes(`https://${domain}/`)) throw new Error('Sitemap is for a different domain')
const entries = []
function walk(dir) {
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const file = path.join(dir, item.name)
    if (item.isDirectory()) walk(file)
    else entries.push([path.relative(root, file).split(path.sep).join('/'), file])
  }
}
walk(root)
entries.push(['netlify.toml', path.resolve('deploy/subdomain.toml')])
const files = {}, byHash = new Map()
for (const [name, file] of entries) {
  const hash = crypto.createHash('sha1').update(fs.readFileSync(file)).digest('hex')
  files[name] = hash
  byHash.set(hash, [name, file])
}
// Always upload a draft first. Publish only after every required file is present.
const deploy = await api.createSiteDeploy({ siteId, body: { files, draft: true, async: false } }, { signal: AbortSignal.timeout(90000) })
fs.mkdirSync('.deploy', { recursive: true })
fs.writeFileSync('.deploy/subdomain-upload.json', JSON.stringify({ deployId: deploy.id, siteId, files, required: deploy.required }, null, 2))
console.log(`Draft ${deploy.id}: ${deploy.required.length} files to upload`)
let completed = 0
const pending = [...deploy.required]
async function worker() {
  while (pending.length) {
    const hash = pending.shift()
    const [name, file] = byHash.get(hash)
    let uploaded = false
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        await api.uploadDeployFile({ deployId: deploy.id, path: encodeURI(name), body: fs.readFileSync(file) }, { signal: AbortSignal.timeout(120000) })
        uploaded = true
        break
      } catch (error) {
        console.log(`Retry ${attempt}: ${name} (${error.name})`)
      }
    }
    if (!uploaded) throw new Error(`Failed to upload ${name}; draft remains unpublished`)
    if (++completed % 25 === 0) console.log(`Uploaded ${completed}/${deploy.required.length}`)
  }
}
await Promise.all(Array.from({ length: 5 }, worker))
let ready
for (let attempt = 0; attempt < 60; attempt++) {
  const state = await api.getSiteDeploy({ siteId, deployId: deploy.id }, { signal: AbortSignal.timeout(15000) })
  if (state.state === 'ready') { ready = state; break }
  if (state.state === 'error') throw new Error(state.error_message)
  await new Promise(resolve => setTimeout(resolve, 2000))
}
if (!ready) throw new Error('Draft processing timeout; no production change made')
const fresh = await api.getSite({ siteId }, { signal: AbortSignal.timeout(30000) })
if (fresh.published_deploy?.id !== site.published_deploy?.id) throw new Error('Production changed during upload; stopped before publishing')
await api.restoreSiteDeploy({ siteId, deployId: deploy.id }, { signal: AbortSignal.timeout(30000) })
const result = { siteId, deployId: deploy.id, domain, url: `https://${domain}/`, fallbackUrl: 'https://gaogao-agent-handbook.netlify.app/', deployUrl: ready.deploy_ssl_url }
fs.writeFileSync('.deploy/subdomain-production.json', JSON.stringify(result, null, 2) + '\n')
console.log(JSON.stringify(result, null, 2))
