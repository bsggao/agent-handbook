import { ref, computed } from 'vue'
import courses from '../../../content/courses.json'
const key = 'agent-handbook-progress-v1'
const completed = ref<string[]>([]), last = ref(''), ready = ref(false), storageError = ref(false)
function restore() {
  if (typeof window === 'undefined' || ready.value) return
  try { const data = JSON.parse(localStorage.getItem(key) || '{}'); completed.value = Array.isArray(data.completed) ? data.completed.filter((x:unknown)=>courses.some(c=>c.slug===x)) : []; last.value = courses.some(c=>c.slug===data.last) ? data.last : '' } catch { storageError.value = true }
  ready.value = true
}
function save() { try { localStorage.setItem(key, JSON.stringify({completed:completed.value,last:last.value})) } catch {storageError.value=true} }
export function useProgress() {
 return { completed,last,ready,storageError,restore,count:computed(()=>completed.value.length),
 visit(slug:string) { if(courses.some(c=>c.slug===slug)){last.value=slug;save()} },
 toggle(slug:string) {completed.value = completed.value.includes(slug) ? completed.value.filter(x=>x!==slug) : [...completed.value,slug];save()},
 clear() {completed.value=[];last.value='';save()} }
}
