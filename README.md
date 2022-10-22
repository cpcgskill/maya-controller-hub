# maya-controller-hub

maya控制器库实现

## 目录

- [快速开始](#快速开始)
    * [安装](#安装)
    * [使用](#使用)
- [版权说明](#版权说明)

## 快速开始

### 安装

注意下方的python是你的Python, 正常情况下可以直接通过python调用, 而Maya的python一般是C:\Program
Files\Autodesk\<Maya版本>\bin\mayapy.exe

```commandline
python -m pip install maya-controller-hub
```

在windows下maya的安装例子

注意:

1. 请将Maya路径替换为自己的。
2. 请使用cmd

```commandline
"C:\Program Files\Autodesk\Maya2018\bin\mayapy.exe" -m pip install maya-controller-hub
```

### 使用

#### 例子

```python
# -*-coding:utf-8 -*-
from __future__ import unicode_literals, print_function, division
import cpmel.cmds as cc
from rig_core.all import *
from controller_hub import ControllerHub

ctx = Ctx()
for i in range(4):
    cc.mel.eval('circle -c 0 0 0 -nr 0 1 0 -sw 360 -r 1 -d 3 -ut 0 -tol 0.1 -s 8 -ch 0;')

with ControllerHub(ctx, 'your-controller-hub-path') as control_hub:
    print('control_hub', control_hub)
    control_hub.use_template(
        'cp.cube',
        [cc.new_object('nurbsCircle1')],
        translate=(1, 1, 1),
        color='#19448e')  # 一个蓝色的正方体控制器
    control_hub.use_template(
        'cp.octahedron',
        [cc.new_object('nurbsCircle2')],
        rotate=(45, 45, 45),
        color=(0.8, 0.8, 0.8))  # 一个白色的正八面体控制器
    control_hub.use_template(
        'cp.flower',
        [cc.new_object('nurbsCircle3')],
        rotate='+y',
        color=(0, 0, 0))  # 一个黑色的花形控制器
    control_hub.use_template(
        'cp.triangle',
        [cc.new_object('nurbsCircle4')],
        scale=(1.5, 1.5, 1.5),
        color=14)  # 一个绿色的三角形控制器
```

## 版权说明

该项目签署了Apache-2.0 授权许可，详情请参阅 LICENSE

