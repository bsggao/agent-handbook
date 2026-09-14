// Exercise the production bootstrap with dynamic JavaScript compilation disabled.
import fs from 'node:fs'
import vm from 'node:vm'
import assert from 'node:assert/strict'

const base = process.env.BASE_PATH || '/'
const files = fs.readdirSync('dist/assets').filter(name => name.startsWith('bootstrap.'))
let checked = false
for (const file of files) {
  const code = fs.readFileSync(`dist/assets/${file}`, 'utf8')
  new vm.Script(code)
  if (!code.includes('window.__VP_SITE_DATA__')) continue
  const context = { window: {} }
  vm.runInNewContext(code, context, { contextCodeGeneration: { strings: false, wasm: false } })
  const data = context.window.__VP_SITE_DATA__
  assert.equal(data.base, base)
  const tokenize = data.themeConfig.search.options.miniSearch.options.tokenize
  assert.equal(typeof tokenize, 'function')
  assert.equal(JSON.stringify(tokenize('工具调用 MCP')), JSON.stringify(['工具', '具调', '调用', 'mcp']))
  assert.equal(JSON.stringify(tokenize('Agent memory')), JSON.stringify(['agent', 'memory']))
  checked = true
}
assert.ok(checked, 'No site bootstrap found')
const html = fs.readFileSync('dist/index.html', 'utf8')
for (const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)) {
  assert.ok(!match[2].trim(), 'Inline script violates the host CSP')
  assert.ok(match[1].includes(`src="${base}assets/`), 'Bootstrap escaped the base path')
}
const sitemap = fs.readFileSync('dist/sitemap.xml', 'utf8')
for (const match of sitemap.matchAll(/<loc>(.*?)<\/loc>/g)) {
  assert.ok(new URL(match[1]).pathname.startsWith(base), 'Sitemap escaped the base path')
}
console.log('PASS: script-src self compatible bootstraps, Chinese/English tokenization, base path and sitemap')
