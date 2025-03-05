from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime
from WorldBuilder.create_random_character import create_character
from WorldBuilder.tdp_system import TDPManager

app = Flask(__name__)

# 获取DeepSeek API密钥
api_key = os.environ.get('DEEPSEEK_API_KEY')
if not api_key:
    raise ValueError("未设置DEEPSEEK_API_KEY环境变量")

# 初始化TDP管理器
tdp_manager = TDPManager("my_universes", api_key)

@app.route('/')
def index():
    return render_template('create_character.html')

@app.route('/api/worlds')
def get_worlds():
    """获取所有可用的世界列表"""
    worlds_dir = os.path.join("my_universes", "worlds")
    if not os.path.exists(worlds_dir):
        return jsonify([])
    
    worlds = []
    for filename in os.listdir(worlds_dir):
        if filename.endswith('.json'):
            world_id = filename[:-5]  # 移除.json后缀
            world_path = os.path.join(worlds_dir, filename)
            try:
                with open(world_path, 'r', encoding='utf-8') as f:
                    world_data = json.load(f)
                    worlds.append({
                        'id': world_id,
                        'name': world_data.get('name', world_id)
                    })
            except:
                worlds.append({
                    'id': world_id,
                    'name': world_id
                })
    
    return jsonify(worlds)

@app.route('/api/create_character', methods=['POST'])
def create_character_api():
    """创建新角色的API端点"""
    try:
        data = request.get_json()
        print("Received data:", data)  # 调试信息
        
        # 获取表单数据
        world_id = data.get('worldId', '')  # 修改这里，设置默认值为空字符串
        character_name = data.get('characterName')
        gender = data.get('gender')
        era = data.get('era')
        birth_date = data.get('birthDate')
        
        # 验证必要字段
        if not character_name or not gender or not era or not birth_date:
            return jsonify({
                'success': False,
                'error': '缺少必要字段：' + ', '.join([
                    '角色名称' if not character_name else '',
                    '性别' if not gender else '',
                    '纪元' if not era else '',
                    '出生日期' if not birth_date else ''
                ])
            })
        
        # 如果没有提供世界ID，创建新世界
        if not world_id:
            try:
                world_id = tdp_manager.create_world()
                print(f"Created new world: {world_id}")  # 调试信息
            except Exception as e:
                print(f"Error creating world: {str(e)}")  # 调试信息
                return jsonify({
                    'success': False,
                    'error': f'创建世界失败：{str(e)}'
                })
        
        # 创建角色
        try:
            char_id, char_data = tdp_manager.create_character(
                world_id=world_id,  # 这里使用更新后的 world_id
                birth_datetime=datetime.fromisoformat(birth_date.replace('Z', '+00:00')),
                gender=gender,
                era=era,
                character_name=character_name
            )
            print(f"Created character: {char_id} in world: {world_id}")  # 调试信息
        except Exception as e:
            print(f"Error creating character: {str(e)}")  # 调试信息
            return jsonify({
                'success': False,
                'error': f'创建角色失败：{str(e)}'
            })
        
        # 获取角色描述
        try:
            char_desc = tdp_manager.get_character_description(world_id, char_id)  # 确保传递正确的 world_id
            print(f"Generated character description for character {char_id} in world {world_id}")  # 调试信息
        except Exception as e:
            print(f"Error getting character description: {str(e)}")  # 调试信息
            return jsonify({
                'success': False,
                'error': f'获取角色描述失败：{str(e)}'
            })
        
        response_data = {
            'success': True,
            'worldId': world_id,  # 确保返回正确的 world_id
            'characterId': char_id,
            'characterName': char_data['basic']['name'],
            'gender': char_data['basic']['gender'],
            'era': char_data['basic']['era'],
            'birthDate': char_data['basic']['birth_datetime'],
            'description': char_desc
        }
        print("Sending response:", response_data)  # 调试信息
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # 调试信息
        return jsonify({
            'success': False,
            'error': f'发生意外错误：{str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True) 