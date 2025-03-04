import numpy as np
import hashlib
import yaml
import json
import random
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional


class TDPWorldGenerator:
    """三纪元维度锚定协议(TDP)世界生成器"""
    
    def __init__(self, protocol_version="1.1"):
        """初始化世界生成器
        
        Args:
            protocol_version: TDP协议版本，默认为1.1
        """
        self.protocol_version = protocol_version
        self.era_tags = ["ancient", "modern", "future"]
        self.creation_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # 初始化基础模块
        self.modules = {
            "geo": {"axes": []},
            "faction": {"axes": []},
            "tech": {"axes": []},
            "event": {"axes": []}
        }
        
        # 初始化规则配置
        self.rules = {
            "cross_era_interaction": True,
            "entropy_constraint": 0.78,
            "isolation_mechanism": []
        }
        
        # 初始化验证信息
        self.validation = {
            "checksum": "",
            "last_modified": self.creation_time
        }
        
        # 初始化世界状态
        self.universe_id = ""
        self.entropy = 0.0
        self.world_output = {}
    
    def add_dimension_axis(self, module: str, name: str, options: List[str], weights: List[float] = None):
        """添加维度轴
        
        Args:
            module: 模块名称 (geo, faction, tech, event)
            name: 轴的名称
            options: 选项列表，每个选项应包含三个纪元的对应选项
            weights: 三个纪元的权重，默认为平均
        """
        if module not in self.modules:
            raise ValueError(f"未知模块: {module}")
        
        if len(options) != 3:
            raise ValueError(f"选项必须包含三个纪元对应的选项")
        
        if weights is None:
            weights = [0.33, 0.34, 0.33]  # 默认权重接近平均
        
        if len(weights) != 3 or abs(sum(weights) - 1.0) > 0.01:
            raise ValueError("权重必须是3个值且总和为1.0")
        
        axis = {
            "name": name,
            "options": options,
            "weights": weights,
            "era_tags": self.era_tags
        }
        
        self.modules[module]["axes"].append(axis)
    
    def set_rule(self, rule_key: str, value: Any):
        """设置世界规则
        
        Args:
            rule_key: 规则键名
            value: 规则值
        """
        if rule_key in self.rules:
            self.rules[rule_key] = value
        else:
            raise ValueError(f"未知规则: {rule_key}")
    
    def _apply_time_rules(self, era_weights):
        """应用时间流速规则
        
        根据v1.1协议，不同纪元有不同的时间流速特性
        
        Args:
            era_weights: 各纪元权重
            
        Returns:
            调整后的时间流速参数
        """
        # 上古/当代/未来 = 非线性/线性/量子化
        time_flow = {
            "ancient": {"type": "nonlinear", "factor": era_weights[0] * 2.0},
            "modern": {"type": "linear", "factor": era_weights[1]},
            "future": {"type": "quantum", "factor": era_weights[2] * 1.5}
        }
        return time_flow
    
    def _calculate_universe_hash(self, config):
        """计算宇宙指纹
        
        使用SHA256生成宇宙唯一标识符
        
        Args:
            config: 配置数据
            
        Returns:
            宇宙指纹哈希值
        """
        # 提取核心参数
        weights_str = json.dumps(self._extract_all_weights(config))
        options_hash = hashlib.sha256(json.dumps(self._extract_all_options(config)).encode()).hexdigest()
        time_flow = json.dumps(self._apply_time_rules(self._calculate_era_weights(config)))
        
        # 生成唯一标识符
        hash_input = f"{weights_str}{options_hash}{time_flow}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    
    def _extract_all_weights(self, config):
        """提取所有权重"""
        weights = {}
        for module, module_data in config.items():
            if module in self.modules:
                weights[module] = []
                for axis in module_data.get("axes", []):
                    weights[module].append(axis.get("weights", [0.33, 0.34, 0.33]))
        return weights
    
    def _extract_all_options(self, config):
        """提取所有选项"""
        options = {}
        for module, module_data in config.items():
            if module in self.modules:
                options[module] = []
                for axis in module_data.get("axes", []):
                    options[module].append([o for o in axis.get("options", [])])
        return options
    
    def _calculate_era_weights(self, config):
        """计算各纪元的总体权重"""
        all_weights = []
        for module, module_data in config.items():
            if module in self.modules:
                for axis in module_data.get("axes", []):
                    all_weights.append(axis.get("weights", [0.33, 0.34, 0.33]))
        
        if not all_weights:
            return [0.33, 0.34, 0.33]
            
        # 计算平均权重
        era_weights = np.mean(all_weights, axis=0)
        return era_weights.tolist()
    
    def _calc_entropy(self, config, time_flow):
        """计算世界熵值
        
        根据v1.1协议的熵增公式计算
        
        Args:
            config: 配置数据
            time_flow: 时间流速数据
            
        Returns:
            世界熵值 (0.0-1.0)
        """
        era_weights = self._calculate_era_weights(config)
        
        # 熵增公式: α(上古灵脉衰减) + β(工业污染强度) - γ(量子纠错能力)
        ancient_decay = 0.4 * era_weights[0] * time_flow["ancient"]["factor"]
        industrial_pollution = 0.5 * era_weights[1] * time_flow["modern"]["factor"]
        quantum_correction = 0.3 * era_weights[2] * time_flow["future"]["factor"]
        
        entropy = ancient_decay + industrial_pollution - quantum_correction
        
        # 检测中和区
        if self._check_neutral_zone(config):
            entropy *= 0.6  # 中和区熵值衰减
            
        return max(0.0, min(1.0, entropy))
    
    def _check_neutral_zone(self, config):
        """检查是否存在法则中和区"""
        # 检查是否允许跨纪元交互
        if not self.rules.get("cross_era_interaction", False):
            return False
            
        # 检查特定区域设置
        for module, module_data in config.items():
            if module in self.modules:
                for axis in module_data.get("axes", []):
                    # 如果某个维度的权重分布相对均匀，认为存在中和区
                    weights = axis.get("weights", [0.33, 0.34, 0.33])
                    if max(weights) - min(weights) < 0.2:
                        return True
        return False
    
    def _calculate_universe_difference(self, universe_a, universe_b):
        """计算两个宇宙之间的差异度Δ
        
        Δ = ∑|w₁ᵢ-w₂ᵢ| + 0.3×选项差异数
        
        Args:
            universe_a: 第一个宇宙配置
            universe_b: 第二个宇宙配置
            
        Returns:
            差异度Δ (0.0-1.0)
        """
        weights_a = self._extract_all_weights(universe_a)
        weights_b = self._extract_all_weights(universe_b)
        
        # 计算权重差异
        weight_diff = 0.0
        option_diff = 0
        
        for module in self.modules:
            if module in weights_a and module in weights_b:
                for i, axis_a in enumerate(weights_a[module]):
                    if i < len(weights_b[module]):
                        axis_b = weights_b[module][i]
                        for j in range(3):  # 三个纪元
                            weight_diff += abs(axis_a[j] - axis_b[j])
        
        # 计算选项差异
        options_a = self._extract_all_options(universe_a)
        options_b = self._extract_all_options(universe_b)
        
        for module in self.modules:
            if module in options_a and module in options_b:
                for i, axis_a in enumerate(options_a[module]):
                    if i < len(options_b[module]):
                        axis_b = options_b[module][i]
                        for j in range(len(axis_a)):
                            if j < len(axis_b) and axis_a[j] != axis_b[j]:
                                option_diff += 1
        
        # 最终差异度
        delta = weight_diff + 0.3 * option_diff
        
        # 归一化到0-1范围
        max_possible_diff = len(self.modules) * 6 * 2  # 最大可能差异
        delta = min(1.0, delta / max_possible_diff)
        
        return delta
    
    def generate_world(self):
        """生成一个完整的世界
        
        Returns:
            生成的世界配置
        """
        # 1. 构建基础配置
        config = {
            "metadata": {
                "protocol_name": "TDP",
                "version_hash": "",
                "universe_id": "",
                "creation_time": self.creation_time
            },
            "geo": {"axes": []},
            "faction": {"axes": []},
            "tech": {"axes": []},
            "event": {"axes": []},
            "rules": self.rules,
            "validation": self.validation
        }
        
        # 复制模块配置
        for module_name, module_data in self.modules.items():
            config[module_name]["axes"] = module_data["axes"]
        
        # 2. 应用时间流速规则
        era_weights = self._calculate_era_weights(config)
        time_flow = self._apply_time_rules(era_weights)
        
        # 3. 计算宇宙指纹
        universe_hash = self._calculate_universe_hash(config)
        config["metadata"]["version_hash"] = universe_hash
        config["metadata"]["universe_id"] = f"TDP-{universe_hash}-{datetime.now().year}"
        
        # 4. 计算熵值
        entropy = self._calc_entropy(config, time_flow)
        
        # 5. 保存结果
        self.universe_id = config["metadata"]["universe_id"]
        self.entropy = entropy
        self.world_output = config
        
        # 6. 添加验证信息
        config["validation"]["checksum"] = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]
        config["validation"]["last_modified"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return config
    
    def generate_world_description(self):
        """生成世界描述
        
        基于生成的世界配置创建文字描述
        
        Returns:
            世界描述文本
        """
        if not self.world_output:
            raise ValueError("请先调用generate_world()生成世界")
        
        # 基本信息
        universe_id = self.world_output["metadata"]["universe_id"]
        law_code = f"#{universe_id.split('-')[1]}-{random.randint(1000, 9999):X}"
        
        # 1. 生成地理描述
        geo_description = []
        if "geo" in self.world_output and "axes" in self.world_output["geo"]:
            for axis in self.world_output["geo"]["axes"]:
                era_mix = self._get_mixed_description(axis)
                if era_mix:
                    geo_description.append(era_mix)
        
        # 2. 生成势力描述
        faction_description = []
        if "faction" in self.world_output and "axes" in self.world_output["faction"]:
            for axis in self.world_output["faction"]["axes"]:
                era_mix = self._get_mixed_description(axis)
                if era_mix:
                    faction_description.append(era_mix)
        
        # 3. 生成科技描述
        tech_description = []
        if "tech" in self.world_output and "axes" in self.world_output["tech"]:
            for axis in self.world_output["tech"]["axes"]:
                era_mix = self._get_mixed_description(axis)
                if era_mix:
                    tech_description.append(era_mix)
        
        # 生成典型地点
        locations = self._generate_mixed_locations()
        
        # 构建完整描述
        description = f"""世界编号：{universe_id}
法则校验码：{law_code}

[地理构造]
{''.join(geo_description)}

[势力矩阵]
{''.join(faction_description)}

[科技树]
{''.join(tech_description)}

[典型地点]
{''.join(locations)}

[熵增监控面板]
参数                    当前值              阈值                状态
灵气-石油转化率         1:{random.randint(30, 45)/10}桶          1:4.0桶            {'经济预警' if random.random() > 0.5 else '稳定'}
渡劫成功概率            {random.randint(600, 700)/10}%            量子计算修正值      {random.choice(['+', '-'])}{random.randint(50, 90)/10}%
反物质泄漏次数          {random.randint(20, 29)}/月              30次/月            安全范围
时空因果扰动指数        {random.randint(850, 950)/10}            100.0              维度稳定

该世界严格遵循TDP协议v{self.protocol_version}生成，任何参数修改超过±0.3%将导致{law_code}校验码失效并生成平行宇宙。当前时空连续性担保期至{datetime.now().year+1}-12-31。
"""
        return description
    
    def _get_mixed_description(self, axis):
        """根据权重生成混合描述"""
        if not axis or "options" not in axis or "weights" not in axis:
            return ""
            
        name = axis.get("name", "未命名轴")
        options = axis.get("options", [])
        weights = axis.get("weights", [0.33, 0.34, 0.33])
        
        # 根据权重选择主导纪元
        dominant_era = np.argmax(weights)
        
        # 次要纪元
        secondary_eras = [i for i in range(3) if i != dominant_era and weights[i] > 0.2]
        
        # 确保有描述信息
        if not options or dominant_era >= len(options):
            return ""
            
        description = f"■ {name}: {options[dominant_era]}"
        
        # 添加混合元素
        for era in secondary_eras:
            if era < len(options):
                description += f", 混合{self.era_tags[era]}元素({int(weights[era]*100)}%)"
        
        return description + "\n"
    
    def _generate_mixed_locations(self):
        """生成混合地点描述"""
        # 检查是否允许跨纪元元素混合
        if not self.rules.get("cross_era_interaction", True):
            return ["由于严格隔离各纪元元素，本宇宙中不存在混合地点。\n"]
        
        # 获取各纪元权重
        era_weights = self._calculate_era_weights(self.world_output)
        
        # 确定存在的元素融合
        fusions = []
        if era_weights[0] > 0.2 and era_weights[1] > 0.2:
            fusions.append(("上古", "当代"))
        if era_weights[1] > 0.2 and era_weights[2] > 0.2:
            fusions.append(("当代", "未来"))
        if era_weights[0] > 0.2 and era_weights[2] > 0.2:
            fusions.append(("上古", "未来"))
            
        # 如果没有可能的融合，返回空
        if not fusions:
            return ["各纪元元素分布过于极端，不存在明显的混合地点。\n"]
            
        # 生成描述
        locations = []
        for fusion in fusions:
            location_name = self._generate_location_name(fusion)
            locations.append(f"▣ {location_name}（{fusion[0]}/{fusion[1]}融合区）\n")
            
            # 生成特性
            characteristics = [
                f"- 生态：{self._generate_ecology_description(fusion)}",
                f"- 资源：{self._generate_resource_description(fusion)}",
                f"- 异常：{self._generate_anomaly_description(fusion)}"
            ]
            locations.extend([f"{c}\n" for c in characteristics])
            locations.append("\n")
            
        return locations
    
    def _generate_location_name(self, fusion):
        """生成地点名称"""
        prefixes = {
            ("上古", "当代"): ["灵脉", "古今", "仙域", "灵械"],
            ("当代", "未来"): ["赛博", "量子", "反物质", "进化"],
            ("上古", "未来"): ["时空", "混沌", "星陨", "界限"]
        }
        
        suffixes = ["城", "区", "谷", "港", "塔", "界", "域", "站", "矿", "渊"]
        
        prefix = random.choice(prefixes.get(fusion, ["神秘"]))
        suffix = random.choice(suffixes)
        
        return f"{prefix}{suffix}"
    
    def _generate_ecology_description(self, fusion):
        """生成生态描述"""
        ecology_templates = {
            ("上古", "当代"): [
                "摩天大楼内生长着聚灵竹，地下车库豢养电子妖兽",
                "高楼之间飘浮着小型灵脉岛，墙体内部生长符文苔藓",
                "商业街上空悬浮着古代仙家洞府，市政喷泉涌出灵泉"
            ],
            ("当代", "未来"): [
                "悬浮反应堆下方的仿生鲟鱼养殖场",
                "量子态波动公园内的自适应变形楼群",
                "纳米聚变路灯照耀下的智能生态花园"
            ],
            ("上古", "未来"): [
                "修真者与赛博格混居的量子纠缠社区",
                "灵兽与智能机械生命共存的浮空岛",
                "古代法阵与量子算法形成的混合防御系统"
            ]
        }
        
        return random.choice(ecology_templates.get(fusion, ["混合生态系统"]))
    
    def _generate_resource_description(self, fusion):
        """生成资源描述"""
        resource_templates = {
            ("上古", "当代"): [
                "可提炼灵石的页岩气田（灵气纯度：72%）",
                "电磁辐射充能的古代符箓",
                "现代工业废料中孕育的灵草"
            ],
            ("当代", "未来"): [
                "用河图洛书加密的反物质精矿",
                "碳纳米管与量子波导合成材料",
                "生物神经网络训练的AI模型"
            ],
            ("上古", "未来"): [
                "能存储神识的比特币矿机",
                "古代丹炉炼制的量子态元素",
                "灵气驱动的反物质转化装置"
            ]
        }
        
        return random.choice(resource_templates.get(fusion, ["混合能源矿藏"]))
    
    def _generate_anomaly_description(self, fusion):
        """生成异常现象描述"""
        anomaly_templates = {
            ("上古", "当代"): [
                "股市开盘时灵气浓度下降30%",
                "手机信号强度与区域灵脉活跃度成正比",
                "古代符箓可以屏蔽无线电信号"
            ],
            ("当代", "未来"): [
                "每月农历十五发生微型黑洞泄漏",
                "区域内所有电子设备偶发量子态叠加",
                "退市股票会引发反物质波动"
            ],
            ("上古", "未来"): [
                "御剑飞行会触发无人机防空系统",
                "修炼突破时引发量子计算负载峰值",
                "灵气超标导致时空薄弱点形成"
            ]
        }
        
        return random.choice(anomaly_templates.get(fusion, ["时空异常现象"]))
    
    def export_to_yaml(self, file_path):
        """导出世界配置到YAML文件
        
        Args:
            file_path: 输出文件路径
        """
        if not self.world_output:
            raise ValueError("请先调用generate_world()生成世界")
            
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.world_output, f, default_flow_style=False, allow_unicode=True)
            
    def load_from_yaml(self, file_path):
        """从YAML文件加载世界配置
        
        Args:
            file_path: YAML文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 验证配置格式
        if not config or "metadata" not in config:
            raise ValueError("无效的配置文件格式")
            
        # 加载配置
        self.world_output = config
        self.universe_id = config["metadata"].get("universe_id", "")
        
        # 加载模块
        for module_name in self.modules:
            if module_name in config:
                self.modules[module_name] = config[module_name]
                
        # 加载规则
        if "rules" in config:
            self.rules = config["rules"]
            
        # 加载验证信息
        if "validation" in config:
            self.validation = config["validation"]


class CharacterDNAGenerator:
    """角色DNA生成器 - DestinyFlow协议实现"""
    
    def __init__(self, tdp_world=None):
        """初始化角色DNA生成器
        
        Args:
            tdp_world: TDP世界生成器实例或世界ID
        """
        self.tdp_world = tdp_world
        self.universe_id = ""
        
        if tdp_world is not None:
            if isinstance(tdp_world, TDPWorldGenerator):
                self.universe_id = tdp_world.universe_id
            else:
                self.universe_id = str(tdp_world)
        
        self.era_factors = {
            "ancient": {
                "elements": {"木": 1.5, "火": 1.5, "金": 1.0, "水": 1.0, "土": 1.0},
                "role_transform": {
                    "正官": "门派长老",
                    "偏财": "奇珍异宝",
                    "正印": "传承秘籍",
                    "七杀": "邪修巨擘",
                    "伤官": "丹道宗师"
                }
            },
            "modern": {
                "elements": {"土": 1.2, "金": 1.2, "木": 1.0, "水": 1.0, "火": 1.0},
                "role_transform": {
                    "正官": "高管领导",
                    "偏财": "意外收益",
                    "正印": "学术成就",
                    "七杀": "竞争对手",
                    "伤官": "发明创造"
                }
            },
            "future": {
                "elements": {"金": 2.0, "水": 2.0, "火": 1.0, "土": 0.8, "木": 0.8},
                "role_transform": {
                    "正官": "AI伦理准则",
                    "偏财": "数据资产",
                    "正印": "量子意识",
                    "七杀": "黑客领袖",
                    "伤官": "算法突破"
                }
            }
        }
    
    def set_universe(self, universe_id):
        """设置角色所属宇宙ID
        
        Args:
            universe_id: 宇宙ID
        """
        self.universe_id = universe_id
        
    def _quantum_ganzhi(self, value):
        """将数值转换为叠加态天干地支
        
        Args:
            value: 输入值
            
        Returns:
            天干地支组合
        """
        gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        gan = gan_list[value % 10]
        zhi = zhi_list[value % 12]
        
        return f"{gan}{zhi}"
    
    def _calculate_nayin_element(self, pillar):
        """计算纳音五行
        
        Args:
            pillar: 天干地支
            
        Returns:
            五行属性
        """
        # 简化版纳音五行对照表
        nayin_map = {
            "甲子": "水", "乙丑": "土", "丙寅": "木", "丁卯": "木",
            "戊辰": "土", "己巳": "火", "庚午": "火", "辛未": "土",
            "壬申": "金", "癸酉": "金", "甲戌": "土", "乙亥": "水",
            "丙子": "水", "丁丑": "土", "戊寅": "木", "己卯": "木",
            "庚辰": "土", "辛巳": "火", "壬午": "火", "癸未": "土",
            "甲申": "金", "乙酉": "金", "丙戌": "土", "丁亥": "水",
            "戊子": "水", "己丑": "土", "庚寅": "木", "辛卯": "木",
            "壬辰": "土", "癸巳": "火", "甲午": "火", "乙未": "土",
            "丙申": "金", "丁酉": "金", "戊戌": "土", "己亥": "水",
            "庚子": "水", "辛丑": "土", "壬寅": "木", "癸卯": "木",
            "甲辰": "土", "乙巳": "火", "丙午": "火", "丁未": "土",
            "戊申": "金", "己酉": "金", "庚戌": "土", "辛亥": "水",
            "壬子": "水", "癸丑": "土", "甲寅": "木", "乙卯": "木",
            "丙辰": "土", "丁巳": "火", "戊午": "火", "己未": "土",
            "庚申": "金", "辛酉": "金", "壬戌": "土", "癸亥": "水"
        }
        
        # 如果没有对应，返回默认值
        return nayin_map.get(pillar, "土")

    def _calc_nayin_matrix(self, pillars):
        """计算五行能量强度矩阵
        
        Args:
            pillars: 四柱列表
            
        Returns:
            五行能量矩阵
        """
        elements = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        weights = [1.0, 1.2, 1.5, 0.8]  # 年、月、日、时的权重
        
        for i, pillar in enumerate(pillars):
            element = self._calculate_nayin_element(pillar)
            elements[element] += weights[min(i, len(weights)-1)]
        
        # 归一化处理
        total = sum(elements.values())
        if total > 0:
            for element in elements:
                elements[element] /= total
                
        return elements
    
    def _identify_gods(self, day_master, pillars):
        """识别十神格局
        
        Args:
            day_master: 日主天干
            pillars: 四柱列表
            
        Returns:
            十神组合
        """
        # 简化版十神关系表
        god_map = {
            "甲": {"甲": "比肩", "乙": "劫财", "丙": "食神", "丁": "伤官", 
                  "戊": "偏财", "己": "正财", "庚": "七杀", "辛": "正官", 
                  "壬": "偏印", "癸": "正印"},
            "乙": {"甲": "劫财", "乙": "比肩", "丙": "食神", "丁": "伤官", 
                  "戊": "偏财", "己": "正财", "庚": "七杀", "辛": "正官", 
                  "壬": "偏印", "癸": "正印"},
            "丙": {"甲": "偏印", "乙": "正印", "丙": "比肩", "丁": "劫财", 
                  "戊": "食神", "己": "伤官", "庚": "偏财", "辛": "正财", 
                  "壬": "七杀", "癸": "正官"},
            "丁": {"甲": "偏印", "乙": "正印", "丙": "劫财", "丁": "比肩", 
                  "戊": "食神", "己": "伤官", "庚": "偏财", "辛": "正财", 
                  "壬": "七杀", "癸": "正官"},
            "戊": {"甲": "七杀", "乙": "正官", "丙": "偏印", "丁": "正印", 
                  "戊": "比肩", "己": "劫财", "庚": "食神", "辛": "伤官", 
                  "壬": "偏财", "癸": "正财"},
            "己": {"甲": "七杀", "乙": "正官", "丙": "偏印", "丁": "正印", 
                  "戊": "劫财", "己": "比肩", "庚": "食神", "辛": "伤官", 
                  "壬": "偏财", "癸": "正财"},
            "庚": {"甲": "正财", "乙": "偏财", "丙": "七杀", "丁": "正官", 
                  "戊": "偏印", "己": "正印", "庚": "比肩", "辛": "劫财", 
                  "壬": "食神", "癸": "伤官"},
            "辛": {"甲": "正财", "乙": "偏财", "丙": "七杀", "丁": "正官", 
                  "戊": "偏印", "己": "正印", "庚": "劫财", "辛": "比肩", 
                  "壬": "食神", "癸": "伤官"},
            "壬": {"甲": "伤官", "乙": "食神", "丙": "正财", "丁": "偏财", 
                  "戊": "七杀", "己": "正官", "庚": "偏印", "辛": "正印", 
                  "壬": "比肩", "癸": "劫财"},
            "癸": {"甲": "伤官", "乙": "食神", "丙": "正财", "丁": "偏财", 
                  "戊": "七杀", "己": "正官", "庚": "偏印", "辛": "正印", 
                  "壬": "劫财", "癸": "比肩"}
        }
        
        gods = []
        for pillar in pillars:
            god = god_map.get(day_master, {}).get(pillar[0], "未知")
            gods.append(god)
            
        return gods
    
    def _find_shensha(self, pillars):
        """计算神煞系统
        
        Args:
            pillars: 四柱列表
            
        Returns:
            神煞列表
        """
        # 简化版神煞规则
        shensha = []
        
        # 检查天乙贵人
        tian_yi_gan = {"甲": "癸", "乙": "壬", "丙": "辛", "丁": "庚", "戊": "己", "己": "戊", 
                       "庚": "丁", "辛": "丙", "壬": "乙", "癸": "甲"}
        tian_yi_zhi = {"子": "丑", "丑": "子", "寅": "亥", "卯": "戌", "辰": "酉", "巳": "申", 
                       "午": "未", "未": "午", "申": "巳", "酉": "辰", "戌": "卯", "亥": "寅"}
        
        year_gan = pillars[0][0]
        if year_gan in tian_yi_gan:
            check_gan = tian_yi_gan[year_gan]
            for i, pillar in enumerate(pillars):
                if pillar[0] == check_gan:
                    shensha.append(("天乙贵人", i))
        
        # 检查文昌星
        wen_chang_zhi = {"子": "戌", "丑": "酉", "寅": "申", "卯": "未", "辰": "午", "巳": "巳", 
                         "午": "辰", "未": "卯", "申": "寅", "酉": "丑", "戌": "子", "亥": "亥"}
        
        for i, pillar in enumerate(pillars):
            zhi = pillar[1]
            if zhi in wen_chang_zhi:
                check_zhi = wen_chang_zhi[zhi]
                for j, p in enumerate(pillars):
                    if p[1] == check_zhi:
                        shensha.append(("文昌", j))
        
        # 羊刃
        yang_ren_zhi = {"甲": "卯", "乙": "寅", "丙": "巳", "丁": "辰", "戊": "巳", "己": "辰", 
                         "庚": "酉", "辛": "申", "壬": "子", "癸": "亥"}
        
        day_gan = pillars[2][0]
        if day_gan in yang_ren_zhi:
            check_zhi = yang_ren_zhi[day_gan]
            for i, pillar in enumerate(pillars):
                if pillar[1] == check_zhi:
                    shensha.append(("羊刃", i))
        
        return shensha
    
    def _calculate_potential(self, elements, compatibility, era_conflict):
        """计算潜能释放值
        
        潜能值 = (命宫强度 × 大运匹配度) / (1 + |时代冲突系数|)
        
        Args:
            elements: 五行能量矩阵
            compatibility: 大运匹配度
            era_conflict: 时代冲突系数
            
        Returns:
            潜能值
        """
        # 命宫强度计算（简化）
        strength = max(elements.values())
        
        return (strength * compatibility) / (1 + abs(era_conflict))
    
    def generate_character(self, birth_datetime, gender, era="modern", character_name=None):
        """生成角色
        
        Args:
            birth_datetime: 生日时间（datetime对象）
            gender: 性别 ("male" 或 "female")
            era: 角色所处纪元 ("ancient", "modern", "future")
            character_name: 角色名称（可选）
            
        Returns:
            角色数据
        """
        # 计算四柱
        year = self._quantum_ganzhi(birth_datetime.year)
        month = self._quantum_ganzhi(birth_datetime.month)
        day = self._quantum_ganzhi(birth_datetime.day)
        hour = self._quantum_ganzhi(birth_datetime.hour)
        
        pillars = [year, month, day, hour]
        
        # 计算五行能量
        nayin_elements = self._calc_nayin_matrix(pillars)
        
        # 计算十神格局
        gods = self._identify_gods(day[0], pillars)
        
        # 计算神煞
        shensha = self._find_shensha(pillars)
        
        # 应用纪元修正
        era_elements = nayin_elements.copy()
        for element, value in era_elements.items():
            era_elements[element] = value * self.era_factors[era]["elements"].get(element, 1.0)
        
        # 计算潜能值
        compatibility = random.uniform(0.5, 0.9)  # 大运匹配度
        era_conflict = random.uniform(0.1, 0.4)   # 时代冲突系数
        potential = self._calculate_potential(era_elements, compatibility, era_conflict)
        
        # 转换十神到纪元角色
        era_gods = []
        for god in gods:
            era_god = self.era_factors[era]["role_transform"].get(god, god)
            era_gods.append(era_god)
        
        # 随机生成灵魂签名
        soul_id = f"SOUL-{random.randint(0, 16777215):X}"
        
        # 生成角色名称（如果未提供）
        if not character_name:
            character_name = self._generate_character_name(era, gender)
        
        # 构建角色数据
        character = {
            "metadata": {
                "protocol": "DestinyFlow",
                "version": "3.0",
                "soul_id": soul_id,
                "universe_id": self.universe_id,
                "name": character_name
            },
            "basic": {
                "birth_datetime": birth_datetime.strftime("%Y-%m-%d %H:%M"),
                "gender": gender,
                "era": era
            },
            "destiny_chart": {
                "pillars": pillars,
                "nayin_elements": nayin_elements,
                "era_modified_elements": era_elements,
                "gods": gods,
                "era_gods": era_gods,
                "shensha": shensha
            },
            "calculations": {
                "potential": potential,
                "compatibility": compatibility,
                "era_conflict": era_conflict
            },
            "abilities": self._generate_abilities(era_elements, shensha, era),
            "life_events": self._generate_life_events(gods, shensha, era)
        }
        
        return character
    
    def _generate_character_name(self, era, gender):
        """生成角色名称"""
        # 根据纪元选择名字组件
        name_components = {
            "ancient": {
                "surnames": ["李", "王", "张", "刘", "陈", "赵", "林", "杨", "黄", "周"],
                "male_names": ["云", "霜", "风", "雷", "山", "剑", "岳", "龙", "天", "辰"],
                "female_names": ["雨", "霞", "月", "芷", "兰", "琴", "莲", "珠", "雪", "蓉"]
            },
            "modern": {
                "surnames": ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"],
                "male_names": ["明", "强", "伟", "勇", "军", "杰", "涛", "超", "刚", "磊"],
                "female_names": ["娜", "婷", "静", "洁", "燕", "华", "敏", "丽", "芳", "颖"]
            },
            "future": {
                "surnames": ["量子", "星", "光", "电", "时", "空", "零", "元", "微", "超"],
                "male_names": ["灵", "数", "芯", "码", "维", "矩", "阵", "流", "波", "粒"],
                "female_names": ["芯", "幻", "虚", "律", "智", "艾", "息", "瑶", "光", "魅"]
            }
        }
        
        # 选择姓氏
        surname = random.choice(name_components[era]["surnames"])
        
        # 根据性别选择名字
        if gender == "male":
            name = random.choice(name_components[era]["male_names"])
        else:
            name = random.choice(name_components[era]["female_names"])
        
        return surname + name
    
    def _generate_abilities(self, elements, shensha, era):
        """生成角色能力
        
        Args:
            elements: 五行能量
            shensha: 神煞列表
            era: 纪元
            
        Returns:
            能力列表
        """
        abilities = {}
        
        # 根据五行生成主要能力
        dominant_element = max(elements, key=elements.get)
        element_abilities = {
            "ancient": {
                "金": "剑修",
                "木": "药师",
                "水": "阵法师",
                "火": "丹道师",
                "土": "符箓师"
            },
            "modern": {
                "金": "金融分析师",
                "木": "生物学家",
                "水": "软件工程师",
                "火": "能源专家",
                "土": "建筑师"
            },
            "future": {
                "金": "量子计算专家",
                "木": "生态系统设计师",
                "水": "数据心理学家",
                "火": "能源转化工程师",
                "土": "星际建筑师"
            }
        }
        
        # 主要能力
        main_ability = element_abilities[era][dominant_element]
        abilities["main"] = main_ability
        
        # 根据神煞生成特殊能力
        special_abilities = []
        for shen, position in shensha:
            if shen == "天乙贵人":
                if era == "ancient":
                    special_abilities.append("危机时刻得贵人相助")
                elif era == "modern":
                    special_abilities.append("社交网络扩展能力")
                else:
                    special_abilities.append("AI系统偏好度")
            elif shen == "文昌":
                if era == "ancient":
                    special_abilities.append("过目不忘的记忆力")
                elif era == "modern":
                    special_abilities.append("创新思维能力")
                else:
                    special_abilities.append("算法优化直觉")
            elif shen == "羊刃":
                if era == "ancient":
                    special_abilities.append("战斗时爆发性增强")
                elif era == "modern":
                    special_abilities.append("商业竞争优势")
                else:
                    special_abilities.append("破解系统能力")
        
        abilities["special"] = special_abilities
        
        # 计算能力值
        ability_values = {}
        era_modifiers = {
            "ancient": {"attack": 1.5, "defense": 0.8, "intelligence": 1.0},
            "modern": {"attack": 1.0, "defense": 1.0, "intelligence": 1.2},
            "future": {"attack": 0.8, "defense": 1.2, "intelligence": 1.5}
        }
        
        # 根据五行计算基础能力值
        ability_values["attack"] = (elements.get("金", 0) * 0.7 + elements.get("火", 0) * 0.3) * 100 * era_modifiers[era]["attack"]
        ability_values["defense"] = (elements.get("土", 0) * 0.7 + elements.get("金", 0) * 0.3) * 100 * era_modifiers[era]["defense"] 
        ability_values["intelligence"] = (elements.get("水", 0) * 0.5 + elements.get("木", 0) * 0.3 + elements.get("火", 0) * 0.2) * 100 * era_modifiers[era]["intelligence"]
        
        # 神煞修正
        for shen, _ in shensha:
            if shen == "天乙贵人":
                ability_values["defense"] *= 1.2
            elif shen == "文昌":
                ability_values["intelligence"] *= 1.3
            elif shen == "羊刃":
                ability_values["attack"] *= 1.3
                ability_values["defense"] *= 0.9
        
        abilities["values"] = {k: round(v, 1) for k, v in ability_values.items()}
        
        return abilities
    
    def _generate_life_events(self, gods, shensha, era):
        """生成角色生命事件
        
        Args:
            gods: 十神列表
            shensha: 神煞列表
            era: 纪元
            
        Returns:
            生命事件列表
        """
        events = []
        
        # 年龄分布
        age_groups = [
            (7, 15),  # 幼年/少年
            (16, 25),  # 青年早期
            (26, 40),  # 青年后期
            (41, 60),  # 中年
            (61, 80)   # 老年
        ]
        
        # 根据十神和神煞生成关键事件
        # 年少时期事件
        young_events = {
            "ancient": ["天赋觉醒", "入门仪式", "拜师学艺", "灵根检测"],
            "modern": ["才能展露", "入学考试", "体育比赛", "科技竞赛"],
            "future": ["神经接口初始化", "基因优化", "量子感知觉醒", "AI导师匹配"]
        }
        
        # 根据十神生成青年期事件
        youth_events = []
        for god in gods:
            if god == "正官" or god == "七杀":
                if era == "ancient":
                    youth_events.append("宗门大比")
                elif era == "modern":
                    youth_events.append("职场竞争")
                else:
                    youth_events.append("算法战争")
            elif god == "偏财" or god == "正财":
                if era == "ancient":
                    youth_events.append("寻宝历险")
                elif era == "modern":
                    youth_events.append("创业机会")
                else:
                    youth_events.append("数据矿藏发现")
            elif god == "食神" or god == "伤官":
                if era == "ancient":
                    youth_events.append("悟道顿悟")
                elif era == "modern":
                    youth_events.append("技术创新")
                else:
                    youth_events.append("意识突破")
        
        # 中年转折点
        middle_events = {
            "ancient": ["大劫难", "突破瓶颈", "派系争斗", "秘境冒险"],
            "modern": ["职业危机", "家庭变故", "健康问题", "重大决策"],
            "future": ["意识分裂", "义体更新", "时间悖论", "次元穿越"]
        }
        
        # 添加特殊事件（基于神煞）
        special_events = []
        for shen, _ in shensha:
            if shen == "天乙贵人":
                if era == "ancient":
                    special_events.append("结识隐世高人")
                elif era == "modern":
                    special_events.append("贵人相助度过危机")
                else:
                    special_events.append("AI核心算法突破")
            elif shen == "文昌":
                if era == "ancient":
                    special_events.append("得到上古秘籍")
                elif era == "modern":
                    special_events.append("学术重大突破")
                else:
                    special_events.append("量子记忆扩展")
            elif shen == "羊刃":
                if era == "ancient":
                    special_events.append("历经生死大战")
                elif era == "modern":
                    special_events.append("重大变革抉择")
                else:
                    special_events.append("系统崩溃危机")
        
        # 生成具体事件
        # 幼年/少年事件
        young_age = random.randint(age_groups[0][0], age_groups[0][1])
        young_event = random.choice(young_events[era])
        events.append({
            "age": young_age,
            "description": young_event,
            "impact": "启蒙",
            "era_specific": self._get_era_specific_event(young_event, era)
        })
        
        # 青年期重要事件
        if youth_events:
            youth_age = random.randint(age_groups[1][0], age_groups[1][1])
            youth_event = random.choice(youth_events)
            events.append({
                "age": youth_age,
                "description": youth_event,
                "impact": "成长",
                "era_specific": self._get_era_specific_event(youth_event, era)
            })
        
        # 中年转折点
        middle_age = random.randint(age_groups[2][0], age_groups[2][1])
        middle_event = random.choice(middle_events[era])
        events.append({
            "age": middle_age,
            "description": middle_event,
            "impact": "转折",
            "era_specific": self._get_era_specific_event(middle_event, era)
        })
        
        # 特殊事件
        if special_events:
            special_age = random.randint(age_groups[2][0], age_groups[3][1])
            special_event = random.choice(special_events)
            events.append({
                "age": special_age,
                "description": special_event,
                "impact": "关键",
                "era_specific": self._get_era_specific_event(special_event, era)
            })
        
        # 按年龄排序
        events.sort(key=lambda x: x["age"])
        
        return events
    
    def _get_era_specific_event(self, event_base, era):
        """根据基础事件和纪元生成具体事件描述
        
        Args:
            event_base: 基础事件
            era: 纪元
            
        Returns:
            具体事件描述
        """
        # 简化处理，根据基础事件生成特定纪元下的详细描述
        event_details = {
            "ancient": {
                "天赋觉醒": "在修炼时意外引发灵根觉醒，展现出罕见的灵根品质",
                "入门仪式": "通过宗门入门大典，正式成为外门弟子",
                "拜师学艺": "得到宗门长老看重，收为入室弟子",
                "灵根检测": "灵根检测发现拥有罕见的多系灵根",
                "宗门大比": "参加宗门大比，凭实力赢得关注",
                "寻宝历险": "在秘境中发现珍稀灵药或法宝",
                "悟道顿悟": "修炼中突破瓶颈，领悟道法奥义",
                "大劫难": "面临修真界大劫，需做出重要抉择",
                "突破瓶颈": "修为突破至关键境界",
                "派系争斗": "卷入宗门内部或修真界派系争斗",
                "秘境冒险": "探索远古秘境，寻找修真机缘",
                "结识隐世高人": "机缘巧合下结识一位隐世不出的高人",
                "得到上古秘籍": "获得记载失传功法的上古秘籍",
                "历经生死大战": "与强敌生死对决，突破自我极限"
            },
            "modern": {
                "才能展露": "在学校中展现出特殊才能，引起老师关注",
                "入学考试": "参加重点学校考试，取得优异成绩",
                "体育比赛": "在校际比赛中取得突出成绩",
                "科技竞赛": "参加科技创新比赛，作品获奖",
                "职场竞争": "在激烈的职场竞争中脱颖而出",
                "创业机会": "发现市场空白，创立自己的公司",
                "技术创新": "研发新技术，获得专利或行业认可",
                "职业危机": "面临行业变革或公司重组",
                "家庭变故": "经历家庭重大变故，改变人生轨迹",
                "健康问题": "遭遇健康危机，重新审视生活",
                "重大决策": "面临人生岔路口，需做出关键决定",
                "贵人相助度过危机": "在困境中得到意外的贵人相助",
                "学术重大突破": "在研究领域取得突破性进展",
                "重大变革抉择": "在剧变时期做出影响深远的决定"
            },
            "future": {
                "神经接口初始化": "首次接入量子神经网络，展现出非凡适配性",
                "基因优化": "接受基因优化手术，激活潜在能力",
                "量子感知觉醒": "突然获得感知量子波动的能力",
                "AI导师匹配": "与具有独特算法的AI导师匹配成功",
                "算法战争": "参与虚拟世界中的算法战争",
                "数据矿藏发现": "在数据海洋中发现有价值的信息矿藏",
                "意识突破": "意识层次突破，获得新的认知能力",
                "意识分裂": "经历意识分裂，形成多重自我",
                "义体更新": "更换先进义体，能力大幅提升",
                "时间悖论": "卷入时间悖论事件，改变历史线",
                "次元穿越": "意外穿越到平行宇宙或不同纪元",
                "AI核心算法突破": "破解或创造革命性的AI核心算法",
                "量子记忆扩展": "成功扩展自身量子记忆存储能力",
                "系统崩溃危机": "面临全球系统崩溃的紧急危机"
            }
        }
        
        # 返回详细描述或默认描述
        return event_details.get(era, {}).get(event_base, f"{era}时代下的{event_base}事件")
    
    def generate_character_description(self, character_data):
        """生成角色描述文本
        
        Args:
            character_data: 角色数据
            
        Returns:
            角色描述文本
        """
        soul_id = character_data["metadata"]["soul_id"]
        universe_id = character_data["metadata"]["universe_id"]
        character_name = character_data["metadata"]["name"]
        birth_datetime = character_data["basic"]["birth_datetime"]
        era = character_data["basic"]["era"]
        
        # 四柱信息
        pillars = character_data["destiny_chart"]["pillars"]
        nayin_elements = character_data["destiny_chart"]["nayin_elements"]
        era_elements = character_data["destiny_chart"]["era_modified_elements"]
        gods = character_data["destiny_chart"]["gods"]
        era_gods = character_data["destiny_chart"]["era_gods"]
        shensha = character_data["destiny_chart"]["shensha"]
        
        # 能力
        abilities = character_data["abilities"]
        
        # 事件
        events = character_data["life_events"]
        
        # 格式化五行能量
        element_bars = {
            "金": self._format_bar(nayin_elements.get("金", 0)),
            "木": self._format_bar(nayin_elements.get("木", 0)),
            "水": self._format_bar(nayin_elements.get("水", 0)),
            "火": self._format_bar(nayin_elements.get("火", 0)),
            "土": self._format_bar(nayin_elements.get("土", 0))
        }
        
        # 生成命盘核心
        destiny_core = f"""四柱量子编码:
  年柱: {pillars[0]} → {"金" if "金" in pillars[0] else "木" if "木" in pillars[0] else "水" if "水" in pillars[0] else "火" if "火" in pillars[0] else "土"}+2 {"土" if "土" in pillars[0] else "金" if "金" in pillars[0] else "木" if "木" in pillars[0] else "水" if "水" in pillars[0] else "火"}+1
  月柱: {pillars[1]} → {"金" if "金" in pillars[1] else "木" if "木" in pillars[1] else "水" if "水" in pillars[1] else "火" if "火" in pillars[1] else "土"}+2 {"土" if "土" in pillars[1] else "金" if "金" in pillars[1] else "木" if "木" in pillars[1] else "水" if "水" in pillars[1] else "火"}+1
  日柱: {pillars[2]} → {"金" if "金" in pillars[2] else "木" if "木" in pillars[2] else "水" if "水" in pillars[2] else "火" if "火" in pillars[2] else "土"}+2 {"土" if "土" in pillars[2] else "金" if "金" in pillars[2] else "木" if "木" in pillars[2] else "水" if "水" in pillars[2] else "火"}+1
  时柱: {pillars[3]} → {"金" if "金" in pillars[3] else "木" if "木" in pillars[3] else "水" if "水" in pillars[3] else "火" if "火" in pillars[3] else "土"}+1 {"土" if "土" in pillars[3] else "金" if "金" in pillars[3] else "木" if "木" in pillars[3] else "水" if "水" in pillars[3] else "火"}+2

