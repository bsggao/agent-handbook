<script setup lang="ts">
import {computed} from 'vue'
import {useData} from 'vitepress'
import courses from '../../../../content/courses.json'
const {frontmatter}=useData()
const course=computed(()=>courses.find(c=>c.slug===frontmatter.value.course))
</script>
<template><div v-if="course" class="lesson-meta"><span>CHAPTER {{course.id}}</span><span>{{course.group}}</span><span>建议 {{course.minutes}} 分钟 + 动手练习</span></div></template>
