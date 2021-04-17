# -*- coding: utf-8 -*-
import scrapy
import base64
from scrapy_splash import SplashRequest
from scrapy.http import FormRequest
from scrapy.selector import Selector
from pprint import pprint
from ytc.items import YtcItem,YtcRec,YtcCookie


class YTSpider(scrapy.Spider):
    name = "ytspider"
    steps = 0
    visited_videos = set([])
    def load_browse(self):

        script = """
	function wait_for_element(splash, css, maxwait)
	  -- Wait until a selector matches an element
	  -- in the page. Return an error if waited more
	  -- than maxwait seconds.
	  if maxwait == nil then
	      maxwait = 10
	  end
	  return splash:wait_for_resume(string.format([[
	    function main(splash) {
	      var selector = '%s';
	      var maxwait = %s;
	      var end = Date.now() + maxwait*1000;

	function check() {
        	if(document.querySelector(selector)) {
	          splash.resume('Element found');
	        } else if(Date.now() >= end) {
	          var err = 'Timeout waiting for element';
        	  splash.error(err + " " + selector);
	        } else {
	          setTimeout(check, 200);
        	}
	      }
	      check();
	    }
	  ]], css, maxwait))
	end


            function main(splash)
            splash:set_user_agent('Mozilla/5.0 (X11;Ubuntu; Linux x86_64;rv15.0) Gecko/20100101 Firefox/17.0.1')
                splash.html5_media_enabled=true
                splash.private_mode_enabled = false
                splash:init_cookies(splash.args.cookies)
                assert(splash:go(splash.args.url))
                splash:set_viewport_full()
                wait_for_element(splash, "#ytp-autonav-toggle-button")
                splash:wait(3)
                splash:evaljs("document.getElementsByClassName('ytp-autonav-toggle-button')[0].click();")
                
                splash:wait(10)
                splash:evaljs("document.getElementsByClassName('more-button style-scope ytd-video-secondary-info-renderer')[0].click();")
                splash:wait(20)
                return {
                    cookies = splash:get_cookies(),
                    html = splash:html(),
                    sshot = splash:png()
                }
            end
        """
        return script

    def load_login(self): # a veces da error yt-button-renderer style text size-small
        script = """
        function main(splash)
        
        	 splash:set_user_agent('Mozilla/5.0 (X11;Ubuntu; Linux x86_64;rv15.0) Gecko/20100101 Firefox/17.0.1')
  splash.private_mode_enabled = false
  splash.html5_media_enabled=true
  assert(splash:go('https://www.youtube.com'))
  splash:set_viewport_full()
  splash:wait(5)
  splash:evaljs("document.getElementById('return-to-youtube').click();") 
  splash:wait(5)
  splash:evaljs("document.getElementsByClassName('button')[2].click();") 
  splash:wait(5)
  
  splash:evaljs("document.getElementsByClassName('style-scope yt-button-renderer style-text size-small')[0].click();") 
  splash:wait(5)
  
  splash:evaljs("document.getElementsByClassName('style-scope ytd-button-renderer style-suggestive size-small')[0].click();") 
  splash:wait(5)
  local select_email = splash:select_all('#Email') 
  select_email = splash:send_text("cesarmillandogwhispererguau@gmail.com")
  splash:wait(5)
  splash:evaljs("document.getElementsByClassName('rc-button rc-button-submit')[0].click();") 
  splash:wait(5)
  local select_pass = splash:select_all('#password')
  select_email = splash:send_text("elperrero")
  splash:wait(5)
  splash:evaljs("document.getElementById('submit').click();") 
  splash:wait(5)

            return {
                html = splash:html(),
                sshot = splash:png(),
                cookies = splash:get_cookies()
            }
        end
"""
        return script


    def save_screenshot(self,data,filename):
        png_bytes = base64.b64decode(data)
        with open(filename,'wb') as f:
            f.write(png_bytes)

    def parse_login(self,response):
        self.steps += 1
        script = self.load_browse()
        yield SplashRequest(url=self.start_url,callback=self.parse,
            endpoint='execute',cache_args=['lua_source'],
            args={'lua_source': script,'timeout': 90},session_id='%s_%s' % (self.profile,self.exp_id))
       # sshot = response.data['sshot']
       # self.save_screenshot(sshot,'/home/jorged/Desktop/screenshot.png')

    def start_requests(self):
        script = self.load_login()
        yield SplashRequest(url='https://www.youtube.com',callback=self.parse_login,
            endpoint='execute',
            args={'lua_source': script, 'timeout': 90},session_id='%s_%s' % (self.profile,self.exp_id))


    def parse(self,response):
        item = YtcItem()
        rec_item = YtcRec()
        script = self.load_browse()
        sel = Selector(text=response.data['html'])
        sshot = response.data['sshot']
        #self.save_screenshot(sshot,'/var/lib/scrapyd/screenshots/screenshot_%u.png' %self.steps)
        rv_titles = sel.xpath("//ytd-compact-video-renderer//h3/span/@title").getall()
        rv_links = sel.xpath("//ytd-compact-video-renderer//a/@href").getall()[1::2]
        rv_channel = sel.xpath("//ytd-compact-video-renderer//a//ytd-channel-name//yt-formatted-string/text()").getall()
        rv_views = sel.xpath("//ytd-compact-video-renderer//a//ytd-video-meta-block//div[2]/span[1]/text()").getall()
        
        #rv_date = sel.xpath("//ytd-compact-video-renderer//a//ytd-video-meta-block/div[1]/div[2]/span[2]/text()").getall()
        
        #rv_title_publi=sel.xpath("//ytd-action-companion-ad-renderer//div[1]/text()").getall()
        #rv_url_publi=sel.xpath("//ytd-action-companion-ad-renderer//div[2]/span/text()").getall()
	
        for (link,title,channel,views) in zip(rv_links,rv_titles,rv_channel,rv_views):
            rec_item['url'] = response.url
            rec_item['rec_url'] = link
            rec_item['title'] = title
            rec_item['rec_channel'] = channel
            rec_item['rec_views'] = views
            
            #rec_item['date_upload']= date_upload

            #rec_item['rec_titlepubli']=title_publi
            #rec_item['rec_urlpubli']=url_publi

            yield rec_item
	
        item['url'] = response.url
        item['title'] = sel.xpath("//h1/yt-formatted-string//text()").getall()
        item['owner'] = sel.xpath("//ytd-video-owner-renderer//ytd-channel-name//yt-formatted-string/a/text()").get()
        item['date'] = sel.xpath("//ytd-video-primary-info-renderer//div[2]/yt-formatted-string/text()").get()
        item['desc'] = sel.xpath("//ytd-video-secondary-info-renderer/div/ytd-expander/div//text()").getall()[1:]
        item['subcount'] = sel.xpath("//ytd-video-secondary-info-renderer//ytd-video-owner-renderer/div[1]/yt-formatted-string/text()").getall()
        #item['viewcount'] = sel.xpath("//yt-view-count-renderer[@class='style-scope ytd-video-primary-info-renderer']/span/text()").get() miguel
        item['viewcount'] = sel.xpath("//ytd-video-primary-info-renderer//div[1]/div[1][@id='count']/ytd-video-view-count-renderer/span[1]/text()").get()
        
        item['likecount'] = sel.xpath("//ytd-toggle-button-renderer[1]/a/yt-formatted-string/text()").get()

        item['dislikecount'] = sel.xpath("//ytd-toggle-button-renderer[2]/a/yt-formatted-string/text()").get()
        
        
        item['title_ad']=sel.xpath("//ytd-action-companion-ad-renderer//div[1][@id='header']/text()").getall()
        item['url_ad']=sel.xpath("//ytd-action-companion-ad-renderer//div[2]/span/text()").getall()
        

        yield item
        if self.steps < int(self.max_steps):
            self.steps += 1
            sel_link = 0
            while rv_links[sel_link] in self.visited_videos and sel_link < 20:
                sel_link += 1
            self.visited_videos.add(rv_links[sel_link])
            yield SplashRequest(url='https://www.youtube.com'+rv_links[sel_link],callback=self.parse,
                endpoint='execute',cache_args=['lua_source'],
                args={'lua_source': script,'timeout':90},session_id='%s_%s' % (self.profile,self.exp_id))
        else:
            cookie_item = YtcCookie()
            for cookie in response.data['cookies']:
                for k in cookie.keys():
                    cookie_item[k] = cookie[k]
                yield cookie_item