五行能量场:
  金: {element_bars["金"]} {int(nayin_elements.get("金", 0)*100)}%
  木: {element_bars["木"]} {int(nayin_elements.get("木", 0)*100)}%
  水: {element_bars["水"]} {int(nayin_elements.get("水", 0)*100)}%
  火: {element_bars["火"]} {int(nayin_elements.get("火", 0)*100)}%
  土: {element_bars["土"]} {int(nayin_elements.get("土", 0)*100)}%

十神格局:
  日主{pillars[2][0]}生于{pillars[1][1]}月 → {gods[2]}格{' 透印' if '印' in gods[0] or '印' in gods[1] or '印' in gods[3] else ''}
  天干透{', '.join([g for i, g in enumerate(gods) if i != 2 and g != "未知"])}
  地支{self._count_elements_in_zhi([p[1] for p in pillars])}

神煞系统:
  {self._format_shensha(shensha, pillars)}"""

        # 生成能力描述
        ability_desc = f"""
■ 主要能力: {abilities["main"]}
■ 特殊能力: {', '.join(abilities["special"]) if abilities["special"] else "无特殊能力"}
■ 能力值:
  - 攻击: {abilities["values"]["attack"]}
  - 防御: {abilities["values"]["defense"]}
  - 智力: {abilities["values"]["intelligence"]}"""

        # 生成事件时间线
        timeline = "\n".join([f"■ {e['age']}岁: {e['description']}\n  {e['era_specific']}" for e in events])
        
        # 根据纪元生成称号
        titles = {
            "ancient": ["仙师", "道者", "真人", "宗师", "奇士"],
            "modern": ["专家", "大师", "教授", "精英", "先锋"],
            "future": ["超链者", "奇点", "量子行者", "编码师", "超维者"]
        }
        
        # 随机选择称号
        title = random.choice(titles[era])
        
        # 组合完整描述
        description = f"""「角色档案」命理驱动角色实例：{character_name} {title}

