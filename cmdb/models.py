#encoding: utf-8

from dbutils import MySQLConnection
import encrypt
import time
import ssh

class User(object):

    def __init__(self, id, username, password, age):
        self.id = id
        self.username = username
        self.password = password
        self.age = age

    @classmethod
    def validate_login(cls, username, password):
        _columns = ('id', 'username')
        _sql = 'select id,username from user where username=%s and password=%s'
        _count, _rt_list = MySQLConnection.execute_sql(_sql, (username, encrypt.md5_str(password)))
        return dict(zip(_columns, _rt_list[0])) if _count != 0 else None

    @classmethod
    def get_list(cls, wheres=[]):
        _columns = ('id', 'username', 'password', 'age')
        _sql = 'select * from user where 1=1'
        _args = []
        for _key, _value in wheres:
            _sql += ' AND {key} = %s'.format(key=_key)
            _args.append(_value)

        _count, _rt_list = MySQLConnection.execute_sql(_sql, _args)
        return [dict(zip(_columns, _line)) for _line in _rt_list]

    @classmethod
    def validate_add(cls, username, password, age):
        if username.strip() == '':
            return False, u'用户名不能为空'

        #检查用户名是否重复
        if cls.get_by_name(username):
            return False, u'用户名已存在'

        #密码要求长度必须大于等于6
        if len(password) < 6:
            return False, u'密码必须大于等于6'

        if not str(age).isdigit() or int(age) <= 0 or int(age) > 100:
            return False, u'年龄必须是0到100的数字'

        return True, ''

    @classmethod
    def get_by_name(cls, username):
        _rt = cls.get_list([('username', username)])
        return _rt[0] if len(_rt) > 0 else None


    @classmethod
    def add(cls, username, password, age):
        _sql = 'insert into user(username, password, age) values(%s, %s, %s)'
        _args = (username, encrypt.md5_str(password), age)
        MySQLConnection.execute_sql(_sql, _args, False)

    def validate_add2(self):
        if self.username.strip() == '':
            return False, u'用户名不能为空'

        #检查用户名是否重复
        if self.get_by_name(self.username):
            return False, u'用户名已存在'

        #密码要求长度必须大于等于6
        if len(self.password) < 6:
            return False, u'密码必须大于等于6'

        if not str(self.age).isdigit() or int(self.age) <= 0 or int(self.age) > 100:
            return False, u'年龄必须是0到100的数字'

        return True, ''

    def save(self):
        _sql = 'insert into user(username, password, age) values(%s, md5(%s), %s)'
        _args = (self.username, self.password, self.age)
        MySQLConnection.execute_sql(_sql, _args, False)

    @classmethod
    def validate_update(cls, uid, username, password, age):
        if cls.get_by_id(uid) is None:
            return False, u'用户信息不存在'


        if not str(age).isdigit() or int(age) <= 0 or int(age) > 100:
            return False, u'年龄必须是0到100的数字'

        return True, ''

    @classmethod
    def get_by_id(cls, uid):
        _rt = cls.get_list([('id', uid)])
        return _rt[0] if len(_rt) > 0 else None


    @classmethod
    def update(cls, uid, username, password, age):
        _sql = 'update user set age=%s where id=%s'
        _args = (age, uid)
        MySQLConnection.execute_sql(_sql, _args, False)

    @classmethod
    def validate_charge_password(cls, uid, upassword, musername, mpassword):
        #检查管理员密码是否正确
        if not cls.validate_login(musername, mpassword):
            return False, '管理员密码错误'

        if cls.get_by_id(uid) is None:
            return False, u'用户信息不存在'

        #密码要求长度必须大于等于6
        if len(upassword) < 6:
            return False, u'密码必须大于等于6'

        return True, ''

    @classmethod
    def charge_password(cls, uid, upassword):
        _sql = 'update user set password=md5(%s) where id=%s'
        _args = (upassword, uid)
        MySQLConnection.execute_sql(_sql, _args, False)


    @classmethod
    def delete(cls, uid):
        _sql = 'delete from user where id=%s'
        _args = (uid, )
        MySQLConnection.execute_sql(_sql, _args, False)


