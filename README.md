# exporter
table exporter writen by python-v2.7.x

# -*- coding: utf-8 -*-
#

1、exporter 是一个非常强大的数据导出工具，可以将各种格式的 excel 表格导出成各种不同格式的配置文件。</br>
   默认支持的数据源插件有：xls、xlsx、xlsm、csv<br>
   默认支持的导出插件有：python dict、json、xml、tars-config（腾讯 tars 引擎配置文件）


2、exporter 支持数据源插件，和导出插件。通过编写不同的数据源插件，可以不局限于对 excel 表格的导出，譬如数据库表导出。


3、exporter 支持导出插件，通过用少量代码编写不同的导出插件，可以支持导出成任何格式的配置文件。


4、导出每一份数据配置都需要用 python 编写一个简单的导出模板，通过该模板制定导出的配置样式。</br>
    导出模板的使用方法，可以参看: exporter/examples/exporter/TableExporter/样板.py
    
    
5、在 examples/ 里有好几个示例，例如直接点击运行：examples/1-开发环境/任务/导出-任务.vbs 即可导出与其同目录下的 “任务.xlsx” 表格。
