#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import datetime, time
import logging
import random
import hashlib
import base64
import urllib
import json
import pkgutil
import importlib

LOG = logging.getLogger('utilities')

_CHARACTORS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+|'

def singleton(clsname):
    instances = {}
    def getinstance(*args,**kwargs):
        if clsname not in instances:
            instances[clsname] = clsname(*args,**kwargs)
        return instances[clsname]
    return getinstance

class Constant(object):
    class ConstError(TypeError) : pass
    
    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise self.ConstError("Can't rebind const (%s)" % key)
        setattr(self, key, value)

class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return json.JSONEncoder.default(self, obj)

def toint(val):
    if not val or val == 'None':
        return 0
    return int(val)

def tofloat(val):
    if not val or val == 'None':
        return 0
    return float(val)

def todatetime(val):
    if not val or val == 'None':
        return datetime.datetime.min
    rt = re.findall(r'(\d{4})\W?(\d{2})\W?(\d{2})(?:[\WT]?(\d{2})\W?(\d{2})\W?(\d{2}))?', val)
    if not rt:
        rt = re.findall(r'(\d{2,4})\W(\d{1,2})\W(\d{1,2})(?:[\WT](\d{1,2})\W(\d{1,2})\W(\d{1,2}))?', val)
    if rt:
        t = [v if v else '00' for v in rt[0]]
        val = '{0}-{1}-{2} {3}:{4}:{5}'.format(t[0], t[1], t[2], t[3], t[4], t[5])
    else:
        return datetime.datetime.min
    return datetime.datetime.strptime(val, '%Y-%m-%d %H:%M:%S')

def tostring(val):
    if isinstance(val, dict) or isinstance(val, list):
        return json.dumps(val, cls=JsonEncoder)
    return str(val)

def toseconds(val):
    dt = todatetime(val)
    if dt is datetime.datetime.min:
        return False
    return dt.timestamp()

def to_human_time(val, fmt=None):
    if not fmt:
        fmt = '%Y-%m-%d %H:%M:%S'
    if not val:
        return ''
    return time.strftime(fmt, time.localtime(val))

def md5_encode(val):
    m = hashlib.md5(val.encode())
    return m.hexdigest()

def base64_encode(val):
    if isinstance(val, bytes):
        return base64.b64encode(val).decode()
    return base64.b64encode(val.encode()).decode()

def base64_decode(val):
    return base64.b64decode(val).decode()

def url_encode(val):
    return urllib.parse.quote(val)

def url_decode(val):
    return urllib.parse.unquote(val)

def random_string(len = 16):
    return ''.join(random.sample(_CHARACTORS, len))

def get_host_from_url(val):
    pos = 0
    if val.startswith('http'):
        pos = 8
    pos = val.find('/', pos)
    if pos >= 0:
        return val[:pos]
    return val

def parse_remote_ip(request):
    ip = request.headers.get('X-Real-Ip')
    if not ip:
        ip = request.remote_ip
    return ip

def format_url_with_params(url, params):
    slices = [str(k)+'='+urllib.parse.quote(str(v).encode()) for k, v in params.items()]
    sep = '&' if '?' in url else '?'
    return url + sep + '&'.join(slices)

def prepare_requests_certs_params(conf):
    if conf and 'cert' in conf and 'key' in conf:
        return (conf.get('cert'), conf.get('key'))
    return None

def get_current_timestamp_millis():
    """
    Get current timestamp as milli seconds
    """
    return int(time.time() * 1000)

def pascal_case(txt: str):
    """Converts xx_yy to XxYy"""
    txt = re.sub(r"(_|-)+", " ", txt).title().replace(' ', '')
    return txt

def camel_case(txt: str):
    """Converts xx_yy to xxYy"""
    txt = re.sub(r"(_|-)+", " ", txt).title().replace(' ', '')
    return txt[0].lower() + txt[1:]

def snake_case(txt: str):
    """Converts XxYy to xx_yy, XxYY to xx_yy"""
    res = [txt[0].lower()]
    insert_sep = txt[0] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for c in txt[1:]:
        if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            if insert_sep:
                res.append('_')
            insert_sep = False
            res.append(c.lower())
        elif c == '-':
            res.append('_')
            insert_sep = False
        else:
            insert_sep = True
            res.append(c)
     
    return ''.join(res)

def kebab_case(txt: str):
    """Converts XxYy to xx-yy, XxYY to xx-yy"""
    res = [txt[0].lower()]
    insert_sep = txt[0] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for c in txt[1:]:
        if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            if insert_sep:
                res.append('-')
            insert_sep = False
            res.append(c.lower())
        elif c == '_':
            res.append('-')
            insert_sep = False
        else:
            insert_sep = True
            res.append(c)
     
    return ''.join(res)

def get_package_name(module_name):
    loader = pkgutil.get_loader(module_name)
    if loader is not None and loader.is_package(module_name):
        return module_name
    else:
        parts = module_name.split('.')
        return '.'.join(parts[:-1])
    
def load_module_by_package_name(module_name):
    package_name = get_package_name(module_name)
    if package_name:
        module_package = importlib.import_module(package_name)
        if package_name == module_name:
            return module_package
        else:
            parts = module_name.split('.')
            short_module_name = ''.join(parts[-1:])
            module = getattr(module_package, short_module_name, None)
            return module
    return None
    
if __name__ == '__main__':
    # todatetime('2018/01/02T03:04:05:Z')
    # todatetime('2018-01-02 03:04:05')
    dt = todatetime('2018-01-02')
    print(dt)
    dt = todatetime('20180102')
    print(dt)
    dt = todatetime('2018-1-2T3:4:5')
    print(dt)
    ts = toseconds('2018-1-2T3:4:5')
    print(ts)
    ts = toseconds('1239-1-1')
    print(ts)
    ts = toseconds('123-1-a')
    print(ts)
