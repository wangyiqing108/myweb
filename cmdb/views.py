#encoding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')                     #设置命令行为utf-8

import os
import time
import json
from functools import wraps

from flask import Flask                             #从flask包导入Flask类
from flask import render_template                   #从flask包导入render_template函数
from flask import request                           #从flask包导入request对象
from flask import redirect                          #从flask包导入redirect函数
from flask import url_for
from flask import session
from flask import flash

import gconf

from cmdb import app                                # user模块下的app变量(Flask对象)

from models import User, IDC, Asset, AccessLog, Performs, Command

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user') is None:
            return redirect('/')

        rt = func(*args, **kwargs)
        return rt

    return wrapper


'''打开用户登录页面
'''
@app.route('/')                                     #将url path=/的请求交由index函数处理
def index():
    return render_template('login.html')            #加载login.html模板，并返回页面内容

    #return 'hello,{0}'.format(name)
    #return '<h1>Hello, %s!</h1>' % name


'''用户登录信息检查
'''
@app.route('/login/', methods=["POST"])             #将url path=/login/的post请求交由login函数处理
def login():
    username = request.form.get('username', '')     #接收用户提交的数据
    password = request.form.get('password', '')

    #需要验证用户名密码是否正确
    _user = User.validate_login(username, password)
    if _user:
        session['user'] = _user
        return redirect('/users/')                  #跳转到url /users/
    else:
        #登录失败
        return render_template('login.html', username=username, error='用户名或密码错误')


'''用户列表显示
'''
@app.route('/users/')                               #将url path=/users/的get请求交由users函数处理
def users():
    return render_template('users.html', users=User.get_list())            #加载渲染users.html模板

'''跳转到新建用户信息输入的页面
'''
@app.route('/user/create/')                         #将url path=/user/create/的get请求交由create_user处理
def create_user():
    return render_template('user_create.html')      #加载渲染user_create.html


'''存储新建用户的信息
'''
@app.route('/user/add/', methods=['POST'])          #将url path=/user/add的post请求交由add_user处理
def add_user():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    age = request.form.get('age', '')

    _user = User(id=None, username=username, password=password, age=age)
    _is_ok, _error = _user.validate_add2()
    if _is_ok:
        _user.save()

    '''
    #检查用户信息
    _is_ok, _error = User.validate_add(username, password, age)
    if _is_ok:
        User.add(username, password, age)      #检查ok，添加用户信息
    '''
    return json.dumps({'is_ok':_is_ok, "error":_error})

'''打开用户信息修改页面
'''
@app.route('/user/modify/')                          #将url path=/user/modify/的歌特请求交由modify_user函数处理
def modify_user():
    uid = request.args.get('id', '')
    _user = User.get_by_id(uid)
    _error = ''
    _uid = ''
    _username = ''
    _password = ''
    _age = ''
    if _user is None:
        _error = '用户信息不存在'
    else:
        _uid = _user.get('id')
        _username = _user.get('username')
        _password = _user.get('password')
        _age = _user.get('age')

    return render_template('user_modify.html', error=_error, password=_password, age=_age, username=_username, uid=_uid)

