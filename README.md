项目自动同步程序
======
>利用github的release模块，自动同步项目代码

使用方法
----
1. 创建github账户
2. 创建项目厂库
3. 使用git命令，将项目push到github创库中
    <pre>
    git init
    git add README.md
    git commit -m "first commit"
    git remote add origin https://github.com/liubo0621/test2.git
    git push -u origin master
    </pre>
4. 给项目打标签，并推送到厂库中
    <pre>
    git tag -a version -m "note"
    注解：git tag 是打标签的命令，-a 是添加标签，其后要跟新标签号，-m 及后面的字符串是对该标签的注释
    git push origin --tags﻿​#origin可省略
    </pre>
5. 配置update_code的配置文件config.conf
    <pre>
    [internet-content-detection]
    # 远程代码发布路径
    remote_url = https://github.com/liubo0621/internet-content-detection/releases
    # 下载来的存储路径
    local_save_path = D:\sync-code
    # 项目路径
    project_path = D:\sync-code\internet-content-detection-test
    # 项目主函数的快捷方式位置
    main_lnk_path = C:\Users\Boris\Desktop\百度.lnk
    # 同步的文件 .*表示全部， $表示以什么结尾 支持正则， 多个逗号分隔
    sync_files = .py$
    # 忽略的文件 支持正则 多个逗号分隔 无忽略文件不填值
    ignore_files =
    
    #-----------------------------------------------------------
    [distributed-spider]
    # 远程代码发布路径
    remote_url = https://github.com/liubo0621/distributed-spider/releases
    # 下载来的存储路径
    local_save_path = D:\sync-code
    # 项目路径
    project_path = D:\sync-code\test
    # 项目主函数的快捷方式位置
    main_lnk_path = C:\Users\Boris\Desktop\百度.lnk
    # 同步的文件 .*表示全部， $表示以什么结尾 支持正则， 多个逗号分隔
    sync_files = .py$
    # 忽略的文件 支持正则 多个逗号分隔 无忽略文件不填值
    ignore_files =
    
    # ==========================================================
    # 按照以上格式配置更多
    </pre>
6. 设置任务计划， 每天定时执行update_code.py 文件

效果
--
每当有新的tag提交， 程序检测新的tag大于当前的tag， 则会自动更新老版本的代码，然后重启运行
