import os
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional
from .bazi_analyzer import BaziAnalyzer
from .bazi_formatter import BaziFormatter
import json
import random

class TextManager:
    """文本元素管理器"""
    
    def __init__(self, config_dir: str = "config", deepseek_api_key: str = None):
        """初始化文本元素管理器
        
        Args:
            config_dir: 配置文件目录
            deepseek_api_key: DeepSeek API密钥
        """
        self.config_dir = config_dir
        # 设置基础目录
        self.base_dir = os.path.dirname(os.path.dirname(config_dir)) if os.path.isabs(config_dir) else os.path.join(os.getcwd(), os.path.dirname(config_dir))
        self.config = self._load_config()
        
        # 设置默认值
        self.model_type = self.config.get('model_type', 'deepseek-chat')
        self.temperature = self.config.get('temperature', 0.9)
        self.max_tokens = self.config.get('max_tokens', 4096)
        
        # 初始化 DeepSeek 客户端
        try:
            from .deepseek_client import DeepSeekClient
            self.deepseek_client = DeepSeekClient(
                api_key=deepseek_api_key,
                max_retries=3,
                timeout=300  # 5分钟超时
            )
            print("DeepSeek 客户端初始化成功")
        except Exception as e:
            print(f"Warning: 初始化 DeepSeek 客户端失败: {e}")
            self.deepseek_client = None
        
        # 初始化八字分析器和格式化器
        from .bazi_analyzer import BaziAnalyzer
        from .bazi_formatter import BaziFormatter
        
        self.bazi_analyzer = BaziAnalyzer()
        self.bazi_formatter = BaziFormatter()
        
        print("文本元素管理器初始化完成")
        
        # 验证配置
        self._validate_config()
        
        # 确保必要的目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        # 加载或创建配置文件
        self.config_file = os.path.join(config_dir, "text_config.yaml")
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config.update(yaml.safe_load(f))
        else:
            # 如果配置文件不存在，创建默认配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.config, f, allow_unicode=True)
                
        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(config_dir), "worlds"), exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(config_dir), "descriptions"), exist_ok=True)
        
    def _validate_config(self):
        """验证配置的完整性"""
        required_sections = ["character", "world"]
        required_character_sections = ["name_generation", "skill_pools"]
        required_eras = ["ancient", "modern", "future"]
        
        # 检查主要部分
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"配置缺少必要部分: {section}")
        
        # 检查角色配置部分
        char_config = self.config["character"]
        for section in required_character_sections:
            if section not in char_config:
                raise ValueError(f"角色配置缺少必要部分: {section}")
        
        # 检查纪元配置
        name_gen = char_config["name_generation"]
        skill_pools = char_config["skill_pools"]
        
        for era in required_eras:
            # 检查名字生成配置
            if era not in name_gen:
                raise ValueError(f"名字生成配置缺少必要纪元: {era}")
            
            # 检查每个纪元的必要名字元素
            era_config = name_gen[era]
            required_elements = ["surnames", "male_given", "female_given"]
            for element in required_elements:
                if element not in era_config or not era_config[element]:
                    raise ValueError(f"纪元 {era} 缺少必要名字元素: {element}")
            
            # 检查技能池配置
            if era not in skill_pools:
                raise ValueError(f"技能池配置缺少必要纪元: {era}")
            if not skill_pools[era]:
                raise ValueError(f"纪元 {era} 的技能池为空")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), "config", "text_elements.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def get_world_description(self, world_id: str, version: str) -> str:
        """生成世界描述
        
        Args:
            world_id: 世界ID
            version: 协议版本
            
        Returns:
            str: 格式化的世界描述
        """
        world_config = self.config["world"]
        checksum = world_id.split("-")[1]
        validation = self._generate_validation_code()
        
        # 基本信息
        lines = [
            world_config["title_format"].format(world_id=world_id),
            world_config["checksum_format"].format(checksum=checksum, validation=validation),
            ""
        ]
        
        # 熵增监控面板
        panel = world_config["entropy_panel"]
        lines.extend([
            panel["title"],
            panel["header"]
        ])
        
        # 添加指标
        import random
        for metric in panel["metrics"]:
            value = random.uniform(3.5, 4.5) if "灵气-石油" in metric["name"] else random.uniform(60, 95)
            line = f"{metric['name']:<20} "
            
            if "format" in metric:
                line += metric["format"].format(value=value)
                line = f"{line:<20}"
            
            if "threshold" in metric:
                line += f" {metric['threshold']:<15}"
            
            if "status" in metric:
                if isinstance(metric["status"], dict):
                    status = metric["status"]["normal"] if random.random() > 0.3 else metric["status"]["warning"]
                else:
                    status = metric["status"]
                line += f" {status}"
                
            if "suffix" in metric and "adjustment" in metric:
                sign = "+" if random.random() > 0.5 else "-"
                adj_value = random.uniform(5, 7)
                line += f" {metric['suffix']} {metric['adjustment'].format(sign=sign, value=adj_value)}"
                
            lines.append(line)
        
        lines.append("")
        
        # 添加地点描述
        locations = world_config["locations"]
        for location in locations.values():
            lines.extend([
                location["title"],
                *[f"- {desc}" for desc in location["descriptions"]],
                ""
            ])
        
        # 添加协议声明
        expiry_date = f"{datetime.now().year + 1}-12-31"
        lines.append(world_config["protocol_statement"].format(
            version=version,
            checksum=checksum,
            validation=validation,
            expiry_date=expiry_date
        ))
        
        return "\n".join(lines)
    
    def generate_character_description(self, char_data: dict, world_data: dict) -> str:
        """生成角色描述
        
        Args:
            char_data: 角色数据
            world_data: 世界数据
            
        Returns:
            str: 角色描述
        """
        try:
            print("\n=== 开始生成角色描述 ===")
            print(f"输入的角色数据: {json.dumps(char_data, ensure_ascii=False, indent=2)}")
            print(f"输入的世界数据: {json.dumps(world_data, ensure_ascii=False, indent=2)}")
            
            # 检查必要字段
            print("\n[步骤1] 检查必要字段...")
            if not char_data.get('metadata'):
                print("错误：缺少 metadata")
                print(f"当前角色数据: {json.dumps(char_data, ensure_ascii=False, indent=2)}")
                return "无法生成角色描述：缺少基本信息"
                
            metadata = char_data['metadata']
            print(f"metadata 内容: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
            
            if not metadata.get('birth_datetime'):
                print("错误：缺少 birth_datetime")
                print(f"当前 metadata: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
                return "无法生成角色描述：缺少出生时间"
                
            if not metadata.get('era'):
                print("错误：缺少 era")
                print(f"当前 metadata: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
                return "无法生成角色描述：缺少纪元信息"
            print("必要字段检查完成")
            
            # 分析八字
            print("\n[步骤2] 开始分析八字...")
            print(f"出生时间: {metadata['birth_datetime']}")
            birth_datetime = datetime.fromisoformat(metadata['birth_datetime'])
            bazi_analysis = self.bazi_analyzer.analyze_bazi(birth_datetime)
            print(f"八字分析结果: {json.dumps(bazi_analysis, ensure_ascii=False, indent=2)}")
            
            if 'error' in bazi_analysis:
                print(f"八字分析错误：{bazi_analysis['error']}")
                return f"八字分析失败：{bazi_analysis['error']}"
            
            # 将八字分析结果添加到角色数据中
            char_data['bazi'] = bazi_analysis
            print("八字分析完成")
            
            # 分析世界影响
            print("\n[步骤3] 开始分析世界影响...")
            print(f"纪元: {metadata['era']}")
            world_influence = self.bazi_analyzer.analyze_world_influence(
                birth_datetime,
                metadata['era']
            )
            print(f"世界影响分析结果: {json.dumps(world_influence, ensure_ascii=False, indent=2)}")
            
            if 'error' in world_influence:
                print(f"世界影响分析错误：{world_influence['error']}")
                return f"世界影响分析失败：{world_influence['error']}"
            
            # 将世界影响分析结果添加到角色数据中
            if 'analysis' not in char_data:
                char_data['analysis'] = {}
            char_data['analysis']['world_influence'] = world_influence
            print("世界影响分析完成")
            
            # 分析派系兼容性
            print("\n[步骤4] 开始分析派系兼容性...")
            if world_data.get('factions'):
                print(f"发现派系数量: {len(world_data['factions'])}")
                faction_compatibility = {}
                for faction_id, faction_data in world_data['factions'].items():
                    print(f"分析派系: {faction_id}")
                    compatibility = self.bazi_analyzer.analyze_faction_compatibility(
                        bazi_analysis,
                        faction_data
                    )
                    faction_compatibility[faction_id] = compatibility
                char_data['analysis']['faction_compatibility'] = faction_compatibility
                print("派系兼容性分析完成")
                print(f"派系兼容性分析结果: {json.dumps(faction_compatibility, ensure_ascii=False, indent=2)}")
            else:
                print("未发现派系数据，跳过派系兼容性分析")
            
            # 预测未来事件
            print("\n[步骤5] 开始预测未来事件...")
            future_events = self.bazi_analyzer.predict_future_events(
                bazi_analysis,
                world_data
            )
            if future_events:
                char_data['analysis']['future_events'] = future_events
                print("未来事件预测完成")
                print(f"未来事件预测结果: {json.dumps(future_events, ensure_ascii=False, indent=2)}")
            else:
                print("未生成未来事件预测")
            
            # 格式化分析结果
            print("\n[步骤6] 开始格式化分析结果...")
            print("准备调用 format_analysis...")
            print(f"最终的角色数据: {json.dumps(char_data, ensure_ascii=False, indent=2)}")
            print(f"最终的世界数据: {json.dumps(world_data, ensure_ascii=False, indent=2)}")
            
            description = self.bazi_formatter.format_analysis(char_data, world_data)
            print("分析结果格式化完成")
            print(f"格式化后的描述长度: {len(description)} 字符")
            
            # 生成AI描述（无论是否有DeepSeek API）
            try:
                print("\n[步骤7] 开始生成 AI 描述...")
                
                # 提取角色基本信息
                name = metadata.get('name', '未知')
                gender = '男性' if metadata.get('gender') == 'male' else '女性'
                birth_date = metadata.get('birth_datetime', '未知').split('T')[0]
                era = metadata.get('era', '未知')
                
                # 提取八字信息
                sizhu = bazi_analysis.get('sizhu', '未知')
                year_pillar = bazi_analysis.get('year_pillar', '未知')
                month_pillar = bazi_analysis.get('month_pillar', '未知')
                day_pillar = bazi_analysis.get('day_pillar', '未知')
                hour_pillar = bazi_analysis.get('hour_pillar', '未知')
                day_master = bazi_analysis.get('day_master', '未知')
                pattern = bazi_analysis.get('pattern', '未知')
                
                # 提取五行统计
                wuxing_count = bazi_analysis.get('wuxing_count', {})
                
                # 生成默认AI描述
                ai_description = f"""## 角色详细描述

{name}是一位出生于{birth_date}的{gender}，生活在{era}纪元。根据八字分析，{name}的四柱为{sizhu}，日主为{day_master}，命局为{pattern}。

### 性格特点

```mermaid
flowchart LR
    A([性格特点]) --> B[坚毅]
    A --> C[聪慧]
    A --> D[善良]
    A --> E[谨慎]
    A --> F[创新]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbf,stroke:#333,stroke-width:2px
    style E fill:#fbb,stroke:#333,stroke-width:2px
    style F fill:#bff,stroke:#333,stroke-width:2px
```

<details>
<summary>性格特点详情（点击展开）</summary>
<table>
  <tr>
    <th colspan="5">性格特点</th>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;text-align:center;'>坚毅</td>
    <td style='background-color:#e6e6ff;text-align:center;'>聪慧</td>
    <td style='background-color:#e6ffe6;text-align:center;'>善良</td>
    <td style='background-color:#ffe6ff;text-align:center;'>谨慎</td>
    <td style='background-color:#fff9e6;text-align:center;'>创新</td>
  </tr>
</table>
</details>

{name}性格坚毅，面对困难时能够保持冷静和坚持；聪慧过人，善于分析问题并找到解决方案；心地善良，乐于助人；做事谨慎，注重细节；同时具有创新精神，勇于尝试新事物。

### 能力分布

```mermaid
pie
    title 能力分布
    "领导力" : 30
    "创造力" : 25
    "分析能力" : 20
    "社交能力" : 15
    "适应能力" : 10
```

<details>
<summary>能力分布详情（点击展开）</summary>
<table>
  <tr>
    <th>领导力</th>
    <th>创造力</th>
    <th>分析能力</th>
    <th>社交能力</th>
    <th>适应能力</th>
  </tr>
  <tr>
    <td style='background-color:#FFD700;text-align:center;'>30%</td>
    <td style='background-color:#90EE90;text-align:center;'>25%</td>
    <td style='background-color:#87CEFA;text-align:center;'>20%</td>
    <td style='background-color:#FF6347;text-align:center;'>15%</td>
    <td style='background-color:#D2B48C;text-align:center;'>10%</td>
  </tr>
</table>
</details>

{name}的能力分布显示，领导力和创造力是其最突出的优势，分析能力也相当出色。这与{name}的八字特征高度吻合，{day_master}的特质使其在组织和创新方面表现出色。

### 人生轨迹

```mermaid
timeline
    title 人生轨迹
    section 幼年期
        启蒙教育 : 展现早慧
        特殊天赋 : 初显才能
    section 青年期
        专业训练 : 能力提升
        重要抉择 : 人生转折
    section 中年期
        事业高峰 : 成就卓著
        人际网络 : 广结善缘
    section 晚年期
        经验传承 : 培养后辈
        圆满人生 : 功成名就
```

<details>
<summary>人生轨迹详情（点击展开）</summary>
<table>
  <tr>
    <th colspan="2">幼年期</th>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;'>启蒙教育</td>
    <td>展现早慧</td>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;'>特殊天赋</td>
    <td>初显才能</td>
  </tr>
  <tr>
    <th colspan="2">青年期</th>
  </tr>
  <tr>
    <td style='background-color:#e6e6ff;'>专业训练</td>
    <td>能力提升</td>
  </tr>
  <tr>
    <td style='background-color:#e6e6ff;'>重要抉择</td>
    <td>人生转折</td>
  </tr>
  <tr>
    <th colspan="2">中年期</th>
  </tr>
  <tr>
    <td style='background-color:#e6ffe6;'>事业高峰</td>
    <td>成就卓著</td>
  </tr>
  <tr>
    <td style='background-color:#e6ffe6;'>人际网络</td>
    <td>广结善缘</td>
  </tr>
  <tr>
    <th colspan="2">晚年期</th>
  </tr>
  <tr>
    <td style='background-color:#ffe6ff;'>经验传承</td>
    <td>培养后辈</td>
  </tr>
  <tr>
    <td style='background-color:#ffe6ff;'>圆满人生</td>
    <td>功成名就</td>
  </tr>
</table>
</details>

{name}的人生轨迹展现了一个不断成长和发展的过程。在幼年期就展现出早慧和特殊天赋，青年期通过专业训练提升能力并做出重要抉择，中年期达到事业高峰并建立广泛的人际网络，晚年致力于经验传承和圆满人生。

### 与世界的互动

在{era}纪元的背景下，{name}的八字特质使其能够很好地适应和影响周围的环境。{day_master}的特性与当前世界的能量场相互呼应，使{name}在这个时代能够发挥出独特的作用。

### 未来发展

基于八字分析，{name}的未来发展充满潜力。随着时间推移，{name}的天赋将得到更充分的发挥，尤其是在与{pattern}相关的领域。建议{name}注重培养自身优势，同时关注弱项的提升，以实现更全面的发展。"""
                
                # 如果有DeepSeek API，尝试使用API生成描述
                if self.deepseek_client:
                    try:
                        print("DeepSeek API 已配置，尝试调用...")
                        print(f"DeepSeek 客户端状态: {self.deepseek_client is not None}")
                        print(f"DeepSeek 客户端类型: {type(self.deepseek_client)}")
                        
                        # 提取世界背景信息
                        world_background = world_data.get('background', '未知')
                        world_era = world_data.get('era', '未知')
                        world_regions = ', '.join(world_data.get('regions', ['未知区域']))
                        world_energy = ', '.join([f"{k}({v}%)" for k, v in world_data.get('energy_system', {}).items()])
                        
                        # 提取派系信息
                        world_factions = []
                        for faction_id, faction_data in world_data.get('factions', {}).items():
                            faction_name = faction_data.get('name', faction_id)
                            faction_desc = faction_data.get('description', '无描述')
                            faction_type = faction_data.get('type', '未知')
                            faction_alignment = faction_data.get('alignment', '未知')
                            world_factions.append(f"- {faction_name}（{faction_type}，{faction_alignment}）: {faction_desc}")
                        
                        factions_text = "\n".join(world_factions) if world_factions else "无派系信息"
                        
                        # 提取派系兼容性
                        faction_compatibility = char_data.get('analysis', {}).get('faction_compatibility', {})
                        compatibility_text = []
                        for faction_id, compatibility in faction_compatibility.items():
                            faction_name = world_data.get('factions', {}).get(faction_id, {}).get('name', faction_id)
                            score = compatibility.get('score', 0)
                            compatibility_text.append(f"- {faction_name}: 兼容性 {score}/10")
                        
                        compatibility_info = "\n".join(compatibility_text) if compatibility_text else "无派系兼容性信息"
                        
                        # 构建提示词
                        prompt = f"""请根据以下信息生成一个详细的角色描述，确保角色与世界背景紧密结合：

基本信息：
- 姓名：{name}
- 性别：{gender}
- 出生时间：{metadata.get('birth_datetime', '未知')}
- 纪元：{world_era}

世界背景：
{world_background}

世界元素：
- 主要区域：{world_regions}
- 能量体系：{world_energy}

派系信息：
{factions_text}

八字分析：
- 四柱：{sizhu}
- 年柱：{year_pillar}
- 月柱：{month_pillar}
- 日柱：{day_pillar}
- 时柱：{hour_pillar}
- 五行统计：{", ".join([f"{k}: {v}" for k, v in wuxing_count.items()]) if wuxing_count else "无五行信息"}
- 日主：{day_master}
- 格局：{pattern}

派系兼容性：
{compatibility_info}

请生成一个生动、详细的角色描述，包括性格特点、天赋能力、人生轨迹等。描述应该与世界背景和八字分析相符合，并考虑角色与各派系的兼容性。角色的特质、能力和经历应该反映出他们所处的世界环境和能量体系的影响。

在描述中，请包含以下Mermaid图表和HTML表格作为备用：

1. 角色性格特点图：
```mermaid
flowchart LR
    A([性格特点]) --> B[特点1]
    A --> C[特点2]
    A --> D[特点3]
    A --> E[特点4]
    A --> F[特点5]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbf,stroke:#333,stroke-width:2px
    style E fill:#fbb,stroke:#333,stroke-width:2px
    style F fill:#bff,stroke:#333,stroke-width:2px
```

<details>
<summary>性格特点详情（点击展开）</summary>
<table>
  <tr>
    <th colspan="5">性格特点</th>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;text-align:center;'>特点1</td>
    <td style='background-color:#e6e6ff;text-align:center;'>特点2</td>
    <td style='background-color:#e6ffe6;text-align:center;'>特点3</td>
    <td style='background-color:#ffe6ff;text-align:center;'>特点4</td>
    <td style='background-color:#fff9e6;text-align:center;'>特点5</td>
  </tr>
</table>
</details>

2. 角色能力分布图（请根据世界能量体系调整能力类型）：
```mermaid
pie
    title 能力分布
    "能力1" : 30
    "能力2" : 25
    "能力3" : 20
    "能力4" : 15
    "能力5" : 10
```

<details>
<summary>能力分布详情（点击展开）</summary>
<table>
  <tr>
    <th>能力1</th>
    <th>能力2</th>
    <th>能力3</th>
    <th>能力4</th>
    <th>能力5</th>
  </tr>
  <tr>
    <td style='background-color:#FFD700;text-align:center;'>30%</td>
    <td style='background-color:#90EE90;text-align:center;'>25%</td>
    <td style='background-color:#87CEFA;text-align:center;'>20%</td>
    <td style='background-color:#FF6347;text-align:center;'>15%</td>
    <td style='background-color:#D2B48C;text-align:center;'>10%</td>
  </tr>
</table>
</details>

3. 角色人生轨迹图（请根据世界背景设计关键事件）：
```mermaid
timeline
    title 人生轨迹
    section 幼年期
        重要事件1 : 描述
        重要事件2 : 描述
    section 青年期
        重要事件3 : 描述
        重要事件4 : 描述
    section 中年期
        重要事件5 : 描述
        重要事件6 : 描述
    section 晚年期
        重要事件7 : 描述
        重要事件8 : 描述
```

<details>
<summary>人生轨迹详情（点击展开）</summary>
<table>
  <tr>
    <th colspan="2">幼年期</th>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;'>重要事件1</td>
    <td>描述</td>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;'>重要事件2</td>
    <td>描述</td>
  </tr>
  <tr>
    <th colspan="2">青年期</th>
  </tr>
  <tr>
    <td style='background-color:#e6e6ff;'>重要事件3</td>
    <td>描述</td>
  </tr>
  <tr>
    <td style='background-color:#e6e6ff;'>重要事件4</td>
    <td>描述</td>
  </tr>
  <tr>
    <th colspan="2">中年期</th>
  </tr>
  <tr>
    <td style='background-color:#e6ffe6;'>重要事件5</td>
    <td>描述</td>
  </tr>
  <tr>
    <td style='background-color:#e6ffe6;'>重要事件6</td>
    <td>描述</td>
  </tr>
  <tr>
    <th colspan="2">晚年期</th>
  </tr>
  <tr>
    <td style='background-color:#ffe6ff;'>重要事件7</td>
    <td>描述</td>
  </tr>
  <tr>
    <td style='background-color:#ffe6ff;'>重要事件8</td>
    <td>描述</td>
  </tr>
</table>
</details>

4. 角色与世界互动图（展示角色与世界元素和派系的关系）：
```mermaid
flowchart TD
    A[{name}] --> B[与世界的关系1]
    A --> C[与世界的关系2]
    A --> D[与世界的关系3]
    B --> E[影响1]
    C --> F[影响2]
    D --> G[影响3]
    style A fill:#f96,stroke:#333,stroke-width:2px
    style B fill:#9cf,stroke:#333,stroke-width:2px
    style C fill:#9cf,stroke:#333,stroke-width:2px
    style D fill:#9cf,stroke:#333,stroke-width:2px
```

<details>
<summary>与世界互动详情（点击展开）</summary>
<table>
  <tr>
    <th>关系类型</th>
    <th>描述</th>
    <th>影响</th>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;'>与世界的关系1</td>
    <td>描述</td>
    <td>影响1</td>
  </tr>
  <tr>
    <td style='background-color:#e6e6ff;'>与世界的关系2</td>
    <td>描述</td>
    <td>影响2</td>
  </tr>
  <tr>
    <td style='background-color:#e6ffe6;'>与世界的关系3</td>
    <td>描述</td>
    <td>影响3</td>
  </tr>
</table>
</details>

请根据角色的八字和世界背景，替换上述图表中的占位符，生成真实、合理的内容。图表应该美观、信息丰富，能够直观地展示角色的特点、能力、发展轨迹以及与世界的互动关系。确保角色描述与世界背景紧密结合，反映出世界元素对角色的影响。"""
                        
                        print("\n=== DeepSeek API 调用详情 ===")
                        print(f"提示词长度: {len(prompt)} 字符")
                        print(f"模型: deepseek-chat")
                        print(f"温度: 0.7")
                        print(f"最大令牌数: 2000")
                        print("正在发送请求...")
                        
                        # 使用generate_text方法调用DeepSeek API
                        api_description = self.generate_text(prompt)
                        
                        if api_description and len(api_description) > 100:
                            print("\nDeepSeek API 描述生成成功")
                            print(f"API 描述长度: {len(api_description)} 字符")
                            print("API 描述预览:")
                            print(api_description[:200] + "...")
                            ai_description = api_description
                        else:
                            print("\nDeepSeek API 返回内容过短或为空，使用默认描述")
                    except Exception as e:
                        print(f"\n=== DeepSeek API 错误详情 ===")
                        print(f"错误类型: {type(e)}")
                        print(f"错误信息: {str(e)}")
                        print(f"错误详情: {e.__dict__ if hasattr(e, '__dict__') else '无详细信息'}")
                        print("使用默认AI描述")
                else:
                    print("DeepSeek API 未配置，使用默认AI描述")
                
                # 合并基础描述和 AI 描述
                final_description = f"{description}\n\n{ai_description}"
                print("\nAI 描述添加完成")
                print(f"最终描述长度: {len(final_description)} 字符")
                
                return final_description
                
            except Exception as e:
                print(f"\n=== 生成AI描述时发生错误 ===")
                print(f"错误类型: {type(e)}")
                print(f"错误信息: {str(e)}")
                print(f"错误详情: {e.__dict__ if hasattr(e, '__dict__') else '无详细信息'}")
                return description
            
            print("\n=== 角色描述生成完成 ===")
            return description
            
        except Exception as e:
            print(f"\n错误：生成角色描述时发生异常: {str(e)}")
            print(f"异常类型: {type(e)}")
            print(f"角色数据: {json.dumps(char_data, ensure_ascii=False, indent=2)}")
            print(f"世界数据: {json.dumps(world_data, ensure_ascii=False, indent=2)}")
            raise

    def _generate_detailed_description(self, char_data: dict, world_data: dict) -> str:
        """生成详细描述的提示词。
        
        Args:
            char_data: 角色数据
            world_data: 世界数据
            
        Returns:
            str: 生成的提示词
        """
        try:
            # 基本信息
            name = char_data['metadata']['name']
            gender = '男性' if char_data['metadata']['gender'] == 'male' else '女性'
            era = char_data['metadata']['era']
            birth_datetime = datetime.fromisoformat(char_data['metadata']['birth_datetime'])
            
            # 八字信息
            bazi = char_data['bazi']
            day_master = bazi['day_master']
            day_master_element = bazi['day_master_element']
            pattern = bazi['pattern']
            
            # 分析结果
            world_influence = char_data['analysis']['world_influence']
            faction_compatibility = char_data['analysis'].get('faction_compatibility', {})
            future_events = char_data['analysis']['future_events']
            
            # 构建提示词
            prompt = f"""请根据以下信息生成一个详细的角色描述：

基本信息：
- 姓名：{name}
- 性别：{gender}
- 纪元：{era}
- 出生时间：{birth_datetime}

八字分析：
- 日主：{day_master}（{day_master_element}）
- 格局：{pattern}
- 年柱：{bazi['year_pillar']}
- 月柱：{bazi['month_pillar']}
- 日柱：{bazi['day_pillar']}
- 时柱：{bazi['hour_pillar']}

世界影响：
{world_influence}

派系兼容性：
{faction_compatibility}

未来事件：
{future_events}

请从以下几个方面描述这个角色：
1. 性格特征和个性
2. 天赋和能力倾向
3. 人生经历和重要事件
4. 与世界的互动和影响
5. 与其他角色的关系网络
6. 未来发展的可能性

要求：
1. 描述要符合角色的八字特征
2. 考虑世界背景和纪元特点
3. 注重人物的独特性和成长轨迹
4. 描述要生动具体，富有画面感
5. 保持内容的连贯性和逻辑性

请用 Markdown 格式输出，适当使用标题、列表和引用等格式。"""
            
            return prompt
            
        except Exception as e:
            print(f"生成详细描述提示词时发生错误: {str(e)}")
            raise

    def generate_world_description(self, world_data: Dict[str, Any]) -> str:
        """生成世界描述
        
        Args:
            world_data: 世界数据
            
        Returns:
            str: 生成的世界描述
        """
        try:
            # 提取世界ID
            world_id = world_data.get('id', 'unknown')
            print(f"生成世界描述，世界ID: {world_id}")
            
            # 如果没有纪元分布，生成随机分布
            if 'era_distribution' not in world_data:
                print("未找到纪元分布，生成随机分布")
                ancient = random.randint(20, 40)
                modern = random.randint(30, 50)
                future = 100 - ancient - modern
                world_data['era_distribution'] = {
                    "ancient": ancient,
                    "modern": modern,
                    "future": future
                }
            
            # 如果没有主要地区，生成随机地区
            if 'main_regions' not in world_data:
                print("未找到主要地区，生成随机地区")
                regions = [
                    "北方山脉", "南方平原", "东方海岸", "西方沙漠", 
                    "中央城市群", "浮空岛屿", "地下洞穴", "热带雨林"
                ]
                selected_regions = random.sample(regions, random.randint(3, 5))
                world_data['main_regions'] = selected_regions
            
            # 如果没有能量系统，生成随机能量系统
            if 'energy_system' not in world_data:
                print("未找到能量系统，生成随机能量系统")
                energy_types = ["元素能量", "科技力量", "灵气", "魔法", "机械能", "生物能"]
                selected_energy = random.sample(energy_types, random.randint(2, 4))
                
                energy_system = {}
                remaining = 100
                for i, energy in enumerate(selected_energy):
                    if i == len(selected_energy) - 1:
                        energy_system[energy] = remaining
                    else:
                        percent = random.randint(10, min(50, remaining - 10 * (len(selected_energy) - i - 1)))
                        energy_system[energy] = percent
                        remaining -= percent
                
                world_data['energy_system'] = energy_system
            
            energy_system = []
            for energy, percent in world_data.get('energy_system', {}).items():
                energy_system.append(f"{energy}({percent}%)")
            energy_system_text = ', '.join(energy_system)
            
            # 提取或生成派系
            if 'factions' not in world_data or not world_data['factions']:
                print("未找到派系信息，生成随机派系")
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
                
                # 保存更新后的世界数据
                self._save_world_data(world_data)
                print("已保存生成的派系信息到世界数据文件")
            
            factions = []
            for faction_id, faction_data in world_data.get('factions', {}).items():
                faction_name = faction_data.get('name', faction_id)
                faction_type = faction_data.get('type', '未知')
                faction_alignment = faction_data.get('alignment', '未知')
                faction_desc = faction_data.get('description', '无描述')
                factions.append(f"- {faction_name}（{faction_type}，{faction_alignment}）: {faction_desc}")
            
            factions_text = "\n".join(factions)
            
            # 构建优化后的提示词
            prompt = """请根据以下参数生成一个连贯、丰富的世界描述：

世界ID: {world_id}

纪元分布:
- 古代: {ancient_percent}%
- 现代: {modern_percent}%
- 未来: {future_percent}%

主要区域: {regions}

能量体系: {energy_system_text}

派系分布:
{factions_text}

请生成一个详细的世界描述，包括以下内容：
1. 世界概述
2. 地理与环境
3. 派系分析
4. 技术与魔法体系
5. 典型事件模板
6. 世界独特规则
7. 当前状态与危机

在描述中，请包含以下Mermaid图表代码：
1. 纪元分布饼图
2. 能量体系饼图
3. 派系关系图
4. 世界地理思维导图

请确保描述丰富、连贯，并与提供的参数保持一致。描述应该具有内部逻辑性，能够为角色提供一个合理的生存和发展环境。"""
            
            # 准备Mermaid图表数据
            energy_system_chart_data = ""
            for energy, percent in world_data.get('energy_system', {}).items():
                energy_name = energy.split("(")[0] if "(" in energy else energy
                percent_value = percent.strip("%)") if isinstance(percent, str) and "%" in percent else percent
                energy_system_chart_data += f'    "{energy_name}" : {percent_value}\n'
            
            # 准备派系数据
            factions_list = list(world_data.get('factions', {}).values())
            faction_1_name = factions_list[0].get('name', '主要派系1') if factions_list else '主要派系1'
            faction_2_name = factions_list[1].get('name', '主要派系2') if len(factions_list) > 1 else '主要派系2'
            faction_3_name = factions_list[2].get('name', '主要派系3') if len(factions_list) > 2 else '主要派系3'
            
            # 根据派系对齐方式设置颜色
            def get_faction_color(faction_index):
                if faction_index >= len(factions_list):
                    return '#bbf'
                alignment = factions_list[faction_index].get('alignment', '中立')
                if '善良' in alignment:
                    return '#bfb'
                elif '邪恶' in alignment:
                    return '#fbb'
                else:
                    return '#bbf'
            
            faction_1_color = get_faction_color(0)
            faction_2_color = get_faction_color(1)
            faction_3_color = get_faction_color(2)
            
            # 准备地理数据
            geography_mindmap_data = ""
            for region in world_data.get('main_regions', ['未知区域']):
                geography_mindmap_data += f'        {region}\n'
            
            # 替换模板中的变量
            prompt = prompt.format(
                world_id=world_id,
                ancient_percent=world_data['era_distribution']['ancient'],
                modern_percent=world_data['era_distribution']['modern'],
                future_percent=world_data['era_distribution']['future'],
                regions=world_data['main_regions'],
                energy_system_text=energy_system_text,
                factions_text=factions_text
            )

            print("\n=== DeepSeek API 调用详情 ===")
            print(f"提示词长度: {len(prompt)} 字符")
            print(f"模型类型: {self.model_type}")
            print(f"温度: {self.temperature}")
            print(f"最大token数: {self.max_tokens}")
            
            # 调用 DeepSeek API 生成世界描述
            world_description = self.generate_text(prompt)
            
            # 后处理：添加Mermaid图表模板
            if "```mermaid" not in world_description:
                print("生成的描述中没有Mermaid图表，添加模板")
                
                # 添加纪元分布饼图
                era_chart = f"""```mermaid
pie
    title 纪元分布
    "古代" : {world_data['era_distribution']['ancient']}
    "现代" : {world_data['era_distribution']['modern']}
    "未来" : {world_data['era_distribution']['future']}
```"""
                
                # 添加能量体系饼图
                energy_chart = f"""```mermaid
pie
    title 能量体系分布
{energy_system_chart_data}```"""
                
                # 添加派系关系图
                faction_chart = f"""```mermaid
flowchart TD
    A[世界格局] --> B[{faction_1_name}]
    A --> C[{faction_2_name}]
    A --> D[{faction_3_name}]
    B -- "合作" --> C
    C -- "竞争" --> D
    D -- "对抗" --> B
    style A fill:#f96,stroke:#333,stroke-width:2px
    style B fill:{faction_1_color},stroke:#333,stroke-width:2px
    style C fill:{faction_2_color},stroke:#333,stroke-width:2px
    style D fill:{faction_3_color},stroke:#333,stroke-width:2px
```"""
                
                # 添加地理思维导图
                geo_chart = f"""```mermaid
mindmap
    root((世界地理))
{geography_mindmap_data}```"""
                
                # 在适当的位置插入图表
                sections = world_description.split("\n## ")
                enhanced_description = sections[0]  # 世界概述
                
                # 在世界概述后添加纪元分布图
                if "纪元分布" in world_description:
                    enhanced_description += "\n\n" + era_chart + "\n"
                
                # 添加其他部分和图表
                for i, section in enumerate(sections[1:], 1):
                    enhanced_description += "\n## " + section
                    
                    # 在地理与环境部分后添加地理思维导图
                    if section.startswith("地理与环境") and "```mermaid" not in section:
                        enhanced_description += "\n\n" + geo_chart
                    
                    # 在能量体系部分后添加能量体系饼图
                    elif ("能量体系" in section or "技术与魔法" in section) and "```mermaid" not in section:
                        enhanced_description += "\n\n" + energy_chart
                    
                    # 在派系分析部分后添加派系关系图
                    elif section.startswith("派系分析") and "```mermaid" not in section:
                        enhanced_description += "\n\n" + faction_chart
                
                world_description = enhanced_description
            
            print(f"生成的世界描述长度: {len(world_description)} 字符")
            print("世界描述生成完成")
            
            return world_description
            
        except Exception as e:
            print(f"生成世界描述时发生错误: {str(e)}")
            print(f"错误类型: {type(e)}")
            
            # 生成一个简单的默认描述
            world_id = world_data.get('id', '未知世界')
            
            # 提取纪元分布
            era_distribution = world_data.get('era_distribution', {})
            ancient_percent = era_distribution.get('ancient', 33)
            modern_percent = era_distribution.get('modern', 33)
            future_percent = era_distribution.get('future', 34)
            
            # 提取区域
            regions = ', '.join(world_data.get('main_regions', ['北方山脉', '南方平原', '东方海岸']))
            
            # 提取能量体系
            energy_system = []
            for energy, percent in world_data.get('energy_system', {'元素能量': 50, '科技力量': 50}).items():
                energy_system.append(f"{energy}({percent}%)")
            energy_system_text = ', '.join(energy_system)
            
            # 提取派系
            factions = []
            for faction_id, faction_data in world_data.get('factions', {
                'faction_1': {'name': '守护者联盟', 'type': '政治', 'alignment': '守序善良', 'description': '守护者联盟是世界中的一个重要势力，致力于维护和平与秩序。'},
                'faction_2': {'name': '探索者协会', 'type': '学术', 'alignment': '中立善良', 'description': '探索者协会专注于探索世界的奥秘和收集知识。'},
                'faction_3': {'name': '自由商会', 'type': '经济', 'alignment': '中立', 'description': '自由商会控制着世界的贸易网络，追求利益最大化。'}
            }).items():
                faction_name = faction_data.get('name', faction_id)
                faction_type = faction_data.get('type', '未知')
                faction_alignment = faction_data.get('alignment', '未知')
                faction_desc = faction_data.get('description', '无描述')
                factions.append(f"- {faction_name}（{faction_type}，{faction_alignment}）: {faction_desc}")
            
            factions_text = "\n".join(factions)
            
            # 生成默认描述
            default_description = """# {world_id} 世界描述

## 世界概述

这是一个融合了古代、现代和未来元素的多元世界，各种力量和派系在此交织。世界历史悠久，文明发展经历了多个阶段，形成了独特的社会结构和文化传统。

## 纪元分布

```mermaid
pie
    title 纪元分布
    "古代" : {ancient_percent}
    "现代" : {modern_percent}
    "未来" : {future_percent}
```

## 地理与环境

这个世界拥有多样化的地理环境，包括{regions}等区域，每个区域都有其独特的气候特点和自然资源。

```mermaid
mindmap
    root((世界地理))
{geography_mindmap_data}
```

## 能量体系

世界中存在多种能量形式，它们相互影响，共同构成了世界的基础力量体系。

```mermaid
pie
    title 能量体系分布
{energy_system_chart_data}
```

## 派系分析

世界中存在多个重要派系，它们各自拥有不同的理念、目标和行动方式。

{factions_text}

```mermaid
flowchart TD
    A[世界格局] --> B[{faction_1_name}]
    A --> C[{faction_2_name}]
    A --> D[{faction_3_name}]
    B -- "合作" --> C
    C -- "竞争" --> D
    D -- "对抗" --> B
    style A fill:#f96,stroke:#333,stroke-width:2px
    style B fill:{faction_1_color},stroke:#333,stroke-width:2px
    style C fill:{faction_2_color},stroke:#333,stroke-width:2px
    style D fill:{faction_3_color},stroke:#333,stroke-width:2px
```

## 技术与魔法体系

世界中的技术和魔法系统相互交织，形成了独特的力量体系。古代的魔法传统与现代科技相结合，同时也有来自未来的先进技术元素。

## 典型事件模板

1. **派系冲突**：不同派系之间的利益冲突和权力争夺
2. **资源探索**：发现和争夺稀有资源的冒险
3. **神秘事件**：超自然现象和神秘事件的调查
4. **技术革新**：新技术的发明和应用带来的社会变革
5. **历史探索**：揭示世界历史秘密的探索活动

## 世界独特规则

1. **能量转化**：不同形式的能量可以相互转化，但转化过程会产生能量损耗
2. **派系平衡**：世界的稳定依赖于各大派系之间的力量平衡
3. **历史循环**：世界历史呈现出一定的循环性，过去的模式会以新的形式重现
4. **区域特性**：每个地理区域都有其独特的能量特性，影响该区域的生物和文明

## 当前状态与危机

世界目前处于相对稳定的状态，但潜在的危机正在酝酿。主要派系之间的紧张关系日益加剧，能量体系的平衡也面临挑战。新的力量正在崛起，可能打破现有的秩序。

> 注：此描述为系统自动生成的默认内容，由于生成过程中出现错误，仅提供基本框架。实际世界特点可能与此描述有所不同。
"""
            
            # 准备Mermaid图表数据
            energy_system_chart_data = ""
            for energy, percent in world_data.get('energy_system', {'元素能量': 50, '科技力量': 50}).items():
                energy_name = energy.split("(")[0] if "(" in energy else energy
                percent_value = percent.strip("%)") if isinstance(percent, str) and "%" in percent else percent
                energy_system_chart_data += f'    "{energy_name}" : {percent_value}\n'
            
            # 准备派系数据
            factions_list = list(world_data.get('factions', {
                'faction_1': {'name': '守护者联盟', 'type': '政治', 'alignment': '守序善良', 'description': '守护者联盟是世界中的一个重要势力，致力于维护和平与秩序。'},
                'faction_2': {'name': '探索者协会', 'type': '学术', 'alignment': '中立善良', 'description': '探索者协会专注于探索世界的奥秘和收集知识。'},
                'faction_3': {'name': '自由商会', 'type': '经济', 'alignment': '中立', 'description': '自由商会控制着世界的贸易网络，追求利益最大化。'}
            }).values())
            faction_1_name = factions_list[0].get('name', '主要派系1') if factions_list else '主要派系1'
            faction_2_name = factions_list[1].get('name', '主要派系2') if len(factions_list) > 1 else '主要派系2'
            faction_3_name = factions_list[2].get('name', '主要派系3') if len(factions_list) > 2 else '主要派系3'
            
            # 根据派系对齐方式设置颜色
            def get_faction_color(faction_index):
                if faction_index >= len(factions_list):
                    return '#bbf'
                alignment = factions_list[faction_index].get('alignment', '中立')
                if '善良' in alignment:
                    return '#bfb'
                elif '邪恶' in alignment:
                    return '#fbb'
                else:
                    return '#bbf'
            
            faction_1_color = get_faction_color(0)
            faction_2_color = get_faction_color(1)
            faction_3_color = get_faction_color(2)
            
            # 准备地理数据
            geography_mindmap_data = ""
            for region in world_data.get('main_regions', ['北方山脉', '南方平原', '东方海岸']):
                geography_mindmap_data += f'        {region}\n'
            
            # 替换模板中的变量
            default_description = default_description.format(
                world_id=world_id,
                ancient_percent=ancient_percent,
                modern_percent=modern_percent,
                future_percent=future_percent,
                regions=regions,
                energy_system_text=energy_system_text,
                factions_text=factions_text,
                energy_system_chart_data=energy_system_chart_data,
                faction_1_name=faction_1_name,
                faction_2_name=faction_2_name,
                faction_3_name=faction_3_name,
                faction_1_color=faction_1_color,
                faction_2_color=faction_2_color,
                faction_3_color=faction_3_color,
                geography_mindmap_data=geography_mindmap_data
            )
            
            return default_description
    
    def _save_world_data(self, world_data: Dict[str, Any]) -> None:
        """保存世界数据
        
        Args:
            world_data: 世界数据
        """
        try:
            world_id = world_data.get('id')
            if not world_id:
                print("无法保存世界数据：缺少世界ID")
                return
                
            # 构建文件路径
            world_file = os.path.join(self.base_dir, "worlds", f"{world_id}.json")
            
            # 如果目录不存在，创建目录
            os.makedirs(os.path.dirname(world_file), exist_ok=True)
            
            # 保存世界数据
            with open(world_file, "w", encoding="utf-8") as f:
                json.dump(world_data, f, ensure_ascii=False, indent=2)
                
            print(f"世界数据已保存到: {world_file}")
            
        except Exception as e:
            print(f"保存世界数据时发生错误: {str(e)}")

    def _generate_recommendations(self, bazi_data: Dict,
                                world_influence: Dict,
                                faction_analysis: Dict) -> Dict[str, List[str]]:
        """生成修正建议"""
        return {
            "development": [
                "根据八字特征调整发展方向",
                "注意把握时运变化",
                "合理利用环境能量"
            ],
            "relationships": [
                "选择合适的合作伙伴",
                "避免不利的人际关系",
                "培养有益的社交圈"
            ],
            "abilities": [
                "强化优势能力",
                "弥补短板",
                "开发潜在天赋"
            ],
            "risks": [
                {"type": "能量冲突", "warning": "注意五行相克"},
                {"type": "时运变化", "warning": "把握机遇窗口"},
                {"type": "环境影响", "warning": "适应世界变迁"}
            ]
        }

    def _format_elements(self, elements: Dict[str, float]) -> str:
        return "\n".join([f"- {element}: {value:.2f}" for element, value in elements.items()])

    def _format_potential(self, potential: List[Dict]) -> str:
        return "、".join([f"{p['path']}({p['probability']:.2f})" for p in potential])

    def _format_challenges(self, challenges: List[Dict]) -> str:
        return "、".join([f"{c['type']}({c['severity']:.2f})" for c in challenges])

    def _format_predictions(self, predictions: List[Dict]) -> str:
        return "\n".join([
            f"- {pred['year']}年：{pred['type']} (概率：{pred['probability']:.2f}，"
            f"重要性：{'★' * pred['significance']})"
            for pred in predictions
        ])

    def get_era_skills(self, era: str) -> List[str]:
        """获取纪元特定的技能池
        
        Args:
            era: 纪元类型
            
        Returns:
            List[str]: 技能列表
        """
        return self.config["character"]["skill_pools"][era]
    
    def get_name_elements(self, era):
        """获取指定纪元的姓名生成元素。
        
        Args:
            era (str): 纪元名称 ('ancient', 'modern', 'future')
            
        Returns:
            dict: 包含姓名生成所需元素的字典
        """
        name_config = self.config["character"]["name_generation"]
        if era not in name_config:
            raise ValueError(f"未找到纪元 '{era}' 的姓名配置")
        
        era_config = name_config[era]
        return {
            "surnames": era_config.get("surnames", []),
            "male_given": era_config.get("male_given", []),
            "female_given": era_config.get("female_given", []),
            "male_middle": era_config.get("male_middle", []),
            "female_middle": era_config.get("female_middle", []),
            "titles": era_config.get("titles", [])
        }
    
    def get_default_config(self):
        """获取默认配置。
        
        Returns:
            dict: 默认配置字典
        """
        return {
            "character": {
                "name_generation": {
                    "ancient": {
                        "surnames": ["李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"],
                        "male_given": ["云", "风", "山", "河", "海", "天", "地", "星", "月", "日"],
                        "female_given": ["霞", "月", "花", "雪", "玉", "珠", "凤", "莲", "春", "秋"],
                        "male_middle": ["子", "文", "武", "德", "明", "志", "仁", "义", "礼", "智"],
                        "female_middle": ["静", "婷", "美", "丽", "雅", "芳", "华", "英", "慧", "贤"],
                        "titles": ["道长", "真人", "仙子", "大师", "前辈"]
                    },
                    "modern": {
                        "surnames": ["张", "王", "李", "赵", "钱", "孙", "周", "吴", "郑", "陈"],
                        "male_given": ["伟", "强", "磊", "超", "勇", "军", "建", "光", "明", "永"],
                        "female_given": ["娟", "敏", "静", "秀", "丽", "艳", "芳", "萍", "英", "华"],
                        "titles": ["先生", "女士", "老师", "博士", "教授"]
                    },
                    "future": {
                        "surnames": ["电子", "量子", "星际", "虚拟", "智能", "光速", "时空", "基因", "纳米", "脑波"],
                        "male_given": ["指挥官", "工程师", "探索者", "战士", "科学家", "领航员", "守护者", "研究员"],
                        "female_given": ["指挥官", "工程师", "探索者", "战士", "科学家", "领航员", "守护者", "研究员"],
                        "titles": ["指挥官", "博士", "教授", "研究员", "工程师"]
                    }
                },
                "skill_pools": {
                    "ancient": [
                        "内功心法",
                        "剑术精通",
                        "丹道修炼",
                        "阵法布置",
                        "符箓制作",
                        "炼器技艺",
                        "轻功身法",
                        "医术精通",
                        "毒术研究",
                        "兵器锻造"
                    ],
                    "modern": [
                        "计算机编程",
                        "数据分析",
                        "人工智能",
                        "网络安全",
                        "商业管理",
                        "市场营销",
                        "金融投资",
                        "项目管理",
                        "研发创新",
                        "团队领导"
                    ],
                    "future": [
                        "量子计算",
                        "基因工程",
                        "纳米技术",
                        "星际导航",
                        "虚拟现实",
                        "人工意识",
                        "时空操控",
                        "能源转换",
                        "生态修复",
                        "智能设计"
                    ]
                }
            },
            "world": {
                "title_format": "=== 三纪元世界实例：{world_id} ===",
                "checksum_format": "校验码：{checksum} | 验证码：{validation}",
                "entropy_panel": {
                    "title": "【熵增监控面板】",
                    "header": "指标名称              当前值          阈值          状态",
                    "metrics": [
                        {
                            "name": "灵气-石油转换率",
                            "format": "{value:.2f}",
                            "threshold": "4.0",
                            "status": {
                                "normal": "正常",
                                "warning": "警告"
                            },
                            "suffix": "μm/s",
                            "adjustment": "{sign}{value:.2f}%"
                        },
                        {
                            "name": "现代化指数",
                            "format": "{value:.1f}%",
                            "threshold": "85%",
                            "status": "稳定",
                            "suffix": "",
                            "adjustment": "{sign}{value:.1f}pt"
                        },
                        {
                            "name": "量子态稳定性",
                            "format": "{value:.1f}%",
                            "threshold": "90%",
                            "status": "波动",
                            "suffix": "",
                            "adjustment": "{sign}{value:.1f}%"
                        }
                    ]
                },
                "locations": {
                    "ancient": {
                        "title": "【修真纪元】",
                        "descriptions": [
                            "灵气复苏，道法自然",
                            "修真门派林立，仙家洞府遍布",
                            "丹鼎阵法，符箓法器，无所不包"
                        ]
                    },
                    "modern": {
                        "title": "【现代纪元】",
                        "descriptions": [
                            "科技发展，信息爆炸",
                            "城市繁华，人流如织",
                            "互联网络，人工智能，方兴未艾"
                        ]
                    },
                    "future": {
                        "title": "【未来纪元】",
                        "descriptions": [
                            "星际殖民，量子革命",
                            "虚拟现实，意识上传",
                            "基因工程，纳米技术，无所不能"
                        ]
                    }
                },
                "protocol_statement": "本世界实例完全符合VUCCP v1.0和TDP v{version}协议标准。\n校验码：{checksum} | 验证码：{validation} | 有效期至：{expiry_date}"
            }
        }
    
    def _generate_validation_code(self) -> str:
        """生成校验码"""
        import uuid
        return uuid.uuid4().hex[:4].upper()

    def get_character_description(self, character_data: Dict[str, Any], world_id: str, protocol_version: str) -> str:
        """生成角色描述。
        
        Args:
            character_data: 角色数据
            world_id: 世界ID
            protocol_version: 协议版本
            
        Returns:
            str: Markdown格式的角色描述
        """
        try:
            print("\n=== 开始生成角色描述 ===")
            print(f"角色数据: {json.dumps(character_data, ensure_ascii=False, indent=2)}")
            print(f"世界ID: {world_id}")
            print(f"协议版本: {protocol_version}")
            print(f"当前工作目录: {os.getcwd()}")
            
            # 构建正确的文件路径
            world_file = os.path.join(self.base_dir, "worlds", f"{world_id}.json")  # 更新世界文件路径
            
            print(f"\n正在查找世界文件: {world_file}")
            print(f"世界文件是否存在: {os.path.exists(world_file)}")
            
            # 如果文件不存在，尝试在不同的目录下查找
            if not os.path.exists(world_file):
                # 尝试在当前工作目录下的my_universes/worlds目录查找
                alt_base_dir = os.path.join(os.getcwd(), "my_universes")
                alt_world_file = os.path.join(alt_base_dir, "worlds", f"{world_id}.json")
                print(f"尝试替代路径1: {alt_world_file}")
                print(f"替代路径1是否存在: {os.path.exists(alt_world_file)}")
                
                if os.path.exists(alt_world_file):
                    world_file = alt_world_file
                    print(f"使用替代路径1: {world_file}")
                else:
                    # 尝试在NeoCore/my_universes/worlds目录下查找
                    alt_base_dir2 = os.path.join(os.getcwd(), "NeoCore", "my_universes")
                    alt_world_file2 = os.path.join(alt_base_dir2, "worlds", f"{world_id}.json")
                    print(f"尝试替代路径2: {alt_world_file2}")
                    print(f"替代路径2是否存在: {os.path.exists(alt_world_file2)}")
                    
                    if os.path.exists(alt_world_file2):
                        world_file = alt_world_file2
                        print(f"使用替代路径2: {world_file}")
                    else:
                        # 如果仍然找不到，创建一个默认的世界数据
                        print("无法找到世界文件，将创建默认世界数据")
                        world_data = {
                            "id": world_id,
                            "era": character_data.get('basic', {}).get('era', '未知')
                        }
                        return self._generate_default_character_description(character_data, world_data)
            
            # 读取世界数据
            print("\n正在读取世界数据...")
            print(f"世界文件路径: {world_file}")
            print(f"世界文件大小: {os.path.getsize(world_file) if os.path.exists(world_file) else '文件不存在'} 字节")
            
            try:
                with open(world_file, "r", encoding="utf-8") as f:
                    world_data = json.load(f)
                print("世界数据加载成功")
                print(f"世界数据字段: {list(world_data.keys())}")
                print(f"世界数据大小: {len(json.dumps(world_data))} 字符")
                
                # 如果世界数据中没有背景描述，生成一个
                if 'background' not in world_data:
                    print("世界数据中缺少背景描述，正在生成...")
                    try:
                        world_data['background'] = self.generate_world_description(world_data)
                        print("世界背景描述生成完成")
                        
                        # 尝试保存更新后的世界数据
                        try:
                            self._save_world_data(world_data)
                            print("更新后的世界数据已保存")
                        except Exception as e:
                            print(f"保存世界数据时发生错误: {str(e)}")
                    except Exception as e:
                        print(f"生成世界背景描述时发生错误: {str(e)}")
                        world_data['background'] = f"这是一个神秘的世界，ID为{world_id}。"
                        print("使用简单的默认世界背景描述")
                
            except json.JSONDecodeError as e:
                print(f"世界数据 JSON 解析错误: {str(e)}")
                print(f"错误位置: 行 {e.lineno}, 列 {e.colno}")
                print(f"错误片段: {e.doc[max(0, e.pos-50):e.pos+50]}")
                # 创建一个默认的世界数据
                world_data = {
                    "id": world_id,
                    "era": character_data.get('metadata', {}).get('era', '未知')
                }
                # 生成世界背景描述
                try:
                    world_data['background'] = self.generate_world_description(world_data)
                    print("世界背景描述生成完成")
                except Exception as e:
                    print(f"生成世界背景描述时发生错误: {str(e)}")
                    world_data['background'] = f"这是一个神秘的世界，ID为{world_id}。"
                    print("使用简单的默认世界背景描述")
                print("使用生成的世界数据")
            except Exception as e:
                print(f"读取世界数据时发生错误: {str(e)}")
                print(f"错误类型: {type(e)}")
                # 创建一个默认的世界数据
                world_data = {
                    "id": world_id,
                    "era": character_data.get('metadata', {}).get('era', '未知')
                }
                # 生成世界背景描述
                try:
                    world_data['background'] = self.generate_world_description(world_data)
                    print("世界背景描述生成完成")
                except Exception as e:
                    print(f"生成世界背景描述时发生错误: {str(e)}")
                    world_data['background'] = f"这是一个神秘的世界，ID为{world_id}。"
                    print("使用简单的默认世界背景描述")
                print("使用生成的世界数据")
            
            # 确保角色数据包含必要的字段
            print("\n验证角色数据...")
            print(f"角色数据字段: {list(character_data.keys())}")
            print(f"角色数据大小: {len(json.dumps(character_data))} 字符")
            
            if 'metadata' not in character_data:
                print("错误：角色数据缺少 metadata 字段")
                print(f"当前角色数据: {json.dumps(character_data, ensure_ascii=False, indent=2)}")
                # 创建一个默认的metadata
                character_data['metadata'] = {
                    "id": "unknown",
                    "name": "未知角色",
                    "gender": "male",
                    "birth_datetime": "1900-01-01T00:00:00",
                    "era": "modern"
                }
                print("使用默认metadata")
            
            metadata = character_data['metadata']
            print(f"metadata 字段: {list(metadata.keys())}")
            
            if 'id' not in metadata:
                print("错误：角色数据缺少 id 字段")
                print(f"当前 metadata: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
                metadata['id'] = "unknown"
                print("使用默认id")
            
            print("角色数据验证完成")
            
            # 生成角色描述
            print("\n开始生成角色描述...")
            print("准备调用 generate_character_description...")
            print(f"角色数据: {json.dumps(character_data, ensure_ascii=False, indent=2)}")
            print(f"世界数据: {json.dumps(world_data, ensure_ascii=False, indent=2)}")
            
            try:
                description = self.generate_character_description(character_data, world_data)
                print("角色描述生成完成")
                print(f"生成的描述长度: {len(description)} 字符")
            except Exception as e:
                print(f"生成角色描述时发生错误: {str(e)}")
                print(f"错误类型: {type(e)}")
                
                # 生成一个简单的默认描述
                name = metadata.get('name', '未知角色')
                gender = '男' if metadata.get('gender') == 'male' else '女'
                birth_date = metadata.get('birth_datetime', '未知').split('T')[0]
                era = metadata.get('era', '未知')
                
                # 提取世界背景信息
                world_background = world_data.get('background', '未知世界背景')
                # 如果世界背景太长，只取前500个字符
                if len(world_background) > 500:
                    world_background_summary = world_background[:500] + "..."
                else:
                    world_background_summary = world_background
                
                # 提取世界元素
                world_regions = ', '.join(world_data.get('main_regions', ['未知区域']))
                world_energy = ', '.join([f"{k}({v}%)" for k, v in world_data.get('energy_system', {}).items()])
                world_factions = []
                for faction_id, faction_data in world_data.get('factions', {}).items():
                    faction_name = faction_data.get('name', faction_id)
                    faction_desc = faction_data.get('description', '无描述')
                    faction_type = faction_data.get('type', '未知')
                    faction_alignment = faction_data.get('alignment', '未知')
                    world_factions.append(f"{faction_name}（{faction_type}，{faction_alignment}）")
                
                factions_text = ", ".join(world_factions) if world_factions else "无派系信息"
                
                description = f"""# {name} 的角色分析

## 基本信息
- 性别：{gender}
- 出生时间：{metadata.get('birth_datetime', '未知')}
- 纪元：{era}

## 世界背景
**世界ID**: {world_id}
**主要区域**: {world_regions}
**能量体系**: {world_energy}
**主要势力**: {factions_text}

{world_background_summary}

## 角色详细描述

{name}是一位出生于{birth_date}的{gender}，生活在{era}纪元的{world_regions}地区。

### 性格特点

```mermaid
flowchart LR
    A([性格特点]) --> B[坚毅]
    A --> C[聪慧]
    A --> D[善良]
    A --> E[谨慎]
    A --> F[创新]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbf,stroke:#333,stroke-width:2px
    style E fill:#fbb,stroke:#333,stroke-width:2px
    style F fill:#bff,stroke:#333,stroke-width:2px
```

<details>
<summary>性格特点详情（点击展开）</summary>
<table>
  <tr>
    <th colspan="5">性格特点</th>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;text-align:center;'>坚毅</td>
    <td style='background-color:#e6e6ff;text-align:center;'>聪慧</td>
    <td style='background-color:#e6ffe6;text-align:center;'>善良</td>
    <td style='background-color:#ffe6ff;text-align:center;'>谨慎</td>
    <td style='background-color:#fff9e6;text-align:center;'>创新</td>
  </tr>
</table>
</details>

{name}性格坚毅，面对困难时能够保持冷静和坚持；聪慧过人，善于分析问题并找到解决方案；心地善良，乐于助人；做事谨慎，注重细节；同时具有创新精神，勇于尝试新事物。在{world_regions}的环境影响下，{name}特别擅长运用{world_energy.split(',')[0] if ',' in world_energy else world_energy}能量。

### 能力分布

```mermaid
pie
    title 能力分布
    "领导力" : 30
    "创造力" : 25
    "分析能力" : 20
    "社交能力" : 15
    "适应能力" : 10
```

<details>
<summary>能力分布详情（点击展开）</summary>
<table>
  <tr>
    <th>领导力</th>
    <th>创造力</th>
    <th>分析能力</th>
    <th>社交能力</th>
    <th>适应能力</th>
  </tr>
  <tr>
    <td style='background-color:#FFD700;text-align:center;'>30%</td>
    <td style='background-color:#90EE90;text-align:center;'>25%</td>
    <td style='background-color:#87CEFA;text-align:center;'>20%</td>
    <td style='background-color:#FF6347;text-align:center;'>15%</td>
    <td style='background-color:#D2B48C;text-align:center;'>10%</td>
  </tr>
</table>
</details>

{name}的能力分布显示，领导力和创造力是其最突出的优势，分析能力也相当出色。这使{name}在{world_factions[0].split('（')[0] if world_factions else '世界各地'}中表现出色，能够应对各种挑战。

### 人生轨迹

```mermaid
timeline
    title 人生轨迹
    section 幼年期
        启蒙教育 : 展现早慧
        特殊天赋 : 初显才能
    section 青年期
        专业训练 : 能力提升
        重要抉择 : 人生转折
    section 中年期
        事业高峰 : 成就卓著
        人际网络 : 广结善缘
    section 晚年期
        经验传承 : 培养后辈
        圆满人生 : 功成名就
```

<details>
<summary>人生轨迹详情（点击展开）</summary>
<table>
  <tr>
    <th colspan="2">幼年期</th>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;'>启蒙教育</td>
    <td>在{world_regions.split(',')[0] if ',' in world_regions else world_regions}接受启蒙教育，展现出早慧</td>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;'>特殊天赋</td>
    <td>初显对{world_energy.split(',')[0] if ',' in world_energy else world_energy}的天赋</td>
  </tr>
  <tr>
    <th colspan="2">青年期</th>
  </tr>
  <tr>
    <td style='background-color:#e6e6ff;'>专业训练</td>
    <td>接受专业训练，能力得到显著提升</td>
  </tr>
  <tr>
    <td style='background-color:#e6e6ff;'>重要抉择</td>
    <td>面临人生重要抉择，决定未来发展方向</td>
  </tr>
  <tr>
    <th colspan="2">中年期</th>
  </tr>
  <tr>
    <td style='background-color:#e6ffe6;'>事业高峰</td>
    <td>在所选领域取得卓越成就</td>
  </tr>
  <tr>
    <td style='background-color:#e6ffe6;'>人际网络</td>
    <td>建立广泛的人际网络，与{world_factions[0].split('（')[0] if world_factions else '当地势力'}建立联系</td>
  </tr>
  <tr>
    <th colspan="2">晚年期</th>
  </tr>
  <tr>
    <td style='background-color:#ffe6ff;'>经验传承</td>
    <td>将积累的经验和知识传授给后辈</td>
  </tr>
  <tr>
    <td style='background-color:#ffe6ff;'>圆满人生</td>
    <td>回顾一生，感到满足和成就</td>
  </tr>
</table>
</details>

{name}的人生轨迹展现了一个不断成长和发展的过程。在幼年期就展现出早慧和特殊天赋，青年期通过专业训练提升能力并做出重要抉择，中年期达到事业高峰并建立广泛的人际网络，晚年致力于经验传承和圆满人生。

### 与世界的互动

```mermaid
flowchart TD
    A[{name}] --> B[与{world_regions.split(',')[0] if ',' in world_regions else world_regions}的联系]
    A --> C[对{world_energy.split(',')[0] if ',' in world_energy else '能量体系'}的理解]
    A --> D[与{world_factions[0].split('（')[0] if world_factions else '当地势力'}的关系]
    B --> E[地域影响]
    C --> F[能力发展]
    D --> G[社会定位]
    style A fill:#f96,stroke:#333,stroke-width:2px
    style B fill:#9cf,stroke:#333,stroke-width:2px
    style C fill:#9cf,stroke:#333,stroke-width:2px
    style D fill:#9cf,stroke:#333,stroke-width:2px
```

<details>
<summary>与世界互动详情（点击展开）</summary>
<table>
  <tr>
    <th>关系类型</th>
    <th>描述</th>
    <th>影响</th>
  </tr>
  <tr>
    <td style='background-color:#f9f9ff;'>与{world_regions.split(',')[0] if ',' in world_regions else world_regions}的联系</td>
    <td>生活在该地区，熟悉当地环境和文化</td>
    <td>地域特色影响了性格和生活方式</td>
  </tr>
  <tr>
    <td style='background-color:#e6e6ff;'>对{world_energy.split(',')[0] if ',' in world_energy else '能量体系'}的理解</td>
    <td>具备该能量体系的基本知识和运用能力</td>
    <td>影响个人能力的发展方向和特长</td>
  </tr>
  <tr>
    <td style='background-color:#e6ffe6;'>与{world_factions[0].split('（')[0] if world_factions else '当地势力'}的关系</td>
    <td>与该势力有一定联系和互动</td>
    <td>影响社会定位和人际关系网络</td>
  </tr>
</table>
</details>

在{era}纪元的{world_regions}背景下，{name}能够很好地适应和影响周围的环境。{name}对{world_energy.split(',')[0] if ',' in world_energy else world_energy}能量有着独特的理解和运用能力，这使{name}在这个世界中能够发挥出独特的作用。

{name}与{world_factions[0].split('（')[0] if world_factions else '当地势力'}有着密切的联系，通过自己的能力和智慧，在复杂的世界格局中找到了自己的位置。

### 未来发展

{name}的未来发展充满潜力。随着时间推移，{name}的天赋将得到更充分的发挥，尤其是在{world_regions.split(',')[0] if ',' in world_regions else world_regions}地区的特殊环境下。建议{name}注重培养自身优势，同时关注弱项的提升，以实现更全面的发展。

注意：由于发生错误，此描述是自动生成的默认内容。
"""
                print("使用默认角色描述")
            
            return description
            
        except Exception as e:
            print(f"生成角色描述时发生错误: {str(e)}")
            print(f"错误类型: {type(e)}")
            print(f"错误详情: {e.__dict__ if hasattr(e, '__dict__') else '无详细信息'}")
            
            # 生成一个默认的角色描述
            try:
                # 创建一个默认的世界数据
                default_world_data = {
                    "id": world_id,
                    "era": character_data.get('basic', {}).get('era', '未知')
                }
                return self._generate_default_character_description(character_data, default_world_data)
            except Exception as inner_e:
                print(f"生成默认角色描述时发生错误: {str(inner_e)}")
                # 返回一个非常简单的错误信息
                char_name = character_data.get('basic', {}).get('name', '未知角色')
                return f"# 角色：{char_name}\n\n由于发生错误，无法生成完整的角色描述。错误信息: {str(e)}"

    def generate_text(self, prompt: str) -> str:
        """使用 DeepSeek API 生成文本。
        
        Args:
            prompt: 提示词
            
        Returns:
            str: 生成的文本
        """
        if not self.deepseek_client:
            print("Warning: DeepSeek API 未配置，将返回默认文本")
            return "由于 DeepSeek API 未配置，无法生成详细描述。"
            
        try:
            print(f"TextManager 开始调用 DeepSeekClient 的 generate_text 方法")
            print(f"DeepSeekClient 类型: {type(self.deepseek_client)}")
            print(f"提示词长度: {len(prompt)}")
            
            # 检查 DeepSeekClient 是否有 generate_text 方法
            if hasattr(self.deepseek_client, 'generate_text'):
                print("DeepSeekClient 有 generate_text 方法")
                result = self.deepseek_client.generate_text(prompt)
                print(f"生成文本成功，长度: {len(result)}")
                return result
            else:
                print("错误: DeepSeekClient 没有 generate_text 方法")
                print(f"可用方法: {dir(self.deepseek_client)}")
                return "DeepSeek API 客户端配置错误，无法生成文本。"
                
        except Exception as e:
            print(f"Warning: 使用 DeepSeek API 生成文本时出错: {e}")
            print(f"错误类型: {type(e)}")
            print(f"错误详情: {e.__dict__ if hasattr(e, '__dict__') else '无详细信息'}")
            return f"生成文本时发生错误: {str(e)}，请检查 API 配置。" 

    def _generate_default_character_description(self, character_data: Dict[str, Any], world_data: Dict[str, Any]) -> str:
        """生成默认的角色描述。
        
        Args:
            character_data: 角色数据
            world_data: 世界数据
            
        Returns:
            str: Markdown格式的角色描述
        """
        try:
            print("\n=== 生成默认角色描述 ===")
            
            # 提取基本信息
            char_name = character_data.get('basic', {}).get('name', '未知角色')
            char_gender = character_data.get('basic', {}).get('gender', 'male')
            char_era = character_data.get('basic', {}).get('era', 'modern')
            birth_datetime = character_data.get('basic', {}).get('birth_datetime', '未知时间')
            
            # 提取八字信息（如果有）
            bazi_info = character_data.get('bazi', {})
            pillars = bazi_info.get('pillars', {})
            year_pillar = pillars.get('year', '未知')
            month_pillar = pillars.get('month', '未知')
            day_pillar = pillars.get('day', '未知')
            hour_pillar = pillars.get('hour', '未知')
            
            # 提取世界信息
            world_id = world_data.get('id', '未知世界')
            world_era = world_data.get('era', char_era)
            
            # 根据纪元设置不同的描述风格
            era_titles = {
                'ancient': '修真',
                'modern': '现代',
                'future': '未来'
            }
            era_title = era_titles.get(char_era, '未知')
            
            # 生成默认描述
            description = f"""# 「{era_title}」角色：{char_name}

## 基本信息

- **姓名**：{char_name}
- **性别**：{'男' if char_gender == 'male' else '女'}
- **所属纪元**：{era_title}
- **出生时间**：{birth_datetime}
- **所属世界**：{world_id}

## 命盘解析

四柱：{year_pillar} {month_pillar} {day_pillar} {hour_pillar}

## 能力特点

```mermaid
pie
    title 能力分布
    "领导力" : 30
    "创造力" : 25
    "分析能力" : 20
    "执行力" : 15
    "适应力" : 10
```

{char_name}的能力分布显示，领导力和创造力是其最突出的优势，分析能力也相当出色。

## 人生轨迹

```mermaid
timeline
    title 人生轨迹
    section 幼年期
        启蒙教育 : 展现早慧
        特殊天赋 : 初显才能
    section 青年期
        专业训练 : 能力提升
        重要抉择 : 人生转折
    section 中年期
        事业高峰 : 成就卓著
        人际网络 : 广结善缘
    section 晚年期
        经验传承 : 培养后辈
        圆满人生 : 功成名就
```

## 与世界的互动

在{era_title}纪元的背景下，{char_name}能够很好地适应和影响周围的环境。{char_name}具有独特的理解和能力，这使{char_name}在这个世界中能够发挥出独特的作用。

## 未来发展

{char_name}的未来发展充满潜力。随着时间推移，{char_name}的天赋将得到更充分的发挥。建议{char_name}注重培养自身优势，同时关注弱项的提升，以实现更全面的发展。

> 注：此描述为系统自动生成的默认内容，由于无法获取完整的世界数据，仅提供基本框架。
"""
            
            return description
            
        except Exception as e:
            print(f"生成默认角色描述时发生错误: {str(e)}")
            print(f"错误类型: {type(e)}")
            
            # 返回一个非常简单的描述
            char_name = character_data.get('basic', {}).get('name', '未知角色')
            return f"# 角色：{char_name}\n\n由于发生错误，无法生成完整的角色描述。"