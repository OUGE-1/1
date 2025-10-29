import json
from pathlib import Path


def jing():
    write=input("写什么")
    mingzi=input("™")

    path = Path(f'{mingzi}.json')
    a_2 = json.dumps(write)
    path.write_text(a_2)
    print("写完了")

def chu():
    json_1 =input("转换什么")
# 使用with语句自动管理文件资源
    with Path(f'{json_1}.json').open(encoding='utf-8') as f:
        data = json.load(f)  # 直接解析文件对象
        print("JSON内容:", data)
        print("翻译完成")

print("=======你要写进还是写出=====")
while True:
    w_1 =input("写进就输j，写出就输c,退出就输q")

    if w_1 =="j":
        jing()
    if w_1 =="c":
        chu()
    if w_1 =="q":
        break
    else:
        print("写进就输j，写出就输c,退出就输q")