class IDC(object):

    @classmethod
    def get_list(cls):
        return [(1, '北京-亦庄'), (2, '北京-酒仙桥'), (3, '北京-西单'), (4, '北京-东单')]

    @classmethod
    def get_list_dict(cls):
        return dict(cls.get_list())


class Asset(object):

    def __init__(self, sn, ip, hostname, os,
                        cpu, ram, disk,
                        idc_id, admin, business,
                        purchase_date, warranty, vendor, model, id=None, status=0):
        self.id = id
        self.sn = sn
        self.ip = ip
        self.hostname = hostname
        self.os = os
        self.cpu = cpu
        self.ram = ram
        self.disk = disk
        self.idc_id = idc_id
        self.admin = admin
        self.business = business
        self.purchase_date = purchase_date
        self.warranty = warranty
        self.vendor = vendor
        self.model = model
        self.status = status

    @classmethod
    def create_object(self, obj):
        obj['purchase_date'] = obj['purchase_date'].strftime('%Y-%m-%d')
        return obj

    @classmethod
    def get_by_key(cls, value, key='id'):
        _column = 'id,sn,ip,hostname,os,cpu,ram,disk,idc_id,admin,business,purchase_date,warranty,vendor,model'
        _columns = _column.split(',')
        _sql = 'SELECT {column} FROM assets WHERE status=0 and {key}=%s'.format(column=_column, key=key)
        _args = (value,)
        _count, _rt_list = MySQLConnection.execute_sql(_sql, _args)
        return None if _count == 0 else cls.create_object(dict(zip(_columns, _rt_list[0])))

    @classmethod
    def get_list(cls):
        _column = 'id,sn,ip,hostname,os,cpu,ram,disk,idc_id,admin,business,purchase_date,warranty,vendor,model'
        _columns = _column.split(',')
        _sql = 'SELECT {column} FROM assets WHERE status=0'.format(column=_column)
        _count, _rt_list = MySQLConnection.execute_sql(_sql)
        return [cls.create_object(dict(zip(_columns, _line))) for _line in _rt_list]

    @classmethod
    def validate_add(cls, req):
        _is_ok = True
        _errors = {}

        for _key in 'sn,ip,hostname,os,admin,business,vendor,model'.split(','):
            _value = req.get(_key, '').strip()
            if _value == '':
                _is_ok = False
                _errors[_key] = '%s不允许为空' % _key
            elif len(_value) > 64:
                _is_ok = False
                _errors[_key] = '%s不允许超过64个字符' % _key

        if cls.get_by_key(req.get('sn'), 'sn'):
            _is_ok = False
            _errors[_key] = 'sn已存在'

        if req.get('idc_id') not in [str(_value[0]) for _value in IDC.get_list()]:
            _is_ok = False
            _errors['idc'] = '机房选择不正确'

        _rules = {
            'cpu' : {'min' : 2, 'max' : 64},
            'ram' : {'min' : 2, 'max' : 512},
            'disk' : {'min' : 2, 'max' : 2048},
            'warranty' : {'min' : 1, 'max' : 5},
        }
        for _key in 'cpu,ram,disk,warranty'.split(','):
            _value = req.get(_key, '').strip()
            if not _value.isdigit():
                _is_ok = False
                _errors[_key] = '%s不是整数' % _key
            else:
                _value = int(_value)
                _min = _rules.get(_key).get('min')
                _max = _rules.get(_key).get('max')
                if _value < _min or _value > _max:
                    _is_ok = False
                    _errors[_key] = '%s取值范围应该为%s ~ %s' % (_key, _min, _max)

        if not req.get('purchase_date', ''):
            _is_ok = False
            _errors['purchase_date'] = '采购日期不同为空'

        return _is_ok, _errors

    @classmethod
    def add(cls, req):
        _column_str = 'sn,ip,hostname,os,admin,business,vendor,model,idc_id,cpu,ram,disk,warranty,purchase_date'
        _columns = _column_str.split(',')
        _args = []
        for _column in _columns:
            _args.append(req.get(_column, ''))

        _sql = 'INSERT INTO assets({columns}) VALUES({values})'.format(columns=_column_str, values=','.join(['%s'] * len(_columns)))
        MySQLConnection.execute_sql(_sql, _args, False)

    @classmethod
    def validate_update(cls, req):
        return True, {}

    @classmethod
    def update(cls, req):
        _column_str = 'sn,ip,hostname,os,admin,business,vendor,model,idc_id,cpu,ram,disk,warranty,purchase_date'
        _columns = _column_str.split(',')
        _values = []
        _args = []
        for _column in _columns:
            _values.append('{column}=%s'.format(column=_column))
            _args.append(req.get(_column, ''))

        _args.append(req.get('id'))

        _sql = 'UPDATE assets SET {values} WHERE id=%s'.format(values=','.join(_values))
        MySQLConnection.execute_sql(_sql, _args, False)

    @classmethod
    def delete(cls, id):
        _sql = 'UPDATE assets SET status=1 WHERE id=%s'
        _args = (id, )
        MySQLConnection.execute_sql(_sql, _args, False)


