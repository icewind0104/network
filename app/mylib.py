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

class page():
    def __init__(self, row_count, per_list, curr_page):
        self.__row_count = row_count
        self.__per_list = per_list
        self.curr_page = curr_page
        self.count = (self.__row_count + self.__per_list-1)//per_list

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
