import json
import urllib
import urllib2
import re

from core.htmlparser import BaseParser

class MarkSixFetcher(object):
    def fetch(self):
        base_url = "http://bet.hkjc.com/marksix/Results.aspx?lang=ch"
        f = {
                'selectDrawID':20,
                'hiddenSelectDrawID':20,
                'radioDrawRange': 'GetDrawDate',
#                'radioDrawRange': 'GetDrawID',
                #'_ctl0:ContentPlaceHolder1:resultsMarkSix:selectDrawFromMonth':'01',
                'hiddenSelectDrawFromMonth': '01',
                #'_ctl0:ContentPlaceHolder1:resultsMarkSix:selectDrawFromYear':1993,
                'hiddenSelectDrawFromYear':2016,
                #'_ctl0:ContentPlaceHolder1:resultsMarkSix:selectDrawToMonth':'03',
                'hiddenSelectDrawToMonth':'03',
                #'_ctl0:ContentPlaceHolder1:resultsMarkSix:selectDrawToYear':'2016',
                'hiddenSelectDrawToYear':2016,
                'radioResultType':'GetAll',
                }
        url = base_url + urllib.urlencode(f)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
                   'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'DNT': '1',
                   'Referer': 'http://hk.centanet.com/findproperty/zh-HK/Home/SearchResult/?mktid=HK&minprice=&maxprice=&minarea=&maxarea=&areatype=N&posttype=S&src=F',
                   'X-Requested-With': 'XMLHttpRequest'}

        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        headers = response.info()
        html = response.read()

        #print html

        parser = MarkSixResultParser()
        parser.start_over()
        parser.feed(html)

        print parser.draw_count


class MarkSixResultParser(BaseParser):
    STATE_INIT = 0
    STATE_TABLE_RESULT_FOUND = 1
    STATE_DRAW_NUMBER_FOUND= 2
    STATE_LOOK_FOR_DATE = 3
    STATE_DATE_FOUND = 4
    STATE_LOOK_FOR_DRAW_RESULT = 5

    __state = 0
    __draw_result_remain = 7


    __draw_number_pattern  = re.compile('_(\d\d)')
    draw_count = 0

    def start_over(self):
        self.__state = self.STATE_INIT
        self.__draw_result_remain = 7

    def handle_starttag(self, tag, attrs):
        if self.__state == self.STATE_INIT:
            classAttr = self.getFromAttrs('class', attrs)
            if tag == 'td' and (classAttr == 'tableResult1' or classAttr == 'tableResult2'):
                print 'table found'
                self.__state = self.STATE_TABLE_RESULT_FOUND
        elif self.__state == self.STATE_TABLE_RESULT_FOUND:
            if tag == 'a':
                self.__state = self.STATE_DRAW_NUMBER_FOUND
        elif self.__state == self.STATE_LOOK_FOR_DATE:
            if tag == 'td':
                print 'date found'
                self.__state = self.STATE_DATE_FOUND
        elif self.__state == self.STATE_LOOK_FOR_DRAW_RESULT:
            if tag == 'img':
                img_src = self.getFromAttrs('src', attrs)
                draw_number = self.extractNumberFromImgSrc(img_src)
                if draw_number is not None:
                    print draw_number
                    self.__draw_result_remain -= 1

                    if self.__draw_result_remain == 0:
                        self.draw_count += 1
                        print 'start over'
                        self.start_over()

    def handle_data(self, data):
        if self.__state == self.STATE_DRAW_NUMBER_FOUND:
            self.__draw_number = data
            print 'draw number %s' % data
            self.__state = self.STATE_LOOK_FOR_DATE
        elif self.__state == self.STATE_DATE_FOUND:
            self.__date = data
            print 'date %s' % data
            self.__state = self.STATE_LOOK_FOR_DRAW_RESULT

    def extractNumberFromImgSrc(self, img_src):
        groups = self.__draw_number_pattern.findall(img_src)
        if len(groups) > 0:
            return groups[0]
        return None


if __name__ == '__main__':
    fetcher = MarkSixFetcher()
    fetcher.fetch()
