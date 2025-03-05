from .tdp_system import TDPManager
from datetime import datetime, timedelta
import random
import os
import argparse

def get_user_input(prompt: str, allow_empty: bool = True) -> str:
    """获取用户输入，支持跳过。
    
    Args:
        prompt: 提示信息
        allow_empty: 是否允许空输入
        
    Returns:
        str: 用户输入的字符串，如果允许空输入且用户直接回车，返回None
    """
    value = input(prompt)
    if not value.strip():
        return None if allow_empty else ""
    return value.strip()

def get_date_input() -> datetime:
    """获取用户输入的日期，支持跳过"""
    print("\n出生日期 (直接回车随机生成):")
    year = get_user_input("年份 (1900-2020): ")
    if not year:
        return None
        
    month = get_user_input("月份 (1-12): ")
    day = get_user_input("日期 (1-31): ")
    hour = get_user_input("小时 (0-23): ")
    minute = get_user_input("分钟 (0-59): ")
    
    try:
        return datetime(
            int(year),
            int(month) if month else 1,
            int(day) if day else 1,
            int(hour) if hour else 0,
            int(minute) if minute else 0
        )
    except:
        print("日期格式错误，将使用随机日期")
        return None

def generate_random_birth_date() -> datetime:
    """生成随机出生日期"""
    # 生成1900年到2020年之间的随机日期
    start_date = datetime(1900, 1, 1)
    end_date = datetime(2020, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    random_date = start_date + timedelta(days=random_days)
    
    # 添加随机时间
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    return random_date.replace(hour=random_hour, minute=random_minute)

def create_character(deepseek_api_key: str = None):
    """创建角色的主函数
    
    Args:
        deepseek_api_key: DeepSeek API密钥
    """
    # 初始化TDP管理器
    manager = TDPManager("my_universes", deepseek_api_key)
    
    try:
        # 1. 创建或选择世界
        world_id = get_user_input("\n请输入现有世界ID (直接回车创建新世界): ")
        if world_id:
            # 检查世界文件是否存在
            world_path = os.path.join("my_universes", "worlds", f"{world_id}.json")
            if not os.path.exists(world_path):
                print(f"错误: 世界 {world_id} 不存在")
                print("创建新世界...")
                world_id = manager.create_world()
                print(f"已创建世界 {world_id}")
        else:
            print("\n创建新世界...")
            world_id = manager.create_world()
            print(f"已创建世界 {world_id}")
        
        # 确保必要的目录存在
        os.makedirs(os.path.join("my_universes", "worlds"), exist_ok=True)
        os.makedirs(os.path.join("my_universes", "characters"), exist_ok=True)
        
        # 2. 获取角色信息
        print("\n=== 角色创建 ===")
        print("(所有选项都可以直接回车跳过，系统将随机生成)")
        
        # 获取角色名称
        name = get_user_input("\n请输入角色名称: ")
        
        # 获取性别
        while True:
            gender = get_user_input("\n请选择性别 (male/female): ")
            if gender is None or gender in ["male", "female"]:
                break
            print("性别只能是 male 或 female")
        
        # 获取纪元
        while True:
            era = get_user_input("\n请选择纪元 (ancient/modern/future): ")
            if era is None or era in ["ancient", "modern", "future"]:
                break
            print("纪元只能是 ancient(修真)、modern(现代) 或 future(未来)")
        
        # 获取出生日期
        birth_date = get_date_input()
        if birth_date is None:
            birth_date = generate_random_birth_date()
        
        # 3. 创建角色
        print("\n正在创建角色...")
        char_id, char_data = manager.create_character(
            world_id=world_id,
            birth_datetime=birth_date,
            gender=gender if gender else random.choice(["male", "female"]),
            era=era if era else random.choice(["ancient", "modern", "future"]),
            character_name=name
        )
        
        # 4. 显示角色信息
        print("\n=== 角色创建成功 ===")
        print(f"所属世界: {world_id}")
        print(f"角色名称: {char_data['metadata']['name']}")
        print(f"角色ID: {char_id}")
        print(f"性别: {'男性' if char_data['basic']['gender'] == 'male' else '女性'}")
        print(f"所属纪元: {char_data['basic']['era']}")
        print(f"出生时间: {char_data['basic']['birth_datetime']}")
        
        # 5. 显示详细描述
        print("\n=== 角色详细描述 ===")
        char_desc = manager.get_character_description(world_id, char_id)
        print(char_desc)
        
        return world_id, char_id
    
    except KeyboardInterrupt:
        print("\n\n已取消角色创建")
        return None, None
    except Exception as e:
        print(f"\n错误: {e}")
        return None, None

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="三纪元角色创建系统")
    parser.add_argument("--api-key", help="DeepSeek API密钥")
    args = parser.parse_args()
    
    # 优先从环境变量获取API密钥
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        api_key = args.api_key
    
    if not api_key:
        print("错误：未设置DeepSeek API密钥。请设置DEEPSEEK_API_KEY环境变量或使用--api-key参数提供。")
        return
    
    print("=== 欢迎使用三纪元角色创建系统 ===")
    
    try:
        while True:
            world_id, char_id = create_character(deepseek_api_key=api_key)
            if world_id is None:
                break
            
            # 询问是否继续创建
            answer = get_user_input("\n是否继续创建角色？(y/n): ", allow_empty=False)
            if not answer or answer.lower() != 'y':
                break
        
        print("\n感谢使用！再见！")
    
    except KeyboardInterrupt:
        print("\n\n已退出程序")
    except Exception as e:
        print(f"\n程序出错: {e}")

if __name__ == "__main__":
    main() 