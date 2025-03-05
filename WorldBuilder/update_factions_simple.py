#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新所有现有世界的派系信息（简化版）
"""

import os
import json
import sys
import glob
import random

def update_world_factions(world_data):
    """更新世界派系信息
    
    Args:
        world_data: 世界数据
    """
    if 'factions' not in world_data or not world_data['factions']:
        print("世界数据中没有派系信息，无需更新")
        return
    
    # 派系描述模板
    faction_desc_templates = {
        "政治": [
            "作为一个{alignment}的政治派系，{name}致力于通过外交和政策制定来塑造世界秩序。他们的影响力遍布各大政治中心，拥有广泛的情报网络和外交关系。",
            "{name}是一个{alignment}的政治组织，专注于建立和维护政治秩序。他们的成员多为精通外交和谈判的政治家，在世界各地的政治舞台上扮演着重要角色。",
            "这个{alignment}的政治派系以其精明的外交策略和强大的政治影响力而闻名。{name}的领导层由经验丰富的政治家组成，他们的决策影响着整个世界的走向。"
        ],
        "军事": [
            "{name}是一支{alignment}的军事力量，以其纪律严明和战术创新而著称。他们拥有精锐的战士和先进的武器装备，在战场上几乎无人能敌。",
            "作为一个{alignment}的军事组织，{name}致力于通过武力维护秩序。他们的军队训练有素，装备精良，是世界上最强大的军事力量之一。",
            "这个{alignment}的军事派系由一群经验丰富的战士和战略家组成。{name}不仅拥有强大的军事力量，还掌握着先进的军事技术和战术。"
        ],
        "经济": [
            "{name}是一个{alignment}的经济组织，控制着世界上大部分的贸易路线和资源。他们的财富和经济影响力使他们能够在全球范围内施加影响。",
            "作为一个{alignment}的商业集团，{name}通过贸易和投资在世界各地建立了广泛的经济网络。他们的商业帝国跨越多个行业，从资源开采到高端制造。",
            "这个{alignment}的经济派系以其商业头脑和经济实力而闻名。{name}控制着多条重要的贸易路线，并在多个行业拥有垄断地位。"
        ],
        "学术": [
            "{name}是一个{alignment}的学术组织，致力于知识的收集、保存和传播。他们的学者和研究人员遍布世界各地，探索未知的领域。",
            "作为一个{alignment}的学术派系，{name}拥有世界上最大的图书馆和最先进的研究设施。他们的研究成果推动了科学和魔法的发展。",
            "这个{alignment}的学术团体由世界上最聪明的学者和研究人员组成。{name}不仅收集和保存知识，还积极探索新的理论和技术。"
        ],
        "宗教": [
            "{name}是一个{alignment}的宗教组织，信奉古老的神灵和传统。他们的神职人员和信徒遍布世界各地，传播他们的信仰和教义。",
            "作为一个{alignment}的宗教派系，{name}通过精神指导和道德教化影响着世界。他们的神殿和圣地是信徒朝圣的目的地。",
            "这个{alignment}的宗教团体以其深厚的精神传统和神秘的仪式而闻名。{name}的神职人员被认为拥有与神灵沟通的能力。"
        ],
        "艺术": [
            "{name}是一个{alignment}的艺术组织，致力于美的创造和传播。他们的艺术家创作出令人惊叹的作品，影响着世界的文化和审美。",
            "作为一个{alignment}的艺术派系，{name}通过音乐、绘画、雕塑等艺术形式表达他们的理念。他们的艺术学院培养了许多杰出的艺术家。",
            "这个{alignment}的艺术团体以其创新的艺术风格和深刻的艺术理念而闻名。{name}的作品不仅美丽，还蕴含着深刻的哲学思考。"
        ],
        "科技": [
            "{name}是一个{alignment}的科技组织，专注于技术创新和发明。他们的工程师和科学家开发出改变世界的技术和设备。",
            "作为一个{alignment}的科技派系，{name}拥有世界上最先进的实验室和研究设施。他们的技术成果推动了世界的进步。",
            "这个{alignment}的科技团体由一群天才发明家和工程师组成。{name}不仅开发新技术，还将这些技术应用于解决世界面临的问题。"
        ]
    }
    
    # 派系目标模板
    faction_goals = {
        "守序善良": "他们的主要目标是建立一个公正、和平的秩序，保护弱者，并促进社会的和谐发展。",
        "中立善良": "他们的主要目标是帮助他人并促进善良，不受法律或混乱的约束，而是根据自己的道德准则行事。",
        "混乱善良": "他们的主要目标是促进自由和幸福，反对压迫，即使这意味着要挑战现有的法律和传统。",
        "守序中立": "他们的主要目标是维护秩序和规则，相信结构和组织是社会稳定的关键，不偏向善恶任何一方。",
        "绝对中立": "他们的主要目标是保持平衡，不偏向任何极端，相信自然的循环和平衡是最重要的。",
        "混乱中立": "他们的主要目标是追求个人自由和选择，反对限制和控制，但不特别关注善恶的问题。",
        "守序邪恶": "他们的主要目标是建立一个严格的等级制度，通过规则和秩序来实现自己的野心和权力。",
        "中立邪恶": "他们的主要目标是追求自身利益，不受道德约束，愿意做任何事情来实现自己的目标。",
        "混乱邪恶": "他们的主要目标是破坏和混乱，享受破坏现有秩序的过程，追求纯粹的自由和力量。"
    }
    
    # 更新每个派系的描述
    for faction_id, faction_data in world_data['factions'].items():
        faction_name = faction_data.get('name', faction_id)
        faction_type = faction_data.get('type', '未知')
        faction_alignment = faction_data.get('alignment', '未知')
        
        # 检查派系描述是否需要更新
        current_desc = faction_data.get('description', '')
        if current_desc.endswith('是世界中的一个重要势力，拥有独特的理念和目标。') or not current_desc:
            # 根据派系类型和阵营选择描述模板
            desc_templates = faction_desc_templates.get(faction_type, ["是世界中的一个重要势力，拥有独特的理念和目标。"])
            desc_template = random.choice(desc_templates)
            
            # 获取派系目标
            goal = faction_goals.get(faction_alignment, "他们的目标和动机不为人所知。")
            
            # 生成完整描述
            faction_desc = desc_template.format(name=faction_name, alignment=faction_alignment) + " " + goal
            
            # 更新派系描述
            faction_data['description'] = faction_desc
            print(f"已更新派系 {faction_name} 的描述")

def main():
    """主函数"""
    print("开始更新所有世界的派系信息...")
    
    # 获取所有世界文件
    base_dirs = ["my_universes", "NeoCore/my_universes"]
    
    for base_dir in base_dirs:
        worlds_dir = os.path.join(base_dir, "worlds")
        if not os.path.exists(worlds_dir):
            print(f"世界目录不存在: {worlds_dir}")
            continue
        
        world_files = glob.glob(os.path.join(worlds_dir, "*.json"))
        print(f"在 {worlds_dir} 中找到 {len(world_files)} 个世界文件")
        
        updated_count = 0
        for world_file in world_files:
            try:
                print(f"\n处理世界文件: {world_file}")
                
                # 读取世界数据
                with open(world_file, 'r', encoding='utf-8') as f:
                    world_data = json.load(f)
                
                # 更新派系信息
                update_world_factions(world_data)
                
                # 保存更新后的世界数据
                with open(world_file, 'w', encoding='utf-8') as f:
                    json.dump(world_data, f, ensure_ascii=False, indent=2)
                
                updated_count += 1
                print(f"成功更新世界文件: {world_file}")
                
            except Exception as e:
                print(f"处理世界文件 {world_file} 时发生错误: {str(e)}")
        
        print(f"\n在 {worlds_dir} 中成功更新 {updated_count} 个世界文件")
    
    print("\n更新完成")

if __name__ == "__main__":
    main() 