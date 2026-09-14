"""Five-stage document Q&A / task assistant. Default model is an explicit simulation."""
import argparse
import hashlib
import json
import time
from pathlib import Path

from retrieval import search, select_context
from storage import Store


class PolicyError(Exception):
    pass


class Executor:
    """Application executes allowlisted tools; model requests never execute themselves."""
    def __init__(self, store: Store, *, approved=False, max_calls=4, request_id='demo', stage=5):
        self.store, self.approved = store, approved
        self.max_calls, self.request_id, self.stage = max_calls, request_id, stage
        self.calls = 0
        self.events = []
        self.started = time.monotonic()

    def execute(self, name: str, arguments: dict):
        if self.calls >= self.max_calls:
            raise PolicyError('LIMIT_REACHED：达到工具调用上限')
        if time.monotonic() - self.started > 10:
            raise PolicyError('DEADLINE：本地流程时间预算耗尽')
        allowed = {'task_count', 'create_task'}
        if self.stage >= 3:
            allowed.add('search_docs')
        if name not in allowed:
            raise PolicyError('UNKNOWN_TOOL：工具不在白名单中')
        if not isinstance(arguments, dict):
            raise PolicyError('INVALID_ARGUMENT：参数必须是对象')
        required = {'search_docs': {'query'}, 'create_task': {'title'}, 'task_count': set()}[name]
        if set(arguments) != required:
            raise PolicyError('INVALID_ARGUMENT：字段不符合 Schema')
        for value in arguments.values():
            if not isinstance(value, str) or not value.strip() or len(value) > 500:
                raise PolicyError('INVALID_ARGUMENT：输入应为 1–500 字符的字符串')
        if name == 'create_task' and not self.approved:
            raise PolicyError('APPROVAL_REQUIRED：尚未授权创建任务')
        self.calls += 1
        # Store only names/counts and a digest; no raw question or memory in application events.
        digest = hashlib.sha256(json.dumps(arguments, sort_keys=True).encode()).hexdigest()[:12]
        if name == 'search_docs':
            result = search(arguments['query'])
        elif name == 'task_count':
            result = {'count': len(self.store.data['tasks'])}
        else:
            result = self.store.create_task(arguments['title'], self.request_id)
        self.events.append({'event': 'tool_completed', 'tool': name, 'arguments_digest': digest})
        return result


class SimulatedModel:
    """An explicit finite rule set. Does not perform LLM inference."""
    def propose(self, question: str, stage: int):
        if stage == 1:
            return None
        if question.startswith('创建任务：'):
            return {'name': 'create_task', 'arguments': {'title': question.split('：', 1)[1].strip()}}
        if '任务' in question and ('多少' in question or '几个' in question):
            return {'name': 'task_count', 'arguments': {}}
        if stage >= 3:
            return {'name': 'search_docs', 'arguments': {'query': question}}
        return None


def run(question: str, stage=5, directory=Path('.assistant-data'), user='learner', approved=False,
        request_id='demo', budget=600, max_calls=4):
    if not isinstance(question, str) or not question.strip() or len(question) > 500:
        raise ValueError('问题应为 1–500 字符。')
    if stage not in range(1, 6) or budget < 0 or max_calls < 0:
        raise ValueError('阶段、上下文预算或调用次数无效。')
    store = Store(directory, user)
    executor = Executor(store, approved=approved, max_calls=max_calls, request_id=request_id, stage=stage)
    request = SimulatedModel().propose(question, stage)
    response = {'mode': '模拟演示：预设规则模型，不调用 API', 'stage': stage, 'citations': [], 'events': []}
    try:
        if request is None:
            response['answer'] = '我是一个教学用模拟助手。当前阶段还不能检索你的文档。'
        else:
            result = executor.execute(request['name'], request['arguments'])
            if request['name'] == 'search_docs':
                selected = select_context(result, budget)
                response['candidates'] = [{'id': d['id'], 'score': d['score']} for d in result]
                response['context_ids'] = [d['id'] for d in selected]
                response['citations'] = response['context_ids']
                # Evidence is quoted exactly; no invented refund claims or internal reasoning.
                response['answer'] = '\n'.join(f"{d['text']} [{d['id']}]" for d in selected) or '当前文档没有足够证据回答，请补充相关材料。'
            elif request['name'] == 'task_count':
                response['answer'] = f"当前有 {result['count']} 个任务。"
            else:
                response['answer'] = f"已创建本地任务 {result['id']}：{result['title']}"
                response['task'] = result
        if stage >= 4:
            response['memory'] = store.data['memory']
            if '简洁' in store.data['memory'].get('answer_style', ''):
                # Presentation changes; do not silently drop citation-bearing facts.
                response['answer'] = response['answer'].replace('\n', ' ')
    except PolicyError as error:
        response['answer'] = str(error)
        response['status'] = 'stopped'
        executor.events.append({'event': 'policy_stop', 'code': str(error).split('：')[0]})
    response['events'] = executor.events
    response['tool_calls'] = executor.calls
    return response


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('question', nargs='?', default='购买后多久可以申请退款？')
    parser.add_argument('--stage', type=int, choices=range(1, 6), default=5)
    parser.add_argument('--data-dir', type=Path, default=Path('.assistant-data'))
    parser.add_argument('--user', default='learner')
    parser.add_argument('--approve', action='store_true', help='明确授权本次本地任务创建')
    parser.add_argument('--request-id', default='demo')
    parser.add_argument('--remember', help='显式保存回答偏好（阶段4及以后）')
    parser.add_argument('--forget', action='store_true', help='清除该用户标签下的本地记忆和任务')
    parser.add_argument('--budget', type=int, default=600, help='文档上下文字符预算，不是 Token')
    parser.add_argument('--max-calls', type=int, default=4)
    args = parser.parse_args()
    try:
        if args.forget:
            # Recover even if the store is malformed, only targeting the explicit user namespace.
            path = args.data_dir / (hashlib.sha256(args.user.encode()).hexdigest() + '.json')
            path.unlink(missing_ok=True)
            print('已清除该用户的本地记忆和任务。')
            return
        if args.remember:
            if args.stage < 4:
                raise ValueError('记忆功能从阶段 4 开始。')
            Store(args.data_dir, args.user).remember(args.remember)
        result = run(args.question, args.stage, args.data_dir, args.user, args.approve,
                     args.request_id, args.budget, args.max_calls)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        parser.exit(2, f'运行失败：{error}\n')


if __name__ == '__main__':
    main()
