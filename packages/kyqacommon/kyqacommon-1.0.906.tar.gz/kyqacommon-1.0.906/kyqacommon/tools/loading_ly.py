import time
import os ,sys

r=os.path.abspath(os.path.dirname(__file__))
rootpath= os.path.split(r)[0]
sys.path.append(rootpath)

from progress.bar import Bar

def loading(msg ="正在加载:",end_msg="加载完成!", t=0.03):
    bar = Bar(msg, max=100, fill="█", empty_fill="⣿", suffix="%(percent)d%%", width=30)
    with bar:
        for i in range(100):
            bar.next()
            time.sleep(t)
    print(end_msg)