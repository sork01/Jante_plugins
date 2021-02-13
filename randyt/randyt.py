#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
import urllib.request
import threading

if __name__ == '__main__':
    import sys
    sys.path.append('../..')
    sys.path.append('../../libs')

from plugins.parsingplugintemplate import parsingplugintemplate

class randyt(parsingplugintemplate):
    def __init__(self, bot):
        self._config = bot.getConfig()
        super(randyt, self).__init__(bot, command=self._config['randyt']['command'], description="Generates a random youtube link")
        self.mutex = threading.Lock()
        self.defaulturlbuffer = []
        self.musicbuffer = []
        self.buffersize = 10
        self.tries = 4
        self.timeout = 0.75

    def getPage(self):
        with self.mutex:
            if len(self.defaulturlbuffer) == 0:
                return "Error buffering, is the site down?"

            return self.defaulturlbuffer.pop()

    def getMusic(self):
        with self.mutex:
            if len(self.musicbuffer) == 0:
                return "Error buffering, is the site down?"

            return self.musicbuffer.pop()

    def parse(self, message):
        text = message.getText()
        if text.startswith("music"):
            return self.getMusic()
        else:
            return self.getPage()

    def buffer(self):
        with self.mutex:
            if len(self.defaulturlbuffer) < self.buffersize:
                # Try to get 'buffersize' number of items in 'tries' number
                # of tries
                for i in range(self.tries):

                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                        html = requests.get('https://www.fantaziu.it/random-youtube-video-generator/', headers=headers , timeout=self.timeout)
                        randyt = re.findall(r'\/embed\/([^"]+)', html.content.decode('utf-8'))
                        url = "http://www.youtube.com/watch?v=" + randyt[0]
                        response = urllib.request.urlopen(url).read().decode("utf-8")
                        title = re.findall(r'title":"([^"]+)', response)

                    except:
                        break
                    if len(randyt) != 0:
                        self.defaulturlbuffer.append(str(title[0]) + ": http://www.youtube.com/watch?v=" + str(randyt[0]))

                    if not len(self.defaulturlbuffer) < self.buffersize:
                        break

            if len(self.musicbuffer) < self.buffersize:
                for i in range(self.tries):

                    #html = urllib.request.urlopen('http://www.randomvideogenerator.com/', timeout=self.timeout)
                    #html = html.read().decode('utf-8')
                    #randyt = re.findall(r'\/embed\/([^ f]+)', html)
                    try:
                        html = requests.get('http://www.randomvideogenerator.com/', timeout=self.timeout)
                        randyt = re.findall(r'\/embed\/([^ f]+)', html.content.decode('utf-8'))
                        if len(randyt) > 0:
                            self.musicbuffer.append(str("http://www.youtube.com/watch?v=" + randyt[0]))
                    except:
                        break

                    if not len(self.musicbuffer) < self.buffersize:
                        break

        return len(self.defaulturlbuffer) and len(self.musicbuffer)

if __name__ == '__main__':
    from mockbot import mockbot
    from jantemessage import jantemessage
    
    bot = mockbot()
    bot.setConfig('randyt', 'command', 'randyt')
    
    p = randyt(bot)
    print(p.parse(jantemessage('')))
