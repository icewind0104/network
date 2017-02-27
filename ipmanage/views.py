# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import ips, nets
from .myFunc import ip2int, int2ip, check, checkIP, checkMASK, rmZero, createUsaleIP, pageRangeConvert, mf_get_username
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
import re, base64, cgi, time
import time

# Create your views here.

error_info = {
    'overlarge': '一次批量创建的IP数量超过最大值256',
    'empty': '必填项目不能为空',
    'less': '启始IP大于结束IP',
    'format': 'IP地址输入有误',
    'exist': '该IP地址已被使用',
    'nonused': '该IP地址尚未启用',
    'incorrect': '输入用户名或密码错误。',
    'userempty': '用户名不能为空。',
    'passempty': '密码不能为空。',
}

#################################################################
#
#    login
#
#################################################################

def login(request):
    error = request.GET.get('error')

    return render(request, 'ipmanage/login.html', {'error':error_info.get(error)})

def login_deal(request):
    username=request.POST.get('username')
    password=request.POST.get('password')

    if not username: return HttpResponseRedirect(reverse('ipmanage:login')+'?error=userempty')
    if not password: return HttpResponseRedirect(reverse('ipmanage:login')+'?error=passempty')

    user = authenticate(username=username, password=password)

    if user is not None:
        auth_login(request, user)
        return HttpResponseRedirect(reverse('ipmanage:net'))
    else:
        return HttpResponseRedirect(reverse('ipmanage:login')+'?error=incorrect')

def logout_deal(request):
    logout(request)
    return HttpResponseRedirect(reverse('ipmanage:login'))

def check_login(request):
    if not request.user.is_authenticated():
        return False
    else:
        return True

#################################################################
#
#    Net
#
#################################################################
def net(request):
    if not check_login(request): return HttpResponseRedirect(reverse('ipmanage:login')) # 验证登录

    error = request.GET.get('error')

    net = nets.objects.all()[0:1]

    if len(net) == 0:
        username = mf_get_username(request)
        return render(request, 'ipmanage/nets/noNet.html', {'username':username, 'error':error_info.get(error)})
    else:
        error = ('?error=%s' % error) if error else ''
        return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net[0].id,))+error)

def net_deal_add(request):
    if not check_login(request): return HttpResponseRedirect(reverse('ipmanage:login')) # 验证登录

    name = request.POST.get('name')
    desc = request.POST.get('desc')

    if not name:
        return HttpResponseRedirect(reverse('ipmanage:net')+'?error=empty')

    if not desc: desc = None

    nets.objects.create(name=name, desc=desc).save()

    return HttpResponseRedirect(reverse('ipmanage:net'))

