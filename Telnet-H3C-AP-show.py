import telnetlib
import time
import threading
from queue import Queue
user = 'itc'
password = 'h3capadmin'
threads = []
f_ip = open("IP-hw.txt")
vlan_correc_t = open("interface_counter.txt","w")
# vlan_mistake_t = open("mistake_t.txt","w")
con_not_reachable_t = open("con_not_reachable_t.txt","w")
con_other_error_t = open("con_other_error_t.txt","w")
semaphore = threading.Semaphore(5)
def ssh_session(ip_list,output_q):
    if semaphore.acquire():
        # print(threading.current_thread().getName() + "获取权限")
        try:
            host = ip_list
            # print(host)
            tn = telnetlib.Telnet(host)
            # tn.read_until(b"login")
            # tn.write(user.encode('ascii') + b'\n')
            time.sleep(5)
            tn.read_until(b"Password:")
            tn.write(password.encode('ascii') + b'\n')
            time.sleep(5)
            # tn.write(b"n \n")
            # print('已经登录交换机：' + host, end="\n")
            tn.write(b"screen-length disable \n")
            tn.write(b'dis interface | include speed  \n')
            time.sleep(3)
            output = tn.read_very_eager().decode('utf-8').replace('\r', '')
            print('正在处理 %s' %(ip_list))
            num1000 = output.count("1000Mbps-speed")
            num100 = output.count("100Mbps-speed")
            num10 = output.count("10Mbps-speed")
            down = output.count("Unknown-speed")
            # print(host + " 1G接口 %s 个"%(num1000))
            # print("100M接口 %s 个"%(num100))
            # print("10M接口 %s 个" % (num10))
            # print("down接口 %s 个" % (down))
            if num1000 > 1:
                vlan_correc_t.write(host + " 1000M %s个 " %(num1000) + "100M %s个 " %(num100) + "10M %s个 " %(num10) + "DOWN %s个 " %(down) + "\n")
        except TimeoutError:
            print(host + " 连接超时")
            con_not_reachable_t.write(host + "\n")
        except:
            # e3 = print("ip address " + host + " 访问异常，请手动telnet连接测试")
            con_other_error_t.write(host)
        semaphore.release()
        # print(threading.current_thread().getName() + "释放权限")

print (f"程序于 {time.strftime('%X')} 开始执行\n")
for ips in f_ip.readlines():
    t1 = threading.Thread(target=ssh_session,args=(ips.strip(),Queue()))
    t1.start()
    threads.append(t1)
# print(threads) # 打印线程数，测试用的
# 线程同步
for t2 in threads:
    t2.join()
print (f"\n程序于 {time.strftime('%X')} 执行结束")


f_ip.close()
vlan_correc_t.close()
con_not_reachable_t.close()
con_other_error_t.close()
# tn.close()
# vlan_c = open("vlan_correct_t.txt")
# vlan_m = open("vlan_mistake_t.txt")
# con_nr = open("con_not_reachable_t.txt")
# con_oe = open("con_other_error_t.txt")
# print("\n......下列交换机的POE配置正常..........")
# for line1 in vlan_c.readlines():
#     print(line1)
# # print("......下列交换机的POE配置异常..........")
# # for line2 in vlan_m.readlines():
# #     print(line2)
# # print("......下列交换机不可达或SSH端口没打开...")
# # for line3 in con_nr.readlines():
# #     print(line3)
# # print("......下列交换机认证账号密码错误........")
# # for line3 in con_oe.readlines():
# #     print(line3)
# vlan_c.close()
# vlan_m.close()
# con_nr.close()
# con_oe.close()
