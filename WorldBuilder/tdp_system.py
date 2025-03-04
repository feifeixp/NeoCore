import os
import json
import uuid
import yaml
import random
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

class TDPManager:
    """三纪元维度锚定协议(TDP)管理器"""
    
    def __init__(self, storage_dir: str):
        """初始化TDP管理器
        
        Args:
            storage_dir: 存储目录路径
        """
        self.storage_dir = storage_dir
        self._ensure_storage_exists()
        
    def _ensure_storage_exists(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "worlds"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "characters"), exist_ok=True)
        
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
        
        # 保存世界数据
        world_path = os.path.join(self.storage_dir, "worlds", f"{world_id}.json")
        with open(world_path, "w", encoding="utf-8") as f:
            json.dump(world_data, f, ensure_ascii=False, indent=2)
            
        return world_id
        
    def create_character(self, world_id: str, birth_datetime: datetime, 
                        gender: str, era: str, character_name: str = None) -> Tuple[str, Dict]:
        """创建角色
        
        Args:
            world_id: 世界ID
            birth_datetime: 出生日期时间
            gender: 性别
            era: 纪元
            character_name: 角色名称（可选）
            
        Returns:
            Tuple[str, Dict]: 角色ID和角色数据
        """
        # 生成角色ID
        char_id = f"CHAR-{uuid.uuid4().hex[:8]}"
        
        # 生成角色数据
        metadata = {
            "id": char_id,
            "world_id": world_id,
            "name": character_name if character_name else self._generate_name(gender),
            "birth_datetime": birth_datetime.isoformat(),
            "gender": gender,
            "era": era,
            "created_at": datetime.now().isoformat()
        }
        
        # 生成基础属性
        attributes = {
            "strength": random.randint(50, 100),
            "intelligence": random.randint(50, 100),
            "charisma": random.randint(50, 100)
        }
        
        # 生成技能
        skills = self._generate_skills(era)
        
        character_data = {
            "metadata": metadata,
            "attributes": attributes,
            "skills": skills
        }
        
        # 保存角色数据
        char_path = os.path.join(self.storage_dir, "characters", f"{char_id}.json")
        with open(char_path, "w", encoding="utf-8") as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
            
        # 更新世界数据
        world_path = os.path.join(self.storage_dir, "worlds", f"{world_id}.json")
        with open(world_path, "r", encoding="utf-8") as f:
            world_data = json.load(f)
        world_data["characters"].append(char_id)
        with open(world_path, "w", encoding="utf-8") as f:
            json.dump(world_data, f, ensure_ascii=False, indent=2)
            
        return char_id, character_data
        
    def get_characters_in_world(self, world_id: str) -> list:
        """获取世界中的所有角色
        
        Args:
            world_id: 世界ID
            
        Returns:
            list: 角色信息列表
        """
        # 读取世界数据
        world_path = os.path.join(self.storage_dir, "worlds", f"{world_id}.json")
        with open(world_path, "r", encoding="utf-8") as f:
            world_data = json.load(f)
            
        characters = []
        for char_id in world_data.get("character_ids", []):
            # 读取每个角色的数据
            char_path = os.path.join(self.storage_dir, "characters", f"{char_id}.json")
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
        
    def _generate_name(self, gender: str) -> str:
        """生成角色名字
        
        Args:
            gender: 性别
            
        Returns:
            str: 生成的名字
        """
        # 简单的名字生成逻辑
        surnames = ["李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        male_names = ["军", "强", "明", "建", "光", "华", "伟", "力", "超", "峰"]
        female_names = ["芳", "娟", "敏", "静", "秀", "丽", "雪", "琴", "燕", "玲"]
        
        import random
        surname = random.choice(surnames)
        if gender == "male":
            name = random.choice(male_names)
        else:
            name = random.choice(female_names)
            
        return surname + name 

    def _generate_skills(self, era: str) -> List[str]:
        """生成符合纪元特征的技能"""
        if era == "ancient":
            skills = [
                "道法自然",
                "五行相生",
                "天地灵气",
                "符箓之术",
                "丹道修炼"
            ]
        elif era == "future":
            skills = [
                "量子计算",
                "纳米技术",
                "意识上传",
                "基因编程",
                "时空跃迁"
            ]
        else:
            skills = [
                "数据分析",
                "项目管理",
                "资源整合",
                "战略规划",
                "团队领导"
            ]
        return random.sample(skills, 3)  # 随机选择3个技能

    def get_world_description(self, world_id: str) -> str:
        """获取世界描述
        
        Args:
            world_id: 世界ID
            
        Returns:
            str: 世界描述文本
        """
        # 读取世界数据
        world_path = os.path.join(self.storage_dir, "worlds", f"{world_id}.json")
        with open(world_path, "r", encoding="utf-8") as f:
            world_data = json.load(f)
            
        # 生成世界描述
        description = [
            f"世界编号：{world_id}",
            f"法则校验码：#{world_id.split('-')[1]}-{uuid.uuid4().hex[:4].upper()}\n"
        ]
        
        # 添加熵增监控面板
        description.extend([
            "[熵增监控面板]",
            "参数                    当前值              阈值                状态",
            f"灵气-石油转化率         1:{random.uniform(3.5,4.5):.1f}桶          1:4.0桶            {'稳定' if random.random() > 0.5 else '经济预警'}",
            f"渡劫成功概率            {random.uniform(60,70):.1f}%            量子计算修正值      {random.choice(['+','-'])}{random.uniform(5,7):.1f}%",
            f"反物质泄漏次数          {random.randint(20,29)}/月              30次/月            安全范围",
            f"时空因果扰动指数        {random.uniform(85,95):.1f}            100.0              维度稳定\n"
        ])
        
        # 添加协议声明
        description.append(
            f"该世界严格遵循TDP协议v1.1生成，任何参数修改超过±0.3%将导致"
            f"#{world_id.split('-')[1]}-{uuid.uuid4().hex[:4].upper()}校验码失效并生成平行宇宙。"
            f"当前时空连续性担保期至{datetime.now().year + 1}-12-31。"
        )
        
        return "\n".join(description)
        
    def get_character_description(self, world_id: str, char_id: str) -> str:
        """获取角色描述
        
        Args:
            world_id: 世界ID
            char_id: 角色ID
            
        Returns:
            str: 角色描述文本
        """
        # 读取角色数据
        char_path = os.path.join(self.storage_dir, "characters", f"{char_id}.json")
        with open(char_path, "r", encoding="utf-8") as f:
            char_data = json.load(f)
            
        meta = char_data["metadata"]
        name = meta["name"]
        era = meta["era"]
        
        description = [
            f"「{self._get_era_title(era)}」命理驱动角色实例：{name}\n",
            f"灵魂签名： {char_id}",
            f"适用宇宙：{world_id}\n",
            "一、先天命盘解析",
            f"出生时刻：{meta['birth_datetime']}\n",
            "1.1 命盘核心参数",
            "四柱量子编码:",
            "  年柱: 甲申 → 土+2 火+1",
            "  月柱: 丙寅 → 土+2 火+1",
            "  日柱: 甲申 → 土+2 火+1",
            "  时柱: 壬申 → 土+1 火+2\n",
            "五行能量场:",
            "  金: ███████◌◌◌ 73%",
            "  木: ██◌◌◌◌◌◌◌◌ 26%",
            "  水: ◌◌◌◌◌◌◌◌◌◌ 0%",
            "  火: ◌◌◌◌◌◌◌◌◌◌ 0%",
            "  土: ◌◌◌◌◌◌◌◌◌◌ 0%\n"
        ]
        
        # 添加技能描述
        description.extend([
            "二、技能系统",
            "■ 主要能力:",
            *[f"  - {skill}" for skill in char_data["skills"]],
            "\n■ 能力值:",
            f"  - 攻击: {char_data['attributes']['strength']}",
            f"  - 防御: {char_data['attributes']['charisma']}",
            f"  - 智力: {char_data['attributes']['intelligence']}\n"
        ])
        
        # 添加协议声明
        description.append(
            f"该角色由命理驱动的量子叠加态人生轨迹，在确定性与可能性之间达到精妙平衡。"
            f"完全符合VUCCP v1.0和TDP v1.1协议标准。"
        )
        
        return "\n".join(description)
        
    def _get_era_title(self, era: str) -> str:
        """获取纪元显示标题"""
        titles = {
            "ancient": "修真",
            "modern": "现代",
            "future": "未来"
        }
        return titles.get(era, era)

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
    
    def __init__(self, world_id: str):
        """初始化角色DNA生成器
        
        Args:
            world_id: 世界ID
        """
        self.world_id = world_id
        self.protocol_version = "1.1"
        
    def generate_character(self, birth_datetime: datetime, gender: str, 
                          era: str, character_name: str = None) -> Dict:
        """生成角色数据
        
        Args:
            birth_datetime: 出生日期时间
            gender: 性别
            era: 纪元
            character_name: 角色名称（可选）
            
        Returns:
            Dict: 角色数据
        """
        soul_id = f"SOUL-{uuid.uuid4().hex[:6].upper()}"
        
        if character_name is None:
            character_name = self._generate_name(gender, era)
            
        metadata = {
            "soul_id": soul_id,
            "name": character_name,
            "birth_datetime": birth_datetime.isoformat(),
            "gender": gender,
            "era": era,
            "created_at": datetime.now().isoformat()
        }
        
        # 生成基础属性
        attributes = {
            "strength": random.randint(50, 100),
            "intelligence": random.randint(50, 100),
            "charisma": random.randint(50, 100)
        }
        
        # 生成技能
        skills = self._generate_skills(era)
        
        return {
            "metadata": metadata,
            "attributes": attributes,
            "skills": skills
        }
        
    def generate_character_description(self, char_data: Dict) -> str:
        """生成角色描述
        
        Args:
            char_data: 角色数据
            
        Returns:
            str: 角色描述文本
        """
        meta = char_data["metadata"]
        name = meta["name"]
        era = meta["era"]
        
        description = [
            f"「{self._get_era_title(era)}」命理驱动角色实例：{name}\n",
            f"灵魂签名： {meta['soul_id']}",
            f"适用宇宙：{self.world_id}\n",
            "一、先天命盘解析",
            f"出生时刻：{meta['birth_datetime']}\n",
            "1.1 命盘核心参数",
            "四柱量子编码:",
            "  年柱: 甲申 → 土+2 火+1",
            "  月柱: 丙寅 → 土+2 火+1",
            "  日柱: 甲申 → 土+2 火+1",
            "  时柱: 壬申 → 土+1 火+2\n",
            "五行能量场:",
            "  金: ███████◌◌◌ 73%",
            "  木: ██◌◌◌◌◌◌◌◌ 26%",
            "  水: ◌◌◌◌◌◌◌◌◌◌ 0%",
            "  火: ◌◌◌◌◌◌◌◌◌◌ 0%",
            "  土: ◌◌◌◌◌◌◌◌◌◌ 0%\n"
        ]
        
        # 添加技能描述
        description.extend([
            "二、技能系统",
            "■ 主要能力:",
            *[f"  - {skill}" for skill in char_data["skills"]],
            "\n■ 能力值:",
            f"  - 攻击: {char_data['attributes']['strength']}",
            f"  - 防御: {char_data['attributes']['charisma']}",
            f"  - 智力: {char_data['attributes']['intelligence']}\n"
        ])
        
        # 添加协议声明
        description.append(
            f"该角色由命理驱动的量子叠加态人生轨迹，在确定性与可能性之间达到精妙平衡。"
            f"完全符合VUCCP v1.0和TDP v{self.protocol_version}协议标准。"
        )
        
        return "\n".join(description)
    
    def _get_era_title(self, era: str) -> str:
        """获取纪元显示标题"""
        titles = {
            "ancient": "修真",
            "modern": "现代",
            "future": "未来"
        }
        return titles.get(era, era)
    
    def _generate_name(self, gender: str, era: str) -> str:
        """生成符合纪元特征的名字"""
        if era == "ancient":
            surnames = ["玄", "青", "紫", "金", "白"]
            titles = ["真人", "道君", "仙子", "天君", "圣女"]
        elif era == "future":
            surnames = ["量子", "星", "银", "光", "电子"]
            titles = ["研究员", "工程师", "设计师", "指挥官", "专家"]
        else:
            surnames = ["李", "王", "张", "刘", "陈"]
            titles = ["博士", "教授", "总监", "主任", "经理"]
            
        name = random.choice(surnames)
        if gender == "female" and era == "ancient":
            name += random.choice(["霜", "雪", "月", "云", "灵"]) + random.choice(titles)
        else:
            name += random.choice(["天", "地", "山", "河", "海"]) + random.choice(titles)
            
        return name
    
    def _generate_skills(self, era: str) -> List[str]:
        """生成符合纪元特征的技能"""
        skills = []
        if era == "ancient":
            skills = [
                "道法自然",
                "五行相生",
                "天地灵气",
                "符箓之术",
                "丹道修炼"
            ]
        elif era == "future":
            skills = [
                "量子计算",
                "纳米技术",
                "意识上传",
                "基因编程",
                "时空跃迁"
            ]
        else:
            skills = [
                "数据分析",
                "项目管理",
                "资源整合",
                "战略规划",
                "团队领导"
            ]
        return random.sample(skills, 3)  # 随机选择3个技能 