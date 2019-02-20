# -*- coding: utf-8 -*-
import scrapy
import json
import re
import time
from lxml import etree
from math import ceil
from requests import get
from ..items import FollowListItem
from ..items import SpaceListItem
from ..items import VideoInfoItem
from ..items import BulletScreen
from ..items import VideoComment


class FollowListSpider(scrapy.Spider):
    name = 'MyBilibili'
    # pipeline = set([FollowlistPipeline, ])
    usr_mid = '66124873'
    # start_urls = ['http://bilibili.com/']
    # cookie = {'_uuid': 'DA5FB876-B0DA-A08A-B5A6-3B53F11593B778782infoc', ' LIVE_BUVID': 'AUTO7515472104257092', ' sid': 'l1x674fb', ' fts': '1547267994', ' CURRENT_FNVAL': '16', ' rpdid': 'oqqspoqqpsdospmixqwww', ' stardustvideo': '1', ' UM_distinctid': '168473ea13a5b6-0be1ff6de870f7-3257487f-1fa400-168473ea13bb51', ' finger': 'edc6ecda', ' im_notify_type_66124873': '0', ' DedeUserID': '66124873', ' DedeUserID__ckMd5': '769f4fc4522a775e', ' SESSDATA': 'df5b8e46%2C1550480697%2C4a641311', ' bili_jct': '7913bf65326b9d976ae0d55ec8980054', ' buvid3': '04295C13-CC6E-443F-B86A-1403CCE0386D84602infoc', ' pgv_pvi': '1684714496', ' CURRENT_QUALITY': '112', ' bp_t_offset_66124873': '221318921734487900', ' _dfcaptcha': '057f8907f688ec54653cb21270f1e712'}
    # cookie = {'_uuid': 'DA5FB876-B0DA-A08A-B5A6-3B53F11593B778782infoc', ' LIVE_BUVID': 'AUTO7515472104257092', ' sid': 'l1x674fb', ' fts': '1547267994', ' CURRENT_FNVAL': '16', ' rpdid': 'oqqspoqqpsdospmixqwww', ' stardustvideo': '1', ' UM_distinctid': '168473ea13a5b6-0be1ff6de870f7-3257487f-1fa400-168473ea13bb51', ' im_notify_type_66124873': '0', ' buvid3': '04295C13-CC6E-443F-B86A-1403CCE0386D84602infoc', ' pgv_pvi': '1684714496', ' CURRENT_QUALITY': '112', ' bp_t_offset_66124873': '221318921734487900', ' DedeUserID': '66124873', ' DedeUserID__ckMd5': '769f4fc4522a775e', ' SESSDATA': '5d38cac3%2C1552982279%2Ca20ae521', ' bili_jct': '2cd2e645ba0065b2e3b6ea6c158c4bf5', ' _dfcaptcha': 'b2c5e0ecab9cdbc0ab3881a27a0616fd'}
    cookie = {'buvid3': '356B65DB-7618-4FC3-BBBD-780D03868DF384624infoc', ' LIVE_BUVID': 'AUTO2515499735515018',
              ' stardustvideo': '1', ' CURRENT_FNVAL': '16', ' rpdid': 'psspqpmowdospllmmqpw', ' sid': 'c5kkso2g',
              ' _uuid': '836167AA-EEA5-7429-30DB-0B6AC5D4083B59176infoc',
              ' UM_distinctid': '168e9901b0986a-0bb783c240b5b9-b781636-1fa400-168e9901b0a50a', ' fts': '1550106948',
              ' DedeUserID': '66124873', ' DedeUserID__ckMd5': '769f4fc4522a775e',
              ' SESSDATA': '70c078a8%2C1552700797%2Cdce86c21', ' bili_jct': '9fac6bbb3ea0d46fa8cad51c3a53ce66',
              ' finger': 'b3372c5f', ' im_notify_type_66124873': '0', ' bp_t_offset_66124873': '221061013248232217',
              ' _dfcaptcha': 'ebdc32fae07fd8d40393b867a5724989',
              ' CNZZDATA2724999': 'cnzz_eid%3D856640912-1550103809-%26ntime%3D1550452018'}
    total_page = 0

    def start_requests(self):
        get_page = get("http://api.bilibili.com/x/relation/followings?vmid={usr_mid}&pn={page_num}&ps=20". \
                       format(usr_mid=self.usr_mid, page_num=1))
        total_page = int(json.loads(get_page.text)['data']['total'])  # 计算页数
        if total_page == 0:
            pass
        else:
            page = ceil(total_page / 20)
            for i in range(1, page + 1):
                start_urls = "http://api.bilibili.com/x/relation/followings?vmid={usr_mid}&pn={page_num}&ps=20". \
                    format(usr_mid=self.usr_mid, page_num=i)  # 返回json字符串
                yield scrapy.Request(start_urls, callback=self.parse, cookies=self.cookie)  # 到下一页

    def parse(self, response):
        json_text = response.text
        text = json.loads(json_text)
        # 创建Item对象
        item = FollowListItem()
        for i in range(20):
            try:
                mid = str(text['data']['list'][i]['mid'])
                mid_name = text['data']['list'][i]['uname']
                mid_url = 'http://space.bilibili.com/{mid_num}/video'.format(mid_num=mid)
                item['mid'] = mid
                item['mid_url'] = mid_url
                item['mid_name'] = mid_name
            except IndexError:
                pass
            except KeyError:
                pass
            else:
                yield item

            start_url = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}&pagesize=30&tid=0&page={page_num}'.format(
                mid=item['mid'], page_num=1)
            yield scrapy.Request(start_url, callback=self.space_list, cookies=self.cookie,
                                 meta={'cur_page': '{page}'.format(page=re.search(r'\d+$', start_url).group()),
                                       'mid': '{mid}'.format(mid=item['mid'])})

    def space_list(self, response):
        json_text = response.text
        text = json.loads(json_text)
        vlist = text['data']['vlist']
        # count = text['data']['count']
        item = SpaceListItem()
        for i in range(30):
            try:
                item['aid'] = str(vlist[i]['aid'])
                item['aid_url'] = 'https://www.bilibili.com/video/av{aid}'.format(aid=item['aid'])
                item['aid_name'] = vlist[i]['title']
                # item['aid_count'] = count
                item['aid_author'] = vlist[i]['author']
                item['aid_created'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(vlist[i]['created'])))
                # item['aid_description'] = vlist[i]['description']
            except IndexError:
                pass
            except KeyError:
                print('本页无内容')
            except Exception:
                print('页面发生错误')
            else:
                video_info = 'https://api.bilibili.com/x/web-interface/view?aid=' + item['aid']
                yield scrapy.Request(video_info, callback=self.third_process, cookies=self.cookie)

                comment_url = "https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn={page}&type=1&oid={aid}&nohot=1".format(
                    page=1, aid=item['aid'])
                yield scrapy.Request(comment_url, callback=self.get_comment, cookies=self.cookie,
                                     meta={'aid': item['aid'],
                                           'cur_page': '{page}'.format(
                                               page=re.search(r'pn=(\d+)', comment_url).group(1))})
                yield item

        # 继续当前UP主的下一页
        t_page = text['data']['pages']
        page = response.meta['cur_page']
        if int(page) < int(t_page):
            next_url = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}&pagesize=30&tid=0&page={page_num}'.format(
                mid=response.meta['mid'], page_num=str(int(page) + 1))
            yield scrapy.Request(next_url, callback=self.space_list, cookies=self.cookie,
                                 meta={'cur_page': '{page}'.format(page=re.search(r'\d+$', next_url).group()),
                                       'mid': '{mid}'.format(mid=response.meta['mid'])})

    def third_process(self, response):
        json_text = response.text
        text = json.loads(json_text)
        item = VideoInfoItem()
        item['video_aid'] = str(text['data']['aid'])
        item['video_title'] = text['data']['title']
        item['video_view'] = str(text['data']['stat']['view'])
        item['video_collection'] = str(text['data']['stat']['favorite'])
        item['video_coin'] = str(text['data']['stat']['coin'])
        item['video_like'] = str(text['data']['stat']['like'])
        item['video_cid'] = str(text['data']['cid'])
        # item['video_reply'] = str(text['data']['stat']['reply'])
        yield item

        # 弹幕地址
        bulletscreen_url = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + item['video_cid']
        yield scrapy.Request(bulletscreen_url, callback=self.get_bulletscreen, cookies=self.cookie, \
                             meta={'aid': item['video_aid']})

    # 获取弹幕
    def get_bulletscreen(self, response):
        aid = response.meta['aid']
        xml_text = response.body
        item = BulletScreen()
        item['bullentscreen'] = xml_text
        item['aid'] = aid
        yield item

    # 获取评论
    def get_comment(self, response):
        json_text = response.text
        text = json.loads(json_text)
        item = VideoComment()
        item['comment_aid'] = response.meta['aid']
        item['comment_msg'] = json_text
        yield item
        # 获取下一页
        page = text['data']['page']['num']
        t_page = text['data']['page']['count']
        if int(page) < int(t_page):
            next_url = "https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn={page}&type=1&oid={aid}&nohot=1".format(
                page=str(int(page) + 1), aid=response.meta['aid'])
            yield scrapy.Request(next_url, callback=self.get_comment, cookies=self.cookie,
                                 meta={'aid': response.meta['aid']})

