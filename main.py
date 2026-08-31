import requests
import re
import json
import time

COOKIE_STR = "_uid=1068616; __client_id=yk63pmlibimhslfk6oo5wzn5jveyocg2c6uwbrcbjaqmqgtf; C3VK=34ef21"
headers = {"User-Agent": "curl/7.68.0", "Accept": "*/*"}
cookies = {}
for item in COOKIE_STR.split('; '):
    if '=' in item:
        k, v = item.split('=', 1)
        cookies[k] = v

# 第一步：获取记录列表
list_url = "https://www.luogu.com/record/list?pid=U719004"
resp = requests.get(list_url, headers=headers, cookies=cookies)
html = resp.text
pattern = r'window\._feInjection\s*=\s*JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)'
match = re.search(pattern, html)
if not match:
    raise Exception("未找到 _feInjection")
encoded = match.group(1)
json_str = requests.utils.unquote(encoded)
data = json.loads(json_str)
records = data['currentData']['records']['result']
print(f"共有 {len(records)} 条提交记录")

# 第二步：遍历每条记录，访问其详情页获取代码
for rec in records:
    rid = rec['id']
    username = rec['user']['name']
    status = rec['status']
    print(f"提交ID: {rid}, 用户: {username}, 状态: {status}")
    
    # 访问单个提交详情页
    detail_url = f"https://www.luogu.com/record/{rid}"
    detail_resp = requests.get(detail_url, headers=headers, cookies=cookies)
    detail_html = detail_resp.text
    
    # 提取 _feInjection
    match_detail = re.search(pattern, detail_html)
    if not match_detail:
        print(f"  无法获取提交 {rid} 的详情")
        continue
    
    encoded_detail = match_detail.group(1)
    json_str_detail = requests.utils.unquote(encoded_detail)
    detail_data = json.loads(json_str_detail)
    
    # 提取源代码
    source_code = detail_data['currentData']['record'].get('sourceCode', '')
    if not source_code:
        print(f"  提交 {rid} 没有源代码")
        continue
    
    # 注意：sourceCode 可能包含转义字符，但 json.loads 已经处理好了
    # 例如这里的源代码是 "jc hex_233\u6216tham" -> 变成 "jc hex_233或tham"
    print(f"  源代码长度: {len(source_code)}")
    print(f"  源代码预览: {source_code[:50]}...")
    
    # 保存到文件
    filename = f"{username}_{rid}.cpp"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(source_code)
    print(f"  已保存 {filename}")
    
    # 你也可以从 detail_data 中获取更多信息，比如编译结果
    detail = detail_data['currentData']['record'].get('detail', {})
    compile_result = detail.get('compileResult', {})
    if not compile_result.get('success', True):
        print(f"  编译错误: {compile_result.get('message', '')[:100]}...")
    
    time.sleep(1)  # 控制请求频率
