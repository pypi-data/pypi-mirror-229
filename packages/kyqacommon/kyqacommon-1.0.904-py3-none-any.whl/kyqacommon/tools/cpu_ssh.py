import os ,sys

r=os.path.abspath(os.path.dirname(__file__))
rootpath= os.path.split(r)[0]
sys.path.append(rootpath)

import paramiko
import time
import sys
import requests

linux = ['192.168.70.207']

def connectHost(ip, uname='ubuntu', passwd='kunyitest'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=uname, password=passwd, port=22)
    return ssh

def MainCheck():
    while True:
        try:

            for a in range(len(linux)):
                ssh = connectHost(linux[a])
                # 查询主机名称
                cmd = 'hostname'
                stdin, stdout, stderr = ssh.exec_command(cmd)
                host_name = stdout.readlines()
                host_name = host_name[0]
                # 查看当前时间
                csj = 'date +%T'
                stdin, stdout, stderr = ssh.exec_command(csj)
                curr_time = stdout.readlines()
                curr_time = curr_time[0]

                # 查看cpu使用率(取三次平均值)
                cpu = "vmstat 1 3|sed  '1d'|sed  '1d'|awk '{print $15}'"
                stdin, stdout, stderr = ssh.exec_command(cpu)
                cpu = stdout.readlines()
                cpu_usage_num = (round((100 - (int(cpu[0]) + int(cpu[1]) + int(cpu[2])) / 3), 2))
                cpu_usage = str(cpu_usage_num) + '%'

                # 查看内存使用率
                mem = "cat /proc/meminfo|sed -n '1,4p'|awk '{print $2}'"
                stdin, stdout, stderr = ssh.exec_command(mem)
                mem = stdout.readlines()
                mem_total = round(int(mem[0]) / 1024)
                mem_total_free = round(int(mem[2]) / 1024)
                mem_usage_num = round(((mem_total - mem_total_free) / mem_total) * 100, 2)
                mem_usage = str(mem_usage_num) + "%"
                print(host_name, curr_time, cpu_usage, mem_usage)

                if mem_usage_num >=8:
                    t = 100
                    RESULT = "Memory"
                elif cpu_usage_num >=70:
                    t = 600
                    RESULT = "CPU"
                else:
                    RESULT = "Pass"
                    t = 10
                if int(curr_time.split(":")[0]) >= 22:
                    t = 36000
                if RESULT != "Pass":
                    if RESULT == "CPU":
                        BUILD_ERROR = f"Rtpc CPU 使用率过高：{cpu_usage_num}%"
                        Other_ = f"Rtpc Memory 使用率:{mem_usage_num}%"
                        Other_info = f"其他信息：<font color='green'>{Other_}</font>\n"
                        COLOUR = "red"
                        BUTTON_TYPE = 'primary'
                        BUILD_ERRORS = f"原因：<font color='{COLOUR}'>{BUILD_ERROR}</font>\n"
                    elif RESULT == "Memory":
                        if cpu_usage_num>=60:
                            BUILD_ERROR = f"Rtpc Memory 使用率过高：{mem_usage_num}%"
                            Other_info = f"其他信息：<font color='red'>Rtpc CPU 使用率过高：{cpu_usage_num}%</font>\n"
                            COLOUR = "red"
                            BUTTON_TYPE = 'primary'
                            BUILD_ERRORS = f"原因：<font color='{COLOUR}'>{BUILD_ERROR}</font>\n"
                        else:
                            BUILD_ERROR = f"Rtpc Memory 使用率过高：{mem_usage_num}%"
                            Other_ = f"Rtpc CPU 使用率:{cpu_usage_num}%"
                            Other_info = f"其他信息：<font color='green'>{Other_}</font>\n"
                            COLOUR = "red"
                            BUTTON_TYPE = 'primary'
                            BUILD_ERRORS = f"原因：<font color='{COLOUR}'>{BUILD_ERROR}</font>\n"

                    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    url_masters = ['https://open.feishu.cn/open-apis/bot/v2/hook/f2cf1dd9-9dcf-4779-b5d5-8dd18b8a67f5'
                                  ]
                    method = 'post'
                    headers = {
                        'Content-Type': 'application/json;charset=utf-8'
                    }
                    json2 = {
                        "msg_type": "interactive",
                        "card":
                            {
                                "config":
                                    {
                                        "wide_screen_mode": True
                                    },
                                "elements":
                                    [
                                        {
                                            "tag": "markdown",
                                            "content": f"类型：<font color='{COLOUR}'>**{RESULT} 告警**</font>\n"
                                                       f"{BUILD_ERRORS}{Other_info}时间：{current_time}\n"
                                        },
                                        {
                                            "tag": "hr"
                                        },
                                    ],
                                "header":
                                    {
                                        "template": f"{COLOUR}",
                                        "title":
                                            {
                                                "content": f"CPU Memory 告警",
                                                "tag": "plain_text"
                                            }
                                    }
                            }
                    }
                    for url_master in url_masters:
                        requests.request(method=method, url=url_master, headers=headers, json=json2)
                    print("Is runing...")
                    time.sleep(t)
                time.sleep(t)
        except:
            print("连接服务器 %s 异常" % (linux[a]))
            time.sleep(30)
            continue


if __name__ == '__main__':
    MainCheck()

