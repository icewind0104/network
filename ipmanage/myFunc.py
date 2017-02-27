#
# 自定义工具函数
# -*- coding: utf-8 -*-

#################################
# 将IP地址和整数形式互相转换
#################################
def ip2int(ipstr):
    r = 0
    for each in ipstr.split('.'):
        r *= 256
        r += int(each)
    return r

def int2ip(num):
    segment = []
    for i in range(4):
        segment.insert(0, str(num % 256))
        num //= 256
    return '.'.join(segment)

#################################
# 基本检测
#################################
def check(string):
    if string == '':
        error = ['该项不能为空']
        return error
    return []

#################################
# 检测IP地址合法性
#################################
def checkIP(ipstr):
    '''
    检查IP地址合法性，检查通过返回空列表，检查失败返回错误信息列表。
    '''
    error = []

    error += check(ipstr)
    if error != []:
        return error

    if len(ipstr.split('.')) != 4:
        error.append('错误的IP地址长度: %s' % ipstr)

    for each in ipstr.split('.')[:4]:
        try:
            int(each)
            if int(each) < 0 or int(each) > 255:
                error.append('IP地址超出合法范围: (%s)' % each)
        except Exception:
            error.append('IP地址包含无法处理的字符: (%s)' % each)
    return error

#################################
# 检测mask地址合法性
#################################
def checkMASK(maskstr):
    '''
    检查掩码合法性，检查通过返回空列表，检查失败返回错误信息列表。
    '''
    error = []

    error += check(maskstr)
    if error != []:
        return error

    if len(maskstr.split('.')) != 4:
        error.append('错误的掩码长度: %s' % maskstr)

    #掩码4个段以从右到左的顺序，遇到第一个非255的段为准，之前必须全为255,之后必须全为0
    FindNone255 = False   #表示是否已经遇到这个非255的段
    for each in maskstr.split('.')[:4]:

        #检测是否为数字
        try:
            int(each)
        except Exception:
            error.append('掩码包含无法处理的字符: (%s)' % each)
            return error

        #检测是否符合MASK格式
        if FindNone255 == False:
            if each == '255':
                continue
            else:
                FindNone255 == True
                if ( 256-int(each) ) not in [2, 4, 8, 16, 32, 64, 128, 256]:
                    error.append('不是合法的掩码')
        else:
            if each != 0:
                error.append('掩码格式错误')
                return error

    return error

#################################
# 规范化IP地址，消除不必要的0
#################################
def rmZero(ipstr):
    return '.'.join([ str(int(each)) for each in ipstr.split('.') ])

#################################
# 根据掩码和网关创建IP地址
#################################
# 算法：将mask转化为整数，与 255**4+1 相减，得到网段可容纳IP地址数(block)。
# 网络地址（or 第一个地址） = 整数型网关 - 整数型网关 % block
# 可用地址 = 第一个地址及之后的(block-1)个地址
def createUsaleIP(mask, gateway):
    int_mask = ip2int(mask)
    int_gateway = ip2int(gateway)

    # 计算 block 和 第一个可用地址
    block = 4294967296 - int_mask
    int_net_IP = int_gateway - (int_gateway % block)

    IPs = []
    for ip in range(int_net_IP + 1, int_gateway):
        IPs.append( int2ip(ip) )
    for ip in range(int_gateway + 1, int_net_IP + block - 1):
        IPs.append( int2ip(ip) )

    return IPs

#################################
# 页数集合转换, [1,2,3,4,5] 转换为 [...,3,4,5,6,...]，以防止页面过多
#################################  
def pageRangeConvert(page_range, page, fr=2, br=2):
    max_page = len(page_range)
    min_page = 1
    pageRange = list(page_range)

    rest 	= 0
    left 	= fr - (page - min_page)
    right 	= br - (max_page - page)

    if left > 0: rest += left
    if right > 0: rest += right

    if left < 0 and rest > 0: fr += rest
    if right < 0 and rest > 0: br += rest

    if page - fr > min_page:
        pageRange = pageRange[page-fr-1:]
        pageRange.insert(0, '...')

    if page + br < max_page:
        pageRange = pageRange[:page+br-max_page]
        pageRange.append('...')

    return pageRange

#################################
# 获取用户名，截取过长的部分
################################# 

def mf_get_username(request, lengh=6):
    return request.user.username if len(request.user.username) <= lengh else request.user.username[:8]+'...'









