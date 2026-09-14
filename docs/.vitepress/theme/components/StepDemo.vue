<script setup lang="ts">
import {ref,computed,watch} from 'vue'
type Step={role:string,title:string,text:string,detail?:string}
const props=defineProps<{kind:'tools'|'rag'|'multi'}>()
const n=ref(0),scenario=ref('normal')
const labels={tools:'工具调用实验',rag:'检索与引用实验',multi:'多 Agent 协作实验'}
const data:Record<string,Step[]>={
 tools:[{role:'用户',title:'提出任务',text:'东京现在还有可预订名额吗？'}, {role:'模型输出',title:'生成工具调用请求',text:'模型只提出请求，此时没有发生查询。',detail:'{"type":"function_call","call_id":"call_01","name":"check_availability","arguments":{"destination":"Tokyo"}}'}, {role:'应用程序',title:'校验并执行',text:'工具在白名单中；destination 是允许的城市。调用本地函数，不进行真实预订。',detail:'check_availability(destination="Tokyo")'}, {role:'工具结果',title:'将结果关联到请求',text:'call_id 将本次结果与先前的请求关联。',detail:'{"call_id":"call_01","result":{"destination":"Tokyo","available":true,"remaining":1}}'}, {role:'模型输出 · 预设',title:'形成最终回答',text:'东京目前还有 1 个名额。这是模拟库存数据，尚未预订。'}],
 rag:[{role:'用户',title:'提出需要证据的问题',text:'购买后多久可以申请退款？'}, {role:'检索器',title:'检索候选片段',text:'本演示采用预设相关性分数，分数不是概率。',detail:'D1 退款政策｜0.92｜签收后 7 天内，未使用可申请。\nD2 配送指南｜0.31｜预计 3 个工作日送达。\nD3 例外条款｜0.84｜定制商品不适用一般退款政策。'}, {role:'应用程序',title:'选入上下文',text:'保留直接回答问题和限制条件的两个片段。排除配送信息。',detail:'[D1] 签收后 7 天内，未使用可申请。\n[D3] 定制商品不适用一般退款政策。'}, {role:'生成器 · 预设',title:'给出可核对的回答',text:'普通商品签收后 7 天内、未使用时可以申请退款 [D1]。定制商品不适用这一条款 [D3]。'}, {role:'检查器',title:'核对引用和边界',text:'D1 支持时间和使用条件，D3 支持例外。文档没有说明审核时长，因此不能补出“当天到账”。'}],
 multi:[{role:'用户',title:'提交跨角色任务',text:'请核对订单 A101 能否退款，并给我一份处理方案。'}, {role:'协调器',title:'分配任务与最小数据',text:'订单角色查订单，政策角色查规则；各自只收到完成任务所需的信息。',detail:'订单角色 ← {order_id:"A101"}\n政策角色 ← {category:"standard", delivered_days:3}'}, {role:'订单角色',title:'返回订单事实',text:'A101 为普通商品，签收 3 天，未使用。只读查询完成。'}, {role:'政策角色',title:'返回政策与依据',text:'根据规则 P1：签收 7 天内、未使用的普通商品可以申请退款。'}, {role:'协调器',title:'汇总并等待授权',text:'订单符合申请条件。已形成退款方案，实际付款操作需由授权用户确认。此演示没有执行退款。'}]
}
const steps=computed(()=>{
 if(scenario.value==='normal')return data[props.kind]
 if(props.kind==='tools')return [{role:'用户',title:'提出任务',text:'亚特兰蒂斯现在还有可预订名额吗？'},{role:'模型输出',title:'生成工具调用请求',text:'模型给出了不受支持的目的地，应用仍需验证。',detail:'{"name":"check_availability","arguments":{"destination":"Atlantis"}}'},{role:'应用程序',title:'拒绝执行',text:'校验发现城市不在允许集合中。返回 INVALID_ARGUMENT，不调用工具。'},{role:'最终回答 · 预设',title:'请求澄清',text:'无法查询该目的地，请选择受支持的城市。'}]
 if(props.kind==='rag')return [data.rag[0],{role:'检索器',title:'未检索到有效证据',text:'候选片段与退款规则无关，不选入上下文。'},{role:'最终回答 · 预设',title:'说明知识边界',text:'当前文档不包含退款条件，无法据此回答。请提供相关政策。'}]
 return [...data.multi.slice(0,3),{role:'政策角色',title:'查询超时',text:'协调器记录角色失败，不把缺失结果当作同意。'},{role:'协调器',title:'返回部分结果',text:'订单事实已核实，退款条件尚未核实。流程暂停并交由人工处理。'}]
})
watch([()=>props.kind,scenario],()=>n.value=0)
</script>
<template><section class="step-demo" :aria-label="labels[kind]">
 <div class="demo-heading"><div><span class="simulation-badge">模拟演示</span><h3>{{labels[kind]}}</h3></div><span>{{n}} / {{steps.length}} 步</span></div>
 <p class="demo-disclaimer">全部输入、请求与输出均为预设教学数据。这里展示应用流程，不代表模型内部推理。</p>
 <label class="demo-scenario">场景 <select v-model="scenario"><option value="normal">正常流程</option><option value="failure">{{kind==='tools'?'参数校验失败':kind==='rag'?'没有有效证据':'角色查询超时'}}</option></select></label>
 <div v-if="n===0" class="demo-empty">点击“下一步”，观察信息如何流动。</div>
 <ol class="demo-steps" aria-live="polite" aria-relevant="additions"><li v-for="(step,index) in steps.slice(0,n)" :key="scenario+index"><span class="step-index">{{index+1}}</span><div><span class="step-role">{{step.role}}</span><h4>{{step.title}}</h4><p>{{step.text}}</p><pre v-if="step.detail"><code>{{step.detail}}</code></pre></div></li></ol>
 <div class="demo-controls"><button class="primary-button" @click="n++" :disabled="n>=steps.length">{{n>=steps.length?'演示完成':'下一步 →'}}</button><button class="secondary-button" @click="n=0" :disabled="n===0">重置</button></div>
</section></template>
