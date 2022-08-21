# 说明
- 此爬虫采用的第三方库有: requests, lxml, fake_useragent, pillow
- 此爬虫使用Python多线程去编写
- 根据wallheaven.cc网站的内容进行爬取, 每页24张图片
- 使用前先执行pip install -r requirement.txt安装第三方库的依赖
- 此脚本封装成工具类形式, 可以直接调用
# 使用方法以及API
- WallHeavenSpider.get_pic(search_name)
- get_pic()方法可接收两个关键字参数,分别为output_dir和classify
- output_dir为图片输出路径, 数据类型为字符串, 如果未指定则在当前目录下生成一个名为wallheaven_wallpaper的文件夹
- classify为下载完图片是否自动根据分辨率进行分类, 数据类型为布尔型, 如果为True则代表自动分类
- 注: search_name为图片英文名字
