import DefaultTheme from 'vitepress/theme'
import { h, onMounted, watch, nextTick } from 'vue'
import { useData, useRoute } from 'vitepress'
import CourseProgress from './components/CourseProgress.vue'
import ProgressSummary from './components/ProgressSummary.vue'
import LessonMeta from './components/LessonMeta.vue'
import ImageZoom from './components/ImageZoom.vue'
import HomePage from './components/HomePage.vue'
import StepDemo from './components/StepDemo.vue'
import Glossary from './components/Glossary.vue'
import MermaidDiagram from './components/MermaidDiagram.vue'
import {useProgress} from './progress'
import './style.css'
export default {
 extends:DefaultTheme,
 Layout:()=>h(DefaultTheme.Layout,null,{'doc-before':()=>h(LessonMeta),'doc-after':()=>h(CourseProgress),'sidebar-nav-before':()=>h(ProgressSummary),'layout-bottom':()=>h(ImageZoom)}),
 enhanceApp({app}:any){app.component('MermaidDiagram',MermaidDiagram);app.component('HomePage',HomePage);app.component('StepDemo',StepDemo);app.component('Glossary',Glossary);app.component('ProgressSummary',ProgressSummary)},
 setup(){const {frontmatter}=useData(),route=useRoute(),p=useProgress();
  const update=async(visit=false)=>{await nextTick();if(visit && frontmatter.value.course)p.visit(frontmatter.value.course);document.querySelectorAll<HTMLAnchorElement>('.VPSidebar a.link').forEach(a=>{const slug=a.pathname.split('/').pop()?.replace('.html','');a.classList.toggle('course-done',p.completed.value.includes(slug||''))});document.querySelectorAll<HTMLImageElement>('.vp-doc img:not(a img)').forEach(img=>{img.tabIndex=0;img.setAttribute('role','button');img.setAttribute('aria-label','放大查看：'+img.alt);img.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();img.click()}}})};
  onMounted(()=>{p.restore();update(true)});watch(()=>route.path,()=>update(true));watch(p.completed,()=>update(false))
 }
}
