__author__ = 'AUTHOR'
# -*- coding:utf-8 -*-
import urllib
# import urllib2
import re
import requests
import threading
import time


# 糗事百科爬虫类
class QSBK:
    # 初始化方法，定义一些变量
    def __init__(self):
        self.pageIndex = 1
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        # 初始化headers
        self.headers = {'User-Agent': self.user_agent}
        # 存放段子的变量，每一个元素是每一页的段子们
        self.stories = []
        # 存放程序是否继续运行的变量
        self.enable = False

    # 传入某一页的索引获得页面代码
    def getPage(self, pageIndex):
        try:
            url = 'http://www.qiushibaike.com/hot/page/' + str(pageIndex)
            # print(url)
            # 构建请求的request
            # request = urllib2.Request(url, headers=self.headers)
            # 利用urlopen获取页面代码
            # response = urllib2.urlopen(request)
            response = requests.get(url,headers=self.headers)
            response.raise_for_status()
            # 将页面转化为UTF-8编码
            # pageCode = response.read().decode('utf-8')
            response.encoding = response.apparent_encoding
            # print(response.text)
            return response.text

        except requests.exceptions.HTTPError as e:
            if hasattr(e, "reason"):
                print(u"连接糗事百科失败,错误原因", e.reason)
                return None

    # 传入某一页代码，返回本页不带图片的段子列表
    def getPageItems(self, pageIndex):
        pageCode = self.getPage(pageIndex)
        if not pageCode:
            print("页面加载失败....")
            return None
        '''
        pattern = re.compile('<div.*?author">.*?<a.*?<img.*?>(.*?)</a>.*?<div.*?' +
                             'content">(.*?)<!--(.*?)-->.*?</div>(.*?)<div class="stats.*?class="number">(.*?)</i>',
                             re.S)
                             
        • re.I(全拼：IGNORECASE): 忽略大小写（括号内是完整写法，下同）
        • re.M(全拼：MULTILINE): 多行模式，改变'^'和'$'的行为
        • re.S(全拼：DOTALL): 点任意匹配模式，改变'.'的行为
        • re.L(全拼：LOCALE): 使预定字符类 \w \W \b \B \s \S 取决于当前区域设定
        • re.U(全拼：UNICODE): 使预定字符类 \w \W \b \B \s \S \d \D 取决于unicode定义的字符属性
        • re.X(全拼：VERBOSE): 详细模式。这个模式下正则表达式可以是多行，忽略空白字符，并可以加入注释。
        
        '''
        pattern = re.compile(
            r'<h2>(.*?)</h2>.*?<span>(.*?)</span>.*?<span class="stats-vote"><i class="number">(.*?)</i>.*?<i class="number">(.*?)</i>',
            re.S)    # re.S(全拼：DOTALL): 点任意匹配模式，改变'.'的行为

        # 如果不使用re.S参数，则只在每一行内进行匹配，如果一行没有，就换下一行重新开始，不会跨行。
        # 而使用re.S参数以后，正则表达式会将这个字符串作为一个整体，将“\n”当做一个普通的字符加入到这个字符串中，在整体中进行匹配。
        # "." Matches any character except a newline.
        # S DOTALL "." matches any character at all, including the newline.
        items = re.findall(pattern, pageCode)
        # 用来存储每页的段子们
        pageStories = []
        # 遍历正则表达式匹配的信息
        '''
        for item in items:
            # 是否含有图片
            haveImg = re.search("img", item[3])
            # 如果不含有图片，把它加入list中
            if not haveImg:
                replaceBR = re.compile('<br/>')
                text = re.sub(replaceBR, "\n", item[1])
                # item[0]是一个段子的发布者，item[1]是内容，item[2]是发布时间,item[4]是点赞数
                pageStories.append([item[0].strip(), text.strip(), item[2].strip(), item[4].strip()])
        '''
        for item in items:
            replaceBR = re.compile('<br/>')
            text = re.sub(replaceBR, "\n", item[1])
            # item[0]是一个段子的发布者，item[1]是内容，item[2]是点赞,item[3]是评论
            pageStories.append([item[0].strip(), text.strip(), item[2].strip(), item[3].strip()])
            # print(pageStories)
        return pageStories

    # 加载并提取页面的内容，加入到列表中
    def loadPage(self):
        # 如果当前未看的页数少于2页，则加载新一页
        if self.enable == True:
            if len(self.stories) < 2:
                # 获取新一页
                pageStories = self.getPageItems(self.pageIndex)
                # 将该页的段子存放到全局list中
                if pageStories:
                    self.stories.append(pageStories)
                    # 获取完之后页码索引加一，表示下次读取下一页
                    self.pageIndex += 1

    # 调用该方法，每次敲回车打印输出一个段子
    def getOneStory(self, pageStories, page):
        # 遍历一页的段子
        for story in pageStories:
            # 等待用户输入
            Input = input("Next OR Q:")
            # 每当输入回车一次，判断一下是否要加载新页面
            self.loadPage()
            # 如果输入Q则程序结束
            if Input == "Q":
                self.enable = False
                return
            print(u"第%d页\t发布人:%s\t发布时间:%s\t赞:%s\n%s" % (page, story[0], story[2], story[3], story[1]))

    # 开始方法
    def start(self):
        print(u"正在读取糗事百科,按回车查看新段子，Q退出")
        # 使变量为True，程序可以正常运行
        self.enable = True
        # 先加载一页内容
        self.loadPage()
        # 局部变量，控制当前读到了第几页
        nowPage = 0
        while self.enable:
            if len(self.stories) > 0:
                # 从全局list中获取一页的段子
                pageStories = self.stories[0]
                # 当前读到的页数加一
                nowPage += 1
                # 将全局list中第一个元素删除，因为已经取出
                del self.stories[0]
                # 输出该页的段子
                self.getOneStory(pageStories, nowPage)


spider = QSBK()
spider.start()