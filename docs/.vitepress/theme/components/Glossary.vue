<script setup lang="ts">
import {ref,computed} from 'vue'
import {withBase} from 'vitepress'
import terms from '../../../../content/glossary.json'
const query=ref('')
const filtered=computed(()=>terms.filter(t=>(t.en+' '+t.zh+' '+t.definition).toLowerCase().includes(query.value.trim().toLowerCase())))
</script>
<template><div class="glossary"><label for="term-query">按中文或英文查找术语</label><input id="term-query" v-model="query" type="search" placeholder="例如：RAG、上下文、Tool calling"/><p role="status">{{filtered.length}} 个术语</p><p v-if="!query.trim()">输入关键词筛选，或在下方浏览全部定义。</p><dl v-else><div v-for="t in filtered" :key="t.en"><dt>{{t.zh}} <span>{{t.en}}</span></dt><dd>{{t.definition}} <a :href="withBase('/lessons/'+t.lesson+'.html')">到章节学习 →</a></dd></div></dl><p v-if="!filtered.length">没有匹配的术语，试试英文缩写或更短的关键词。</p></div></template>
