
from netmiko import Netmiko
from tabulate import tabulate
import threading
from textfsm import TextFSM
from queue import Queue
semaphore = threading.Semaphore(10)

result_file = open('contain.txt', 'w')
ip_list = open('ip_addresses')

threads = []
except_list = []


def ssh_session(ip_list, output_q):
    if semaphore.acquire():
        try:
            print(threading.current_thread().getName() + " got permissions")
            device = {"device_type":'huawei_telnet', "ip": ip_list, "username": "xx",
                      "password": "xxx", }
            net_connect = Netmiko(**device)
            # print(net_connect.find_prompt())
            others = '\n' + 'hostip ' + ip_list + '\n' + net_connect.find_prompt() + '\n'
            net_connect.send_command('screen-length 0 temporary')
            command = 'display transceiver diagnosis interface'
            output = others + net_connect.send_command(command, strip_command=False)
            result_file.write(output)
        # except TimeoutError:
        #     cc = ('%s is unreachable' % ip_list)
        #     except_list.append(cc)
        except Exception as e:
            dd = str(e) + ip_list
            except_list.append(dd)
        semaphore.release()
        print(threading.current_thread().getName() + " released permissions")


for ip in ip_list.readlines():
    t1 = threading.Thread(target=ssh_session, args=(ip, Queue()))
    t1.start()
    threads.append(t1)
for t2 in threads:
    t2.join()
result_file.close()
result_list = []
with open('contain.txt') as r, open('display_transceiver_hw_template') as f:
    re_table = TextFSM(f)
    header = re_table.header
    result = r.read()
    for i in re_table.ParseText(result):
        result_list.append(i)
print(tabulate(result_list, header))
print('\n'.join(except_list))
result_file.close()
