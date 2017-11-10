#encoding: utf-8
import hashlib

def md5_str(value):
    _md5 = hashlib.md5()
    _md5.update(value)
    return _md5.hexdigest()

if __name__ == '__main__':
    print md5_str('123')