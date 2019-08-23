项目功能
==================================================================
爬虫搜索服务


本地启动
==================================================================
1、克隆项目到本地  

2、进入项目目录，安装requirements.txt依赖的python库  

3、进入项目目录，执行启动命令：  
```
src/app_main.py
```

测试
==================================================================
1、test/api目录下是服务接口测试

Docker部署
================================================================== 
1、提交代码到master或develop分支（Gitlab将自动构建Docker镜像并push到Docker仓库）

2、登录服务器,执行启动命令：
```
cd /data/apps/server/crawl-search
./xstart.sh
```
备注: crawl-search目录下要有以下3个文件：
```
.dockeraddr                          #文件内容：Docker仓库地址，例如：192.168.8.8:6666
.dockerdir                           #文件内容：Docker仓库地址下的目录，例如：mygroup/myproject
.version                             #文件内容：Docker镜像版本号，与项目根目录下的.version一致
```

数据源
==================================================================  
http://search.people.com.cn/cnpeople/news/index.html  
http://jhsjk.people.cn/result  
http://search.qstheory.cn/qiushi  
http://so.news.cn  