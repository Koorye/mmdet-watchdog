# MMDet Watchdog
一款用于监测mmdetection的小工具

## 安装
```
git clone https://github.com/Koorye/mmdet-watchdog.git
pip install -r requirements.txt
```

## 目前功能

### 绘制图表
绘制若干目录的loss和AP统计图，可以指定若干本地或远程目录，程序会自动合并目录里的所有log文件，并绘制loss和AP的分组折线图

编写config文件，格式类似 `configs/example.py`
```python
root = 'xxx'

class Config(object):
    logs = [
        dict(
            name='autoassign',
            dir=root + 'autoassign_r50_fpn_xxx/'),
        dict(
            name='yolox',
            dir=root + 'yolox_s_xxx/'),
         dict(
            name='fcos',
            dir=root + 'fcos_r50_fpn_xxx/')]
```

之后运行命令
```python
python main.py --config configs/example.py
```

就会生成图片`viz.png`
![examples/viz.png]
