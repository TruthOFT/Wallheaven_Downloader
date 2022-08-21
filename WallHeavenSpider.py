import os
import re
import shutil
import threading
from queue import Queue

import requests
from fake_useragent import UserAgent
from lxml import etree
from PIL import Image


class WallHeavenSpider:
    __q = Queue(24)
    __url_q = Queue()

    @classmethod
    def __get_html(cls, _url: str):
        f_u = UserAgent()
        _text = requests.get(url=_url, headers={"User-Agent": f_u.random})
        return etree.HTML(_text.text)

    @classmethod
    def __get_pic(cls, **kwargs):
        while not cls.__url_q.empty():
            _url = cls.__url_q.get()
            _html = cls.__get_html(_url)
            if _html is not None:
                _hrefs = _html.xpath("//*//div[@id='thumbs']//ul//li//figure//a//@href")
                if len(_hrefs) > 0:
                    for h in _hrefs:
                        cls.__q.put(h)
                else:
                    print("未获取到任何图片")
                    return
            else:
                print("未获取到任何图片")
                return
        while not cls.__q.empty():
            _detail_url = cls.__q.get()
            _detail_html = cls.__get_html(_detail_url)
            _pic_href = _detail_html.xpath("//*//div[@class='scrollbox']//img//@src")[0]
            _pic_content = requests.get(_pic_href).content
            name_left_realm = _pic_href.rfind("/") + 1
            _pic_file_name = _pic_href[name_left_realm::]
            _output_dir = kwargs.get("output_dir")
            if _output_dir != "":
                if not os.path.exists(_output_dir):
                    os.mkdir(_output_dir)
                with open(f"{kwargs['output_dir']}/{_pic_file_name}", 'wb') as f:
                    f.write(_pic_content)
                    print(f"[ + ] Downloading: {_pic_file_name}")

    @classmethod
    def __get_pages(cls, _url: str) -> int:
        _html = cls.__get_html(_url)
        if _html is not None:
            _title = _html.xpath("//*//header//h1//text()")[0]
            page_count = re.findall(r"^\d+", _title)[0]
            return int(page_count)

    @classmethod
    def __start(cls, data: list, threads=16, **kwargs):
        for i in data:
            cls.__url_q.put(i)
        t_lst = []

        for _ in range(threads):
            t = threading.Thread(target=cls.__get_pic, kwargs=kwargs)
            t.start()
            t_lst.append(t)
        for t in t_lst:
            t.join()

    @classmethod
    def __classify(cls, output_dir: str):
        for images in os.listdir(output_dir):
            image_path = os.path.join(output_dir, images).replace("\\", "/")
            img = Image.open(image_path)
            width = img.width
            if 1920 <= width < 2560:
                width_dir = "1080"
            elif 2560 <= width < 3200:
                width_dir = "2K"
            elif 3200 <= width < 4096:
                width_dir = "3K"
            elif 4096 <= width < 5120:
                width_dir = "4K"
            else:
                width_dir = "other"

            img.close()
            if not os.path.exists(f"./{output_dir}/{width_dir}"):
                os.mkdir(f"./{output_dir}/{width_dir}")
            shutil.move(f"{image_path}", f"{output_dir}/{width_dir}/{images}")

    @classmethod
    def get_pic(cls, key: str, **kwargs):
        _url = f"https://wallhaven.cc/search?q={key}"
        _page_count = cls.__get_pages(_url)
        _page = _page_count // 24 if _page_count % 24 == 0 else _page_count // 24 + 1
        _want_download = input(f"一共获取到{_page_count}张图片,共{_page}页,您想下载几页:")
        _urls = []
        if _want_download == "":
            _urls = [f"https://wallhaven.cc/search?q={key}&page={i}" for i in range(1, _page + 1)]
        else:
            _urls = [f"https://wallhaven.cc/search?q={key}&page={i}" for i in range(1, int(_want_download) + 1)]
        if "output_dir" not in kwargs:
            kwargs["output_dir"] = "./wallheaven_wallpaper"
        cls.__start(_urls, **kwargs)
        # 分类, 待完善
        if "classify" in kwargs:
            if kwargs["classify"]:
                cls.__classify(kwargs["output_dir"])


search_key = input("请输入您想下载的图片英文名字:")
WallHeavenSpider.get_pic(search_key, classify=True)
