import json
import os
import pandas as pd
import patchworklib as pw
from plotnine import ggplot, aes, geom_line, geom_text, facet_wrap

from .file import FileLoader


class Stats(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.file_loader = FileLoader()
    
    def stat_and_draw(self):
        self.load_json_logs()
        self.split_and_unique()
        self.draw()
    
    def load_json_logs(self):
        """
        读取cfg中所有log目录，建立name到dataframe的字典name2df_raw
        形如：{'my_model1': <pd.Dataframe>,
              'my_model2': <pd.Dataframe>}
        """
        self.name2df_raw = dict()
        for log in self.cfg.logs:
            print('Loading log: {}...'.format(log['name']))
            work_dir = log['dir']
            # df_raw = self._load_json_log_dir(work_dir)
            df_raw = self.file_loader.load_json_log_dir(work_dir)
            self.name2df_raw[log['name']] = df_raw
    
    def split_and_unique(self):
        """
        将name2df_raw中的每个dataframe转换为mode到dataframe的字典mode2name2df
        dataframe每个行会根据log文件的创建时间进行排序，保留最新的数据
        形如：{'train': {'my_model1': <pd.Dataframe>,
                        'my_model2': <pd.Dataframe>},
              'val':   {'my_model1': <pd.Dataframe>,
                        'my_model2': <pd.Dataframe>}}
        """
        def get_latest(df, mode):
            assert mode in ['train', 'val']
            df = df[df['mode'] == mode]
            subset = ['mode', 'epoch', 'iter'] if mode == 'train' else ['mode', 'epoch']
            df = df.sort_values('time_create').dropna(axis=1).drop_duplicates(subset, keep='last').reset_index(drop=True)
            return df
        
        modes = []
        for name in self.name2df_raw:
            modes += self.name2df_raw[name]['mode'].tolist()
        modes = list(set(sorted(modes)))

        self.mode2name2df = dict()
        for mode in modes:
            name2df = dict() 
            for name in self.name2df_raw:
                df_ = get_latest(self.name2df_raw[name], mode)
                name2df[name] = df_
            self.mode2name2df[mode] = name2df
    
    def draw(self):
        p1 = self.draw_train(self.mode2name2df['train'])
        p2 = self.draw_val(self.mode2name2df['val'])
        print('Start concating plots...')
        p1 = pw.load_ggplot(p1, figsize=(15, 10))
        p2 = pw.load_ggplot(p2, figsize=(15, 10))
        p = p1 / p2
        p.savefig('viz.png')
        print('Concating finished, plot saved to viz.png!')
    
    def draw_train(self, name2df):
        print('Start drawing train plot...')
        dfs = []
        for name in name2df:
            df_ = name2df[name]
            df_['name'] = name
            dfs.append(df_)
        df = pd.concat(dfs).drop(columns=['mode', 'lr', 'memory', 'data_time', 
                                          'time', 'time_create'])
        df['global_iter'] = (df['epoch'] - 1) * df['iter'].max() + df['iter']
        df = df.drop(columns=['epoch', 'iter'])
        print('Train dataframe:')
        print(df.head())

        df = df.melt(id_vars=['global_iter', 'name'])
        return (
            ggplot(df, aes('global_iter', 'value', color='name'))
            + geom_line()
            + facet_wrap('variable', scales='free')
        )
        
    def draw_val(self, name2df):
        print('Start drawing val plot...')
        dfs = []
        for name in name2df:
            df_ = name2df[name]
            df_['name'] = name
            dfs.append(df_)
        df = pd.concat(dfs).drop(columns=['mode', 'iter', 'lr', 'bbox_mAP_copypaste', 'time_create'])
        print('Val dataframe:')
        print(df.head())
        df = df.melt(id_vars=['epoch', 'name'])
        return (
            ggplot(df, aes('epoch', 'value', color='name', label='value'))
            + geom_line()
            + geom_text(va='bottom', size=5)
            + facet_wrap('variable', scales='free')
        )
            
