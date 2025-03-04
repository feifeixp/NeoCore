from tdp_system import TDPManager, TDPWorldGenerator, CharacterDNAGenerator
from datetime import datetime

def basic_example():
    """基本使用示例"""
    # 创建世界与角色管理器（默认存储在tdp_worlds目录）
    manager = TDPManager("my_universes")
    
    # 1. 创建新世界
    print("正在创建世界...")
    world_id = manager.create_world()
    print(f"已创建世界 {world_id}")
    
    # 2. 创建不同纪元的角色
    # 修真纪元角色
    print("\n创建修真纪元角色...")
    ancient_id, ancient_data = manager.create_character(
        world_id=world_id,
        birth_datetime=datetime(1995, 3, 12, 5, 30),
        gender="male",
        era="ancient",
        character_name="李青云"  # 可以指定角色名称
    )
    print(f"角色创建成功: {ancient_data['metadata']['name']} (ID: {ancient_id})")
    
    # 现代纪元角色
    print("\n创建现代纪元角色...")
    modern_id, modern_data = manager.create_character(
        world_id=world_id,
        birth_datetime=datetime(2000, 8, 23, 15, 45),
        gender="female",
        era="modern"
    )
    print(f"角色创建成功: {modern_data['metadata']['name']} (ID: {modern_id})")
    
    # 未来纪元角色
    print("\n创建未来纪元角色...")
    future_id, future_data = manager.create_character(
        world_id=world_id,
        birth_datetime=datetime(2005, 12, 10, 3, 15),
        gender="male",
        era="future"
    )
    print(f"角色创建成功: {future_data['metadata']['name']} (ID: {future_id})")
    
    # 3. 检索世界信息
    print("\n获取世界描述...")
    world_desc = manager.get_world_description(world_id)
    print(world_desc[:200] + "...")  # 只显示前200字符
    
    # 4. 检索角色信息
    print("\n获取角色信息...")
    characters = manager.get_characters_in_world(world_id)
    print(f"世界 {world_id} 中有 {len(characters)} 个角色:")
    
    for char in characters:
        print(f"- {char['name']} ({char['era']}纪元, ID: {char['id']})")
    
    # 获取详细角色描述
    char_desc = manager.get_character_description(world_id, ancient_id)
    print(f"\n角色描述示例 ({ancient_data['metadata']['name']}):")
    print(char_desc[:300] + "...")  # 只显示前300字符
    
    return world_id, [ancient_id, modern_id, future_id]


def advanced_example():
    """高级使用示例：创建多个世界，每个世界多个角色"""
    manager = TDPManager("my_universes")
    
    # 创建3个不同的世界
    worlds = []
    for i in range(3):
        world_id = manager.create_world()
        worlds.append(world_id)
        print(f"已创建世界 {i+1}: {world_id}")
    
    # 在每个世界中创建不同的角色组合
    world_characters = {}
    eras = ["ancient", "modern", "future"]
    
    for i, world_id in enumerate(worlds):
        # 每个世界创建2-4个角色
        char_count = i + 2
        world_characters[world_id] = []
        
        for j in range(char_count):
            # 选择不同的纪元
            era = eras[j % 3]
            # 创建角色
            char_id, _ = manager.create_character(
                world_id=world_id,
                birth_datetime=datetime(1990 + j*5, (j*3 % 12) + 1, (j*7 % 28) + 1, j*2 % 24, 0),
                gender="female" if j % 2 else "male",
                era=era
            )
            world_characters[world_id].append(char_id)
            
    # 打印创建的世界和角色结构
    print("\n创建的世界与角色结构:")
    for world_id in worlds:
        print(f"世界: {world_id}")
        chars = manager.get_characters_in_world(world_id)
        for char in chars:
            print(f"  ├─ 角色: {char['name']} ({char['era']}纪元)")
    
    return worlds, world_characters


