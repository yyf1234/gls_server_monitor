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

def monitor_memory(host_name, log_file, sim_cmd):
    """监控服务器内存使用情况"""
    try:
        # 获取bsub job id
        job_id = None
        bjobs_cmd = ['bjobs', '-l']
        bjobs_result = subprocess.run(bjobs_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if bjobs_result.returncode == 0:
            for line in bjobs_result.stdout.split('\n'):
                job_id_match = re.search(r'Job <(\d+)>', line)
                if job_id_match:
                    job_id = job_id_match.group(1)
                    break

        # 获取指定job的内存使用情况
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

def run_simulation(host_name, simulation_command):
    """运行仿真任务"""
    log_file = f"simulation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # 开始仿真
    sim_process = subprocess.Popen(simulation_command, shell=True)
    
    # 每10分钟监控一次内存
    try:
        while sim_process.poll() is None:
            monitor_memory(host_name, log_file, ' '.join(simulation_command))
            time.sleep(600)  # 等待10分钟
    except KeyboardInterrupt:
        print("用户中断仿真")
        sim_process.terminate()
    
    # 仿真结束后再次记录内存状态
    monitor_memory(host_name, log_file, ' '.join(simulation_command))
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
    
    # 定义仿真命令
    simulation_command = sys.argv[1].replace("\\","")
    
    # 运行仿真
    run_simulation(selected_host, simulation_command)

if __name__ == "__main__":
    main() 