# -*- coding: utf-8 -*-
import re

# 字符串形式 --> 整数形式
def inet_pton(addr):
    if re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', addr) is None:
        return None
    res = 0
    for index, value in enumerate(addr.split('.')):
        res += (int(value) << (24-index*8))
    return res

# 整数形式 --> 字符串形式
def inet_ntop(addr):
    try:
        addr = int(addr)
    except Exception:
        return None
    res = []
    for i in range(4):
        res.append(str(addr & 255))
        addr >>= 8
    res.reverse()
    return '.'.join(res)

if __name__ == '__main__':
    print(inet_ntop(16909060))
    print(inet_pton('1.2.3.4'))
    if inet_pton('1.2.3.4') != 16909060 or inet_pton('1.1.1.1.1') is not None or inet_ntop(16909060) != '1.2.3.4':
        print('Test Failed')
    else:
        print('Test Success')
