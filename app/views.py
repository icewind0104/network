# -*- coding: utf-8 -*-
from app import app, models, mylib, db, lm
from flask import render_template, flash, redirect, url_for, g, request
from app.forms import Net, Ip, Login
from wtforms import StringField
from sqlalchemy import or_
from flask_login import login_required, login_user, logout_user, current_user
import re

#prefix = '/oeasy-asset-center'
prefix = ''

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
            return redirect(next or url_for('admin'))
    return render_template('login.html', form=form, prefix=prefix)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    net_id = request.args.get('net', None)
    search = request.form['search'] if request.method == 'POST' else None

    # 获取网络列表
    Nets = models.nets.query.order_by(models.nets.ipstart).all()

    # 获取IP列表
    IPs = []
    if search is not None:
        IPs = models.ips.query.filter(or_(
            models.ips.user.contains(search),
            models.ips.mac.contains(search),
            models.ips.device.contains(search),
            models.ips.addr_str.contains(search)
        )).all()
        for each in IPs:
            each.addr_str = each.addr_str.replace(search, '<span class="search">'+search+'</span>')
            each.mac = each.mac.replace(search, '<span class="search">'+search+'</span>')
            each.device = each.device.replace(search, '<span class="search">'+search+'</span>')
            each.user = each.user.replace(search, '<span class="search">'+search+'</span>')
    if net_id is not None:
        net_id = int(net_id)
        curr_net = models.nets.query.get(net_id)
        if curr_net is not None:
            ips = models.ips.query.filter(models.ips.addr.between(curr_net.ipstart, curr_net.ipend)).order_by(models.ips.addr).all()
            # add tail element
            ips.append(None)
            ip = ips.pop(0)
            for each in range(curr_net.ipstart, curr_net.ipend+1):
                # 未使用的IP
                if ip is None or each != ip.addr:
                    IPs.append(models.ips(addr=each, user=None))
                # 已使用的IP
                else:
                    IPs.append(ip)
                    ip = ips.pop(0)

    # 渲染
    return render_template('index.html', nets=Nets, currNetId=net_id, IPs=IPs, prefix=prefix)

@app.route('/admin/', methods=['GET', 'POST'])
@login_required
def admin():
    net_id = request.args.get('net', None)
    search = request.form['search'] if request.method == 'POST' else None

    form = Net()
    form_ip = Ip()

    # 获取网络列表
    Nets = models.nets.query.order_by(models.nets.ipstart).all()

    # 获取IP列表
    IPs = []
    if search is not None:
        IPs = models.ips.query.filter(or_(
            models.ips.user.contains(search),
            models.ips.mac.contains(search),
            models.ips.device.contains(search),
            models.ips.addr_str.contains(search)
        )).all()
        for each in IPs:
            each.addr_str = each.addr_str.replace(search, '<span class="search">'+search+'</span>')
            each.mac = each.mac.replace(search, '<span class="search">'+search+'</span>')
            each.device = each.device.replace(search, '<span class="search">'+search+'</span>')
            each.user = each.user.replace(search, '<span class="search">'+search+'</span>')
    if net_id is not None:
        net_id = int(net_id)
        form_ip.net.data = net_id
        curr_net = models.nets.query.get(net_id)
        if curr_net is not None:
            ips = models.ips.query.filter(models.ips.addr.between(curr_net.ipstart, curr_net.ipend)).order_by(models.ips.addr).all()
            # add tail element
            ips.append(None)
            ip = ips.pop(0)
            for each in range(curr_net.ipstart, curr_net.ipend+1):
                # 未使用的IP
                if ip is None or each != ip.addr:
                    IPs.append(models.ips(addr=each, user=None))
                # 已使用的IP
                else:
                    IPs.append(ip)
                    ip = ips.pop(0)

    # 渲染
    return render_template('admin.html', form=form, form_ip=form_ip, nets=Nets, currNetId=net_id, IPs=IPs, prefix=prefix)

# --------ip--------
@app.route('/ip/add/', methods=['GET', 'POST'])
def ip_add():
    form = Ip()
    if form.validate_on_submit():
        ip = models.ips(addr = form.addr.data,
                        addr_str = mylib.inet_ntop(form.addr.data),
                        user = form.user.data,
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
def ip_update(ID):
    form = Ip()
    if form.validate_on_submit():
        ip = models.ips.query.get(ID)
        ip.user = form.user.data
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
def net():
    form = Net()
    nets = models.nets.query.order_by(models.nets.ipstart).all()
    return render_template('net.html', form=form, nets=nets, prefix=prefix)

@app.route('/net/add/', methods=['GET', 'POST'])
def net_add():
    form = Net()
    if form.validate_on_submit():
        net = models.nets(name = form.name.data,
                          ipstart = mylib.inet_pton(form.ipstart.data),
                          ipend = mylib.inet_pton(form.ipend.data))
        try:
            db.session.add(net)
            db.session.commit()
            return redirect(url_for('admin')+'?net='+str(net.id))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('创建网络失败')
    return form.redirect()

@app.route('/net/<int:ID>/delete/', methods=['GET', 'POST'])
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

@app.route('/net/<int:net_id>/update/', methods=['GET', 'POST'])
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

# 仅作为开发测试各项功能时使用
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
