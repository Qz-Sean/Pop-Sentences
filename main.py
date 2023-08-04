from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import random
import html

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)

def filter_input(input_str):
    # 过滤用户输入，只保留合法字符
    return ''.join(char for char in input_str if char.isalnum() or char in ['_', '-', ' '])

def get_random_item_with_replacement(search_term, replace_term, data_list):
    random_item = random.choice(data_list)
    replaced_item = random_item.replace(search_term, replace_term)
    return replaced_item

@app.route('/', methods=['GET'])
def hello_world():
    return 'hello, world'

@app.route('/fd', methods=['GET'])
@limiter.limit("10 per second")  # 使用key_func装饰器设置速率限制
def process_request():
    msg = request.args.get('msg')
    full_msg = request.full_path  # 获取完整的请求消息

    # 检查是否包含type=json字符串，并提取出来
    response_type = 'string'
    if 'type=json' in full_msg.lower():
        response_type = 'json'

    if msg:
        # 过滤用户输入，防止恶意输入和木马代码
        filtered_msg = filter_input(msg)
        filtered_msg  = filtered_msg.rstrip('typejson')
        # 转义用户输入，防止XSS攻击
        escaped_msg = html.escape(filtered_msg)

        search_term = '<name>'  # 将此处替换为您想要替换的固定词语
        replace_term = escaped_msg

        file_path = './psycho.json'  # JSON文件的路径

        with open(file_path, 'r', encoding='utf-8') as file:
            data_list = json.load(file)

        response = get_random_item_with_replacement(search_term, replace_term, data_list)

        if response_type == 'json':
            response_str = json.dumps({'response': response}, ensure_ascii=False)
            return response_str, 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            return response.replace(search_term, msg).encode('utf-8')

    else:
        return '请提供msg参数作为请求。'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
