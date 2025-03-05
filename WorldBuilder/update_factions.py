#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新所有现有世界的派系信息
"""

import os
import json
import sys
import glob

# 添加父目录到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from NeoCore.WorldBuilder.tdp_system import TDPManager

def main():
    """主函数"""
    print("开始更新所有世界的派系信息...")
    
    # 创建TDP管理器
    manager = TDPManager()
    
    # 获取所有世界文件
    worlds_dir = os.path.join(manager.base_dir, "worlds")
    if not os.path.exists(worlds_dir):
        print(f"世界目录不存在: {worlds_dir}")
        return
    
    world_files = glob.glob(os.path.join(worlds_dir, "*.json"))
    print(f"找到 {len(world_files)} 个世界文件")
    
    updated_count = 0
    for world_file in world_files:
        try:
            print(f"\n处理世界文件: {world_file}")
            
            # 读取世界数据
            with open(world_file, 'r', encoding='utf-8') as f:
                world_data = json.load(f)
            
            # 更新派系信息
            manager.update_world_factions(world_data)
            
            # 保存更新后的世界数据
            with open(world_file, 'w', encoding='utf-8') as f:
                json.dump(world_data, f, ensure_ascii=False, indent=2)
            
            updated_count += 1
            print(f"成功更新世界文件: {world_file}")
            
        except Exception as e:
            print(f"处理世界文件 {world_file} 时发生错误: {str(e)}")
    
    print(f"\n更新完成，成功更新 {updated_count} 个世界文件")

if __name__ == "__main__":
    main() 