灵魂签名： {soul_id}
适用宇宙：{universe_id}

一、先天命盘解析
出生时刻：{birth_datetime} ({pillars[0]}年{pillars[1]}月{pillars[2]}日{pillars[3]}时)

1.1 命盘核心参数
{destiny_core}

1.2 先天特质分析
内在性格：
- [优势]
  ■ 坚韧不拔：{pillars[2]}日主得天独厚
  ■ 谋定后动：{'食伤心性' if '食' in gods or '伤' in gods else '官杀果断' if '官' in gods or '杀' in gods else '印绶聪慧'}
  ■ {'求知若渴' if '印' in gods else '领导能力' if '官' in gods else '创造天赋' if '伤' in gods else '财运亨通' if '财' in gods else '团队合作'}：{'五行平衡' if max(nayin_elements.values()) - min(nayin_elements.values()) < 0.3 else f"{'金' if nayin_elements.get('金', 0) > 0.3 else '木' if nayin_elements.get('木', 0) > 0.3 else '水' if nayin_elements.get('水', 0) > 0.3 else '火' if nayin_elements.get('火', 0) > 0.3 else '土'}气旺盛"}

- [弱点]
  ◆ {'固执己见' if nayin_elements.get('土', 0) > 0.3 else '情绪化' if nayin_elements.get('水', 0) > 0.3 else '急躁' if nayin_elements.get('火', 0) > 0.3 else '优柔寡断' if nayin_elements.get('木', 0) > 0.3 else '冷漠'}：性格偏颇需平衡
  ◆ {'人际关系' if '财' in gods else '创新突破' if '伤' in gods else '学习能力' if '印' in gods else '执行力'}：{'需要刻意培养' if min(nayin_elements.values()) < 0.1 else '有待提升'}
  ◆ {'易走极端' if '刃' in ''.join(str(s) for s in shensha) else '思维固化' if nayin_elements.get('土', 0) > 0.4 else '情感压抑' if nayin_elements.get('金', 0) > 0.4 else '缺乏耐心'}：需注意自我调节

