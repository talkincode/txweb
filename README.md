# txweb

TOUGHSTRUCT项目WEB框架，基于Python2.7, twisted, cyclone组成的WEB开发框架。

## 快速安装 

    pip install -U https://github.com/talkincode/txweb/archive/master.zip

## 创建项目

以下指令会从github下载应用模板并创建应用目录，目录名就是应用名，参数 -U 表示重新下载，否则直接取本地缓存

    txwebctl --create -U --dir=appdir

## 运行项目

以下指令会在8888端口（可选）监听http请求，--logging=none是由于cyclone内部自动打印日志，与txweb日志打印重复，所以关掉。

    txwebctl --port=8888 --dir=appdir --conf=appdir/etc/appname.json -logging=none

    [May 25 09:30:13 appname] Log opened.
    [May 25 09:30:13 appname] add free route [/:<class 'appname.handlers.index.IndexHandler'>]
    [May 25 09:30:13 appname] Application starting on 8888
    [May 25 09:30:13 appname] Starting factory <txweb.web.Application instance at 0x105731e18>