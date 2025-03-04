from tdp_system import TDPManager
from datetime import datetime

# 创建管理器
manager = TDPManager("tdp_universes")

# 1. 创建世界
world_id = manager.create_world()
print(f"已创建世界: {world_id}")

# 2. 创建不同纪元的角色
# 修真纪元角色
ancient_char_id, _ = manager.create_character(
    world_id=world_id,
    birth_datetime=datetime(1998, 4, 15, 7, 30),
    gender="male",
    era="ancient"
)
print(f"已创建修真纪元角色，ID: {ancient_char_id}")

# 现代纪元角色
modern_char_id, _ = manager.create_character(
    world_id=world_id,
    birth_datetime=datetime(2000, 8, 23, 15, 45),
    gender="female",
    era="modern"
)
print(f"已创建现代纪元角色，ID: {modern_char_id}")

# 3. 获取角色信息
characters = manager.get_characters_in_world(world_id)
print(f"\n世界 {world_id} 中有 {len(characters)} 个角色:")
for char in characters:
    print(f"- {char['name']} ({char['era']}纪元)")