def net_detail(request, net_id):
    if not check_login(request): return HttpResponseRedirect(reverse('ipmanage:login')) # 验证登录

    net = get_object_or_404(nets, pk=net_id)

    error = request.GET.get('error')

    # 获取该NET下的IP总数
    IP_count = net.ips_set.count()

    # 获取网络信息，用于左侧信息栏
    Nets = []
    for e in nets.objects.all():
        count_all = e.ips_set.count()
        count_used = e.ips_set.filter(person__isnull=False).count()
        Nets.append({
            'id': e.id,
            'name': e.name,
            'desc': e.desc,
            'count_all': count_all,
            'count_used': count_used,
            'use_per': '%.2f' % (count_used/count_all*100) if count_all !=0 else '0'
        })    

    # 根据搜索条件生成IP结果集
    search_key = request.POST.get('search', request.GET.get('lsr', None))    # 如果没有新的搜索，则保持的搜索
    search_area = None
    # 搜索处理
    if search_key:
        search_key = cgi.escape(search_key)
        if re.match('[0-9.]*$', search_key):
        # search_key 满足IP地址格式，仅搜索IP地址
            all_ip = net.ips_set.values('id', 'ip_addr', 'person', 'seq', 'net_id__name').filter(ip_addr__contains=search_key)
            search_area = 'ip_addr'
        else:
        # 在使用人中搜索匹配内容
            all_ip = net.ips_set.values('id', 'ip_addr', 'person', 'seq', 'net_id__name').filter(person__contains=search_key)
            search_area = 'person'
    else:
        # 如果没有使用搜索条件则列出所有IP
        all_ip = net.ips_set.values('id', 'ip_addr', 'person', 'seq', 'net_id__name')

    # 赛选处理
    Filter = request.GET.get('filter', request.GET.get('lft', None))
    if Filter == 'all':
        Filter = None
    if Filter == 'used':
        all_ip = all_ip.filter(person__isnull=False)
    if Filter == 'nonuse':
        all_ip = all_ip.filter(person__isnull=True)

    # 排序处理
    all_ip = all_ip.order_by('seq')

    # 页码处理
    page = request.GET.get('page', request.GET.get('lpg', None))    # 如果没有浏览其他页，则保持上次选定的页数

    paginator = Paginator(all_ip, 40)
    try:
        IPs = paginator.page(page)
    except (InvalidPage, EmptyPage, PageNotAnInteger):
        page = '1'
        IPs = paginator.page(page)

    # 空结果处理
    if all_ip.count() == 0:
        IPs = []

    # 着色
    if search_key:
        try:
            for each in IPs:
                each[search_area] = each[search_area].replace(search_key, "<span>%s</span>" % search_key)
        except AttributeError:
            IPs = []

    page_range = paginator.page_range
    page_range = pageRangeConvert(page_range, int(page))  #页数集合转换为 [...,3,4,5,6,...]形式，防止页面过多

    # 保存本次查询的参数，返回给客户端，以便记忆用户筛选情况
    get_param = []
    if search_key: get_param.append('lsr=%s' % search_key)
    if page: get_param.append('lpg=%s' % page)
    if Filter: get_param.append('lft=%s' % Filter)
    get_string = '?'+'&'.join(get_param) if get_param else None

    return render(request, 'ipmanage/nets/detail.html', {
        'net':net,
        'nets':Nets,
        'IPs':IPs,
        'IP_count':IP_count,
        'page_range':page_range,
        'last_get':get_string,
        'search_key':search_key,
        'Filter':Filter,
        'username':mf_get_username(request),
        'error':error_info.get(error)
        }
    )

#def net_add(request):
#    if not check_login(request): return HttpResponseRedirect(reverse('ipmanage:login')) # 验证登录
#    return render(request, 'ipmanage/nets/add.html')

#def net_ip_detail(request, net_id, ip_id):
#    net = get_object_or_404(nets, pk=net_id)
#    IP = get_object_or_404(ips, pk=ip_id)
#    return render(request, 'ipmanage/nets/ip_detail.html', {'net':net, 'IP':IP})

#def net_deal_add(request):
# Deal the form and check avild then save to DATABASE
#
#    error = []    # 保存处理过程中发现的错误，以便反馈用户
#
#    form = request.POST
#
#    desc 	= form['description']
#    mask 	= form['mask']
#    gateway 	= form['gateway']
#
    # 检查值的正确性，通过追加空列，否则追加error信息
#    error	+= check(desc)
#    error 	+= checkMASK(mask) if mask != None else []    # mask 和 gateway 可以不填
#    error 	+= checkIP(gateway) if gateway != None else []
#
#    kw = {}
#    kw['desc'] 				= desc
#    if mask != None: 	kw['mask'] 	= rmZero(mask)
#    if gateway != None: kw['gateway'] 	= rmZero(gateway)
#
    # Without any error, then save the NETWORK and CREATE usable IPs.
#    if error == []:
#        net = nets(**kw)
#        net.save()
#
#        return HttpResponseRedirect(reverse('ipmanage:net_ip_add', args=(net.id,)))
#
#    return render(request, 'ipmanage/nets/add.html', {'error':error})

#def net_ip_add (request, net_id):
#    net = get_object_or_404(nets, pk=net_id)
#    IPs = createUsaleIP(net.mask, net.gateway)
#    return render(request, 'ipmanage/nets/ip_add.html', {'net':net, 'IPs':IPs})

#def net_deal_ip_add(request, net_id):
#    net = get_object_or_404(nets, pk=net_id)
#    IPs = createUsaleIP(net.mask, net.gateway)
#
    # 查看该网络是否已经配置可用IP，如果有则返回错误信息
