import { defineConfig } from 'vitepress'
import courses from '../../content/courses.json'
const base = process.env.BASE_PATH || '/'
const groups = [...new Set(courses.map(c => c.group))]
// 同一个分词器用于构建索引和浏览器查询；中文双字切分避免整句才可命中。
function tokenize(text: string) {
  const words = text.toLowerCase().match(/[a-z0-9_]+|[\u3400-\u9fff]+/g) || []
  return words.flatMap(w => /[\u3400-\u9fff]/.test(w) ? w.length === 1 ? [w] : Array.from({length:w.length-1}, (_,i)=>w.slice(i,i+2)) : [w])
}
export default defineConfig({
  title: 'AI Agent 中文学习指南', lang: 'zh-CN', base,
  description: '从入门到工程实践：基于微软开源课程整理的非官方中文学习指南，含完整课程、Python 代码导读和无需 API 的交互实验。',
  outDir: '../dist', cleanUrls: false,
  sitemap: { hostname: new URL(base, process.env.SITE_URL || 'http://localhost:4173').href, transformItems: items => items.filter(i => i.url !== '404.html') },
  head: [['link', {rel:'icon', type:'image/svg+xml', href:base+'favicon.svg'}],['meta',{name:'theme-color',content:'#2563eb'}]],
  markdown: {lineNumbers:true, image:{lazyLoading:true}, config(md) {
    // 导入的课程可能含泛型、模板和原始 HTML；正文当作 Markdown 处理以防执行上游标签。
    const linkOpen = md.renderer.rules.link_open!
    md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
      const href = tokens[idx].attrGet('href') || ''
      if (href.startsWith('/notebooks/') && href.endsWith('.ipynb')) {
        tokens[idx].attrSet('download', '')
        tokens[idx].attrSet('href', base + href.slice(1))
      }
      return linkOpen(tokens,idx,options,env,self)
    }
    const fence = md.renderer.rules.fence!
    md.renderer.rules.fence = (tokens, idx, options, env, self) => {
      if (tokens[idx].info.trim() === 'mermaid') {
        const code = JSON.stringify(tokens[idx].content).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        return `<MermaidDiagram :code="${code}" />`
      }
      return fence(tokens,idx,options,env,self)
    }
    const original = md.renderer.rules.image!
    md.renderer.rules.image = (tokens, idx, options, env, self) => {
      tokens[idx].attrSet('loading','lazy')
      return original(tokens,idx,options,env,self)
    }
  }},
  themeConfig: {
    skipToContentLabel:'跳到正文',
    logo: '/favicon.svg', siteTitle: 'AI Agent 中文学习指南',
    nav:[{text:'课程',link:'/guide/courses'},{text:'学习路线',link:'/guide/roadmap'},{text:'术语表',link:'/guide/glossary'},{text:'综合实践',link:'/guide/project'}],
    sidebar: groups.map(group=>({text:group,collapsed:false,items:courses.filter(c=>c.group===group).map(c=>({text:`${c.id}  ${c.title}`,link:`/lessons/${c.slug}`}))})).concat([{text:'学习资源',collapsed:false,items:[{text:'术语表',link:'/guide/glossary'},{text:'常见问题与排错',link:'/guide/faq'},{text:'综合实践项目',link:'/guide/project'},{text:'来源、覆盖与版本',link:'/guide/sources'}]}]),
    outline:{level:[2,3],label:'本页目录'},
    search:{provider:'local',options:{miniSearch:{options:{tokenize},searchOptions:{prefix:true,fuzzy:0.1}},translations:{button:{buttonText:'搜索课程',buttonAriaLabel:'搜索全部课程正文'},modal:{displayDetails:'显示详细列表',resetButtonTitle:'清除搜索',backButtonTitle:'关闭搜索',noResultsText:'没有找到相关内容',footer:{selectText:'选择',navigateText:'切换',closeText:'关闭'}}}}},
    docFooter:{prev:'上一章',next:'下一章'}, returnToTopLabel:'返回顶部',sidebarMenuLabel:'课程导航',darkModeSwitchLabel:'主题',lightModeSwitchTitle:'切换浅色模式',darkModeSwitchTitle:'切换深色模式',
    notFound:{title:'这一页走丢了',quote:'可以回到课程目录，继续你的学习旅程。',linkLabel:'返回首页',linkText:'返回首页'},
    footer:{message:'基于 Microsoft AI Agents for Beginners · 非官方中文学习版',copyright:'原课程 © Microsoft Corporation · MIT License'}
  }
})
