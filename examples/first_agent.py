"""No-API teaching simulation: model requests are distinct from tool execution."""
import argparse
import json


def get_destinations():
    return ['Barcelona', 'Tokyo', 'Bali']


def run(max_steps=3):
    registry={'get_destinations':get_destinations}
    result=None
    for step in range(max_steps):
        if result is None:
            request={'name':'get_destinations','arguments':{}}
            print('request:',json.dumps(request))
            if request['name'] not in registry or request['arguments']:
                print('stopped: invalid_tool');return
            result=registry[request['name']](**request['arguments'])
            print('tool_result:',result)
        else:
            print('final:', '可考虑 Bali（预设教学推荐，不代表实时天气或库存）。' if 'Bali' in result else '没有可推荐目的地。')
            return
    print('stopped: step_limit')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--max-steps',type=int,default=3)
    print('模拟演示：不调用真实模型。')
    run(parser.parse_args().max_steps)
