from typing import Callable

from requests import Session

from utils.crawler.web import _Web
from utils.errno import Error, NO_M3U8
from utils.log import logger
from utils.media.m3u8 import download_m3u8_v, merge_m3u8_ts


class WebM3u8ByUrl(_Web):
    def __init__(self):
        super().__init__()
        self._req_session = Session()

    def __del__(self):
        super().__del__()
        self._req_session.close()

    def get_m3u8_url(self, m3u8_filter: Callable = None) -> str:
        if m3u8_filter:
            for req in self.driver.requests:
                if not req.response:
                    continue
                if m3u8_filter(req.url):
                    return req.url

        # 一般页面只会有一个<video>
        element = self.find_element("//video")
        if not element:
            logger.error(f"get_m3u8 no element")
            return ""
        return element.get_dom_attribute("data-src")

    def download_ts(self, m3u8_dir: str, con_num=3) -> Error:
        m3u8 = self.get_m3u8_url()
        if not m3u8:
            logger.error(f"download_ts no m3u8")
            return NO_M3U8
        logger.info(f"download_ts {m3u8}")
        download_m3u8_v(m3u8, m3u8_dir, con_num=con_num)
        return merge_m3u8_ts(m3u8_dir)
