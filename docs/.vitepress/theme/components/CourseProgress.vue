<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useData } from 'vitepress'
import { useProgress } from '../progress'
const {frontmatter} = useData()
const p=useProgress()
onMounted(p.restore)
const slug = computed(()=>frontmatter.value.course as string | undefined)
</script>
<template>
<section v-if="slug" class="lesson-complete" aria-label="学习进度">
 <div><strong>读完了，也动手试过了吗？</strong><p>标记完成，记录自己的学习节奏。进度仅保存在当前浏览器。</p></div>
 <button class="primary-button" @click="p.toggle(slug)" :aria-pressed="p.completed.value.includes(slug)">{{p.completed.value.includes(slug) ? '✓ 已完成 · 取消标记' : '标记本章完成'}}</button>
 <p v-if="p.storageError.value" role="status">浏览器存储不可用，本次进度只能保留到关闭页面。</p>
</section>
</template>
