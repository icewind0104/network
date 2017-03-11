# -*- coding: utf-8 -*-
from app import app, models, mylib, db, lm
from flask import render_template, flash, redirect, url_for, g, request, session
from app.forms import Net, Ip, Login, Asset, Employee, BooleanSelectField
from wtforms import StringField
from sqlalchemy import or_
from flask_login import login_required, login_user, logout_user, current_user
import re, urllib, wtforms 

prefix = app.config['MOUNT_POINT']

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
        user = models.users.query.filter_by(username=username).first()
        if user is None or password != user.password:
            flash('用户名或密码错误')
        else:
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('index'))
    return render_template('login.html', form=form, prefix=prefix)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

# --------- User Manage [ END ] ----------

#--------------------------------------------
#   IP - /
#--------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    net_id = request.args.get('net', None)
    search = request.form['search'] if request.method == 'POST' else None

    form = Net()
    form_ip = Ip()

    # 获取网络列表
    Nets = models.nets.query.order_by(models.nets.ipstart).all()

    # 获取IP列表
    IPs = []
    if search is not None:
        IPs = db.session.query(models.ips, models.nets.name, models.employees).outerjoin(models.nets, models.employees
        ).filter(or_(
            models.nets.name.contains(search),
            models.employees.name.contains(search),
            models.ips.mac.contains(search),
            models.ips.device.contains(search),
            models.ips.addr_str.contains(search)
        )).all()
        for ip, net_name, employee in IPs:
            ip.net_name = net_name.replace(search, '<span class="search">'+search+'</span>')
            ip.addr_str = ip.addr_str.replace(search, '<span class="search">'+search+'</span>')
            ip.mac = ip.mac.replace(search, '<span class="search">'+search+'</span>') if ip.mac else None
            ip.device = ip.device.replace(search, '<span class="search">'+search+'</span>') if ip.device else None
            ip.employee_name = employee.name.replace(search, '<span class="search">'+search+'</span>')
    if net_id is not None:
        net_id = int(net_id)
        form_ip.net.data = net_id
        curr_net = models.nets.query.get(net_id)
        if curr_net is not None:
            res = db.session.query(models.ips, models.nets.name, models.employees).outerjoin(models.nets).outerjoin(models.employees
            ).filter(
                models.ips.addr.between(curr_net.ipstart, curr_net.ipend)
            ).order_by(
                models.ips.addr
            ).all()
            # add tail element
            res.append(None)
            one_res = res.pop(0)
            for each in range(curr_net.ipstart, curr_net.ipend+1):
                # 未使用的IP
                if one_res is None or each != one_res[0].addr:
                    ip = models.ips(addr=each)
                    ip.net_name = curr_net.name
                    IPs.append((ip, None, None))
                # 已使用的IP
                else:
                    one_res[0].net_name = curr_net.name
                    one_res[0].employee_name = one_res[2].name
                    IPs.append(one_res)
                    one_res = res.pop(0)

    # 渲染
    return render_template('index.html', form=form, form_ip=form_ip, nets=Nets, currNetId=net_id, IPs=IPs, prefix=prefix)

#--------------------------------------------
#   Asset - /asset/
#--------------------------------------------

@app.route('/asset/', methods=['GET', 'POST'])
def asset():
    max_list = 12
    query = db.session.query(models.assets, models.employees).outerjoin(models.employees)

    # 过滤未使用的资产
    unused = request.args.get('unused', None)
    if unused == 'true':
        session['unused'] = True
    elif unused == 'false':
        session['unused'] = False

    # 搜索关键词
    search = request.form['search'] if request.method == 'POST' else request.args.get('search', None)
    if search is not None and search != '':
        query = query.filter(or_(
            models.employees.name.contains(search),
            models.assets.catagory.contains(search),
            models.assets.name.contains(search),
            models.assets.serial.contains(search),
            models.assets.note.contains(search)
        ))

    # 设置分类
    catagory = request.args.get('catagory', None)
    if catagory:
        catagory = urllib.parse.unquote(catagory)
        query = query.filter(models.assets.catagory == catagory)

    form = Asset()
    if session.get('unused', False) == True:
        query = query.filter(or_(models.assets.employee_id == None, models.employees.status == False))

    # 页码
    curr_page = request.args.get('page', None) or 1
    try:
        curr_page = int(curr_page)
    except:
        curr_page = 1
    Page = mylib.page(query.count(), max_list, curr_page)
    if curr_page < 1 or curr_page > Page.count:
        Page.curr_page = 1

    # 排序
    query = query.order_by(models.assets.id.desc())
    assets = query[(int(curr_page)-1)*max_list:(int(curr_page)-1)*max_list+max_list]

    # 渲染搜索结果
    if search is not None and search != '':
        for asset, employee in assets:
            asset.employee_name = employee.name.replace(search, '<span class="search">'+search+'</span>') if employee_name else None
            asset.name = asset.name.replace(search, '<span class="search">'+search+'</span>') if asset.name else None
            asset.serial = asset.serial.replace(search, '<span class="search">'+search+'</span>') if asset.serial else None
            asset.note = asset.note.replace(search, '<span class="search">'+search+'</span>') if asset.note else None
            asset.catagory = asset.catagory.replace(search, '<span class="search">'+search+'</span>') if asset.catagory else None

    return render_template('asset.html', prefix=prefix, assets=assets, form=form, catagory=catagory, Page=Page, search=search)

