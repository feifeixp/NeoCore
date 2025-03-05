import os
import json
import uuid
import yaml
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from .text_manager import TextManager
from .bazi_analyzer import BaziAnalyzer
from .deepseek_client import DeepSeekClient

class TDPManager:
    """三纪元维度锚定协议(TDP)管理器"""
    
    def __init__(self, base_dir: str = "my_universes", deepseek_api_key: str = None):
        """初始化TDP管理器。
        
        Args:
            base_dir: 基础目录路径
            deepseek_api_key: DeepSeek API密钥
        """
        self.base_dir = base_dir
        self.text_manager = TextManager(os.path.join(base_dir, "config"), deepseek_api_key=deepseek_api_key)
        self.bazi_analyzer = BaziAnalyzer()  # 添加八字分析器
        self.deepseek_client = DeepSeekClient(deepseek_api_key)  # 添加 DeepSeek 客户端
        self.character_generator = CharacterDNAGenerator(self.text_manager)  # 添加角色生成器
        
        # 确保必要的目录存在
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(os.path.join(base_dir, "worlds"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "characters"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "config"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "descriptions"), exist_ok=True)  # 添加描述文件目录
        
    def create_world(self) -> str:
        """创建新世界
        
        Returns:
            str: 世界ID
        """
        world_id = f"TDP-{uuid.uuid4().hex[:8]}-{datetime.now().year}"
        world_data = {
            "id": world_id,
            "created_at": datetime.now().isoformat(),
            "characters": [],
            "entropy": 0.0,
            "validation": {
                "checksum": uuid.uuid4().hex,
                "last_modified": datetime.now().isoformat()
            }
        }
        
        # 生成随机派系
        faction_names = [
            "守护者联盟", "探索者协会", "自由商会", "科技公司", 
            "神秘学院", "军事联邦", "艺术家联盟", "工匠协会"
        ]
        faction_types = ["政治", "军事", "经济", "学术", "宗教", "艺术", "科技"]
        faction_alignments = ["守序善良", "中立善良", "混乱善良", "守序中立", "绝对中立", "混乱中立", "守序邪恶", "中立邪恶", "混乱邪恶"]
        
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
        
        # 随机选择3-5个派系
        num_factions = random.randint(3, 5)
        selected_faction_names = random.sample(faction_names, num_factions)
        
        factions = {}
        for i, name in enumerate(selected_faction_names):
            faction_type = random.choice(faction_types)
            faction_alignment = random.choice(faction_alignments)
            
            # 根据派系类型和阵营选择描述模板
            desc_templates = faction_desc_templates.get(faction_type, ["是世界中的一个重要势力，拥有独特的理念和目标。"])
            desc_template = random.choice(desc_templates)
            
            # 获取派系目标
            goal = faction_goals.get(faction_alignment, "他们的目标和动机不为人所知。")
            
            # 生成完整描述
            faction_desc = desc_template.format(name=name, alignment=faction_alignment) + " " + goal
            
            factions[f"faction_{i+1}"] = {
                "name": name,
                "type": faction_type,
                "alignment": faction_alignment,
                "description": faction_desc
            }
        
        world_data['factions'] = factions
        
        # 保存世界数据
        world_path = os.path.join(self.base_dir, "worlds", f"{world_id}.json")
        with open(world_path, "w", encoding="utf-8") as f:
            json.dump(world_data, f, ensure_ascii=False, indent=2)
            
        # 保存世界描述
        description = self.text_manager.get_world_description(world_id, "1.1")
        desc_path = os.path.join(self.base_dir, "descriptions", f"{world_id}_description.txt")
        with open(desc_path, "w", encoding="utf-8") as f:
            f.write(description)
            
        return world_id
        
    def create_character(self, world_id: str, birth_datetime: datetime, gender: str = None, era: str = None, character_name: str = None) -> Tuple[str, dict]:
        """创建新角色
        
        Args:
            world_id: 世界ID
            birth_datetime: 出生日期时间
            gender: 性别 ('male' 或 'female')
            era: 纪元类型 ('ancient', 'modern', 'future')
            character_name: 角色名称（可选）
            
        Returns:
            Tuple[str, dict]: (角色ID, 角色数据)
        """
        try:
            # 确保目录存在
            print(f"当前工作目录: {os.getcwd()}")
            print(f"base_dir: {self.base_dir}")
            
            # 检查base_dir是否是绝对路径
            if not os.path.isabs(self.base_dir):
                # 如果不是绝对路径，则尝试在当前工作目录下查找
                if os.path.exists(os.path.join(os.getcwd(), self.base_dir)):
                    self.base_dir = os.path.join(os.getcwd(), self.base_dir)
                    print(f"更新base_dir为绝对路径: {self.base_dir}")
            
            worlds_dir = os.path.join(self.base_dir, "worlds")
            characters_dir = os.path.join(self.base_dir, "characters")
            os.makedirs(worlds_dir, exist_ok=True)
            os.makedirs(characters_dir, exist_ok=True)
            
            print(f"worlds_dir: {worlds_dir}")
            print(f"characters_dir: {characters_dir}")
            
            # 检查世界数据文件是否存在，如果不存在则创建
            world_file = os.path.join(worlds_dir, f"{world_id}.json")
            if not os.path.exists(world_file):
                world_data = {
                    "id": world_id,
                    "created_at": datetime.now().isoformat(),
                    "characters": [],
                    "entropy": 0.0,
                    "validation": {
                        "checksum": uuid.uuid4().hex,
                        "last_modified": datetime.now().isoformat()
                    }
                }
                with open(world_file, 'w', encoding='utf-8') as f:
                    json.dump(world_data, f, ensure_ascii=False, indent=2)
                print(f"创建世界数据文件：{world_file}")
            
            # 生成角色数据
            char_id = str(uuid.uuid4())
            char_data = self.character_generator.generate_character(
                era=era,
                gender=gender,
                name=character_name,
                birth_datetime=birth_datetime.strftime("%Y-%m-%dT%H:%M")
            )
            
            # 添加metadata字段
            char_data['metadata'] = {
                'id': char_id,
                'name': character_name,
                'gender': gender,
                'era': era,
                'world_id': world_id,
                'birth_datetime': birth_datetime.isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            # 保存角色数据
            char_file = os.path.join(characters_dir, f"{char_id}.json")
            try:
                with open(char_file, 'w', encoding='utf-8') as f:
                    json.dump(char_data, f, ensure_ascii=False, indent=2)
                print(f"角色数据已保存到: {char_file}")
            except Exception as e:
                print(f"保存角色数据时发生错误: {str(e)}")
                raise
            
            # 更新世界数据中的角色列表
            try:
                with open(world_file, 'r', encoding='utf-8') as f:
                    world_data = json.load(f)
            except Exception as e:
                print(f"读取世界数据时发生错误: {str(e)}")
                raise
                
            if 'characters' not in world_data:
                world_data['characters'] = []
            world_data['characters'].append(char_id)
            
            try:
                with open(world_file, 'w', encoding='utf-8') as f:
                    json.dump(world_data, f, ensure_ascii=False, indent=2)
                print(f"世界数据已更新: {world_file}")
            except Exception as e:
                print(f"更新世界数据时发生错误: {str(e)}")
                raise
            
            return char_id, char_data
            
        except Exception as e:
            print(f"创建角色时发生错误: {str(e)}")
            raise
        
    def get_characters_in_world(self, world_id: str) -> list:
        """获取世界中的所有角色
        
        Args:
            world_id: 世界ID
            
        Returns:
            list: 角色信息列表
        """
        # 读取世界数据
        world_path = os.path.join(self.base_dir, "worlds", f"{world_id}.json")
        with open(world_path, "r", encoding="utf-8") as f:
            world_data = json.load(f)
            
        characters = []
        for char_id in world_data.get("character_ids", []):
            # 读取每个角色的数据
            char_path = os.path.join(self.base_dir, "characters", f"{char_id}.json")
            with open(char_path, "r", encoding="utf-8") as f:
                char_data = json.load(f)
                meta = char_data["metadata"]
                characters.append({
                    "id": char_id,
                    "name": meta["name"],
                    "era": meta["era"],
                    "birth_datetime": meta["birth_datetime"]
                })
                
        return characters
        
    def _generate_name(self, gender: str, era: str) -> str:
        """生成角色名字
        
        Args:
            gender: 性别
            era: 纪元
            
        Returns:
            str: 生成的名字
        """
        name_elements = self.text_manager.get_name_elements(era)
        
        surname = random.choice(name_elements["surnames"])
        title = random.choice(name_elements["titles"])
        
        # 只有古代女性角色才使用中间名
        if era == "ancient" and gender == "female" and "female_middle" in name_elements:
            middle = random.choice(name_elements["female_middle"])
            return surname + middle + title
            
        return surname + title

    def get_world_description(self, world_id: str) -> str:
        """获取世界描述"""
        return self.text_manager.get_world_description(world_id, "1.1")
        
    def get_character_description(self, world_id: str, char_id: str) -> str:
        """获取角色描述
        
        Args:
            world_id: 世界ID
            char_id: 角色ID
            
        Returns:
            str: 角色描述
        """
        try:
            # 构建文件路径
            char_file = os.path.join(self.base_dir, "characters", f"{char_id}.json")
            world_file = os.path.join(self.base_dir, "worlds", f"{world_id}.json")  # 更新世界文件路径
            
            # 检查文件是否存在
            if not os.path.exists(char_file):
                print(f"角色文件不存在：{char_file}")
                raise FileNotFoundError(f"角色文件不存在：{char_file}")
            if not os.path.exists(world_file):
                print(f"世界文件不存在：{world_file}")
                raise FileNotFoundError(f"世界文件不存在：{world_file}")
            
            # 读取角色数据
            try:
                with open(char_file, 'r', encoding='utf-8') as f:
                    char_data = json.load(f)
            except Exception as e:
                print(f"读取角色数据时发生错误：{str(e)}")
                raise
            
            # 读取世界数据
            try:
                with open(world_file, 'r', encoding='utf-8') as f:
                    world_data = json.load(f)
                
                # 检查世界数据中的派系信息是否需要更新
                need_update = False
                if 'factions' in world_data:
                    for faction_id, faction_data in world_data['factions'].items():
                        # 检查派系描述是否是默认的简单描述
                        if faction_data.get('description', '').endswith('是世界中的一个重要势力，拥有独特的理念和目标。'):
                            need_update = True
                            break
                
                # 如果需要更新派系信息，调用更新方法
                if need_update:
                    print("检测到派系信息需要更新，正在更新...")
                    self.update_world_factions(world_data)
                    # 保存更新后的世界数据
                    with open(world_file, 'w', encoding='utf-8') as f:
                        json.dump(world_data, f, ensure_ascii=False, indent=2)
                    print("派系信息更新完成")
                
            except Exception as e:
                print(f"读取世界数据时发生错误：{str(e)}")
                raise
            
            # 获取八字分析
            try:
                birth_datetime = datetime.fromisoformat(char_data['basic']['birth_datetime'])
                bazi_analysis = self.bazi_analyzer.analyze_bazi(birth_datetime)
                char_data['bazi'] = bazi_analysis
            except Exception as e:
                print(f"八字分析时发生错误：{str(e)}")
                # 继续执行，不中断程序
                
            # 生成角色描述
            try:
                # 调用 text_manager 的 get_character_description 方法，传递正确的 world_id
                print(f"正在生成角色描述，世界ID：{world_id}")
                print(f"世界文件路径：{world_file}")
                description = self.text_manager.get_character_description(char_data, world_id, "1.1")
                return description
            except Exception as e:
                print(f"生成角色描述时发生错误：{str(e)}")
                raise
                
        except Exception as e:
            print(f"获取角色描述时发生错误：{str(e)}")
            raise
            
    def _get_key_event_type(self, dasyun_element: str, era: str) -> str:
        """根据大运五行和纪元确定关键事件类型"""
        event_types = {
            'ancient': {
                '生': '修炼突破',
                '克': '遭遇劫难',
                '比': '获得机缘',
                '泄': '失去机缘',
                '耗': '遭遇挫折'
            },
            'modern': {
                '生': '事业突破',
                '克': '遭遇危机',
                '比': '获得机会',
                '泄': '失去机会',
                '耗': '遭遇挫折'
            },
            'future': {
                '生': '科技突破',
                '克': '遭遇危机',
                '比': '获得机遇',
                '泄': '失去机遇',
                '耗': '遭遇挫折'
            }
        }
        return event_types[era][dasyun_element]
        
    def _format_key_years(self, key_years: List[Dict], era: str) -> str:
        """格式化关键流年信息"""
        formatted = []
        for year_info in key_years:
            year = year_info['year']
            age = year_info['age']
            event_type = year_info['event_type']
            element = year_info['dasyun_element']
            
            # 根据纪元生成具体事件描述
            event_desc = self._generate_event_description(event_type, era, year, age)
            
            formatted.append(f"- {year}年（{age}岁）：{event_desc}（{element}运）")
            
        return "\n".join(formatted)
        
    def _generate_event_description(self, event_type: str, era: str, year: int, age: int) -> str:
        """生成具体事件描述"""
        event_templates = {
            'ancient': {
                '修炼突破': [
                    f'在{year}年突破修为境界，实力大增',
                    f'获得重要功法传承，修为突飞猛进',
                    f'在{year}年领悟重要功法，实力提升'
                ],
                '遭遇劫难': [
                    f'在{year}年遭遇重大劫难，但最终化险为夷',
                    f'经历生死考验，获得重要机缘',
                    f'在{year}年遭遇危机，但得到贵人相助'
                ],
                '获得机缘': [
                    f'在{year}年获得重要机缘，实力提升',
                    f'遇到重要传承，获得特殊能力',
                    f'在{year}年获得意外机缘，改变命运'
                ],
                '失去机缘': [
                    f'在{year}年错失重要机缘，但获得其他机遇',
                    f'失去一次机会，但获得新的方向',
                    f'在{year}年遭遇挫折，但获得新的领悟'
                ],
                '遭遇挫折': [
                    f'在{year}年遭遇挫折，但获得成长',
                    f'经历失败，但获得新的机遇',
                    f'在{year}年遇到困难，但获得突破'
                ]
            },
            'modern': {
                '事业突破': [
                    f'在{year}年事业获得重大突破',
                    f'完成重要项目，获得认可',
                    f'在{year}年实现重要目标，事业上升'
                ],
                '遭遇危机': [
                    f'在{year}年遭遇事业危机，但最终化解',
                    f'经历困难，但获得新的机会',
                    f'在{year}年遇到挑战，但获得突破'
                ],
                '获得机会': [
                    f'在{year}年获得重要机会，事业提升',
                    f'遇到重要机遇，实现突破',
                    f'在{year}年获得意外机会，改变方向'
                ],
                '失去机会': [
                    f'在{year}年错失机会，但获得新的方向',
                    f'失去一次机会，但获得新的机遇',
                    f'在{year}年遭遇挫折，但获得新的领悟'
                ],
                '遭遇挫折': [
                    f'在{year}年遭遇挫折，但获得成长',
                    f'经历失败，但获得新的机会',
                    f'在{year}年遇到困难，但获得突破'
                ]
            },
            'future': {
                '科技突破': [
                    f'在{year}年完成重要科技突破',
                    f'发明新技术，获得认可',
                    f'在{year}年实现重要创新，事业上升'
                ],
                '遭遇危机': [
                    f'在{year}年遭遇科技危机，但最终化解',
                    f'经历困难，但获得新的突破',
                    f'在{year}年遇到挑战，但获得创新'
                ],
                '获得机遇': [
                    f'在{year}年获得重要机遇，实现突破',
                    f'遇到重要机会，完成创新',
                    f'在{year}年获得意外机遇，改变方向'
                ],
                '失去机遇': [
                    f'在{year}年错失机遇，但获得新的方向',
                    f'失去一次机会，但获得新的突破',
                    f'在{year}年遭遇挫折，但获得新的领悟'
                ],
                '遭遇挫折': [
                    f'在{year}年遭遇挫折，但获得成长',
                    f'经历失败，但获得新的机遇',
                    f'在{year}年遇到困难，但获得突破'
                ]
            }
        }
        
        return random.choice(event_templates[era][event_type])

    def generate_random_name(self, gender: str) -> str:
        """生成随机名字。
        
        Args:
            gender: 性别 ('male' 或 'female')
            
        Returns:
            str: 生成的名字
        """
        # 姓氏列表
        surnames = ['李', '王', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
                   '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
        
        # 男性名字常用字
        male_chars = ['伟', '强', '军', '磊', '明', '超', '勇', '涛', '斌', '波',
                     '宇', '浩', '凯', '鹏', '杰', '峰', '旭', '昊', '龙', '辰']
        
        # 女性名字常用字
        female_chars = ['芳', '娟', '敏', '静', '秀', '丽', '艳', '娜', '燕', '玲',
                       '华', '萍', '红', '莉', '婷', '雪', '琳', '晶', '倩', '云']
        
        # 随机选择姓氏
        surname = random.choice(surnames)
        
        # 根据性别选择名字字符
        name_chars = male_chars if gender == 'male' else female_chars
        
        # 生成1-2个字的名字
        name_length = random.randint(1, 2)
        name = ''.join(random.sample(name_chars, name_length))
        
        return surname + name

    def update_world_factions(self, world_data: Dict[str, Any]) -> None:
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

class TDPWorldGenerator:
    """三纪元维度锚定协议(TDP)世界生成器"""
    
    def __init__(self, protocol_version="1.1"):
        """初始化世界生成器
        
        Args:
            protocol_version: TDP协议版本
        """
        self.protocol_version = protocol_version
        self.dimensions = {
            "geo": {"axes": []},
            "faction": {"axes": []},
            "tech": {"axes": []},
            "event": {"axes": []}
        }
        self.rules = {
            "cross_era_interaction": True,
            "entropy_constraint": 0.78
        }
        
    def add_dimension_axis(self, module: str, name: str, 
                          options: List[str], weights: List[float] = None):
        """添加维度轴
        
        Args:
            module: 模块名称
            name: 轴名称
            options: 选项列表
            weights: 权重列表
        """
        if weights is None:
            weights = [1.0/len(options)] * len(options)
            
        self.dimensions[module]["axes"].append({
            "name": name,
            "options": options,
            "weights": weights
        })
        
    def set_rule(self, rule_key: str, value: Any):
        """设置规则
        
        Args:
            rule_key: 规则键
            value: 规则值
        """
        self.rules[rule_key] = value
        
    def generate_world(self) -> Dict:
        """生成世界数据
        
        Returns:
            Dict: 世界数据
        """
        world_id = f"TDP-{uuid.uuid4().hex[:8]}-{datetime.now().year}"
        
        # 生成各维度的选择
        selections = {}
        for module, config in self.dimensions.items():
            selections[module] = []
            for axis in config["axes"]:
                choice = np.random.choice(
                    axis["options"],
                    p=axis["weights"]
                )
                selections[module].append({
                    "axis": axis["name"],
                    "value": choice
                })
        
        # 计算熵值
        entropy = self._calculate_entropy(selections)
        
        return {
            "metadata": {
                "universe_id": world_id,
                "protocol_version": self.protocol_version,
                "created_at": datetime.now().isoformat(),
                "entropy": entropy
            },
            "dimensions": selections,
            "rules": self.rules
        }
        
    def generate_world_description(self) -> str:
        """生成世界描述
        
        Returns:
            str: 世界描述文本
        """
        world_data = self.generate_world()
        world_id = world_data["metadata"]["universe_id"]
        
        description = [
            f"世界编号：{world_id}",
            f"法则校验码：#{world_id.split('-')[1]}-{uuid.uuid4().hex[:4].upper()}\n"
        ]
        
        # 添加各维度描述
        for module, selections in world_data["dimensions"].items():
            if selections:
                description.append(f"[{self._get_module_name(module)}]")
                for item in selections:
                    description.append(f"■ {item['axis']}: {item['value']}")
                description.append("")
        
        # 添加典型地点描述
        description.extend(self._generate_mixed_locations())
        
        # 添加熵增监控面板
        description.extend([
            "\n[熵增监控面板]",
            "参数                    当前值              阈值                状态",
            f"灵气-石油转化率         1:{random.uniform(3.5,4.5):.1f}桶          1:4.0桶            {'稳定' if random.random() > 0.5 else '经济预警'}",
            f"渡劫成功概率            {random.uniform(60,70):.1f}%            量子计算修正值      {random.choice(['+','-'])}{random.uniform(5,7):.1f}%",
            f"反物质泄漏次数          {random.randint(20,29)}/月              30次/月            安全范围",
            f"时空因果扰动指数        {random.uniform(85,95):.1f}            100.0              维度稳定\n"
        ])
        
        # 添加协议声明
        description.append(
            f"该世界严格遵循TDP协议v{self.protocol_version}生成，任何参数修改超过±0.3%将导致"
            f"#{world_id.split('-')[1]}-{uuid.uuid4().hex[:4].upper()}校验码失效并生成平行宇宙。"
            f"当前时空连续性担保期至{datetime.now().year + 1}-12-31。"
        )
        
        return "\n".join(description)
    
    def _get_module_name(self, module: str) -> str:
        """获取模块显示名称"""
        names = {
            "geo": "地理构造",
            "faction": "势力矩阵",
            "tech": "科技树",
            "event": "事件系统"
        }
        return names.get(module, module)
    
    def _calculate_entropy(self, selections: Dict) -> float:
        """计算世界熵值"""
        entropy = 0.0
        for module, items in selections.items():
            for item in items:
                if "ancient" in item["value"].lower():
                    entropy += 0.1
                elif "future" in item["value"].lower():
                    entropy += 0.2
        return round(entropy, 3)
    
    def _generate_mixed_locations(self) -> List[str]:
        """生成混合地点描述"""
        locations = ["\n[典型地点]"]
        
        # 上古/当代融合区
        locations.extend([
            "▣ 灵脉域（上古/当代融合区）",
            "- 生态：商业街上空悬浮着古代仙家洞府，市政喷泉涌出灵泉",
            "- 资源：可提炼灵石的页岩气田（灵气纯度：72%）",
            "- 异常：手机信号强度与区域灵脉活跃度成正比\n"
        ])
        
        # 当代/未来融合区
        locations.extend([
            "▣ 反物质塔（当代/未来融合区）",
            "- 生态：纳米聚变路灯照耀下的智能生态花园",
            "- 资源：用河图洛书加密的反物质精矿",
            "- 异常：退市股票会引发反物质波动\n"
        ])
        
        # 上古/未来融合区
        locations.extend([
            "▣ 星陨谷（上古/未来融合区）",
            "- 生态：古代法阵与量子算法形成的混合防御系统",
            "- 资源：能存储神识的比特币矿机",
            "- 异常：修炼突破时引发量子计算负载峰值\n"
        ])
        
        return locations


class CharacterDNAGenerator:
    """角色DNA生成器"""
    
    def __init__(self, text_manager: TextManager):
        """初始化角色DNA生成器
        
        Args:
            text_manager: 文本管理器实例
        """
        self.text_manager = text_manager
        self.protocol_version = "1.1"
        
    def generate_character(self, era: str = None, gender: str = None, name: str = None, birth_datetime: str = None) -> Dict[str, Any]:
        """生成角色数据
        
        Args:
            era: 纪元类型 ('ancient', 'modern', 'future')
            gender: 性别 ('male' 或 'female')
            name: 角色名称
            birth_datetime: 出生日期时间
            
        Returns:
            Dict[str, Any]: 角色数据
        """
        # 如果未指定，随机生成
        if not era:
            era = random.choice(['ancient', 'modern', 'future'])
        if not gender:
            gender = random.choice(['male', 'female'])
        if not name:
            name = self._generate_name(era, gender)
        if not birth_datetime:
            birth_datetime = self._generate_birth_datetime()
            
        # 生成基本信息
        basic_info = {
            "name": name,
            "gender": gender,
            "era": era,
            "birth_datetime": birth_datetime
        }
        
        # 生成物理特征
        physical = {
            "height": random.randint(160, 190),
            "weight": random.randint(50, 90),
            "blood_type": random.choice(["A", "B", "O", "AB"]),
            "face_shape": random.choice(["圆形", "方形", "瓜子脸", "鹅蛋脸", "菱形"]),
            "eye_color": random.choice(["黑色", "棕色", "蓝色", "绿色", "琥珀色"])
        }
        
        # 生成性格特征
        personality = {
            "main_traits": random.sample([
                "开朗", "内向", "谨慎", "大胆", "理性", "感性", "乐观", "悲观",
                "正直", "圆滑", "固执", "灵活", "温和", "激进"
            ], 3),
            "minor_traits": random.sample([
                "完美主义", "拖延症", "工作狂", "理想主义", "现实主义",
                "冒险精神", "保守主义", "浪漫主义", "实用主义"
            ], 2)
        }
        
        # 生成技能
        skills = {
            "main": random.sample(self.text_manager.get_era_skills(era), 3),
            "special": []
        }
        
        # 根据纪元生成特殊能力
        special_abilities = {
            "ancient": [
                {"name": "内功心法", "level": random.randint(1, 10), "description": "运用内力增强体魄，提升战斗力。"},
                {"name": "剑术精通", "level": random.randint(1, 10), "description": "精通各种剑法，能够应对各种战斗情况。"},
                {"name": "丹道修炼", "level": random.randint(1, 10), "description": "能够炼制各种丹药，提升修为。"}
            ],
            "modern": [
                {"name": "计算机精通", "level": random.randint(1, 10), "description": "精通各种编程语言和系统架构。"},
                {"name": "商业头脑", "level": random.randint(1, 10), "description": "具有敏锐的商业洞察力和决策能力。"},
                {"name": "社交能力", "level": random.randint(1, 10), "description": "善于处理人际关系，建立有效的社交网络。"}
            ],
            "future": [
                {"name": "量子计算", "level": random.randint(1, 10), "description": "能够操作和编程量子计算机。"},
                {"name": "基因工程", "level": random.randint(1, 10), "description": "掌握基因编辑和克隆技术。"},
                {"name": "纳米技术", "level": random.randint(1, 10), "description": "能够控制和编程纳米机器人。"}
            ]
        }
        
        # 组合所有数据
        return {
            "basic": basic_info,
            "physical": physical,
            "personality": personality,
            "skills": skills,
            "special_abilities": special_abilities.get(era, [])
        }
        
    def _generate_personality_traits(self) -> Dict:
        """生成性格特征"""
        traits_pool = {
            "positive": ["勇敢", "正直", "智慧", "谨慎", "乐观", "坚韧", "温和", "细心", "果断", "耐心"],
            "neutral": ["神秘", "理性", "感性", "内向", "外向", "传统", "创新", "务实", "理想主义"],
            "negative": ["固执", "多疑", "冲动", "傲慢", "优柔寡断", "敏感", "急躁", "孤僻"]
        }
        
        return {
            "main_traits": random.sample(traits_pool["positive"], 2) + random.sample(traits_pool["neutral"], 1),
            "minor_traits": random.sample(traits_pool["neutral"], 1) + random.sample(traits_pool["negative"], 1)
        }
        
    def _generate_special_abilities(self, era: str) -> List[Dict]:
        """生成特殊能力"""
        abilities = []
        era_abilities = {
            "ancient": [
                {"name": "天眼通", "level": 1, "description": "能够看透物体表象，洞察真相"},
                {"name": "御剑术", "level": 1, "description": "操控飞剑的基础能力"},
                {"name": "丹道", "level": 1, "description": "炼制丹药的能力"},
                {"name": "符箓", "level": 1, "description": "制作和使用符箓的能力"},
                {"name": "阵法", "level": 1, "description": "布置和破解阵法的能力"}
            ],
            "modern": [
                {"name": "超感知", "level": 1, "description": "增强的感知能力"},
                {"name": "心灵感应", "level": 1, "description": "基础的心灵感应能力"},
                {"name": "能量操控", "level": 1, "description": "操控自然能量的能力"},
                {"name": "科技亲和", "level": 1, "description": "与科技设备快速同步的能力"},
                {"name": "数据分析", "level": 1, "description": "快速处理和分析数据的能力"}
            ],
            "future": [
                {"name": "量子计算", "level": 1, "description": "进行量子级运算的能力"},
                {"name": "纳米控制", "level": 1, "description": "控制纳米机器的能力"},
                {"name": "时空感知", "level": 1, "description": "感知时空波动的能力"},
                {"name": "反物质操控", "level": 1, "description": "操控反物质能量的能力"},
                {"name": "星际导航", "level": 1, "description": "进行星际空间导航的能力"}
            ]
        }
        
        # 随机选择2-3个特殊能力
        num_abilities = random.randint(2, 3)
        selected_abilities = random.sample(era_abilities[era], num_abilities)
        
        for ability in selected_abilities:
            ability["level"] = random.randint(1, 5)  # 1-5级
            abilities.append(ability)
            
        return abilities
        
    def _generate_background_story(self, era: str, gender: str, attributes: Dict[str, int]) -> Dict[str, Any]:
        """生成角色的背景故事。
        
        Args:
            era: 纪元类型
            gender: 性别
            attributes: 属性值
            
        Returns:
            Dict[str, Any]: 背景故事数据
        """
        # 根据纪元生成不同的背景故事模板
        origin_templates = {
            "ancient": [
                "出生于武林世家，自小习武",
                "生于山野道观，拜入仙门",
                "出身书香门第，精通诗书",
                "来自江湖世家，继承衣钵"
            ],
            "modern": [
                "出生于普通工薪家庭",
                "来自科技创业家庭",
                "成长于学术世家",
                "出身商业世家"
            ],
            "future": [
                "出生于太空殖民地",
                "来自地球最后的城市",
                "诞生于量子实验室",
                "成长于虚拟现实中"
            ]
        }
        
        details_templates = {
            "ancient": [
                "自幼展现出惊人的天赋，被视为修炼奇才",
                "经历重重磨难，最终悟得真传",
                "游历江湖，结识各路豪杰",
                "潜心修炼，追求大道"
            ],
            "modern": [
                "在竞争激烈的环境中成长，培养出坚韧的性格",
                "通过不断学习和实践，掌握了专业技能",
                "经历多个领域的尝试，找到自己的方向",
                "在社会变迁中寻找自己的位置"
            ],
            "future": [
                "接受最先进的教育，掌握未来科技",
                "参与多个前沿项目，推动技术革新",
                "在虚实之间穿梭，探索新的可能",
                "致力于解决人类面临的终极问题"
            ]
        }
        
        # 生成重要事件
        events = []
        current_year = int(datetime.now().year)
        birth_year = current_year - random.randint(20, 40)
        
        for i in range(3):
            age = random.randint(5 + i * 5, 10 + i * 5)
            year = birth_year + age
            
            event_templates = {
                "ancient": [
                    "开始修炼内功",
                    "习得绝世武功",
                    "参与门派大比",
                    "游历江湖历练",
                    "突破修为境界"
                ],
                "modern": [
                    "获得重要奖项",
                    "创立自己的公司",
                    "完成重要项目",
                    "达成人生目标",
                    "实现重要突破"
                ],
                "future": [
                    "完成量子计算突破",
                    "发明新型能源",
                    "探索外太空",
                    "解决环境危机",
                    "开发新技术"
                ]
            }
            
            events.append({
                "year": year,
                "age": age,
                "title": random.choice(event_templates[era]),
                "significance": random.randint(1, 5)
            })
        
        return {
            "origin": random.choice(origin_templates[era]),
            "details": random.choice(details_templates[era]),
            "important_events": sorted(events, key=lambda x: x["year"])
        }

    def generate_character_description(self, char_data: Dict) -> str:
        """生成角色描述
        
        Args:
            char_data: 角色数据
            
        Returns:
            str: 角色描述文本
        """
        # 确保角色数据中包含world_id
        if 'metadata' not in char_data or 'world_id' not in char_data['metadata']:
            raise ValueError("角色数据缺少world_id字段")
            
        world_id = char_data['metadata']['world_id']
        return self.text_manager.get_character_description(char_data, world_id, self.protocol_version)

    def _generate_name(self, era: str, gender: str) -> str:
        """生成一个符合纪元特征的角色名字。
        
        Args:
            era: 纪元类型
            gender: 性别 ('male' 或 'female')
            
        Returns:
            str: 生成的名字
        """
        name_elements = self.text_manager.get_name_elements(era)
        
        # 随机选择姓氏
        surname = random.choice(name_elements["surnames"])
        
        # 根据性别选择名字
        given_names = name_elements[f"{gender}_given"]
        given = random.choice(given_names)
        
        # 古代角色可能有中间名
        middle = ""
        if era == "ancient" and f"{gender}_middle" in name_elements:
            middle_names = name_elements[f"{gender}_middle"]
            if middle_names:
                middle = random.choice(middle_names)
        
        # 根据纪元和性别决定是否添加称号
        title = ""
        if "titles" in name_elements and random.random() < 0.3:  # 30%的概率添加称号
            title = random.choice(name_elements["titles"])
        
        # 组合名字
        if middle:
            full_name = f"{surname}{middle}{given}"
        else:
            full_name = f"{surname}{given}"
        
        # 添加称号
        if title:
            full_name = f"{full_name}{title}"
        
        return full_name

    def _generate_id(self) -> str:
        """生成一个唯一的ID。
        
        Returns:
            str: 8位十六进制ID
        """
        return uuid.uuid4().hex[:8]

    def _generate_birth_datetime(self) -> str:
        """生成一个随机的出生时间。
        
        Returns:
            str: 格式化的出生时间
        """
        year = random.randint(1950, 2020)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month}-{day}" 