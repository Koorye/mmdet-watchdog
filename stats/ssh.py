import os
import paramiko


class SSH(object):
    def __init__(self, username, password, host, port=22):
        t = paramiko.Transport((host, port))
        t.connect(username=username, password=password)
        self.sftp = paramiko.SFTPClient.from_transport(t)
        print(f'Connecting success: {username}@{host}!')
    
    def download_dir(self, download_dir, save_dir, prefix=None, suffix=None):
        filenames = self.ls(download_dir)
        filenames = list(filter(lambda x: x.startswith(prefix), filenames)) if prefix is not None else filenames
        filenames = list(filter(lambda x: x.endswith(suffix), filenames)) if suffix is not None else filenames
        for filename in filenames:
            download_path = os.path.join(download_dir, filename).replace('\\', '/')
            save_path = os.path.join(save_dir, filename).replace('\\', '/')
            self.download_path(download_path, save_path)

    def ls(self, dir):
        return self.sftp.listdir(dir)

    def download_path(self, download_path, save_path):
        print(f'Download from: {download_path} -> {save_path}')
        self.sftp.get(download_path, save_path)
   