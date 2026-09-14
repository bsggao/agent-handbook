<script setup lang="ts">
import {onMounted,ref,computed} from 'vue'
import {withBase} from 'vitepress'
import {useProgress} from '../progress'
import courses from '../../../../content/courses.json'
const p=useProgress(), confirmClear=ref(false)
onMounted(p.restore)
const current=computed(()=>courses.find(c=>c.slug===p.last.value))
</script>
<template><aside class="progress-summary" aria-label="我的学习进度">
 <span class="eyebrow">我的学习进度</span><strong>{{p.count.value}} <span>/ {{courses.length}} 章</span></strong>
 <progress :value="p.count.value" :max="courses.length" aria-label="已完成章节"/>
 <a v-if="current" :href="withBase('/lessons/'+current.slug+'.html')">继续：{{current.title}} →</a><a v-else :href="withBase('/lessons/setup.html')">开始第一章 →</a>
 <button v-if="p.count.value || p.last.value" class="text-button" @click="confirmClear=!confirmClear">清除学习进度</button>
 <div v-if="confirmClear" class="clear-confirm"><p>清除本设备的完成标记和上次阅读位置？</p><button @click="p.clear();confirmClear=false">确认清除</button><button @click="confirmClear=false">保留</button></div>
</aside></template>
