from typing import Dict, List, Any
from datetime import datetime
import json

class BaziFormatter:
    """八字分析结果格式化器"""
    
    def format_analysis(self, char_data: dict, world_data: dict) -> str:
        """格式化分析结果为Markdown格式
        
        Args:
            char_data: 角色数据
            world_data: 世界数据
            
        Returns:
            str: 格式化后的分析结果
        """
        try:
            print("\n=== 开始格式化分析结果 ===")
            print(f"角色数据: {json.dumps(char_data, ensure_ascii=False, indent=2)}")
            print(f"世界数据: {json.dumps(world_data, ensure_ascii=False, indent=2)}")
            
            # 获取基本信息
            print("\n[步骤1] 获取基本信息...")
            if 'metadata' not in char_data:
                print("错误：角色数据缺少 metadata 字段")
                print(f"当前角色数据: {json.dumps(char_data, ensure_ascii=False, indent=2)}")
                return "无法生成角色描述：缺少基本信息"
                
            metadata = char_data['metadata']
            print(f"metadata 内容: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
            
            # 检查必要字段
            required_fields = ['name', 'gender', 'birth_datetime', 'era']
            missing_fields = [field for field in required_fields if field not in metadata]
            if missing_fields:
                print(f"错误：metadata 缺少必要字段: {missing_fields}")
                print(f"当前 metadata: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
                return f"无法生成角色描述：缺少必要字段 {', '.join(missing_fields)}"
            
            # 获取八字信息
            print("\n[步骤2] 获取八字信息...")
            if 'bazi' not in char_data:
                print("错误：角色数据缺少 bazi 字段")
                print(f"当前角色数据: {json.dumps(char_data, ensure_ascii=False, indent=2)}")
                return "无法生成角色描述：缺少八字信息"
                
            bazi = char_data['bazi']
            print(f"八字信息: {json.dumps(bazi, ensure_ascii=False, indent=2)}")
            
            # 检查八字必要字段
            required_bazi_fields = ['sizhu', 'year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar', 'wuxing_count', 'day_master', 'pattern']
            missing_bazi_fields = [field for field in required_bazi_fields if field not in bazi]
            if missing_bazi_fields:
                print(f"错误：bazi 缺少必要字段: {missing_bazi_fields}")
                print(f"当前 bazi: {json.dumps(bazi, ensure_ascii=False, indent=2)}")
                return f"无法生成角色描述：八字信息不完整，缺少 {', '.join(missing_bazi_fields)}"
            
            # 获取分析结果
            print("\n[步骤3] 获取分析结果...")
            if 'analysis' not in char_data:
                print("错误：角色数据缺少 analysis 字段")
                print(f"当前角色数据: {json.dumps(char_data, ensure_ascii=False, indent=2)}")
                return "无法生成角色描述：缺少分析结果"
                
            analysis = char_data['analysis']
            print(f"分析结果: {json.dumps(analysis, ensure_ascii=False, indent=2)}")
            
            # 构建描述
            print("\n[步骤4] 开始构建描述...")
            description = []
            
            # 基本信息
            print("\n[步骤4.1] 添加基本信息...")
            description.append(f"# {metadata['name']} 的角色分析")
            description.append(f"\n## 基本信息")
            description.append(f"- 性别：{'男' if metadata['gender'] == 'male' else '女'}")
            description.append(f"- 出生时间：{metadata['birth_datetime']}")
            description.append(f"- 纪元：{metadata['era']}")
            
            # 八字信息 - 只保留基本信息
            print("\n[步骤4.2] 添加八字基本信息...")
            description.append(f"\n## 八字信息")
            description.append(f"- 八字：{bazi['sizhu']}")
            
            # 添加八字结构的表格
            description.append(f"\n### 八字结构")
            description.append(f"<table>")
            description.append(f"  <tr>")
            description.append(f"    <th>年柱</th>")
            description.append(f"    <th>月柱</th>")
            description.append(f"    <th>日柱</th>")
            description.append(f"    <th>时柱</th>")
            description.append(f"  </tr>")
            description.append(f"  <tr>")
            description.append(f"    <td style='background-color:#f9f9ff;text-align:center;font-weight:bold;'>{bazi['year_pillar']}</td>")
            description.append(f"    <td style='background-color:#e6e6ff;text-align:center;font-weight:bold;'>{bazi['month_pillar']}</td>")
            description.append(f"    <td style='background-color:#e6ffe6;text-align:center;font-weight:bold;'>{bazi['day_pillar']}</td>")
            description.append(f"    <td style='background-color:#ffe6ff;text-align:center;font-weight:bold;'>{bazi['hour_pillar']}</td>")
            description.append(f"  </tr>")
            description.append(f"</table>")
            
            # 添加五行分布的Mermaid饼图
            print("\n[步骤4.3] 添加五行分布图...")
            wuxing_count = bazi['wuxing_count']
            description.append(f"\n### 五行分布")
            
            # 计算最大值用于标准化
            max_value = max(wuxing_count.values()) if wuxing_count else 1
            
            # 添加Mermaid饼图
            description.append(f"```mermaid")
            description.append(f"pie")
            description.append(f"    title 五行力量分布")
            
            # 添加五行数据
            for element, count in wuxing_count.items():
                normalized = int(count/max_value * 100)
                description.append(f"    \"{element}\" : {normalized}")
            
            description.append(f"```")
            
            # 添加五行分布的表格作为备用
            description.append(f"\n<details>")
            description.append(f"<summary>五行分布详情（点击展开）</summary>")
            description.append(f"<table>")
            description.append(f"  <tr>")
            for element in ['金', '木', '水', '火', '土']:
                if element in wuxing_count:
                    description.append(f"    <th>{element}</th>")
            description.append(f"  </tr>")
            description.append(f"  <tr>")
            for element in ['金', '木', '水', '火', '土']:
                if element in wuxing_count:
                    count = wuxing_count[element]
                    normalized = int(count/max_value * 100)
                    # 根据五行设置不同的颜色
                    color = "#FFD700" if element == '金' else "#90EE90" if element == '木' else "#87CEFA" if element == '水' else "#FF6347" if element == '火' else "#D2B48C"
                    description.append(f"    <td style='background-color:{color};text-align:center;'>{count} ({normalized}%)</td>")
            description.append(f"  </tr>")
            description.append(f"</table>")
            description.append(f"</details>")
            
            # 世界背景信息
            print("\n[步骤4.4] 添加世界背景信息...")
            description.append(f"\n## 世界背景")
            description.append(f"{world_data.get('background', '未知世界背景')}")
            
            # 派系信息
            print("\n[步骤4.5] 添加派系信息...")
            if 'factions' in world_data and world_data['factions']:
                description.append(f"\n## 派系信息")
                for faction_id, faction_data in world_data.get('factions', {}).items():
                    faction_name = faction_data.get('name', faction_id)
                    faction_desc = faction_data.get('description', '无描述')
                    description.append(f"### {faction_name}")
                    description.append(f"{faction_desc}")
            
            print("\n[步骤5] 合并描述...")
            result = "\n".join(description)
            print(f"生成的描述长度: {len(result)} 字符")
            print("描述预览:")
            print(result[:200] + "...")
            
            print("\n=== 分析结果格式化完成 ===")
            return result
            
        except Exception as e:
            print(f"\n=== 格式化分析结果时发生错误 ===")
            print(f"错误类型: {type(e)}")
            print(f"错误信息: {str(e)}")
            print(f"错误详情: {e.__dict__ if hasattr(e, '__dict__') else '无详细信息'}")
            print(f"角色数据: {json.dumps(char_data, ensure_ascii=False, indent=2)}")
            print(f"世界数据: {json.dumps(world_data, ensure_ascii=False, indent=2)}")
            return f"生成角色描述时发生错误：{str(e)}"
    
    def _format_header(self, bazi_data: Dict[str, Any]) -> str:
        """格式化文档标题"""
        return f"""# 八字命盘分析报告

## 基本信息

- 日主：{bazi_data["day_master"]}
- 命局：{bazi_data["pattern"]}
- 日主天干：{bazi_data["day_master_element"]}"""

    def _format_bazi_structure(self, bazi_data: Dict[str, Any]) -> str:
        """格式化八字结构图"""
        return f"""## 八字结构

```mermaid
graph TB
    subgraph 年柱
    A[{bazi_data["year_pillar"]}]
    end
    subgraph 月柱
    B[{bazi_data["month_pillar"]}]
    end
    subgraph 日柱
    C[{bazi_data["day_pillar"]}]
    end
    subgraph 时柱
    D[{bazi_data["hour_pillar"]}]
    end
    A --> B --> C --> D
```"""

    def _format_elements_chart(self, elements: Dict[str, float]) -> str:
        """格式化五行分布图"""
        # 计算最大值用于标准化
        max_value = max(elements.values())
        normalized = {k: int(v/max_value * 100) for k, v in elements.items()}
        
        return f"""## 五行分布

```mermaid
pie
    title 五行力量分布
    "金" : {normalized.get("金", 0)}
    "木" : {normalized.get("木", 0)}
    "水" : {normalized.get("水", 0)}
    "火" : {normalized.get("火", 0)}
    "土" : {normalized.get("土", 0)}
```

### 详细数值
| 五行 | 力量值 |
|------|--------|
| 金 | {elements.get("金", 0):.1f} |
| 木 | {elements.get("木", 0):.1f} |
| 水 | {elements.get("水", 0):.1f} |
| 火 | {elements.get("火", 0):.1f} |
| 土 | {elements.get("土", 0):.1f} |"""

    def _format_pattern_analysis(self, bazi_data: Dict[str, Any]) -> str:
        """格式化命局分析"""
        return f"""## 命局分析

### 日主强度
- 数值：{bazi_data["day_master_strength"]:.2f}
- 判定：{bazi_data["pattern"]}

### 格局特点
- 当前格局：{bazi_data["formation"]}
- 特征：{self._get_formation_characteristics(bazi_data["formation"])}"""

    def _format_world_influence(self, world_influence: Dict[str, Any]) -> str:
        """格式化世界影响分析"""
        return f"""## 世界环境影响

### 环境能量分布
```mermaid
graph LR
    subgraph 环境能量
    {self._format_energy_nodes(world_influence["environmental_energy"])}
    end
```

### 稳定性分析
- 等级：{world_influence["stability"]["level"]}
- 分数：{world_influence["stability"]["score"]:.2f}

### 时运影响
- 影响系数：{world_influence["temporal_influence"]:.2f}
- 共振度：{world_influence["resonance"]:.2f}"""

    def _format_faction_analysis(self, faction_analysis: Dict[str, Any]) -> str:
        """格式化势力分析"""
        return f"""## 势力相性分析

### 基础契合度
- 契合度：{faction_analysis["compatibility"]:.2f}

### 发展路径
```mermaid
graph TD
    {self._format_development_paths(faction_analysis["potential"])}
```

### 潜在挑战
| 挑战类型 | 严重程度 |
|----------|----------|
{self._format_challenges(faction_analysis["challenges"])}"""

    def _format_future_events(self, future_events: List[Dict[str, Any]]) -> str:
        """格式化未来事件预测"""
        events_md = "\n".join([
            f"- {event['year']}年：{event['type']} (重要性：{event['significance']}，"
            f"概率：{event['probability']:.2f})"
            for event in future_events
        ])
        
        return f"""## 未来事件预测

```mermaid
timeline
{self._format_timeline_events(future_events)}
```

### 详细预测
{events_md}"""

    def _get_formation_characteristics(self, formation: str) -> str:
        """获取格局特征描述"""
        characteristics = {
            "正印格": "利于学习进取，重视个人修养",
            "偏印格": "思维灵活，创新能力强",
            "正官格": "正统威严，组织能力强",
            "偏官格": "独立自主，决断力强",
            "七杀格": "勇于进取，战斗力强",
            "正财格": "理财有道，稳健发展",
            "偏财格": "创业能力强，善于开拓",
            "食神格": "智慧聪颖，领导能力强",
            "伤官格": "变革创新，突破能力强",
            "比劫格": "自我意识强，独立性强"
        }
        return characteristics.get(formation, "格局特征待分析")

    def _format_energy_nodes(self, energy: Dict[str, float]) -> str:
        """格式化能量节点"""
        nodes = []
        for element, value in energy.items():
            nodes.append(f"{element}[{element}: {value:.2f}]")
        return "\n    ".join(nodes)

    def _format_development_paths(self, paths: List[Dict[str, Any]]) -> str:
        """格式化发展路径"""
        nodes = []
        for i, path in enumerate(paths):
            nodes.append(f"P{i}[{path['path']}\n{path['probability']:.2f}]")
        return "\n    ".join(nodes)

    def _format_challenges(self, challenges: List[Dict[str, Any]]) -> str:
        """格式化挑战列表"""
        return "\n".join([
            f"| {challenge['type']} | {challenge['severity']:.2f} |"
            for challenge in challenges
        ])

    def _format_timeline_events(self, events: List[Dict[str, Any]]) -> str:
        """格式化时间线事件"""
        return "\n".join([
            f"    section {event['year']}年\n"
            f"    {event['type']} : {event['significance']}"
            for event in events
        ]) 