#--------------------------------------------
#   Employee - /employee/
#--------------------------------------------

@app.route('/employee/', methods=['GET', 'POST'])
def employee():
    form = Employee()
    query = models.employees.query
    max_list = 12

    # 搜索
    search = request.form['search'] if request.method == 'POST' else request.args.get('search', None)
    if search is not None and search != '':
        query = query.filter(or_(
            models.employees.name.contains(search),
            models.employees.department.contains(search),
        ))

    # 页码
    curr_page = request.args.get('page', None) or 1
    try:
        curr_page = int(curr_page)
    except:
        curr_page = 1
    Page = mylib.page(query.count(), max_list, curr_page)
    if curr_page < 1 or curr_page > Page.count:
        Page.curr_page = 1

    # 排序
    query = query.order_by(models.employees.id.desc())
    employees = query[(int(curr_page)-1)*max_list:(int(curr_page)-1)*max_list+max_list]

    # 渲染搜索结果
    if search is not None and search != '':
        for employee in employees:
            employee.name = employee.name.replace(search, '<span class="search">'+search+'</span>') if employee.name else None
            employee.department = employee.department.replace(search, '<span class="search">'+search+'</span>') if employee.department else None

    return render_template('employee.html', prefix=prefix, employees=employees, form=form, Page=Page, search=search)

# --------ip--------
@app.route('/ip/add/', methods=['GET', 'POST'])
@login_required
def ip_add():
    form = Ip()
    if form.validate_on_submit():
        employee = models.employees.query.filter_by(name=form.user.data).first()
        if employee is None:
            flash('IP地址启用失败: 未找到员工 %s' % form.user.data)
            return form.redirect()

        ip = models.ips(addr = form.addr.data,
                        addr_str = mylib.inet_ntop(form.addr.data),
                        employee_id = employee.id,
                        mac = form.mac.data,
                        device = form.device.data,
                        net = form.net.data)
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
    try:
        ip = models.ips.query.get(ID)
        db.session.delete(ip)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('IP地址停用失败')
    return form.redirect()

@app.route('/ip/<int:ID>/update/', methods=['GET', 'POST'])
@login_required
def ip_update(ID):
    form = Ip()
    if form.validate_on_submit():
        employee = models.employees.query.filter_by(name=form.user.data).first()
        if employee is None:
            flash('IP地址更新失败: 未找到员工 %s' % form.user.data)
            return form.redirect()

        ip = models.ips.query.get(ID)
        ip.employee_id = employee.id
        ip.mac = form.mac.data
        ip.device = form.device.data
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
    return render_template('net.html', form=form, nets=nets, prefix=prefix)

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

from wtforms import StringField
@app.route('/test/', methods=['GET', 'POST'])
def test():
    objs = db.session.query(models.employees).all()
    form = Employee()
    return render_template('test.html', form=form, objs=objs)

def create_model_func(model, Form):
    # 模板-添加记录
    def add():
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
                        if getattr(each, 'need_search_id', None):
                            rl_model = getattr(models, each.related_model)
                            related_model =  rl_model.query.filter_by(**{each.related_column:value}).first()
                            if related_model is None:
                                flash('添加失败, 未找到(%s)' % each.data)
                                return form.redirect()
                            else:
                                value = related_model.id
                        kw.update({key:value})
            obj = model(**kw)
            try:
                db.session.add(obj)
                db.session.commit()
            except:
                flash('添加失败')
        else:
            flash('表单填写无效')
        return form.redirect()
    add.__name__ = model.__name__+'_add'
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
    app.route('/%s/<int:ID>/delete/' % model.__name__, methods=['GET', 'POST'])(delete)

    # 模板-修改记录
    def update(ID):
        form = Form()
        obj = model.query.get(ID)
        if obj is not None and form.validate_on_submit():
            for each in form:
                if each.id != 'csrf_token':
                    key = each.name
                    value = each.data
                    if key != 'id' and value != '':
                        if isinstance(each, BooleanSelectField):
                            if value == '0':
                                value = False
                            if value == '1':
                                value = True
                        if getattr(each, 'need_search_id', None):
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
            flash('表单填写无效')
        return form.redirect()
    update.__name__ = model.__name__+'update'
    app.route('/%s/<int:ID>/update/' % model.__name__, methods=['GET', 'POST'])(update)

create_model_func(models.assets, Asset)
create_model_func(models.employees, Employee)

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