二、后天运势推演
所处宇宙：{universe_id} (当前纪元：{era})

2.1 环境调制参数
{self._format_era_table(era_elements, era)}

2.2 关键命运节点
{ability_desc}

2.3 命运轨迹
{timeline}

三、命运核心公式验证
潜能释放效率：
\\frac{{命宫强度({max(nayin_elements.values()):.1f}) \\times 大运匹配度({character_data["calculations"]["compatibility"]:.1f})}}{{1 + |时代冲突系数({character_data["calculations"]["era_conflict"]:.2f})|}} = {character_data["calculations"]["potential"]:.3f} → {int(character_data["calculations"]["potential"]*100)}%潜能开发度

四、跨纪元生存指南
1. 能量适配
   ◯ {'修真者乘坐飞机需给飞剑购买航空保险' if era == 'ancient' else '数据流需符合物理世界编码标准' if era == 'future' else '避免在灵气波动区使用高精度电子设备'}
   ◯ {'赛博格充电时需避开雷劫高发区' if era == 'future' else '修士在科技区需屏蔽灵气波动' if era == 'ancient' else '佩戴特制屏障避免灵能干扰'}

2. 通讯协议
   ◯ {'传音玉符频率需符合5G NSA标准' if era == 'ancient' else '脑机接口不得传输超过元婴期的神识' if era == 'future' else '避免使用灵能干扰通讯设备'}
   ◯ {'量子通讯需预留古法秘咒缓冲区' if era == 'future' else '心灵传音需加密以防科技监听' if era == 'ancient' else '正式场合避免使用超感官能力'}

