<script setup lang="ts">
import {ref,onMounted,watch,useId} from 'vue'
import {useData} from 'vitepress'
const props=defineProps<{code:string}>(),{isDark}=useData()
const drawing=ref(''),error=ref('')
const uid=useId().replace(/[^a-z0-9]/gi,'');let counter=0
async function render(){try{const {default:mermaid}=await import('mermaid');mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:isDark.value?'dark':'neutral',fontFamily:'sans-serif'});const result=await mermaid.render('mermaid-'+uid+'-'+counter++,props.code);const doc=new DOMParser().parseFromString(result.svg,'image/svg+xml');const svg=doc.documentElement;const box=svg.getAttribute('viewBox')?.split(/\s+/).map(Number);if(box?.length===4){svg.setAttribute('width',String(box[2]));svg.setAttribute('height',String(box[3]));svg.setAttribute('style',`width:${box[2]}px;height:${box[3]}px;max-width:none`)}drawing.value=svg.outerHTML;error.value=''}catch{error.value='这张源图无法自动渲染，可展开下方 Mermaid 源码查看结构。'}}
onMounted(render);watch(isDark,render)
</script>
<template><figure class="mermaid-figure"><div v-if="drawing" class="mermaid-render" v-html="drawing" role="img" aria-label="课程流程图，可横向滚动查看" tabindex="0"/><p v-if="error" role="status">{{error}}</p><figcaption>原课程流程图 · 保留原图节点与关系</figcaption><details><summary>查看 Mermaid 源码</summary><pre>{{code}}</pre></details></figure></template>
