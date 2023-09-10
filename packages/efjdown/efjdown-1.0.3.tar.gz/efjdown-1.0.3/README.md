# Enflame Jfrog Downloader

## 介绍

- 引导token配置到home目录，即使在docker内也不用重复配置
- 支持文件和目录的下载，同步目录树
- 支持全局命令
- 提供-d debug详细信息
- 支持Python导入使用
- 下载完毕后支持打印目录树，还有文件大小
## 原理
通过携带header方式直接访问jfrog的http接口，通过正则表达式取出所有a标签中的链接，如果是目录就递归调用，规避上级目录链接，以此实现了同步整个目录下载的功能。

## 安装
下载啥东西的时候就直接 `pip install efjdwon` 就好了

**文件：**

```shell
 efjdown -u https://art.xxxxx.com/blabla.xx. -p 保存路径不要写文件名
```

**目录** 

```shell
efjdown -u https://art.xxxxx.com/ -p `保存父目录的名字，不写就是同步原父目录名`
```

## 环境和依赖

- Python >= 3.6 
- pip3 
- re
- request
- loguru

## CLI调用

可以通过配置文件配置token，在CLI第一次运行时，会检测本地有没有配置文件，没有的话会引导创建

如果有现成的配置文件，就直接执行下载，但是判断到403的权限错误的话，会提示错误，并引导重建配置
为了支持测试环境，也支持 shell中 -t + token的方式，但是这种方式不会保存token，只会在这次调用中生效。
举个例子
```shell
efjdown -u https://art.xxxxx.com/blabla.xx. -p 保存路径不要写文件名 -t token
```



## 导入引用

```python
import efjdown
# 下载单个文件
efjdown.download_file(url="file.url",save_path="/path/you/want/save",save_name="不写这个参数就是原名字")
# 下载整个目录
efjdown.download_dir(url="dir.url",save_path="/path/you/want/save",save_name="不写这个参数就是原名字")
```

## 错误定位

404：一般是没权限或者url给的不对，也有可能这个资源点的文件已经被删除

403：登录的token错误或无权访问该资源

5xx：内部服务错误，先手动试试可以访问不

## Bug提交

带本地失败log提交issue就行，看到了会修的就修了。

