import json
import os
import pandas as pd
import re
import shutil

from .ssh import SSH


class FileLoader(object):   
    def load_json_log_dir(self, log_dir):
        """
        读取某个目录下的所有json log文件并拼接为dataframe
        : param include_keys list<str>: 包含include_keys中所有key的行将被保留
        """
        if re.match(r'^\w+:.+\@\d+\.\d+\.\d+\.\d+(:\d+)?:(/.*)+$', log_dir):
            return self.load_log_dir_remote(log_dir)
        self.load_log_dir_local(log_dir)

    def load_log_dir_local(self, log_dir):
        filenames = os.listdir(log_dir)
        json_log_names = list(filter(lambda filename: filename.endswith('.log.json'), filenames))
        dfs_raw = []
        for log_name in json_log_names:
            log_path = os.path.join(log_dir, log_name)
            df_raw = self._load_json_log_single(log_path)
            dfs_raw.append(df_raw)
        df_raw = pd.concat(dfs_raw)
        return df_raw

    def load_log_dir_remote(self, log_dir):
        assert re.match(r'^\w+:.+\@\d+\.\d+\.\d+\.\d+(:\d+)?:(/.*)+$', log_dir)
        s = log_dir.split(':')
        if len(s) == 3:
            username, meta, download_dir = s
            password, ip = meta.split('@')
            ssh = SSH(username, password, ip)
        else:
            username, meta, port, download_dir  = s
            password, ip = meta.split('@')
            ssh = SSH(username, password, ip, int(port))
        
        tmp = download_dir[:-1] if download_dir.endswith('/') else download_dir
        save_dir = os.path.join('cache', tmp.split('/')[-1]).replace('\\', '/')
        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        os.makedirs(save_dir)
        ssh.download_dir(download_dir, save_dir, suffix='.log.json')
        return self.load_log_dir_local(save_dir)

    def _load_json_log_single(self, log_path):
        """
        读取json log文件转换为dataframe，并添加创建时间信息
        : param log_path str:
        """
        assert log_path.endswith('.log.json')
        log_name = log_path.replace('\\', '/').split('/')[-1].split('.')[0]
        time_create = int(log_name.split('.')[0])
        with open(log_path) as f:
            lines = f.readlines()
        df_raw = []
        for line in lines:
            res = json.loads(line)
            if 'mode' in res.keys():
                df_raw.append(res)
        df_raw = pd.DataFrame(df_raw)
        df_raw['time_create'] = time_create
        return df_raw
    