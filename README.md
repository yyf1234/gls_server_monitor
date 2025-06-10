# gls_server_monitor

## 项目简介
本项目用于在LSF集群环境下，自动选择可用服务器，提交仿真任务，并定时监控作业内存使用情况。同时支持记录指定文件的创建时间和最终修改时间。

## 主要功能
- 自动获取可用服务器并分配仿真任务
- 支持自定义仿真命令
- 定时监控LSF作业的内存使用（MAX MEM/AVG MEM）
- 记录指定文件的路径、创建时间和最终修改时间到日志

## 依赖环境
- Python 3.x
- LSF集群命令（bhosts, bsub, bjobs等）

## 使用方法
1. 克隆本仓库：
   ```bash
   git clone https://github.com/yyf1234/gls_server_monitor.git
   cd gls_server_monitor
   ```
2. 运行脚本：
   ```bash
   python simulation_monitor.py "<仿真命令>" <需要检测的文件路径>
   ```
   例如：
   ```bash
   python simulation_monitor.py "bsub -q adas -R 'rusage[mem=20000] select[cs]' -Is ./run -sim_opt=+plus" ./result/output.txt
   ```

## 日志说明
- 日志文件以`simulation_log_年月日_时分秒.txt`命名，包含作业ID、内存信息、文件信息等。

## 作者
风花雪叶  
邮箱：429499583@qq.com 