#    for test in net.ips_set.all():
#        return HttpResponseRedirect(reverse('ipmanage:net_ip_add', args=(net.id,)) + '?error=exists')
#
    # 存入IP地址
#    for each_IP in IPs:
#        args = {
#            'ip_addr': each_IP,
#            'seq': ip2int(each_IP),
#        }
#        net.ips_set.create(**args).save()
#
    # 存入网关
#    args = {
#        'ip_addr': net.gateway,
#        'person': '网关 IP',
#        'seq': ip2int(net.gateway),
#    }
#    net.ips_set.create(**args).save()
#
#    return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,)))

def net_deal_ip_modify(request, net_id):
    if not check_login(request): return HttpResponseRedirect(reverse('ipmanage:login')) # 验证登录

    operate = request.POST['operate']
    ip_id = request.POST['ip_id']
    person = request.POST.get('person', None)

    net = get_object_or_404(nets, pk=net_id)
    ip = get_object_or_404(ips, pk=ip_id)

    # 处理IP地址启用
    if operate == 'use':
        if ip.person == None:
            if person == '': return  HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=empty')
            ip.person = cgi.escape(person)
            ip.save()
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,)))
        return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=exist')

    # 处理IP地址修改
    if operate == 'modify':
        if ip.person != None:
            if person == '': return  HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=empty')
            ip.person = cgi.escape(person)
            ip.save()
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,)))
        return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=nonused')

    # 处理IP地址弃用
    if operate == 'disuse':
        if ip.person != None:
            ip.person = None
            ip.save()
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,)))
        return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=nonused')

    # 处理IP地址删除
    if operate == 'delete':
        ip.delete()
        return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,)))

def net_deal_muti_modify(request, net_id):
    if not check_login(request): return HttpResponseRedirect(reverse('ipmanage:login')) # 验证登录

    operate = request.POST['operate']
    net = get_object_or_404(nets, pk=net_id)

    # 处理IP批量添加
    if operate == 'muti_add':
        start_addr = request.POST.get('start', None)
        end_addr = request.POST.get('end', None)

        error = []

        if not end_addr: end_addr = start_addr    #处理结束IP留空的情况

        if not start_addr:
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=empty')

        if checkIP(start_addr) or checkIP(end_addr):
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=format')

        int_start_addr = ip2int(start_addr)
        int_end_addr = ip2int(end_addr)

        if int_start_addr > int_end_addr:
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=less')

        if (int_end_addr + 1) - int_start_addr > 256:
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=overlarge')

        used_list = [x['seq'] for x in net.ips_set.values('seq').filter(seq__gte=int_start_addr).filter(seq__lte=int_end_addr)]

        for i in range(int_start_addr, int_end_addr+1):
            if i not in used_list:
                net.ips_set.create(ip_addr=int2ip(i), seq=i, add_date=time.time()).save()

        return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,)))


    # 处理IP批量删除
    if operate == 'muti_delete':
        start_addr = request.POST.get('start')
        end_addr = request.POST.get('end')

        if not end_addr: end_addr = start_addr

        if not start_addr:
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=empty')

        if checkIP(start_addr) or checkIP(end_addr):
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=format')

        int_start_addr = ip2int(start_addr)
        int_end_addr = ip2int(end_addr)

        if int_start_addr > int_end_addr:
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=less')

        for IP in net.ips_set.filter(seq__gte=int_start_addr).filter(seq__lte=int_end_addr):
            IP.delete()

        return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,)))

def net_deal_net_modify(request):
    if not check_login(request): return HttpResponseRedirect(reverse('ipmanage:login')) # 验证登录

    operate = request.POST['operate']
    net_id = request.POST.get('net_id')
    name = request.POST.get('name', None)
    desc = request.POST.get('desc', None)
    net = get_object_or_404(nets, pk=net_id)

    # 处理修改操作
    if operate == 'modify':
        if not name:
            return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,))+'?error=empty')

        if not desc:
            desc = None

        net.name = name
        net.desc = desc

        net.save()

        return HttpResponseRedirect(reverse('ipmanage:net_detail', args=(net.id,)))

    # 处理删除操作
    if operate == 'delete':
        net.delete()

        return HttpResponseRedirect(reverse('ipmanage:net'))





    