class AccessLog(object):

    @classmethod
    def get_list(cls, topn=10):
        _sql = 'select ip, url, code, cnt from accesslog order by cnt desc limit %s'
        _args = (topn, )
        _count, _rt_list = MySQLConnection.execute_sql(_sql, _args)
        return _rt_list


    @classmethod
    def log2db(cls, logfile):
        MySQLConnection.execute_sql('DELETE FROM accesslog;', (), False)
        fhandler = open(logfile, 'r')
        rt_dict = {}
        while True:
            line = fhandler.readline()
            if line == '':
                break

            nodes = line.split()
            #print nodes;
            ip, url, code = nodes[3], nodes[6], nodes[4]
            #print "ip->%s\nurl->%s\ncode->%s" % (ip,url,code)

            key = (ip, url, code)
            if key not in rt_dict:
                rt_dict[key] = 1
            else:
                rt_dict[key] = rt_dict[key] + 1
        fhandler.close()
        rt_list = []

        for _key, _cnt in rt_dict.items():
            rt_list.append(_key + (_cnt, ))

        _sql = 'insert into accesslog(ip, url, code, cnt) values (%s, %s, %s, %s)'
        MySQLConnection.bulker_execute_sql(_sql, rt_list)

class Performs(object):

    @classmethod
    def add(cls, req):
        _ip = req.get('ip')
        _cpu = req.get('cpu')
        _ram = req.get('ram')
        _time = req.get('time')
        _sql = 'insert into performs(ip, cpu, ram, time)values(%s, %s, %s, %s)';
        MySQLConnection.execute_sql(_sql, (_ip, _cpu, _ram, _time), False)

    @classmethod
    def get_list(cls, ip):
        _sql = 'SELECT cpu, ram, time FROM performs WHERE ip=%s and time>=%s order by time asc'
        _args = (ip, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 60 * 60)))
        _count, _rt_list = MySQLConnection.execute_sql(_sql, _args)
        datetime_list = []
        cpu_list = []
        ram_list = []
        for _cpu, _ram, _time in _rt_list:
            cpu_list.append(_cpu)
            ram_list.append(_ram)
            datetime_list.append(_time.strftime('%H:%M:%S'))

        return datetime_list, cpu_list, ram_list


class Command(object):

    @classmethod
    def validate(cls, req):
        return True, {}

    @classmethod
    def execute(cls, req):
        _id = req.get('id', '')
        _username = req.get('username', '')
        _password = req.get('password', '')
        _cmds = req.get('cmds', '').splitlines()
        _asset = Asset.get_by_key(_id)
        _result = ssh.ssh_execute(_asset['ip'], _username, _password, _cmds)
        _echos = []
        for _cmd, _outs, _errs in _result:
            _echos.append(_cmd)
            _echos.append(''.join(_outs))
        return '\n'.join(_echos)

if __name__ == '__main__':
    #print User.validate_login('kk', '123456')
    #print User.validate_login('kk', '1234567')
    logfile = '/myapp/python/projects/myweb/cmdb/logfile'
    a = AccessLog.log2db(logfile=logfile)
    print a
