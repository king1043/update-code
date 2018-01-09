# -*- coding: utf-8 -*-
'''
Created on 2018-01-03 15:40
---------
@summary: 利用github来更新代码
---------
@author: Boris
'''
import utils.tools as tools
from utils.log import log
import os
from multiprocessing import Process
import configparser #读配置文件的
import codecs

VERSION_FILE = '.version'

class UpdateCode():
    def __init__(self, remote_url, local_save_path, project_path, main_lnk_paths, sync_files = [], ignore_files = []):
        '''
        @summary: 更新代码初始化函数
        ---------
        @param remote_url: 远程代码发布地址
        @param local_save_path: 代码下载路径
        @param project_path: 本地项目路径
        @param main_lnk_paths: 本地项目执行文件快捷方式地址
        @param sync_files: 同步的文件 .* 表示同步全部
        @param ignore_files: 忽略的文件
        ---------
        @result:
        '''

        self._remote_url = remote_url
        self._local_save_path = local_save_path
        self._project_path = project_path
        self._main_lnk_paths = main_lnk_paths
        self._sync_files = sync_files
        self._ignore_files = ignore_files

        self._remote_zip_url = ''
        self._tag = ''
        self._zip_path = ''
        self._unpack_path = ''

        self._project_name = tools.get_info(remote_url, '/([^/]*?)/releases', fetch_one = True)
        self._tag_json = tools.get_json(tools.read_file(VERSION_FILE)) or {}

    def __get_per_tag(self):
        return self._tag_json.get(self._project_name, '')

    def __record_current_tag(self, current_tag):
        self._tag_json[self._project_name] = current_tag
        tools.write_file(VERSION_FILE, tools.dumps_json(self._tag_json))

    def check_remote_tag(self):
        '''
        @summary: 检查远程代码的版本
        ---------
        ---------
        @result: True / False (需要更新 / 不需要更新)
        '''
        # 加载上次同步的版本
        log.info('检查版本更新：%s'%self._project_name)
        per_tag = self.__get_per_tag()

        html = tools.get_html_by_requests(self._remote_url)
        regex = '<span class="tag-name">(.*?)</span>'
        current_tag = tools.get_info(html, regex, fetch_one = True)

        if current_tag > per_tag:
            self._tag = current_tag
            self._remote_zip_url = self._remote_url.replace('releases', 'archive/{tag}.zip'.format(tag = current_tag))
            self._zip_path = tools.join_path(self._local_save_path, self._project_name + '-' + self._tag + '.zip')
            self._unpack_path = tools.join_path(self._local_save_path, self._project_name + '-' + self._tag)
            log.info('''
                项目 ：   %s
                本地版本：%s
                同步版本：%s
                版本地址：%s
                正在同步 ...
                '''%(self._project_name, per_tag, current_tag, self._remote_zip_url))
            return True
        else:
            log.info('''
                项目 ：   %s
                本地版本：%s
                同步版本：%s
                版本一致 不需要同步。
                '''%(self._project_name, per_tag, current_tag))

            return False

    def download_code(self):
        tools.download_file(self._remote_zip_url, self._zip_path)
        tools.unpack_zip(self._zip_path, self._unpack_path)


    def copy_file(self):
        unpack_file_root_path = tools.get_next_path(self._unpack_path)
        file_list = tools.walk_file(self._unpack_path)
        for file in file_list:
            if tools.get_info(file, self._sync_files) and not tools.get_info(file, self._ignore_files):
                file_relative_path = file.replace(unpack_file_root_path, '')
                move_to_path = self._project_path + file_relative_path

                is_success = tools.copy_file(file, move_to_path)
                log.debug('''
                        复制文件 %s
                        至       %s
                        是否成功 %s
                        '''%(file, move_to_path, is_success))
                if not is_success:
                    log.error('同步失败：{project_name} ({per_tag} -> {current_tag})'.format(project_name = self._project_name, per_tag = self.__get_per_tag(), current_tag = self._tag))
                    break
        else:
            log.info('同步成功：{project_name} ({per_tag} -> {current_tag})'.format(project_name = self._project_name, per_tag = self.__get_per_tag(), current_tag = self._tag))
            self.__record_current_tag(self._tag)


    def close_process(self):
        pid_file = tools.join_path(self._project_path, 'pid.txt')
        pid = tools.read_file(pid_file)
        command = 'taskkill /F /PID %s'%pid
        log.info(command)
        tools.exec_command(command)

    def start_process(self):
        for main_lnk_path in self._main_lnk_paths:
            command = 'start %s'%main_lnk_path
            log.info(command)
            tools.exec_command(command)

def main():
    # 用记事本打开文件后，会在conf文本头前面加上\ufeff，需要处理掉
    content = tools.read_file('config.conf')
    tools.write_file('config.conf', content.replace('\ufeff', ''))

    # 读配置
    cp = configparser.ConfigParser(allow_no_value = True)
    with codecs.open('config.conf', 'r', encoding='utf-8') as f:
        cp.read_file(f)

    sections = cp.sections()
    for section in sections:
        remote_url = cp.get(section, 'remote_url')
        local_save_path = cp.get(section, 'local_save_path')
        project_path = cp.get(section, 'project_path')
        main_lnk_paths = cp.get(section, 'main_lnk_paths').split(',')
        sync_files = cp.get(section, 'sync_files').split(',')
        ignore_files = cp.get(section, 'ignore_files').split(',')

        # # 调用
        update_code = UpdateCode(remote_url, local_save_path, project_path, main_lnk_paths, sync_files, ignore_files)
        if update_code.check_remote_tag():
            update_code.download_code()
            update_code.copy_file()
            update_code.close_process()
            update_code.start_process()

if __name__ == '__main__':
    while True:
        main()
        tools.delay_time(60 * 60)