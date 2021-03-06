#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: StudyEveryday
@file: __init__.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-08-02(星期五) 16:35
@Copyright © 2019. All rights reserved.
'''

from pathlib import Path
import re
from configparser import ConfigParser
from .logs import create_logger
from time import sleep
#from . import logger, cfg

path = Path(__file__).parent
for item in ['json', 'xml', 'xls']:
    p = path/'src'/item
    p.mkdir(parents=True, exist_ok=True)
logger = create_logger('xuexi', 'DEBUG')
cfg = ConfigParser()
cfg.read(path/'config-default.ini', encoding='utf-8')
cfg.read(path/'config-custom.ini', encoding='utf-8')

class App(object):
    def __init__(self):
        self.rules = cfg.get('common', 'device')
        # print("rules:", self.rules)
        self.xmluri = Path(cfg.get(self.rules, 'xml_uri'))
        # print("xmluri:", self.xmluri)
        self.ad = adble.Adble(
                            self.xmluri,
                            cfg.getboolean(self.rules, 'is_virtual_machine'), 
                            cfg.get(self.rules, 'host'),
                            cfg.getint(self.rules, 'port'))
        self.xm = xmler.Xmler(self.xmluri)

    def _art_run(self):
        logger.debug(f'阅读文章,开始')
        rd = reader.Reader(self.rules, self.ad, self.xm)
        count = cfg.getint('common', 'article_count')
        delay = cfg.getint('common', 'article_delay')
        ssc = cfg.getint('common', 'star_share_comment')       # star_share_comment 收藏、分享、留言
        rd.run(count, delay, ssc)


    def _vdo_run(self):
        logger.debug(f'视听学习，开始')
        vd = viewer.Viewer(self.rules, self.ad, self.xm)
        count = cfg.getint('common', 'video_count')
        delay = cfg.getint('common', 'video_delay')
        vd.run(count, delay)

    def _quiz_run(self, day, chg):
        logger.debug(f'我要答题，开始')
        qApp = Quiz(self.rules, self.ad, self.xm)
        qApp.start(day, chg)

    def _getScore(self):
        self.ad.uiautomator()
        self.xm.load()
        wode=self.xm.pos(cfg.get(self.rules, 'rule_wode_bounds'))
        print("wode:",wode,type(wode))
        sleep(5)
        self.ad.tap(wode)
        print("tap")
        sleep(2)
        self.ad.uiautomator()
        self.xm.load()
        sleep(2)
        # wodejifen = self.xm.pos(cfg.get(self.rules, 'rule_wode_score_bounds'))
        # self.ad.tap(wodejifen)
        # self.ad.uiautomator()
        # self.xm.load()
        # sleep(2)
        # readcount = self.xm.texts(cfg.get(self.rules, 'rule_readcount_content'))
        # videocount = self.xm.texts(cfg.get(self.rules, 'rule_videocount_content'))
        # readtime = self.xm.texts(cfg.get(self.rules, 'rule_readtime_content'))
        # videotime = self.xm.texts(cfg.get(self.rules, 'rule_videotime_content'))
        # daylycount = self.xm.texts(cfg.get(self.rules, 'rule_daylycount_content'))
        # challcount = self.xm.texts(cfg.get(self.rules, 'rule_challcount_content'))
        # print(readcount, videocount, readtime, videotime, daylycount, challcount)

        # back_pos = self.xm.pos(cfg.get(self.rules, 'rule_back'))
        self.ad.back()
        sleep(2)
        self.ad.uiautomator()
        self.xm.load()
        #xuexi_pos = self.xm.pos(cfg.get(self.rules, 'rule_xuexi_bounds'))
        #self.ad.tap(xuexi_pos)


        pass



    def start(self, art, vdo, day, chg):
        #self._getScore()
        if day or chg:
            with timer.Timer() as t:
                self._quiz_run(day, chg)
            logger.info(f'答题耗时 {round(t.elapsed, 2)} 秒')

        if vdo:
            with timer.Timer() as t:
                self._vdo_run()
            logger.info(f'观影耗时 {round(t.elapsed, 2)} 秒')
        
        if art:
            with timer.Timer() as t:
                self._art_run()
            logger.info(f'阅读耗时 {round(t.elapsed, 2)} 秒')
        

    def __del__(self):
        self.ad.close()


    
        


from .common import adble, xmler, timer
from .model import Model
from .quiz import Quiz
from .media import viewer, reader