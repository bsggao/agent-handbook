"""Local single-user teaching store; user labels are namespaces, not authentication."""
import hashlib
import json
from pathlib import Path


class Store:
    def __init__(self, directory: Path, user: str):
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / (hashlib.sha256(user.encode()).hexdigest() + '.json')
        self.data = {'memory': {}, 'tasks': []}
        if self.path.exists():
            try:
                value = json.loads(self.path.read_text(encoding='utf-8'))
                if not isinstance(value.get('memory'), dict) or not isinstance(value.get('tasks'), list):
                    raise ValueError('invalid store shape')
                self.data = value
            except (json.JSONDecodeError, AttributeError, ValueError) as error:
                raise ValueError('本地状态文件损坏；请备份后使用 --forget，不自动覆盖。') from error

    def save(self):
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(self.path)

    def remember(self, preference: str):
        if not preference.strip() or len(preference) > 200:
            raise ValueError('偏好应为 1–200 个字符。')
        self.data['memory']['answer_style'] = preference.strip()
        self.save()

    def forget(self):
        self.data = {'memory': {}, 'tasks': []}
        self.path.unlink(missing_ok=True)

    def create_task(self, title: str, request_id: str):
        # Same explicit request ID + same action gives the same task. A new ID is a new action.
        digest = hashlib.sha256((request_id + '\0' + title).encode()).hexdigest()
        for task in self.data['tasks']:
            if task['request_hash'] == digest:
                return {**task, 'deduplicated': True}
        task = {'id': 'T' + str(len(self.data['tasks']) + 1), 'title': title, 'request_hash': digest}
        self.data['tasks'].append(task)
        self.save()
        return task
