#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 https://pvp.qq.com/web201605/herolist.shtml 爬取英雄名字及其皮肤。
图片保存在 ./heroes 目录下，保存名字格式为 英雄名.jpg。

@Author: Fadegentle
@Last Modified by: Fadegentle
@Github: https://github.com/Fadegentle
"""
# TODO:
#  进度条
#  重试
#  日志
#  缩略图
#  增量更新
#  检验个数是否正确，是否损坏

import argparse
import os
import random
import time
from typing import List, Any

import requests
import sqlite3
from fake_useragent import UserAgent
from lxml import etree
from sqlite3 import Cursor

# 参数获取
detail_help = '-d/--detail 展示下载详细信息（默认是不显示）\n-d/--detail show download details (default is not show)'
parser = argparse.ArgumentParser(description=detail_help)
parser.add_argument('-d', '--d', '--detail', dest='detail', action='store_true', help=detail_help)
args = parser.parse_args()
detail = args.detail

# 存储路径检验
save_path = './heroes'
if not os.path.exists(save_path):
    os.makedirs(save_path)

occupations = {
    1: '战士',
    2: '法师',
    3: '坦克',
    4: '刺客',
    5: '射手',
    6: '辅助',
}
data = []

# 伪装
headers = {'User-Agent': UserAgent().random}


def detail_print(s: Any):
    """
    打印细节

    :return: 无
    ----------------------------------------
    Print the details

    :return: None
    """
    if detail:
        print('----------------------------------------')
        print(s)
        print('----------------------------------------')


def create_heroes_table(cur: Cursor, table: str):
    """
    创建表

    :param cur: 游标
    :param table: 表名
    :return: 无
    ----------------------------------------
    Create table

    :param cur: cursor
    :param table: table name
    :return: None
    """
    create = '''
        CREATE TABLE IF NOT EXISTS heroes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ename TEXT NOT NULL,
            name TEXT NOT NULL,
            hero_type TEXT NOT NULL,
            hero_type2 TEXT,
            skins TEXT NOT NULL,
            skins_num INTEGER NOT NULL)
    '''
    cur.execute(create)
    print(f"表 {table} 创建成功")


def insert_data(cur: Cursor, table: str):
    """
    插入数据

    :param cur: 游标
    :param table: 表名
    :return: 无
    ----------------------------------------
    Insert data

    :param cur: cursor
    :param table: table name
    :return: None
    """
    insert = f'INSERT INTO {table} (ename, name, hero_type, hero_type2, skins, skins_num) VALUES (?, ?, ?, ?, ?, ?)'
    cur.executemany(insert, data)


def update_data(cur: Cursor, table: str):
    """
    更新数据

    :param cur: 游标
    :param table: 表名
    :return: 无
    ----------------------------------------
    Update data

    :param cur: cursor
    :param table: table name
    :return: None
    """

    # 检查表是否为空
    cur.execute(f'SELECT COUNT(*) FROM {table}')
    row_count = cur.fetchone()[0]
    if not row_count:
        print(f"表 {table} 为空")
        insert_data(cur, table)
        return

    update = f'UPDATE {table} SET ename=?, name=?, hero_type=?, hero_type2=?, skins=?, skins_num=?'
    cur.executemany(update, data)
    if not cur.rowcount:
        print(f"表 {table} 无数据更新")


def table_is_exist(cur: Cursor ,table: str) -> bool:
    """
    检查表是否存在

    :param cur: 游标
    :param table: 表名
    :return: 是否存在
    ----------------------------------------
    Check if the table exists

    :param cur: cursor
    :param table: table name
    :return: is exist
    """
    query = f'SELECT name FROM sqlite_master WHERE type="table" AND name="{table}"'
    return cur.execute(query).fetchone()


def fresh_db():
    """
    更新数据库，如果不存在则创建并导入数据

    :return: 无
    ----------------------------------------
    Update the database, create and import data if not exist

    :return: None
    """
    database = 'hok-funnier.db'
    conn = sqlite3.connect(database=database)
    print(f"数据库 {database} 连接成功")

    table = 'heroes'
    cur = conn.cursor()
    detail_print(data)

    if table_is_exist(cur, table):
        print(f"表 {table} 已存在")
        update_data(cur, table)
    else:
        print(f"表 {table} 不存在")
        create_heroes_table(cur, table)
        insert_data(cur, table)

    conn.commit()
    cur.close()
    conn.close()
    print(f"表 {table} 数据更新成功")


def get_skins_name(ename: str, cname: str) -> List[str]:
    """
    获取皮肤名字列表

    :param ename: 英雄电子名
    :param cname: 英雄名字
    :return skin_names: 皮肤名字列表
    ----------------------------------------
    Get the list of skin names

    :param ename: hero's electronic name
    :param cname: hero's name
    :return skin_names: list of skin names
    """

    # 访问解析英雄主页网页源码
    hero_info_url = f'https://pvp.qq.com/web201605/herodetail/{ename}.shtml'
    response = requests.get(hero_info_url, headers=headers)
    if response.status_code != 200:
        print(f'{cname}: {hero_info_url} 访问失败')
        return []

    response.encoding = 'gbk'
    result = etree.HTML(response.text)

    # 获取皮肤名字，因为 json 中不全
    skins = result.xpath('//ul[@class="pic-pf-list pic-pf-list3"]/@data-imgname')[0]
    skin_names = [n.split('&')[0] for n in skins.split('|')]

    return skin_names


def get_skin_img(ename: str, cname: str, skin_names: List[str]):
    """
    获取皮肤图片

    :param ename: 英雄电子名
    :param cname: 英雄名字
    :param skin_names: 皮肤名字列表
    :return: 无
    ----------------------------------------
    Get the skin images

    :param ename: hero's electronic name
    :param cname: hero's name
    :param skin_names: list of skin names
    :return: None
    """
    for i, n in enumerate(skin_names):
        img_path = f'{save_path}/{cname}/{n}.jpg'
        if os.path.exists(img_path):
            detail_print(f'{img_path} 已存在')
            continue
        img_url = f'https://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{ename}/{ename}-bigskin-{i + 1}.jpg'
        img_data = requests.get(img_url, headers=headers).content
        with open(img_path, 'wb') as f:
            f.write(img_data)
            detail_print(f'{img_path} 下载成功')
            time.sleep(random.uniform(0.2, 0.8))


def get_herolist():
    """
    获取英雄的名字及其皮肤图片

    :return: 无
    ----------------------------------------
    Gather the names and skin-images of the heroes

    :return: None
    """

    # 获取英雄列表 json
    herolist_json_url = 'https://pvp.qq.com/web201605/js/herolist.json'
    herolist_json = requests.get(herolist_json_url, headers=headers).json()

    # 获取所有的英雄信息
    for hero in herolist_json:
        # 获取所有英雄的电子名、中文名、职业、第二职业
        ename = hero.get('ename')
        cname = hero.get('cname')
        hero_type = occupations.get(hero.get('hero_type'))
        hero_type2 = occupations.get(hero.get('hero_type2', ''))

        # 检查英雄目录
        if not os.path.exists(f'{save_path}/{cname}'):
            os.makedirs(f'{save_path}/{cname}')

        # 获取皮肤
        if not (skin_names := get_skins_name(ename, cname)):
            continue
        get_skin_img(ename, cname, skin_names)
        data.append((ename, cname, hero_type, hero_type2, '|'.join(skin_names), len(skin_names)))

    print('资源下载完成')
    fresh_db()


if __name__ == '__main__':
    get_herolist()