'''保存修改用户数据
'''
@app.route('/user/update/', methods=['POST'])           #将url path=/user/update/的post请求交由update_user函数处理
def update_user():
    uid = request.form.get('id', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    age = request.form.get('age', '')

    #检查用户信息
    _is_ok, _error = User.validate_update(uid, username, password, age)

    if _is_ok:
        User.update(uid, username, password, age)
    return json.dumps({'is_ok':_is_ok, "error":_error})

@app.route('/user/delete/')
def delete_user():
    uid = request.args.get('id', '')
    User.delete(uid)
    flash('删除用户信息成功')
    return redirect('/users/')


@app.route('/logs/')
def logs():
    topn = request.args.get('topn', 10)
    topn = int(topn) if str(topn).isdigit() else 10

    return render_template('logs.html', rt_list=AccessLog.get_list(topn=topn))

@app.route('/logout/')
def logout():
    session.clear()
    return redirect('/')

@app.route('/uploadlogs/', methods=['POST'])
def uploadlogs():
    _file = request.files.get('logfile')
    if _file:
        _filepath = 'temp/%s' % time.time()
        _file.save(_filepath)
        AccessLog.log2db(_filepath)
    return redirect('/logs/')


@app.route('/user/charge-password/', methods=['POST'])
def charge_user_password():
    uid = request.form.get('userid')
    manager_password = request.form.get('manager-password')
    user_password = request.form.get('user-password')
    _is_ok, _error = User.validate_charge_password(uid, user_password, \
                                    session['user']['username'], manager_password)
    if _is_ok:
        User.charge_password(uid, user_password)

    return json.dumps({'is_ok':_is_ok, "error":_error})

'''资产列表显示
'''
@app.route('/assets/')
def assets():
    return render_template('assets.html', assets=Asset.get_list(), idcs=IDC.get_list_dict())

@app.route('/asset/create/', methods=['POST', 'GET'])
def create_asset():
    return render_template('asset_create.html', idcs=IDC.get_list())

@app.route('/asset/add/', methods=['POST'])
def add_asset():
    _is_ok, _errors = Asset.validate_add(request.form)
    if _is_ok:
        Asset.add(request.form)
    return json.dumps({'is_ok' : _is_ok, 'errors' : _errors, 'success' : '添加成功'})


@app.route('/asset/modify/')
def modify_asset():
    _id = request.args.get('id', '')
    return render_template('asset_modify.html', asset=Asset.get_by_key(_id), idcs=IDC.get_list())


@app.route('/asset/update/', methods=['POST'])
def update_asset():
    _is_ok, _errors = Asset.validate_update(request.form)
    if _is_ok:
        Asset.update(request.form)
    return json.dumps({'is_ok' : _is_ok, 'errors' : _errors, 'success' : '更新成功'})


@app.route('/asset/delete/')
def delete_asset():
    _id = request.args.get('id', '')
    Asset.delete(_id)
    return redirect('/assets/')


@app.route('/asset/perform/')
def perform_asset():
    _id = request.args.get('id', '')
    _asset = Asset.get_by_key(_id)
    datetime_list, cpu_list, ram_list = Performs.get_list(_asset['ip'])
    # datetime_list = ['2016-7-10 19:16:50', '2016-7-10 19:16:50', '2016-7-10 19:16:50', '2016-7-10 19:16:50', '2016-7-10 19:16:50', '2016-7-10 19:16:50', '2016-7-10 19:16:50', '2016-7-10 19:16:50','2016-7-10 19:16:50', '2016-7-10 19:16:50', '2016-7-10 19:16:50']
    # cpu_list = [-0.9, 0.6, 3.5, 8.4, 13.5, 17.0, 18.6, 17.9, 14.3, 9.0, 3.9, 1.0]
    # ram_list = [3.9, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
    return render_template('asset_perform.html', datetime_list=json.dumps(datetime_list),
                                                    cpu_list=json.dumps(cpu_list),
                                                    ram_list=json.dumps(ram_list))

@app.route('/asset/cmd/')
@login_required
def cmd_asset():
    _id = request.args.get('id', '')
    return render_template('asset_cmd.html', aid=_id)

@app.route('/asset/cmd_execute/', methods=['POST'])
@login_required
def cmd_execute_asset():
    _is_ok, _errors = Command.validate(request.form)
    _success = ''
    if _is_ok:
        _success = Command.execute(request.form)
    return json.dumps({'is_ok' : _is_ok, 'errors' : _errors, 'success' : _success})


@app.route('/test/', methods=['POST', 'GET'])
def test():
    print request.args
    print request.form
    print request.files
    print request.headers
    return render_template('test.html')


@app.route('/performs/', methods=['POST'])
def performs():
    _app_key = request.headers.get('app_key', '')
    _app_secret = request.headers.get('app_secret', '')
    # _app_key = request.args.get('app_key', '')
    # _app_secret = request.args.get('app_secret', '')
    if _app_key != gconf.APP_KEY or _app_secret != gconf.APP_SECRET:
        return json.dumps({'code' : 400, 'text' : 'secret error'})
    #获取json数据
    Performs.add(request.json)
    #0.10 request.get_json()
    return json.dumps({'code' : 200, 'text' : 'success'})
