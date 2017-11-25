# -*- coding: utf-8 -*-
from app import app, models, mylib, db, lm
from flask import render_template, flash, redirect, url_for, g, request, session
from app.forms import Net, Ip, Login, Host, Display, Laptop, Employee, Department, BooleanSelectField, NeedSearchIdField
from wtforms import StringField
from sqlalchemy import or_
from urllib import request as request2, parse
from flask_login import login_required, login_user, logout_user, current_user
import re, urllib, wtforms, json, time, gzip, urllib

# --------- User Manage [START] ----------

@lm.user_loader
def load_user(id):
    try:
        uid = int(id)
        return models.users.query.get(uid)
    except Exception:
        return None

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        is_remember = True if form.remember.data else False
        user = models.users.query.filter_by(username=username).first()
        if user is None or password != user.password:
            flash('用户名或密码错误')
        else:
            login_user(user, remember=is_remember)
            next = request.args.get('next')
            return redirect(next or url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

# --------- User Manage [ END ] ----------

#--------------------------------------------
#   check_name
#--------------------------------------------
@app.route('/check_name/<string:name>/')
def check_name(name):
    if models.employees.query.filter_by(name=parse.unquote(name)).count() == 1:
        return 'OK'
    else:
        return 'FAILED'

#--------------------------------------------
#   find_mac
#--------------------------------------------

@app.route('/find_mac/<string:ipaddr>/')
def find_mac(ipaddr):
    req = request2.Request('http://192.168.0.1/find_mac.asp?ip='+ipaddr)
    req.add_header('Cookie', 'wys_userid=admin,wys_passwd=5364728ACB0AEEFE362FD4FF6B5FA415')
    f = request2.urlopen(req, timeout=12)
    
    return f.read().decode('gb2312')

#--------------------------------------------
#   IP - /
#--------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    net_id = request.args.get('net', None)
    search = request.args.get('search', None)
    # 忽略 search 为空字符串
    if search == "":
        search = None

    form = Net()
    form_ip = Ip()

    # 获取网络列表
    Nets = models.nets.query.order_by(models.nets.ipstart).all()

    # 获取IP列表
    IPs = []
    query = db.session.query(models.ips, models.nets.name, models.employees.name, models.employees.status).outerjoin(models.nets, models.employees)
    
    # 按照搜索结果呈现IP
    if search is not None:
        IPs = query.filter(or_(
            models.nets.name.contains(search),
            models.employees.name.contains(search),
            models.ips.mac.contains(search),
            models.ips.device.contains(search),
            models.ips.addr_str.contains(search)
        )).all()
    
    # 按照网段呈现IP，呈现包括未使用的IP
    if net_id is not None:
        net_id = int(net_id)
        curr_net = models.nets.query.get(net_id)
        
        # 预先把网段ID写入IP表单中
        form_ip.net.data = net_id
        
        if curr_net is not None:
            res = query.filter(
                models.ips.addr.between(curr_net.ipstart, curr_net.ipend)
            ).order_by(
                models.ips.addr
            ).all()
            
            # add tail element
            res.append(None)
            one_res = res.pop(0)
            
            # 遍历该网段所有IP
            for each in range(curr_net.ipstart, curr_net.ipend+1):
                # 该IP未被使用
                if one_res is None or each != one_res[0].addr:
                    ip = models.ips(addr=each)
                    IPs.append((ip, curr_net.name, None, None))
                # 该IP已被使用
                else:
                    IPs.append(one_res)
                    one_res = res.pop(0)
    
    for each in IPs:
        each[0].net_name = each[1]
        each[0].employee_name = each[2]
        each[0].employee_status = each[3]
                    
    Ips = [x[0] for x in IPs]

    # 渲染
    return render_template('index.html', navi='ip', form=form, form_ip=form_ip, nets=Nets, currNetId=net_id, IPs=Ips, search=search)

#--------------------------------------------
#   Asset - /asset/
#--------------------------------------------

@app.route('/asset/<string:catagory>/', methods=['GET', 'POST'])
def asset(catagory):
    # configure
    rows_per_page = 12
    
    # 设置分类以及当前分类下的关键字搜索
    search = request.form['search'] if request.method == 'POST' else request.args.get('search', None)
    # 忽略 search 为空字符串
    if search == "":
        search = None
        
    if catagory == 'host':
        form = Host()
        query = db.session.query(models.hosts, models.employees.name, models.employees.status).outerjoin(models.employees)
        if search is not None:
            query = query.filter(or_(
                models.employees.name.contains(search),
                models.hosts.cpu.contains(search),
                models.hosts.memory.contains(search),
                models.hosts.motherboard.contains(search),
                models.hosts.graphics.contains(search),
                models.hosts.note.contains(search),
                models.hosts.asset_sn.contains(search)
            ))
    if catagory == 'display':
        form = Display()
        query = db.session.query(models.displays, models.employees.name, models.employees.status).outerjoin(models.employees)
        if search is not None:
            query = query.filter(or_(
                models.employees.name.contains(search),
                models.displays.vendor.contains(search),
                models.displays.model.contains(search),
                models.displays.serial.contains(search),
                models.displays.note.contains(search),
                models.displays.asset_sn.contains(search)
            ))
    if catagory == 'laptop':
        form = Laptop()
        query = db.session.query(models.laptops, models.employees.name, models.employees.status).outerjoin(models.employees)
        if search is not None:
            query = query.filter(or_(
                models.employees.name.contains(search),
                models.laptops.vendor.contains(search),
                models.laptops.model.contains(search),
                models.laptops.serial.contains(search),
                models.laptops.note.contains(search),
                models.hosts.asset_sn.contains(search)
            ))

    # 过滤未使用的资产
    unused = request.args.get('unused', None)
    if unused == 'true':
        session['unused'] = True
    elif unused == 'false':
        session['unused'] = False
    if session.get('unused', False) == True:
        query = query.filter(or_(getattr(models, catagory+"s").employee_id == None, models.employees.status == False))

    # 页码
    Page = mylib.page(query.count(), request, rows_per_page)
    
    # 按分类进行排序
    query = query.order_by(getattr(models, catagory+"s").id.desc())
    
    # 分页
    assets = mylib.paging(query, request, rows_per_page)
    
    # 分类渲染结果
    for asset, employee_name, employee_status in assets:
        asset.employee_name = employee_name
        asset.employee_status = employee_status
        
        if getattr(asset, 'create_time', None):
            asset.create_time_str = time.strftime('%Y-%m-%d', time.localtime(asset.create_time))

    Assets = [x[0] for x in assets]
    
    # 计算分类资产总量
    Count = {}
    Count['displays'] = db.session.query(models.displays).count()
    Count['hosts'] = db.session.query(models.hosts).count()
    Count['laptops'] = db.session.query(models.laptops).count()

    return render_template('asset.html', navi='asset', assets=Assets, form=form, catagory=catagory, Page=Page, search=search, Count=Count)

#--------------------------------------------
#   Employee - /employee/
#--------------------------------------------

@app.route('/employee/', methods=['GET', 'POST'])
def employee():
    curr_dep_id = request.args.get('dep', None)
    departments = models.departments.query.order_by(models.departments.name).all()
    query = db.session.query(models.employees, models.departments.name).outerjoin(models.departments)
    
    form = Employee()
    form.department_id.choices = [('', '未指定')]
    form.department_id.choices.extend([(str(r.id), r.name) for r in departments])
    form_dep = Department()
    
    rows_per_page = 12
    
    # 限制部门
    if curr_dep_id != None:
        if curr_dep_id == '0':
            query = query.filter(models.employees.department_id == None)
        else:
            query = query.filter(models.employees.department_id == int(curr_dep_id))

    # 搜索
    search = request.args.get('search', None)
    if search is not None and search != '':
        query = query.filter(or_(
            models.employees.name.contains(search)
        ))

    # 页码
    Page = mylib.page(query.count(), request, rows_per_page)

    # 排序
    query = query.order_by(models.employees.id.desc())
    
    # 分页
    employees = mylib.paging(query, request, rows_per_page)

    # 渲染搜索结果
    if search is not None and search != '':
        for employee, deparment in employees:
            employee.name = employee.name.replace(search, '<span class="search">'+search+'</span>') if employee.name else None

    return render_template('employee.html',
        navi        = 'employee',
        employees   = employees,
        form        = form,
        form_dep    = form_dep,
        Page        = Page,
        departments = departments,
        curr_dep_id = curr_dep_id,
        search      = search
    )
    
@app.route('/employee/json/', methods=['GET', 'POST'])
def employee_json():
    # configure
    rows_per_page = 12
    
    # result: 用来返回结果的字典
    result = {}
    result['rowsPerPage'] = rows_per_page
    curr_dep_id = request.args.get('dep', None)
    query = db.session.query(models.employees, models.departments.name).outerjoin(models.departments)
    
    # 限制部门
    if curr_dep_id != None:
        if curr_dep_id == '0':
            query = query.filter(models.employees.department_id == None)
        else:
            query = query.filter(models.employees.department_id == int(curr_dep_id))

    # 搜索
    search = request.args.get('search', None)
    if search is not None and search != '':
        query = query.filter(or_(
            models.employees.name.contains(search)
        ))

    if (request.args.get('count', None) == 'true'):
        result['count'] = query.count()

    # 排序
    query = query.order_by(models.employees.id.desc())
    
    # 分页
    employees = mylib.paging(query, request, rows_per_page)

    # 渲染搜索结果
    if search is not None and search != '':
        for employee, deparment in employees:
            employee.name = employee.name.replace(search, '<span class="search">'+search+'</span>') if employee.name else None
            
    result['list'] = [dict(**r1.to_dict(), dep=r2) for r1,r2 in employees]          

    return json.dumps(result)
    
@app.route('/departments/add/', methods=['GET', 'POST'])
@login_required
def department_add():
    form = Department()
    if form.validate_on_submit():
        try:
            parent = int(form.parent.data)
        except Exception as e:
            flash("创建部门失败 (parent值不是数字)")
            return form.redirect()
            
        if parent == 0:
            parent = None
            
        else:
            if not models.departments.query.filter_by(id=parent).one_or_none():
                flash('未找到对应的上级部门(部门ID:%s)' % parent)
                return form.redirect()
            
        department = models.departments(
            name = form.name.data,
            parent = form.parent.data
        )
        db.session.add(department)
        db.session.commit()
        
        return form.redirect()
        
@app.route('/departments/<int:id>/delete/')
@login_required
def department_delete(id):
    sub_departments = models.departments.query.filter_by(parent=id).all()
    if len(sub_departments) == 0:
        try:
            db.session.delete(models.departments.query.get(id))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('部门(ID:%d)删除失败' % id)
    else:
        flash('请先删除所有子部门')
    return redirect(request.referrer)
    
@app.route('/departments/<int:id>/update/', methods=['GET', 'POST'])
@login_required
def department_update(id):
    form = Department()
    if form.validate_on_submit():
        department = models.departments.query.get(id)
        department.name = form.name.data
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('重命名部门失败: 数据库更新失败')
    else:
        flash("重命名部门失败: 表单无效")
        
    return form.redirect()
    
# --------ip--------
@app.route('/ip/add/', methods=['GET', 'POST'])
@login_required
def ip_add():
    form = Ip()
    if form.validate_on_submit():
        # 检查员工是否存在
        employee = models.employees.query.filter_by(name=form.user.data).first()
        if employee is None:
            flash('IP地址启用失败: 未找到员工 %s' % form.user.data)
            return form.redirect()

        # 同步到网关
        if request.form.get('sync', None) != None:
            res = mylib.sync2gateway(
                                        addr    = mylib.inet_ntop(form.addr.data),
                                        title   = form.user.data,
                                        mac     = form.mac.data,
                                        opt     = 'add'
                                    )
            if res['status'] == False:
                flash('网关同步失败:'+res['error'])
                return form.redirect()

        # 写入数据库
        ip = models.ips(
                            addr        = form.addr.data,
                            addr_str    = mylib.inet_ntop(form.addr.data),
                            employee_id = employee.id,
                            mac         = form.mac.data,
                            device      = form.device.data,
                            net         = form.net.data
                       )
        try:
            db.session.add(ip)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('IP地址启用失败')

    return form.redirect()

@app.route('/ip/<int:ID>/delete/', methods=['GET', 'POST'])
@login_required
def ip_delete(ID):
    form = Ip()
    ip = models.ips.query.get(ID)
    
    if ip != None:
        # 同步到网关
        if request.form.get('sync', None) != None:
            res = mylib.sync2gateway(addr=ip.addr_str, opt='del')
            if res['status'] == False:
                flash('网关同步失败:'+res['error'])
                return form.redirect()

        try:
            db.session.delete(ip)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('IP地址停用失败: 数据库操作失败')
    else:
        flash('IP地址停用失败: 主键对应的IP地址不存在(%d)' % ID)
        
    return form.redirect()

@app.route('/ip/<int:ID>/update/', methods=['GET', 'POST'])
@login_required
def ip_update(ID):
    form = Ip()
    if form.validate_on_submit():
        employee = models.employees.query.filter_by(name=form.user.data).one()
        if employee is None:
            flash('IP地址更新失败: 未找到员工 %s' % form.user.data)
            return form.redirect()

        ip = models.ips.query.get(ID)
        ip.employee_id = employee.id
        ip.mac = form.mac.data
        ip.device = form.device.data
        
        # 同步到网关
        if request.form.get('sync', None) != None:
            res = mylib.sync2gateway(addr=ip.addr_str, title=form.user.data, mac=ip.mac, opt='mod')
            if res['status'] == False:
                flash('网关同步失败:'+res['error'])
                return form.redirect()
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('IP地址更新失败')
    return form.redirect()

# --------net--------
@app.route('/net/')
@login_required
def net():
    form = Net()
    nets = models.nets.query.order_by(models.nets.ipstart).all()
    return render_template('net.html', navi='ip', form=form, nets=nets)

@app.route('/nets/add/', methods=['GET', 'POST'])
@login_required
def net_add():
    form = Net()
    if form.validate_on_submit():
        net = models.nets(name = form.name.data,
                          ipstart = mylib.inet_pton(form.ipstart.data),
                          ipend = mylib.inet_pton(form.ipend.data))
        try:
            db.session.add(net)
            db.session.commit()
            return redirect(url_for('net'))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('创建网络失败:'+str(e))
    return form.redirect()

@app.route('/nets/<int:ID>/delete/', methods=['GET', 'POST'])
@login_required
def net_delete(ID):
    form = Net()
    try:
        net = models.nets.query.get(ID)
        ips = models.ips.query.filter(models.ips.addr.between(net.ipstart, net.ipend)).order_by(models.ips.addr).all()
        for ip in ips:
            db.session.delete(ip)
        db.session.delete(net)
        db.session.commit()
    except Exception as e:
        print(e)
        flash('网络删除失败')
    return form.redirect()

@app.route('/nets/<int:net_id>/update/', methods=['GET', 'POST'])
@login_required
def net_update(net_id):
    form = Net()
    if form.validate_on_submit():
        net = models.nets.query.get(net_id)
        net.name = form.name.data
        net.ipstart = mylib.inet_pton(form.ipstart.data)
        net.ipend = mylib.inet_pton(form.ipend.data)
        try:
            db.session.commit()
        except Exception as e: 
            db.session.rollback()
            print(e)
            flash('网络更新失败')
    return form.redirect()

# -------------[ Test Start ]---------------
@app.route('/inital/', methods=['GET', 'POST'])
def test_init():
    user = models.users.query.filter_by(username = 'admin').first()
    if user is None:
        user = models.users(username='admin', password='admin', catagory='administrator')
        try:
            db.session.add(user)
            db.session.commit()
            return 'User(%s) create success' % user.username
        except Exception as e:
            return 'User(%s) create failed: %s' % (user.username, str(e))
    else:
        return 'User has already created'

@app.route('/clean/', methods=['GET'])
def test_clean():
    user = current_user
    if user.is_authenticated:
        try:
            username = user.username
            db.session.delete(user)
            db.session.commit()
            logout_user()
            return 'User(%s) delete success' % username
        except Exception as e:
            return 'User(%s) delete failed: %s' % (username, str(e))
    else:
         return 'User not exist'

@app.route('/test/', methods=['GET', 'POST'])
def test():
    return render_template('test.html')

def create_model_func(model, Form, form_func=None):
    # 模板-添加记录
    def add():
        if form_func != None:
            form = form_func(Form)
        else:
            form = Form()
        if form.validate_on_submit():
            kw = {}
            for each in form:
                if each.id != 'csrf_token':
                    key = each.name
                    value = each.data
                    if value != '':
                        if isinstance(each, BooleanSelectField):
                            if value == '0':
                                value = False
                            if value == '1':
                                value = True
                        # 搜索名字对应ID再插入
                        elif isinstance(each, NeedSearchIdField):
                            rl_model = getattr(models, each.related_model)
                            related_model =  rl_model.query.filter_by(**{each.related_column:value}).first()
                            if related_model is None:
                                flash('添加失败, 未找到(%s)' % each.data)
                                return form.redirect()
                            else:
                                value = related_model.id
                        kw.update({key:value})
            try:
                # 一次插入最多不超过4条
                add_count = int(request.form.get('add_count', 1))
                
                assert add_count > 0 and add_count < 5
                
                for i in range(add_count):
                    obj = model(**kw)
                    db.session.add(obj)
                    
                db.session.commit()
                
            except Exception as e:
                print(e)
                flash('添加失败')
        else:
            flash('表单填写无效')
            for each in form:
                for error in each.errors:
                    print('[Warnning] Form submit failed: %s - %s' % (each.name, error))
        return form.redirect()
    add.__name__ = model.__name__+'_add'
    # 装饰 @login_required
    add = login_required(add)
    app.route('/%s/add/' % model.__name__, methods=['GET', 'POST'])(add)

    # 模板-删除记录
    def delete(ID):
        form = Form()
        obj = model.query.get(ID)
        try:
            db.session.delete(obj)
            db.session.commit()
        except:
            flash('删除失败')
        return form.redirect()
    delete.__name__ = model.__name__+'_delete'
    # 装饰 @login_required
    delete = login_required(delete)
    app.route('/%s/<int:ID>/delete/' % model.__name__, methods=['GET', 'POST'])(delete)

    # 模板-修改记录
    def update(ID):
        if form_func != None:
            form = form_func(Form)
        else:
            form = Form()
        # 检查被更新记录是否存在
        obj = model.query.get(ID)
        if obj is not None:
            if form.validate_on_submit():
                for each in form:
                    if each.id != 'csrf_token':
                        key = each.name
                        value = each.data
                        if key != 'id':
                            if value == '':
                                value = None
                            elif isinstance(each, BooleanSelectField):
                                if value == '0':
                                    value = False
                                if value == '1':
                                    value = True
                            elif isinstance(each, NeedSearchIdField):
                                rl_model = getattr(models, each.related_model)
                                related_model =  rl_model.query.filter_by(**{each.related_column:value}).first()
                                if related_model is None:
                                    flash('修改失败')
                                    return form.redirect()
                                else:
                                    value = related_model.id
                            setattr(obj, key, value)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    flash('更新失败')
            else:
                # 后台打印表单无效的原因
                flash('表单填写无效')
                for each in form:
                    for error in each.errors:
                        print('[Warnning] Form submit failed: %s - %s' % (each.name, error))
        else:
            flash('更新失败: 未找到 ID:%d 对映的记录' % ID)
        return form.redirect()
    update.__name__ = model.__name__+'update'
    # 装饰 @login_required
    update = login_required(update)
    app.route('/%s/<int:ID>/update/' % model.__name__, methods=['GET', 'POST'])(update)
    
# --------------- 自动生成数据库操作方法 ---------------
# 自动生成3个数据库操作 URL:
# add: /<model_name>/add/
# update: /model_name/<primary_key>/update
# delete: /model_name/<primary_key>/delete

# 生成动态 selectfeild 内容，用于检测合法性
def employee_form_func(form):
    F = form()
    F.department_id.choices = [('', '未指定')]
    F.department_id.choices.extend([(str(r.id), r.name) for r in models.departments.query.all()])
    return F
create_model_func(models.employees, Employee, form_func=employee_form_func)
create_model_func(models.hosts, Host)
create_model_func(models.displays, Display)
create_model_func(models.laptops, Laptop)

# ---------------[ Test END ]---------------

# context processor
@app.context_processor
def search_processor():
    def generate_search(**kw):
        args = []
        if kw:
            for key, value in kw.items():
                if value is not None and value != '':
                    args.append('%s=%s' % (key, value))
            if len(args) > 0:
                return '?'+'&'.join(args)
        return ''
    return dict(processor_generate_search = generate_search)