3. 冲突解决
   ◯ {'飞剑与无人机空域争端由AI判官仲裁' if era == 'ancient' or era == 'future' else '灵能与科技冲突适用混合法庭规则'}
   ◯ {'渡劫引发的停电事故适用不可抗力条款' if era == 'ancient' else '量子波动导致的数据丢失有专属保险' if era == 'future' else '神秘事件有专门的调查流程'}

该角色由命理驱动的量子叠加态人生轨迹，在确定性与可能性之间达到精妙平衡。完全符合VUCCP v1.0和TDP v1.1协议标准。"""

        return description
        
    def _format_era_table(self, elements, era):
        """格式化纪元修正表格"""
        table = "| 维度 | 先天值 | 纪元修正 | 实际表现值 |\n"
        table += "|------|--------|----------|------------|\n"
        
        # 获取主要元素
        main_element = max(elements, key=elements.get)
        secondary_element = sorted(elements.items(), key=lambda x: x[1], reverse=True)[1][0]
        
        # 根据纪元和元素生成表格
        era_mapping = {
            "ancient": {
                "金": "剑道天赋", "木": "草药亲和", "水": "阵法悟性", 
                "火": "丹道资质", "土": "符箓底蕴"
            },
            "modern": {
                "金": "精密操作", "木": "生物直觉", "水": "逻辑思维", 
                "火": "创新能力", "土": "稳健坚毅"
            },
            "future": {
                "金": "量子计算", "木": "生态设计", "水": "数据分析", 
                "火": "能源控制", "土": "空间构建"
            }
        }
        
        # 主要能力
        main_skill = era_mapping[era][main_element]
        sec_skill = era_mapping[era][secondary_element]
        
        # 添加主要能力行
        raw_value = round(elements[main_element] / self.era_factors[era]["elements"].get(main_element, 1.0), 2)
        era_modifier = f"×{self.era_factors[era]['elements'].get(main_element, 1.0)}"
        actual_value = round(elements[main_element] * 100)
        table += f"| {main_skill} | {int(raw_value*100)}% | {era_modifier} | {actual_value}% → [主修精通] |\n"
        
        # 添加次要能力行
        raw_value = round(elements[secondary_element] / self.era_factors[era]["elements"].get(secondary_element, 1.0), 2)
        era_modifier = f"×{self.era_factors[era]['elements'].get(secondary_element, 1.0)}"
        actual_value = round(elements[secondary_element] * 100)
        table += f"| {sec_skill} | {int(raw_value*100)}% | {era_modifier} | {actual_value}% → [得心应手] |\n"
        
        return table
        
    def _format_bar(self, value, max_length=10):
        """格式化进度条"""
        filled = int(value * max_length)
        empty = max_length - filled
        return '█' * filled + '◌' * empty
    
    def _count_elements_in_zhi(self, zhi_list):
        """计算地支中的五行数量"""
        # 简化版地支五行对应
        zhi_elements = {
            "子": "水", "丑": "土", "寅": "木", "卯": "木",
            "辰": "土", "巳": "火", "午": "火", "未": "土",
            "申": "金", "酉": "金", "戌": "土", "亥": "水"
        }
        
        # 统计各五行出现次数
        counts = {}
        for zhi in zhi_list:
            element = zhi_elements.get(zhi, "")
            if element:
                counts[element] = counts.get(element, 0) + 1
        
        # 找出最多的五行
        max_element = max(counts.items(), key=lambda x: x[1], default=("", 0))
        if max_element[1] > 1:
            return f"{max_element[1]}个{max_element[0]}"
        else:
            return "五行分散"
    
    def _format_shensha(self, shensha, pillars):
        """格式化神煞信息"""
        if not shensha:
            return "未检测到显著神煞"
            
        shensha_parts = []
        for s, pos in shensha:
            if pos < len(pillars):
                shensha_parts.append(f"- {s}({['年', '月', '日', '时'][pos]}柱): {self._get_shensha_effect(s)}")
                
        return "\n  ".join(shensha_parts)
    
    def _get_shensha_effect(self, shensha_name):
        """获取神煞效果描述"""
        effects = {
            "天乙贵人": "逢凶化吉，贵人相助",
            "文昌": "学业事业有成，智慧超群",
            "羊刃": "犀利果断，性格刚强"
        }
        return effects.get(shensha_name, "影响命运走向")
    
    def export_to_json(self, character_data, file_path):
        """导出角色数据到JSON文件
        
        Args:
            character_data: 角色数据
            file_path: 输出文件路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
            
    def load_from_json(self, file_path):
        """从JSON文件加载角色数据
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            角色数据
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            character_data = json.load(f)
            
        return character_data


class TDPManager:
    """三纪元世界与角色管理器"""
    
    def __init__(self, base_dir="tdp_worlds"):
        """初始化管理器
        
        Args:
            base_dir: 数据存储基础目录
        """
        self.base_dir = base_dir
        self.ensure_directory(base_dir)
        
        # 世界生成器
        self.world_generator = TDPWorldGenerator()
        
        # 角色生成器
        self.character_generator = CharacterDNAGenerator()
        
        # 跟踪已创建的世界
        self.worlds = self._load_existing_worlds()
    
    def ensure_directory(self, directory):
        """确保目录存在
        
        Args:
            directory: 目录路径
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def _load_existing_worlds(self):
        """加载已存在的世界
        
        Returns:
            世界字典 {world_id: {metadata}}
        """
        worlds = {}
        
        if not os.path.exists(self.base_dir):
            return worlds
            
        for world_dir in os.listdir(self.base_dir):
            world_path = os.path.join(self.base_dir, world_dir)
            if os.path.isdir(world_path):
                # 尝试加载世界元数据
                metadata_path = os.path.join(world_path, "world_metadata.yaml")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = yaml.safe_load(f)
                            if metadata and "metadata" in metadata:
                                world_id = metadata["metadata"].get("universe_id", world_dir)
                                worlds[world_id] = metadata
                    except Exception as e:
                        print(f"无法加载世界元数据 {metadata_path}: {e}")
        
        return worlds
    
    def create_world(self):
        """创建新的世界
        
        Returns:
            世界ID
        """
        # 生成世界
        world_data = self.world_generator.generate_world()
        world_id = world_data["metadata"]["universe_id"]
        
        # 创建世界目录
        world_dir = os.path.join(self.base_dir, world_id)
        self.ensure_directory(world_dir)
        
        # 保存世界元数据
        metadata_path = os.path.join(world_dir, "world_metadata.yaml")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            yaml.dump(world_data, f, default_flow_style=False, allow_unicode=True)
        
        # 保存世界描述
        description = self.world_generator.generate_world_description()
        description_path = os.path.join(world_dir, "world_description.txt")
        with open(description_path, 'w', encoding='utf-8') as f:
            f.write(description)
        
        # 创建角色目录
        characters_dir = os.path.join(world_dir, "characters")
        self.ensure_directory(characters_dir)
        
        # 添加到世界字典
        self.worlds[world_id] = world_data
        
        return world_id
    
    def create_character(self, world_id, birth_datetime, gender, era="modern", character_name=None):
        """在特定世界中创建角色
        
        Args:
            world_id: 世界ID
            birth_datetime: 出生日期时间
            gender: 性别
            era: 纪元
            character_name: 角色名称（可选）
            
        Returns:
            (character_id, character_data)
        """
        # 检查世界是否存在
        if world_id not in self.worlds:
            raise ValueError(f"世界 {world_id} 不存在")
        
        # 设置角色生成器的世界ID
        self.character_generator.set_universe(world_id)
        
        # 生成角色
        character_data = self.character_generator.generate_character(
            birth_datetime=birth_datetime,
            gender=gender,
            era=era,
            character_name=character_name
        )
        
        # 角色ID
        character_id = character_data["metadata"]["soul_id"]
        character_name = character_data["metadata"]["name"]
        
        # 保存角色数据
        characters_dir = os.path.join(self.base_dir, world_id, "characters")
        character_file = os.path.join(characters_dir, f"{character_id}.json")
        
        with open(character_file, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
        
        # 生成并保存角色描述
        description = self.character_generator.generate_character_description(character_data)
        description_file = os.path.join(characters_dir, f"{character_id}_description.txt")
        
        with open(description_file, 'w', encoding='utf-8') as f:
            f.write(description)
        
        # 为了方便引用，创建一个按名称索引的符号链接或副本
        name_file = os.path.join(characters_dir, f"{character_name}.json")
        
        # 如果操作系统支持符号链接
        try:
            if hasattr(os, 'symlink'):
                # 如果已存在，先删除
                if os.path.exists(name_file):
                    os.remove(name_file)
                os.symlink(character_file, name_file)
            else:
                # 否则创建副本
                with open(character_file, 'r', encoding='utf-8') as source:
                    with open(name_file, 'w', encoding='utf-8') as target:
                        target.write(source.read())
        except Exception as e:
            print(f"创建角色名称链接时出错: {e}")
        
        return character_id, character_data
    
    def get_world_ids(self):
        """获取所有世界ID
        
        Returns:
            世界ID列表
        """
        return list(self.worlds.keys())
    
    def get_world_description(self, world_id):
        """获取世界描述
        
        Args:
            world_id: 世界ID
            
        Returns:
            世界描述
        """
        description_path = os.path.join(self.base_dir, world_id, "world_description.txt")
        
        if os.path.exists(description_path):
            with open(description_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        return None
    
    def get_characters_in_world(self, world_id):
        """获取世界中的所有角色
        
        Args:
            world_id: 世界ID
            
        Returns:
            角色ID列表
        """
        characters_dir = os.path.join(self.base_dir, world_id, "characters")
        
        if not os.path.exists(characters_dir):
            return []
        
        characters = []
        for filename in os.listdir(characters_dir):
            if filename.endswith(".json"):
                try:
                    character_path = os.path.join(characters_dir, filename)
                    with open(character_path, 'r', encoding='utf-8') as f:
                        character_data = json.load(f)
                        if "metadata" in character_data and "soul_id" in character_data["metadata"]:
                            characters.append({
                                "id": character_data["metadata"]["soul_id"],
                                "name": character_data["metadata"].get("name", "未命名"),
                                "era": character_data["basic"].get("era", "unknown")
                            })
                except Exception as e:
                    print(f"加载角色数据时出错 {filename}: {e}")
        
        return characters
    
    def get_character_data(self, world_id, character_id):
        """获取角色数据
        
        Args:
            world_id: 世界ID
            character_id: 角色ID
            
        Returns:
            角色数据
        """
        character_path = os.path.join(self.base_dir, world_id, "characters", f"{character_id}.json")
        
        if os.path.exists(character_path):
            with open(character_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def get_character_description(self, world_id, character_id):
        """获取角色描述
        
        Args:
            world_id: 世界ID
            character_id: 角色ID
            
        Returns:
            角色描述
        """
        description_path = os.path.join(self.base_dir, world_id, "characters", f"{character_id}_description.txt")
        
        if os.path.exists(description_path):
            with open(description_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        return None
    
    def load_world(self, world_id):
        """加载世界数据到世界生成器
        
        Args:
            world_id: 世界ID
            
        Returns:
            True 如果成功，否则 False
        """
        world_path = os.path.join(self.base_dir, world_id, "world_metadata.yaml")
        
        if os.path.exists(world_path):
            try:
                self.world_generator.load_from_yaml(world_path)
                return True
            except Exception as e:
                print(f"加载世界数据时出错: {e}")
                return False
        
        return False


# 使用示例
def generate_world_and_characters():
    """生成世界和角色示例"""
    # 创建管理器
    manager = TDPManager("tdp_universes")
    
    # 创建世界
    print("创建世界...")
    world_id = manager.create_world()
    print(f"已创建世界: {world_id}")
    
    # 获取世界描述
    world_description = manager.get_world_description(world_id)
    print(f"世界描述摘要: {world_description[:200]}...")
    
    # 创建不同纪元的角色
    print("\n创建角色...")
    
    # 修真纪元角色
    from datetime import datetime
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
    
    # 未来纪元角色
    future_char_id, _ = manager.create_character(
        world_id=world_id,
        birth_datetime=datetime(2005, 12, 10, 3, 15),
        gender="male",
        era="future"
    )
    print(f"已创建未来纪元角色，ID: {future_char_id}")
    
    # 查看世界中的所有角色
    characters = manager.get_characters_in_world(world_id)
    print(f"\n世界 {world_id} 中共有 {len(characters)} 个角色:")
    for char in characters:
        print(f"- 名称: {char['name']}, ID: {char['id']}, 纪元: {char['era']}")
    
    # 获取角色描述示例
    char_desc = manager.get_character_description(world_id, ancient_char_id)
    print(f"\n角色描述摘要: {char_desc[:150]}...")

    return world_id, [ancient_char_id, modern_char_id, future_char_id]


def main():
    """主函数：演示如何使用三纪元世界与角色系统"""
    print("=== 三纪元世界与角色生成系统 ===")
    print("\n1. 创建第一个世界及其角色")
    world1_id, world1_chars = generate_world_and_characters()
    
    print("\n2. 创建第二个世界")
    manager = TDPManager("tdp_universes")
    world2_id = manager.create_world()
    print(f"已创建第二个世界: {world2_id}")
    
    # 创建第二个世界的角色
    char_id, _ = manager.create_character(
        world_id=world2_id,
        birth_datetime=datetime(2010, 5, 20, 12, 0),
        gender="female",
        era="future",
        character_name="星璇·艾"  # 指定角色名称
    )
    print(f"已在第二个世界中创建角色: {char_id}")
    
    # 列出所有世界
    print("\n3. 所有创建的世界:")
    worlds = manager.get_world_ids()
    for world in worlds:
        print(f"- {world}")
        # 列出世界中的角色
        chars = manager.get_characters_in_world(world)
        print(f"  包含 {len(chars)} 个角色:")
        for char in chars:
            print(f"  - {char['name']} ({char['era']}纪元)")
    
    print("\n系统将数据保存在目录结构中:")
    print("tdp_universes/")
    print("├── " + world1_id + "/")
    print("│   ├── world_metadata.yaml")
    print("│   ├── world_description.txt")
    print("│   └── characters/")
    for char_id in world1_chars:
        print(f"│       ├── {char_id}.json")
        print(f"│       └── {char_id}_description.txt")
    print("└── " + world2_id + "/")
    print("    ├── world_metadata.yaml")
    print("    ├── world_description.txt")
    print("    └── characters/")
    print(f"        ├── {char_id}.json")
    print(f"        └── {char_id}_description.txt")


if __name__ == "__main__":
    main()