# pac4china_ipaddress
下载apnic的ip分配文件，生成pac文件。代理程序可以根据生成的pac文件对国外ip进行代理。这样可以优化国内网站的打开速度并节省代理服务器带宽。

# 运行
1. 生成pac.txt
     `$ ./gen_pac.py` 或 `$python3 gen_pac.py`
2. ss客户端配置
    ss客户端先编辑本地pac（一般在ss安装目录下）选择**使用本地pac**
