#!/usr/bin/env python3
import subprocess
import time
import re
import os
import sys
from datetime import datetime

def get_available_hosts():
    """获取可用的服务器列表"""
    try:
        result = subprocess.run(['bhosts', 'adas_gls'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            print("执行bhosts命令失败")
            return []
        
        # 解析输出，找到可用的服务器
        lines = result.stdout.split('\n')
        available_hosts = []
        for line in lines[1:]:  # 跳过标题行
            if line.strip():
                parts = line.split()
                if len(parts) >= 3 and parts[1] == 'ok':  # part1: 检查服务器状态
                    available_hosts.append(parts[0])
        return available_hosts
    except Exception as e:
        print(f"获取服务器列表时出错: {e}")
        return []

def log_file_info(file_path, log_file):
    """记录文件路径、创建时间和最终修改时间到日志"""
    try:
        if file_path:
            try:
                create_time = os.path.getctime(file_path)
                modify_time = os.path.getmtime(file_path)
                create_time_str = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")
                modify_time_str = datetime.fromtimestamp(modify_time).strftime("%Y-%m-%d %H:%M:%S")
                file_info = f"文件路径: {file_path}\n文件创建时间: {create_time_str}\n文件最终修改时间: {modify_time_str}\n"
            except Exception as fe:
                file_info = f"文件路径: {file_path}\n文件信息获取失败: {fe}\n"
            with open(log_file, 'a') as f:
                f.write(f"\n=== 文件信息 ===\n")
                f.write(file_info)
    except Exception as e:
        print(f"记录文件信息时出错: {e}")

def monitor_memory(job_id, log_file):
    """监控服务器内存使用情况"""
    try:
        # 直接使用传入的job_id
        if job_id:
            mem_cmd = ['bjobs', '-l', job_id]
            mem_result = subprocess.run(mem_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            if mem_result.returncode == 0:
                max_mem = avg_mem = ""
                for line in mem_result.stdout.split('\n'):
                    if "MAX MEM:" in line and "AVG MEM:" in line:
                        max_match = re.search(r'MAX MEM:\s*([0-9.]+\s*\w+);', line)
                        avg_match = re.search(r'AVG MEM:\s*([0-9.]+\s*\w+)', line)
                        if max_match:
                            max_mem = max_match.group(1)
                        if avg_match:
                            avg_mem = avg_match.group(1)
                        break
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(log_file, 'a') as f:
                    f.write(f"\n=== {timestamp} ===\n")
                    f.write(f"Job ID: {job_id}\n")
                    f.write(f"MAX MEM: {max_mem}\n")
                    f.write(f"AVG MEM: {avg_mem}\n")
        else:
            print("未找到对应的job ID")
            
    except Exception as e:
        print(f"监控内存时出错: {e}")

def run_simulation(host_name, simulation_command, file_path=None):
    """运行仿真任务"""
    log_file = f"simulation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # 开始仿真
    sim_process = subprocess.Popen(f"{simulation_command} | tee /dev/tty", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = sim_process.communicate()
    
    # 从输出中提取job ID
    job_id_match = re.search(r'Job <(\d+)>', output)
    if job_id_match:
        job_id = job_id_match.group(1)
        print(f"获取到Job ID: {job_id}")
    else:
        print("未能获取Job ID")
        job_id = None
    # 每10分钟监控一次内存
    try:
        while sim_process.poll() is None:
            monitor_memory(job_id, log_file)
            time.sleep(600)  # 等待10分钟
    except KeyboardInterrupt:
        print("用户中断仿真")
        sim_process.terminate()
    
    # 仿真结束后记录文件信息和内存状态
    log_file_info(file_path, log_file)
    monitor_memory(job_id, log_file)
    print(f"仿真完成，日志文件保存在: {log_file}")

def main():
    # 获取可用服务器
    available_hosts = get_available_hosts()
    if not available_hosts:
        print("没有找到可用的服务器")
        return
    
    # 选择第一个可用的服务器
    selected_host = available_hosts[0]
    print(f"选择服务器: {selected_host}")
    
    # 解析命令行参数
    if len(sys.argv) < 3:
        print("用法: python simulation_monitor.py <仿真命令> <需要检测的文件路径>")
        return
    simulation_command = sys.argv[1].replace("\\","")
    file_path = sys.argv[2]
    
    # 检查命令中是否包含 -m 选项
    if "-m" in simulation_command:
        # 如果包含 -m 选项，替换主机名
        simulation_command = re.sub(r'-m\s+\S+', f'-m {selected_host}', simulation_command)
    else:
        # 如果不包含 -m 选项，在 bsub 后添加
        simulation_command = simulation_command.replace("bsub", f"bsub -m {selected_host}")
    
    # 运行仿真
    run_simulation(selected_host, simulation_command, file_path)

if __name__ == "__main__":
    main() 