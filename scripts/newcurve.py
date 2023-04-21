#!/usr/bin/python
# -*-coding:utf-8 -*-
u"""
:创建时间: 2021/5/18 8:23
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:QQ: 2921251087
:爱发电: https://afdian.net/@Phantom_of_the_Cang
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127

"""
from __future__ import unicode_literals, print_function, division

import os

import cpmel.cmds as cc
import json

obj = "bezierShape1"
language = "mel"


def new_controller_code(obj, language):
    obj_typ = cc.objectType(obj)
    o = cc.new_object(obj)
    if obj_typ == "bezierCurve":
        fn = o.api1_m_fn()
        # 曲线度数
        degree = o.degree()
        # 曲线点
        pts = o.get_points()
        # 曲线结值
        knots = [fn.knot(i) for i in range(o.num_knots())]
        if language == "mel":
            p_str = u" ".join([u"-p {} {} {}".format(i[0], i[1], i[2]) for i in pts])
            knots_str = u" ".join([u"-k {}".format(i) for i in knots])
            return u"curve -bezier -d {} {} {};".format(degree, p_str, knots_str)
        elif language == "python":
            p_str = u", ".join([u"({}, {}, {})".format(i[0], i[1], i[2]) for i in pts])
            knots_str = u", ".join([repr(i) for i in knots])
            return u"curve(bezier=True, d={}, p=[{}], k=[{}])".format(degree, p_str, knots_str)
        elif language == "json":
            pts = [(i[0], i[1], i[2]) for i in pts]
            return json.dumps({
                "type": "bezierCurve",
                "data": {
                    "cvs": pts,
                    "knots": knots,
                    "degree": degree
                }
            })
    elif obj_typ == "nurbsCurve":
        fn = o.api1_m_fn()
        # 曲线度数
        degree = o.degree()
        # 曲线点
        pts = o.get_points()
        # 曲线结值
        knots = [fn.knot(i) for i in range(o.num_knots())]
        # 曲线形式
        form = fn.form()
        is_periodic = form == 3
        if language == "mel":
            p_str = u" ".join([u"-p {} {} {}".format(i[0], i[1], i[2]) for i in pts])
            knots_str = u" ".join([u"-k {}".format(i) for i in knots])

            return u"curve -d {} {} {};".format(degree, p_str, knots_str)
        elif language == "python":
            p_str = u", ".join([u"({}, {}, {})".format(i[0], i[1], i[2]) for i in pts])
            knots_str = u", ".join([repr(i) for i in knots])
            return u"curve(d={}, p=[{}], k=[{}], per={})".format(degree, p_str, knots_str, is_periodic)
        elif language == "json":
            pts = [(i[0], i[1], i[2]) for i in pts]
            return json.dumps({
                "type": "nurbsCurve",
                "data": {
                    "cvs": pts,
                    "knots": knots,
                    "degree": degree,
                    "is_periodic": is_periodic,
                }
            })
        elif language == 'rig_post_processing_json_v1':
            pts = [(i[0], i[1], i[2]) for i in pts]
            return json.dumps({
                'version': '1',
                "type": 'NurbsCurve',
                "data": {
                    "cvs": pts,
                    "knots": knots,
                    "degree": degree,
                    "is_periodic": is_periodic,
                }
            })


def new_control_hub_file(path, name):
    obj = cc.selected()[0]
    json_str = new_controller_code(obj, 'rig_post_processing_json_v1')
    with open(os.sep.join([path, "{}.control".format(name)]), 'wb') as f:
        f.write(json_str.encode('utf-8'))


if __name__ == "__main__":
    new_control_hub_file(r'E:\backup_to_cloud\dev\python_for_maya\package\rig_lib\test\control_hub\cp', 'square-based-pyramid')