def custom_world_example():
    """自定义世界参数示例"""
    # 创建自定义世界生成器
    world_gen = TDPWorldGenerator(protocol_version="1.1")
    
    # 添加地理维度
    world_gen.add_dimension_axis(
        module="geo",
        name="大陆形态",
        options=["灵脉浮岛（上古）", "现代都市（当代）", "太空殖民地（未来）"],
        weights=[0.6, 0.3, 0.1]  # 强调上古元素
    )
    
    world_gen.add_dimension_axis(
        module="geo",
        name="能量类型",
        options=["天地灵气（上古）", "化石能源（当代）", "反物质反应堆（未来）"],
        weights=[0.7, 0.2, 0.1]
    )
    
    # 添加势力维度
    world_gen.add_dimension_axis(
        module="faction",
        name="权力架构",
        options=["修仙门派（上古）", "民族国家（当代）", "巨型企业联合体（未来）"],
        weights=[0.8, 0.1, 0.1]
    )
    
    # 添加科技维度
    world_gen.add_dimension_axis(
        module="tech",
        name="能量应用",
        options=["炼丹炼器（上古）", "内燃机（当代）", "量子脑机接口（未来）"],
        weights=[0.8, 0.1, 0.1]
    )
    
    # 设置规则
    world_gen.set_rule("cross_era_interaction", True)
    
    # 生成世界
    world_data = world_gen.generate_world()
    world_description = world_gen.generate_world_description()
    
    print("创建了以上古纪元为主的世界:")
    print(world_description[:300] + "...")
    
    # 使用此世界创建角色
    manager = TDPManager("my_universes")
    
    # 保存自定义世界
    world_id = world_data["metadata"]["universe_id"]
    world_dir = f"my_universes/{world_id}"
    import os
    if not os.path.exists(world_dir):
        os.makedirs(world_dir)
    if not os.path.exists(f"{world_dir}/characters"):
        os.makedirs(f"{world_dir}/characters")
        
    # 保存世界元数据和描述
    with open(f"{world_dir}/world_metadata.yaml", "w", encoding="utf-8") as f:
        import yaml
        yaml.dump(world_data, f, allow_unicode=True)
    with open(f"{world_dir}/world_description.txt", "w", encoding="utf-8") as f:
        f.write(world_description)
    
    # 创建角色
    char_gen = CharacterDNAGenerator(world_id)
    char_data = char_gen.generate_character(
        birth_datetime=datetime(980, 6, 15, 3, 30),
        gender="male",
        era="ancient",
        character_name="玄天真人"
    )
    
    # 保存角色数据
    import json
    with open(f"{world_dir}/characters/{char_data['metadata']['soul_id']}.json", "w", encoding="utf-8") as f:
        json.dump(char_data, f, ensure_ascii=False, indent=2)
    
    # 生成并保存角色描述
    char_desc = char_gen.generate_character_description(char_data)
    with open(f"{world_dir}/characters/{char_data['metadata']['soul_id']}_description.txt", "w", encoding="utf-8") as f:
        f.write(char_desc)
    
    print(f"\n在自定义世界中创建了角色: {char_data['metadata']['name']}")
    print(char_desc[:200] + "...")
    
    return world_id, char_data['metadata']['soul_id']


def main():
    """主函数：示范TDP系统的各种使用方式"""
    print("=== 三纪元世界与角色生成系统演示 ===\n")
    
    print("1. 基本功能演示")
    print("=" * 50)
    world_id, char_ids = basic_example()
    print("\n基本功能演示完成")
    print("=" * 50)
    
    print("\n2. 多世界与多角色演示")
    print("=" * 50)
    worlds, chars = advanced_example()
    print("\n多世界与多角色演示完成")
    print("=" * 50)
    
    print("\n3. 自定义世界参数演示")
    print("=" * 50)
    custom_world_id, custom_char_id = custom_world_example()
    print("\n自定义世界参数演示完成")
    print("=" * 50)
    
    print("\n所有演示完成。数据已保存到my_universes目录。")
    print("\n目录结构示例:")
    print("my_universes/")
    print(f"├── {world_id}/")
    print("│   ├── world_metadata.yaml")
    print("│   ├── world_description.txt")
    print("│   └── characters/")
    for char_id in char_ids:
        print(f"│       ├── {char_id}.json")
        print(f"│       └── {char_id}_description.txt")
    print(f"├── {worlds[0]}/")
    print("│   └── ...")
    print(f"├── {worlds[1]}/")
    print("│   └── ...")
    print(f"├── {worlds[2]}/")
    print("│   └── ...")
    print(f"└── {custom_world_id}/")
    print("    ├── world_metadata.yaml")
    print("    ├── world_description.txt")
    print("    └── characters/")
    print(f"        ├── {custom_char_id}.json")
    print(f"        └── {custom_char_id}_description.txt")


if __name__ == "__main__":
    main()
