import hashlib
import numpy as np
from typing import Dict, List

class WorldGenerator:
    def __init__(self):
        # 三维度权重矩阵（可扩展为6x6矩阵）
        self.dimensions = {
            "geo": {
                "axes": ["大陆形态", "能量类型", "生态法则"],
                "options": [
                    ["灵脉浮岛（上古）", "现代都市（当代）", "太空殖民地（未来）"],
                    ["天地灵气（上古）", "化石能源（当代）", "反物质反应堆（未来）"],
                    ["灵兽共生（上古）", "工业污染（当代）", "基因定制（未来）"]
                ],
                "weights": [[0.3, 0.4, 0.3] for _ in range(3)]# 可自定义权重
            },
            "faction": {
                "axes": ["势力类型", "组织结构", "发展方向"],
                "options": [
                    ["修仙门派（上古）", "现代企业（当代）", "星际联盟（未来）"],
                    ["宗门制度（上古）", "公司架构（当代）", "虚拟网络（未来）"],
                    ["长生大道（上古）", "资本扩张（当代）", "跨维度发展（未来）"]
                ],
                "weights": [[0.3, 0.4, 0.3] for _ in range(3)]
            }
        }
        
        # 时间流速参数（v1.1新增）
        self.time_flow_params = {
            "ancient": 0.3,
            "modern": 0.4,
            "future": 0.3
        }

    def _detect_era(self, choice: str) -> str:
        """检测选项所属的时代
        
        Args:
            choice: 选项字符串
            
        Returns:
            str: 'ancient' | 'modern' | 'future'
        """
        if any(keyword in choice for keyword in ["上古", "灵脉", "灵气", "灵兽"]):
            return "ancient"
        elif any(keyword in choice for keyword in ["当代", "现代", "工业", "化石"]):
            return "modern"
        else:
            return "future"

    def generate_world(self) -> Dict:
        """根据TDP协议生成世界核心参数"""
        world_config = {}
        
        # 维度裂变引擎（v1.1升级版）
        for dim, config in self.dimensions.items():
            world_config[dim] = self._select_dimension_options(config)
        
        # 时间流速处理（三纪元独立时间流）
        world_config["time_flow"] = self._apply_time_rules()
        
        # 生成宇宙指纹（62位跨宇宙识别符）
        world_config["universe_hash"] = self._generate_universe_hash(world_config)
        
        # 熵值计算（简化版）
        world_config["entropy"] = self._calculate_entropy(world_config)
        
        return world_config

    def _select_dimension_options(self, config: Dict) -> List:
        """基于权重矩阵选择维度选项"""
        selected = []
        for idx, options in enumerate(config["options"]):
            weights = config["weights"][idx]
            choice = np.random.choice(options, p=weights)
            selected.append({
                "axis": config["axes"][idx],
                "value": choice,
                "era": self._detect_era(choice)
            })
        return selected

    def _apply_time_rules(self) -> Dict:
        """应用三纪元时间流速规则"""
        return {
            "ancient": np.random.normal(0.8, 0.1),  # 非线性时间流
            "modern": 1.0,                          # 线性时间基准
            "future": np.random.uniform(1.2, 1.5)   # 量子化时间
        }

    def _generate_universe_hash(self, config: Dict) -> str:
        """生成62位量子纠缠校验码"""
        config_str = str(config).encode()
        return hashlib.sha256(config_str).hexdigest()[:62]

    def _calculate_entropy(self, config: Dict) -> float:
        """简化版熵增模型"""
        entropy = 0.0
        for dim in self.dimensions.keys():
            for option in config.get(dim, []):
                era_weight = self.time_flow_params.get(option["era"], 1.0)
                entropy += np.log1p(era_weight)
        return round(entropy * 0.1, 4)

    def generate_story_element(self) -> Dict:
        """生成符合VUCCP协议的故事原子单元"""
        element = {
            "story_cell": f"CT-{hashlib.md5(str(np.random.rand()).encode()).hexdigest()[:4]}",
            "content": self._generate_cross_era_concept(),
            "constraints": {
                "era": list(self.time_flow_params.keys()),
                "media": ["novel", "game", "film"],
                "trigger_conditions": ["tech_level≥5", "character.age>30"]
            }
        }
        return element

    def _generate_cross_era_concept(self) -> str:
        """生成跨纪元融合概念"""
        combinations = [
            f"{np.random.choice(['灵脉', '量子', '赛博'])}{np.random.choice(['金融城', '反应堆', '社区'])}",
            f"{np.random.choice(['机甲', '御剑', '纳米'])}{np.random.choice(['渡劫', '协议', '生态'])}",
            f"{np.random.choice(['符箓','区块链', '神经'])}{np.random.choice(['矿机', '契约', '接口'])}"
        ]
        return np.random.choice(combinations)

# 使用示例
if __name__ == "__main__":
    generator = WorldGenerator()
    
    # 生成世界基础参数
    world = generator.generate_world()
    print("=== 世界核心参数 ===")
    print(f"宇宙指纹: {world['universe_hash']}")
    print(f"熵值指数: {world['entropy']}")
    print("地理特征:", [geo['value'] for geo in world['geo']])
    
    # 生成故事元素
    story = generator.generate_story_element()
    print("\n=== 故事原子单元 ===")
    print(f"编号: {story['story_cell']}")
    print(f"核心概念: {story['content']}")
    print(f"跨媒介扩展: {story.get('extension', '待生成')}")
