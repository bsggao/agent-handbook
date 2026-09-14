<script setup lang="ts">
import {onMounted,onUnmounted,ref,nextTick} from 'vue'
const dialog=ref<HTMLDialogElement>(),src=ref(''),alt=ref(''),zoom=ref(1)
function open(e:MouseEvent){const target=e.target as HTMLElement;if(target.tagName==='IMG' && target.closest('.vp-doc') && !target.closest('a')) {src.value=(target as HTMLImageElement).src;alt.value=(target as HTMLImageElement).alt;zoom.value=1;nextTick(()=>dialog.value?.showModal())}}
onMounted(()=>document.addEventListener('click',open));onUnmounted(()=>document.removeEventListener('click',open))
</script>
<template><dialog ref="dialog" class="image-dialog" aria-label="放大查看图片" @click="e=>{if(e.target===dialog)dialog?.close()}"><div class="zoom-controls"><button @click="zoom=Math.max(1,zoom-.5)" :disabled="zoom<=1">缩小 −</button><span>{{Math.round(zoom*100)}}%</span><button @click="zoom=Math.min(3,zoom+.5)" :disabled="zoom>=3">放大 ＋</button><button autofocus @click="dialog?.close()">关闭 ×</button></div><div class="zoom-stage" tabindex="0" aria-label="图片区域，可横向和纵向滚动"><img :src="src || undefined" :alt="alt" :style="{width:zoom*100+'%'}"/></div><p>{{alt}}</p></dialog></template>
