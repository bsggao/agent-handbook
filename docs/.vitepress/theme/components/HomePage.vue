<script setup lang="ts">
import {computed,onMounted} from 'vue'
import {withBase} from 'vitepress'
import courses from '../../../../content/courses.json'
import {useProgress} from '../progress'
const p=useProgress();onMounted(p.restore)
const groups=[...new Set(courses.map(c=>c.group))]
const resume=computed(()=>'/lessons/'+(p.last.value || 'setup')+'.html')
</script>
<template><div class="home-page">
 <section class="home-intro">
  <div><p class="eyebrow">开源课程 · 中文精读 · 动手实践</p><h1>理解 Agent，<br/>从原理走到实践。</h1><p class="intro-copy">一份可以一步步读完、亲手做出来的学习指南。<br class="desktop-only"/>从第一次工具调用，到有记忆、可评估的 AI 助手。</p>
  <div class="hero-actions"><a class="primary-button" :href="withBase('/lessons/setup.html')">开始学习 <span aria-hidden="true">→</span></a><a class="secondary-button" :href="withBase(resume)">继续上次学习</a></div>
  <p class="source-note">基于微软 AI Agents for Beginners · 非官方中文学习版</p></div>
  <aside class="learning-map" aria-label="Agent 基本工作流程"><span class="eyebrow">学习的起点</span><div class="map-goal"><span>01</span> 接收目标 <small>“用文档回答我的问题”</small></div><div class="map-line" aria-hidden="true">↓</div><div class="map-middle"><div><span>02</span> 选择行动<br/><small>模型生成工具请求</small></div><div><span>03</span> 获取证据<br/><small>应用检索并返回结果</small></div></div><div class="map-line" aria-hidden="true">↓</div><div class="map-goal"><span>04</span> 检查与回答 <small>不足则重试，超限则停止</small></div><p>模型 + 工具 + 状态 + 可控的执行循环</p></aside>
 </section>
 <section class="home-stats" aria-label="课程概览"><div><strong>{{courses.length}}</strong><span>章系统课程（含准备篇）</span></div><div><strong>3</strong><span>个免 API 交互实验</span></div><div><strong>5</strong><span>步完成一个综合项目</span></div><div><strong>Python</strong><span>保留原课程代码与框架</span></div></section>
 <section class="home-route"><div><span class="eyebrow">不必一次学完</span><h2>先跑通一个小循环，再逐步扩展。</h2></div><a :href="withBase('/guide/roadmap.html')">查看零基础学习路线 →</a><ol><li><b>建立直觉</b><span>准备环境 · 理解 Agent</span></li><li><b>让它行动</b><span>工具调用 · 文档检索</span></li><li><b>让它可靠</b><span>规划协作 · 上下文与记忆</span></li><li><b>完成项目</b><span>执行限制 · 评估与部署</span></li></ol></section>
 <section class="home-curriculum"><div class="section-heading"><div><span class="eyebrow">课程目录</span><h2>你的 Agent 工程学习手册</h2></div><span>{{p.count.value}} / {{courses.length}} 章已完成</span></div>
 <div v-for="(group,index) in groups" :key="group" class="course-group"><header><span class="group-number">0{{index+1}}</span><h3>{{group}}</h3><p>{{['从基础概念建立共同语言','用明确的输入、行动与反馈组织任务','让应用具备证据、记忆和工程保障','扩展执行环境，守住系统边界'][index]}}</p></header><div class="course-list"><a v-for="c in courses.filter(c=>c.group===group)" :key="c.id" :href="withBase('/lessons/'+c.slug+'.html')"><span class="course-number">{{p.completed.value.includes(c.slug)?'✓':c.id}}</span><div><b>{{c.title}}</b><p>{{c.summary}}</p></div><span class="course-time">{{c.minutes}} 分钟</span><span aria-hidden="true">↗</span></a></div></div>
 </section>
 <section class="practice-banner"><div><span class="eyebrow">扩展实践</span><h2>做一个文档问答与任务助手</h2><p>从确定性的本地模拟开始，逐步加入工具、检索、记忆和评估。<br/>每一步都能运行，每一步都有验收方法。</p></div><a class="primary-button" :href="withBase('/guide/project.html')">进入综合实践 →</a></section>
 <p class="home-footnote">阅读和交互演示无需账号或 API Key。可选云端实验需要相应服务权限，可能产生费用。<a :href="withBase('/guide/sources.html')">查看来源与验证范围</a></p>
</div></template>
