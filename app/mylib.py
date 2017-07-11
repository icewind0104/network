# -*- coding: utf-8 -*-
import re, time, gzip
from urllib import request, parse

#------------------------------------------
# FUNCTION: check_mac(检查MAC合法性)
#------------------------------------------

def check_mac(mac):
    check = True
    tmp = mac.split(':')

    if len(tmp) != 6:
        check = False

    for each in mac.split(':'):
        try:
            if int(each, 16) < 0 or int(each, 16) > 255:
                check = False
        except:
            check = False

    return check

#------------------------------------------
# FUNCTION: sync2gateway(同步到网关)
#
# addr: 字符串形式的IP地址
# title: 对于改条记录的描述，一般采用使用人姓名
# mac: 对应的mac地址
#------------------------------------------

def sync2gateway(addr, opt, title=None, mac=None):
    now = int(time.time()*1000)
    ret = {'status': True, 'error': None}

    if opt == 'mod' or opt == 'add':
        title = parse.quote(title.encode('gb2312'))
        
        if not check_mac(mac):
            ret['status'] = False
            ret['error'] = 'MAC地址不合法'
        
        req = request.Request('http://192.168.0.1/arp_static.asp?n=%s&i=%s&m=%s&t=1&d=lan&opt=mod&_=%d' % (title, addr, mac, now))

    if opt == 'del':
        req = request.Request('http://192.168.0.1/arp_static.asp?n=&i=%s&m=&t=1&d=lan&opt=del&_=%d' % (addr, now))
        
    req.add_header('Cookie', 'wys_userid=admin,wys_passwd=5364728ACB0AEEFE362FD4FF6B5FA415')
    f = request.urlopen(req, timeout=30)
    
    # 检测是否写入网关
    try:
        response_text = gzip.decompress(f.read()).decode('gb2312')
    except:
        response_text = f.read().decode('gb2312')
        
    status = response_text.split(':', 1)[0]
    
    if status == '{err':
        ret['status'] = False
        ret['error'] = '网关返回错误:%s' % response_text
    
    return ret

#------------------------------------------
# FUNCTION: paging(分页)
#
# query: sqlalchemy 的 query 对象
# request: 路由函数就收的 request 对象
# row_per_page: 每页显示的条目数
# 返回: 数据库的查询结果
#------------------------------------------

def paging(query, request, rows_per_page):
    try:
        curr_page = int(request.args.get('page', 1))
        assert curr_page > 0
    except:
        curr_page = 1
    return query[(curr_page-1)*rows_per_page:(curr_page)*rows_per_page]

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

class page():
    def __init__(self, row_count, request, per_list):
        self.__row_count = row_count
        self.__per_list = per_list
        self.count = (self.__row_count + self.__per_list-1)//per_list
        
        try:
            self.curr_page = int(request.args.get('page',1))
            assert self.curr_page > 0
        except:
            self.curr_page = 1

    @property
    def previous_page(self):
        if self.curr_page > 1:
            return self.curr_page - 1
        return None

    @property
    def next_page(self):
        if self.curr_page < self.count:
            return self.curr_page + 1
        return None

    def all_page(self):
        before = 3
        after = 5
        if self.curr_page - 2 <= before:
            for i in range(1, self.curr_page):
                yield i
        else:
            yield 1
            yield '...'
            for i in range(self.curr_page - before, self.curr_page):
                yield i
        if self.count-1 - self.curr_page <= after:
            for i in range(self.curr_page, self.count):
                yield i
        else:
            for i in range(self.curr_page, self.curr_page+after+1):
                yield i
            yield '...'
        yield self.count

if __name__ == '__main__':
    if inet_pton('1.2.3.4') != 16909060 or inet_pton('1.1.1.1.1') is not None or inet_ntop(16909060) != '1.2.3.4':
        print('Test Failed')
    else:
        print('Test Success')

    for n in range(10):
        p = page(109, 10, n)
        print('----------------------------')
        for each in p.all_page():
            print(each)
