import sys
sys.path.append('..')
from urllib import request
from utils.log import log
import sys
import re
import os
import zipfile
import shutil
import requests
import json

TIME_OUT = 30

def get_html_by_requests(url, headers = '', code = 'utf-8', data = None, proxies = {}):
    html = ''
    r = None
    try:
        if data:
            r = requests.post(url, headers = headers, timeout = TIME_OUT, data = data, proxies = proxies)
        else:
            r = requests.get(url, headers = headers, timeout = TIME_OUT, proxies = proxies)

        if code:
            r.encoding = code
        html = r.text

    except Exception as e:
        log.error(e)
    finally:
        r and r.close()

    return html

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        pass

def download_file(url, base_path, filename = '', call_func = ''):
    file_path = base_path + filename
    directory = os.path.dirname(file_path)
    mkdir(directory)

    # 进度条
    def progress_callfunc(blocknum, blocksize, totalsize):
        '''回调函数
        @blocknum : 已经下载的数据块
        @blocksize : 数据块的大小
        @totalsize: 远程文件的大小
        '''
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        # print ('进度条 %.2f%%' % percent, end = '\r')
        sys.stdout.write('进度条 %.2f%%' % percent + "\r")
        sys.stdout.flush()

    if url:
        try:
            log.debug('''
                         正在下载 %s
                         存储路径 %s
                      '''
                         %(url, file_path))

            request.urlretrieve(url, file_path, progress_callfunc)

            log.debug('''
                         下载完毕 %s
                         文件路径 %s
                      '''
                         %(url, file_path)
                     )

            call_func and call_func()
            return 1
        except Exception as e:
            log.error(e)
            return 0
    else:
        return 0

def unpack_zip(zip_path, save_path):
    try:
        azip = zipfile.ZipFile(zip_path)
        azip.extractall(save_path)
    except Exception as e:
        log.error('解压失败 %s'%e)
        return False
    finally:
        azip.close()

    return True

def join_path(path, file):
    return os.path.join(path, file)

def walk_file(folder_path):
    '''
    @summary: 遍历文件夹里面的文件
    ---------
    @param folder_path:
    ---------
    @result:
    '''
    file_list = []

    try:
        for current_path, sub_folders, files_name in os.walk(folder_path):
            # current_path 当前文件夹路径
            # sub_folders 当前路径下的子文件夹
            # filesname 当前路径下的文件

            for file in files_name:
                file_path = join_path(current_path, file)
                file_list.append(file_path)
    except Exception as e:
        log.error(e)

    return file_list

def get_next_path(path):
    next_path = ''
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isdir(file_path):
            next_path = file_path
    return next_path

def read_file(filename, readlines = False, encoding = 'utf-8'):
    '''
    @summary: 读文件
    ---------
    @param filename: 文件名（有路径）
    @param readlines: 按行读取 （默认False）
    ---------
    @result: 按行读取返回List，否则返回字符串
    '''

    content = ''
    try:
        with open(filename, 'r', encoding = encoding) as file:
            content = file.readlines() if readlines else file.read()
    except Exception as e:
        log.error(e)

    return content

def write_file(filename, content, mode = 'w'):
    '''
    @summary: 写文件
    ---------
    @param filename: 文件名（有路径）
    @param content: 内容
    @param mode: 模式 w/w+ (覆盖/追加)
    ---------
    @result:
    '''

    directory = os.path.dirname(filename)
    mkdir(directory)
    with open(filename, mode, encoding = 'utf-8') as file:
        file.writelines(content)

_regexs = {}
# @log_function_time
def get_info(html, regexs, allow_repeat = False, fetch_one = False, split = None):
    regexs = isinstance(regexs, str) and [regexs] or regexs

    infos = []
    for regex in regexs:
        if regex == '':
                continue

        if regex not in _regexs.keys():
            _regexs[regex] = re.compile(regex, re.S)

        if fetch_one:
                infos = _regexs[regex].search(html)
                if infos:
                    infos = infos.groups()
                else:
                    continue
        else:
            infos = _regexs[regex].findall(str(html))

        if len(infos) > 0:
            # print(regex)
            break

    if fetch_one:
        infos = infos if infos else ('',)
        return infos if len(infos) > 1 else infos[0]
    else:
        infos = allow_repeat and infos or sorted(set(infos),key = infos.index)
        infos = split.join(infos) if split else infos
        return infos

def exec_command(command):
    os.system(command)

def copy_file(src_path, dst_path):
    try:
        directory = os.path.dirname(dst_path)
        mkdir(directory)
        shutil.copyfile(src_path, dst_path)
    except Exception as e:
        log.debug(e)
        return False
    return True

def get_json(json_str):
    '''
    @summary: 取json对象
    ---------
    @param json_str: json格式的字符串
    ---------
    @result: 返回json对象
    '''

    try:
        return json.loads(json_str) if json_str else {}
    except Exception as e:
        log.error(e)
        return {}

def dumps_json(json_):
    '''
    @summary: 格式化json 用于打印
    ---------
    @param json_: json格式的字符串或json对象
    ---------
    @result: 格式化后的字符串
    '''
    try:
        if isinstance(json_, str):
            json_ = get_json(json_)

        json_ = json.dumps(json_, ensure_ascii=False, indent=4, skipkeys = True)

    except Exception as e:
        log.error(e)
        json_ = pformat(json_)

    return json_