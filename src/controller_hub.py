# -*-coding:utf-8 -*-
"""
:创建时间: 2022/10/15 19:14
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division
import json
import os
import re

import cpmel.cmds as cc
from rig_core.all import *

if False:
    from typing import AnyStr, Dict, Tuple, List

_color_id_to_hex_color_map = {
    0: "#787878",
    1: "#000000",
    2: "#404040",
    3: "#999999",
    4: "#9b0028",
    5: "#000460",
    6: "#0000ff",
    7: "#004619",
    8: "#260043",
    9: "#c800c8",
    10: "#8a4833",
    11: "#3f231f",
    12: "#992600",
    13: "#ff0000",
    14: "#00ff00",
    15: "#004199",
    16: "#ffffff",
    17: "#ffff00",
    18: "#64dcff",
    19: "#43ffa3",
    20: "#ffb0b0",
    21: "#e4ac79",
    22: "#ffff63",
    23: "#009954",
    24: "#a16a30",
    25: "#9ea130",
    26: "#68a130",
    27: "#30a15d",
    28: "#30a1a1",
    29: "#3067a1",
    30: "#6f30a1",
    31: "#a1306a",
}


def _hex_color_to_hsv(hex_color):
    """

    :param hex_color:
    :rtype: (float, float, float)
    """
    if hex_color[0] == '#':
        hex_color = hex_color[1:]
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return r, g, b


def _clear_shape(ctx, *objs):
    """

    :type ctx: Ctx
    :param objs:
    :return:
    """
    for obj in objs:
        shapes = cc.listRelatives(obj, s=True, pa=True)
        if shapes is not None:
            ctx.delete_node(shapes)
    if 'automatic_view_refresh' in ctx.feature:
        cc.refresh()


def _add_shape(ctx, obj, shape_obj):
    """

    :type ctx: Ctx
    :param obj:
    :param shape_obj:
    :return:
    """
    new_shape_obj = shape_obj.copy()
    shapes = cc.listRelatives(new_shape_obj, s=True, pa=True)
    if shapes is not None:
        for i in shapes:
            cc.parent(i, obj, s=True, add=True)
    ctx.delete_node(new_shape_obj)
    if 'automatic_view_refresh' in ctx.feature:
        cc.refresh()


def _replace_shape(ctx, obj, shape_obj):
    """

    :type ctx: Ctx
    :param obj:
    :param shape_obj:
    :return:
    """
    _clear_shape(ctx, obj)
    _add_shape(ctx, obj, shape_obj)


class ControllerHub(object):
    def __init__(self, ctx, source_dir, global_size=1.0):
        source_dir = os.path.abspath(source_dir)
        self.__ctx = ctx  # type: Ctx
        self.__global_size = global_size
        self.__nodes_that_need_to_perform_gc = list()
        self.__control_table = dict()  # type: Dict[AnyStr, cc.Transform]
        self.__name_remake_regexp = re.compile('^[a-zA-Z0-9_]')
        for root, dirs, files in os.walk(source_dir):
            for f in files:
                f = os.sep.join([root, f])
                name = f.split(os.sep)[len(source_dir.split(os.sep)):]
                name = name[:-1] + ['-'.join(name[-1].split('.')[:-1])]
                if any((i[0] == '.' for i in name[:-1])):
                    continue
                name = '.'.join((self.__name_remake_regexp.sub(i, '_') for i in name))
                if f.split('.')[-1] == 'control':
                    with open(f, 'rb') as f_handle:
                        data = json.loads(f_handle.read().decode('utf-8'))
                    if data['version'] == '1':
                        if data['type'] == 'NurbsCurve':
                            self.__control_table[name] = cc.curve(
                                d=data['data']['degree'],
                                p=data['data']['cvs'],
                                k=data['data']['knots'],
                                per=data['data']['is_periodic']
                            )
        self.add_to_gc(*self.__control_table.values())

    def add_to_gc(self, *nodes):
        """
        将控制器添加到自动回收

        :type nodes: cc.Transform
        :rtype: ControllerHub
        """
        for n in nodes:
            self.__nodes_that_need_to_perform_gc.append(n)
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__ctx.delete_node(*self.__nodes_that_need_to_perform_gc)

    def __unicode__(self):
        return '{}{}'.format(self.__class__.__name__, self.__control_table)

    def __str__(self):
        return str('{}{}'.format(self.__class__.__name__, self.__control_table))

    def __getitem__(self, item):
        """

        :type item: AnyStr
        :rtype: cc.Transform
        """
        return self.__control_table[item]

    def read_template(self, name, translate=(0, 0, 0), rotate=(0, 0, 0), scale=1, color=None):
        """
        获得自动名称的模板

        :type name: AnyStr
        :type translate: Tuple[float, float, float]
        :type rotate: AnyStr or Tuple[float, float, float]
        :type scale: float or Tuple[float, float, float]
        :type color: int or AnyStr or Tuple[float, float, float]
        :rtype: cc.Transform
        """

        template = self[name].copy()
        self.add_to_gc(template)
        if isinstance(scale, (int, float)):
            scale = scale * self.__global_size
            template.scale = (scale, scale, scale)
        else:
            scale = (scale[0] * self.__global_size, scale[1] * self.__global_size, scale[2] * self.__global_size)
            template.scale = scale
        if isinstance(rotate, (type(''), type(b''))):
            axial_table = {
                'x': (0, 0, 0),
                'y': (0, 0, 90),
                'z': (0, -90, 0),

                '+x': (0, 0, 0),
                '+y': (0, 0, 90),
                '+z': (0, -90, 0),

                '-x': (0, 0, 180),
                '-y': (0, 0, -90),
                '-z': (0, 90, 0),
            }
            rotate = axial_table[rotate.lower()]

        template.rotation = rotate
        template.translation = (
            translate[0] * self.__global_size,
            translate[1] * self.__global_size,
            translate[2] * self.__global_size,
        )
        if color is not None:
            # 如果是以#3067a1这种形式输入的颜色就先转化为rgb(0-1)颜色
            if isinstance(color, (type(b''), type(''))):
                color = _hex_color_to_hsv(color)

            if isinstance(color, int):
                # 如果是id颜色
                for i in template.shapes:
                    i.overrideEnabled.set_value(1)
                    i.overrideColor.set_value(color)

                template.useOutlinerColor.set_value(True)
                template.outlinerColor.set_value(_hex_color_to_hsv(_color_id_to_hex_color_map[color]))
                template.shape.useOutlinerColor.set_value(True)
                template.shape.outlinerColor.set_value(_hex_color_to_hsv(_color_id_to_hex_color_map[color]))
            else:
                # 如果是rgb(0-1)颜色
                for i in template.shapes:
                    i.overrideEnabled.set_value(1)
                    i.overrideRGBColors.set_value(1)
                    i.overrideColorRGB.set_value(color)

                template.useOutlinerColor.set_value(True)
                template.outlinerColor.set_value(color)
                template.shape.useOutlinerColor.set_value(True)
                template.shape.outlinerColor.set_value(color)

        cc.makeIdentity(template, apply=True, t=1, r=1, s=1, n=0, pn=1)
        cc.makeIdentity(template, apply=False, t=1, r=1, s=1)
        cc.delete(template, ch=True)
        return template

    def use_template(self,
                     template_name, target_controller_list,
                     translate=(0, 0, 0), rotate=(0, 0, 0), scale=1,
                     color=None
                     ):
        """
        为目标控制器列表使用指定名称的模板

        :type template_name: AnyStr
        :type target_controller_list: List[cc.Transform]
        :type translate: Tuple[float, float, float]
        :type rotate: AnyStr or Tuple[float, float, float]
        :type scale: float or Tuple[float, float, float]
        :type color: int or AnyStr or Tuple[float, float, float]
        :rtype: ControllerHub
        """
        template = self.read_template(template_name,
                                      translate=translate,
                                      rotate=rotate,
                                      scale=scale,
                                      color=color,
                                      )
        for c in target_controller_list:
            _replace_shape(self.__ctx, c, template)
            c.useOutlinerColor.set_value(template.useOutlinerColor.get_value())
            c.outlinerColor.set_value(template.outlinerColor.get_value())

        return self


__all__ = ['ControllerHub']

if __name__ == '__main__':
    def test():
        from maya_test_tools import open_file, question_open_maya_gui

        ctx = Ctx()
        for i in range(4):
            cc.mel.eval('circle -c 0 0 0 -nr 0 1 0 -sw 360 -r 1 -d 3 -ut 0 -tol 0.1 -s 8 -ch 0;')

        # control_hub = ControlHub(ctx, './../test/control_hub/')
        with ControllerHub(ctx, './../test/control_hub/') as control_hub:
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

        question_open_maya_gui()


    test()
