#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: quizXue
@file: reader.py
@author: kessil
@contact: https://github.com/kessil/quizXue/
@time: 2019-08-09(星期五) 12:01
@Copyright © 2019. All rights reserved.
'''
import json,datetime
from random import choice
from pathlib import Path
from time import sleep
from .. import logger, cfg
from ..common import timer


class Reader:
    '''设计思路：
        0. 前提，APP位于首页
        1. 点击Home，找到订阅栏，要求用户有订阅公号，建议取关各大学习平台，因为学习平台喜欢上传本地新闻联播视频
        2. 点击订阅栏，刷新
        3. 保存第一个Item坐标
        4. 依次学习后续可点击Item（第二个开始），将最后一个Item拉至第一个Item处
        5. 在第一轮阅读中插入收藏、分享、评论操作
        6. 重复步骤4直到完成指定篇数新闻阅读
        7. 退出文章学习（其实不用退出，本来就在Home页
    '''
    def __init__(self, rules, ad, xm):
        self.rules = rules
        self.ad = ad
        self.xm = xm

        self.home = 0j
        self.feeds = 0j
        self.fixed = 0j
        self.json_comments = self._load()

    def _fresh(self):
        sleep(1)
        self.ad.uiautomator()
        self.xm.load()

    def _load(self):
        '''load json file'''
        path = Path(cfg.get('common', 'comments_json'))
        res = []
        if path.exists():
            with open(path,'r',encoding='utf-8') as fp:
                try:
                    res = json.load(fp)
                except Exception:
                    logger.debug(f'加载JSON数据失败')
                logger.debug(res)
            logger.debug(f'载入JSON数据{path}')
            return res
        else:
            logger.debug('JSON文件{path}不存在')
            return res

    def _dump(self, data):
        '''save json file'''
        filename = cfg.get('common', 'comments_json')        
        with open(filename,'w',encoding='utf-8') as fp:
            json.dump(data,fp,indent=4,ensure_ascii=False)
        logger.debug(f'导出JSON数据{filename}')
        return True

    def enter(self):
        # 进入‘订阅’，要求用户首先订阅公号
        self._fresh()
        self.home = self.xm.pos(cfg.get(self.rules, 'rule_bottom_work'))
        self.ad.tap(self.home)
        # print(list(columns)[-1])
        # 找到“订阅”栏，这里第一次感受到while...else...和for...else...的妙处
        # columns = [(t, p) for t, p in zip(self.xm.texts(cfg.get(self.rules, 'rule_columns_content')),
        #                                   self.xm.pos(cfg.get(self.rules, 'rule_columns_bounds')))]
        # p0, p1 = columns[0][1], columns[-1][1]
        # self.ad.slide(p0, p1, duration=1000)
        # self.ad.slide(p0, p1, duration=1000)
        # self.ad.slide(p0, p1, duration=1000)
        # sleep(3)

        while 0j == self.feeds:


            columns = [(t, p) for t, p in zip(self.xm.texts(cfg.get(self.rules, 'rule_columns_content')), self.xm.pos(cfg.get(self.rules, 'rule_columns_bounds')))]
            #logger.info(str(self.xm.pos(cfg.get(self.rules, 'rule_columns_bounds'))))
            #logger.info(str(columns))
            #print("read_line83:columns=",columns)
            p0, p1 = columns[0][1], columns[-1][1]
            for col in columns:
                
                if '订阅' == col[0]:
                #if '新思想' == col[0]:
                    self.feeds = col[1]
                    break
            else:
                self.ad.slide(p1,p0, duration=1000)
                self._fresh()
        else:
            self.ad.tap(self.feeds)
            sleep(3) # 等3秒刷新


    def _read_news(self, count, delay):     
        '''一篇新闻耗时包括：指定阅读时间+5秒等待渲染时间+5秒划动时间+3~5秒程序运行时间+评论收藏分享时间（如果有的话）'''   
        total_delay = delay
        # logger.info(f'[{count}] 正在阅读，请勿打扰！{total_delay}秒...')
        
        slide_times = 5 # 上划次数
        per_delay = total_delay // slide_times
        logger.debug(f'阅读时长{total_delay},上划{slide_times}次，每次{per_delay}秒')
        sleep(5) # 等待文章渲染
        for i in range(slide_times):
            self.ad.draw('up', distance=500)
            sleep(per_delay)

    def _star_share_comment(self, msg):
        self._fresh()
        pos_star = self.xm.pos(cfg.get(self.rules, 'rule_star_bounds'))
        pos_share = self.xm.pos(cfg.get(self.rules, 'rule_share_bounds'))
        pos_comment = self.xm.pos(cfg.get(self.rules, 'rule_comment_bounds'))

        # 分享
        self.ad.tap(pos_share)
        sleep(1)
        self.ad.uiautomator(filesize=6000)
        self.xm.load()
        pos_share2xuexi = self.xm.pos(cfg.get(self.rules, 'rule_share2xuexi_bounds'))
        self.ad.tap(pos_share2xuexi)
        # logger.debug(f'分享一篇文章')
        logger.info(f'分享一篇文章!')
        sleep(1)
        self.ad.back()
        sleep(1)

       
        # 留言
        self.ad.tap(pos_comment)
        sleep(1)
        
        self.ad.input(msg)
        logger.info(f'留言一篇文章: {msg}')        
        sleep(1)
        self.ad.uiautomator(filesize=2000)
        self.xm.load()
        pos_publish = self.xm.pos(cfg.get(self.rules, 'rule_publish_bounds'))
        self.ad.tap(pos_publish)
        self.ad.tap(pos_publish-23j) # 不知道为什么，有时发布按钮解析的位置会出现23px的偏差，所以，这里点击两次怕点不到
        sleep(1)

        # 收藏
        self.ad.tap(pos_star)
        # logger.debug(f'收藏一篇文章 {pos_star}')
        logger.info(f'收藏一篇文章!')
        sleep(1) 


    def collect_comments(self, tag='default'):
        json_comments = self._load()
        flag = True
        rule = f'//node[@text="・回复"]/../preceding-sibling::node[1]/node'
        middle_width = min(self.ad.wmsize)//2
        logger.debug(f'抓取评论，开始！')
        self._fresh()
        pos = self.xm.pos('//node[@text="欢迎发表你的观点"]/../node[2]/@bounds')
        self.ad.tap(pos)
        sleep(2)
        while flag:
            self._fresh()
            comments = [(t,p) for t,p in zip(self.xm.texts(f'{rule}/@text'), self.xm.pos(f'{rule}/@bounds'))]
            fixed = (100, comments[0][1].imag)[len(comments)>0]
            for comment in comments:                
                if len(comment[0]) < 15:
                    logger.debug(f'放弃 {comment[0]}')
                else: # if else
                    if comment[0] in json_comments.get(tag, list()):
                        logger.debug(f' 重复 {comment[0]}')
                    else: # if else
                        logger.info(f'添加 {comment[0]}')
                        json_comments.setdefault(tag, list()).append(comment[0])
            else: # for else
                if self.xm.pos('//node[@text="已显示全部观点"]/@bounds'):
                    flag = False
                    break
                else:
                    dynamic = (max(self.ad.wmsize)-100, comment[1].imag)[len(comments)>0]
                    self.ad.slide(complex(middle_width, dynamic), complex(middle_width, fixed))
        self._dump(json_comments)




    def run(self, count=25, delay=30, ssc=2):
        self.enter()    
        logger.info(f'新闻学习中...')      
        while count>0:
            self._fresh()
            #logger.info(str(self.xm.texts(cfg.get(self.rules, 'rule_news_content'))))
            #if(len(self.xm.pos(cfg.get(self.rules, 'rule_news_bounds')))<2):
            #print("reader_lin193:", self.xm.texts(cfg.get(self.rules, 'rule_news_content')))
            #print(self.xm.pos(cfg.get(self.rules, 'rule_news_bounds')))
            today = str(datetime.date.today())
            pos_rule = cfg.get(self.rules, 'rule_news_bounds')
            pos_rule = pos_rule.replace("2020-03-01",today)
            pos = self.xm.pos(pos_rule)
            
            content_rule = cfg.get(self.rules, 'rule_news_content')
            content_rule = content_rule.replace("2020-03-01",today)
            content = self.xm.texts(content_rule)

            # print("reader_205_pos:",pos)
            if(len(pos)==1):
                pos = [pos]

            articles = [(t, p) for t, p in zip(content, pos)]
            logger.info(f"aricles:{articles}")
            if(articles == []):
                print("slide")
                self.ad.swipe(500, 1300, 500, 300, 1000)
                sleep(3)

            if 0j == self.fixed:
                self.fixed = self.xm.pos(cfg.get(self.rules, 'rule_news_fixed_bounds'))
                begin = 0
            else:
                begin = 1
            logger.debug(f'固定坐标点 {self.fixed}')
            # logger.debug(f'{articles}')
            for article in articles[begin:]:
                with timer.Timer() as t:
                    count -= 1
                    logger.debug(f'阅读一篇新闻 {article[0]}')
                    logger.info(f'[{count:>02}] {article[0]}...')
                    keywords = self.json_comments.keys()
                    for keyword in keywords:
                        if keyword in article[0]:
                            msg = choice(self.json_comments[keyword]) or f'{article[0]} 不忘初心牢记使命！为实现中华民族伟大复兴的中国梦不懈奋斗！'
                            break
                    else:
                        msg = choice(self.json_comments['default']) or f'{article[0]} 不忘初心牢记使命！为实现中华民族伟大复兴的中国梦不懈奋斗！'
                    self.ad.tap(article[1])
                    sleep(1)
                    self._read_news(count, delay)
                    if count < ssc:
                        self._star_share_comment(msg)

                    # 时间到了，不读了
                    self.ad.back()
                    sleep(1)
                logger.info(f'新闻：第 {count:>2} 则已阅，耗时 {round(t.elapsed,2):>05} 秒')
                if 0 == count:
                    break
                else:
                    #self.ad.slide(complex(self.fixed.real, article[1].imag), self.fixed, duration=1000)
                    sleep(3)
            print("next slide")
            self.ad.slide(complex(400, 1300), complex(400, 200), duration=2000)
        sleep(5)
        



    

if __name__ == '__main__':
    from pathlib import Path
    from argparse import ArgumentParser
    from ..common import adble, xmler
    logger.debug('running viewer.py')
    parse = ArgumentParser()
    parse.add_argument('-c', '--count', metavar='count', type=int, default=25, help='观看视频数')
    parse.add_argument('-d', '--delay', metavar='delay', type=int, default=30, help='单个视频观看时间')
    parse.add_argument('-s', '--star', metavar='star', type=int, default=2, help='单个视频观看时间')
    parse.add_argument('-t', '--tag', metavar='tag', type=str, default='default', help='抓评论的tag')
    parse.add_argument('-v', '--virtual', metavar='virtual', nargs='?', const=True, type=bool, default=False, help='是否模拟器')
    parse.add_argument('-m', '--comment', metavar='comment', nargs='?', const=True, type=bool, default=False, help='搜集留言')
    args = parse.parse_args()

    path = Path('./xuexi/src/xml/reader.xml')
    ad = adble.Adble(path, args.virtual)
    xm = xmler.Xmler(path)

    rd = Reader('mumu', ad, xm)
    if not args.comment:
        rd.run(args.count, args.delay, args.star)
    else:
        # 收集评论用，请先注释上一行，取消注释下一行，页面置于评论页，第一条评论在屏幕顶端， 运行python -m xuexi.media.reader -v
        # 新的使用方法 venv\scripts\python -m xuexi.media.reader -v -m -t {tag}
        rd.collect_comments(args.tag)

    ad.close()
