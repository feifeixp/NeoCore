from tdp_system import TDPManager
from datetime import datetime

def main():
    # 初始化TDP管理器
    manager = TDPManager("my_universes")
    
    # 1. 创建新世界（如果没有现成的世界ID）
    print("创建新世界...")
    world_id = manager.create_world()
    print(f"已创建世界 {world_id}\n")
    
    # 2. 在世界中创建一个角色
    print("创建角色...")
    char_id, char_data = manager.create_character(
        world_id=world_id,
        birth_datetime=datetime(1995, 3, 12, 5, 30),
        gender="male",
        era="ancient",  # 可选: "ancient"(修真), "modern"(现代), "future"(未来)
        character_name="李青云"  # 可选，不指定则自动生成
    )
    
    print(f"角色创建成功!")
    print(f"- 角色名称: {char_data['metadata']['name']}")
    print(f"- 角色ID: {char_id}")
    print(f"- 所属纪元: {char_data['metadata']['era']}")
    print(f"- 出生时间: {char_data['metadata']['birth_datetime']}")
    print("\n属性:")
    for attr, value in char_data['attributes'].items():
        print(f"- {attr}: {value}")
    print("\n技能:")
    for skill in char_data['skills']:
        print(f"- {skill}")
    
    # 3. 获取角色的详细描述
    print("\n角色详细描述:")
    char_desc = manager.get_character_description(world_id, char_id)
    print(char_desc)
    
    # 4. 获取世界中的所有角色
    print("\n世界中的所有角色:")
    characters = manager.get_characters_in_world(world_id)
    for char in characters:
        print(f"- {char['name']} ({char['era']}纪元, ID: {char['id']})")

if __name__ == "__main__":
    main() 