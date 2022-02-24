#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 10:39
# @Author  : liyubin

"""
文件内容搜索
"""
import json


def read_file_text(file):
    """读取文件内容"""
    try:
        if file.suffix.lower() in ('.exe', '.mp4', '.png', '.jpg'):
            return ''
        elif file.suffix.lower() in ('.xls', '.xlsx'):
            return read_excel(file)
        elif file.suffix.lower() == '.csv':
            return read_csv(file)
        elif file.suffix.lower() in ('.pptx', '.ppt'):
            return read_ppt(file)
        elif file.suffix.lower() in ('.docx', '.doc'):
            return read_doc(file)
        elif file.suffix.lower() == '.xmind':
            return read_xmind(file)
        elif file.suffix.lower() == '.pdf':
            return read_pdf(file)
        else:
            with open(file.as_posix(), 'r', encoding='utf8') as fp:
                if file.as_posix().endswith('json'):
                    return json.load(fp)
                else:
                    return fp.read()
    except Exception as e:
        print('e: ', e)


def read_excel(file):
    pass


def read_csv(file):
    pass


def read_ppt(file):
    pass


def read_doc(file):
    pass


def read_xmind(file):
    pass


def read_pdf(file):
    pass


def filter_term_in(search_term, read_data):
    """搜索文件内容"""
    try:
        if search_term in read_data:
            return True
        else:
            return False
    except Exception as e:
        print('e: ', e)
