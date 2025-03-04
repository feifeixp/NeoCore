import numpy as np
import json
import networkx as nx
from collections import deque
from copy import deepcopy
from scipy import ndimage

class WorldGenerator:
    def __init__(self, config_path, width=64, height=64):
        self.load_config(config_path)
        self.width = width
        self.height = height
        self.initialize_world()
      
    def load_config(self, config_path):
        """加载增强版配置文件"""
        with open(config_path) as f:
            self.config = json.load(f)
        self.tiles = {t['name']: t for t in self.config['tiles']}
        self.symbol_map = {t['name']: t['symbol'] for t in self.config['tiles']}

    def initialize_world(self):
        """初始化世界参数"""
        self.elevation = np.zeros((self.height, self.width))
        self.temperature = np.zeros((self.height, self.width))
        self.humidity = np.zeros((self.height, self.width))
        self.terrain = np.full((self.height, self.width), 'ocean', dtype=object)
        self.rivers = []

    def generate_continent(self):
        """生成大陆核心"""
        # 使用Perlin噪声生成基础地形
        x = np.linspace(0, 5, self.width)
        y = np.linspace(0, 5, self.height)
        xv, yv = np.meshgrid(x, y)
        self.elevation = np.sin(xv)*np.cos(yv) + 0.5*np.sin(2.3*xv)*np.cos(3.7*yv)
      
        # 应用大陆形状规则
        core_size = self.config['global_rules']['continent_shape']['core']['size']
        center = (self.height//2, self.width//2)
        self.elevation = ndimage.gaussian_filter(self.elevation, sigma=core_size)
      
    def calculate_climate(self):
        """计算气候参数"""
        # 温度随海拔变化
        self.temperature = 30 - 0.6*self.elevation*1000/100  # 每升高100米降0.6℃
      
        # 湿度计算
        distance_to_sea = ndimage.distance_transform_edt(self.terrain != 'water')
        self.humidity = np.clip(0.3 + 0.7*np.exp(-distance_to_sea/20), 0, 1)

    def apply_terrain_rules(self):
        """应用地形生成规则"""
        wfc = TerrainWFC(self.config, self.width, self.height)
        wfc.elevation = self.elevation
        wfc.temperature = self.temperature
        wfc.humidity = self.humidity
        self.terrain = wfc.generate()

    def generate_rivers(self):
        """生成河流系统"""
        river_gen = RiverGenerator(self.elevation, self.terrain)
        self.rivers = river_gen.generate_rivers(
            min_length=5,
            water_source='mountain',
            destination='water'
        )

    def add_civilizations(self):
        """添加文明遗迹"""
        city_placer = CivilizationPlacer(self.config, self.terrain)
        self.terrain = city_placer.place_cities()

    def generate_full_world(self):
        """完整生成流程"""
        self.generate_continent()
        self.calculate_climate()
        self.apply_terrain_rules()
        self.generate_rivers()
        self.add_civilizations()
        return self

class TerrainWFC:
    def __init__(self, config, width, height):
        self.config = config
        self.width = width
        self.height = height
        self.grid = np.empty((height, width), dtype=object)
        self.propagate_queue = deque()
        self.backtrack_limit = 3
        
        # Initialize tiles from config
        self.tiles = {t['name']: t for t in self.config['tiles']}
      
        for y in range(height):
            for x in range(width):
                self.grid[y][x] = {
                    'possible': list(self.tiles.keys()),
                    'collapsed': False
                }

    def apply_dynamic_rules(self, x, y):
        """应用动态地形规则"""
        cell = self.grid[y][x]
        elevation = self.elevation[y][x]
        temp = self.temperature[y][x]
        humidity = self.humidity[y][x]

        new_possible = []
        for tile in cell['possible']:
            tile_cfg = self.tiles[tile]
          
            # 检查海拔限制
            if not (tile_cfg['elevation']['min'] <= elevation <= tile_cfg['elevation']['max']):
                continue
              
            # 检查气候限制
            if not (tile_cfg['temperature']['min'] <= temp <= tile_cfg['temperature']['max']):
                continue
              
            # 检查特殊条件
            if self.check_conditional_rules(x, y, tile_cfg):
                new_possible.append(tile)
              
        cell['possible'] = new_possible

    def check_conditional_rules(self, x, y, tile_cfg):
        """检查额外约束条件"""
        for rule in tile_cfg.get('conditional_rules', []):
            if rule['type'] == 'adjacent':
                required = rule['required']
                if not self.check_adjacent(x, y, required):
                    return False
        return True

    def check_adjacent(self, x, y, requirements):
        """检查相邻区域条件"""
        count = 0
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<self.width and 0<=ny<self.height:
                if self.terrain[ny][nx] in requirements:
                    count +=1
        return count >= requirements.get('min_count', 1)

    def get_min_entropy_cell(self):
        """找到熵最小的未坍缩单元格"""
        min_entropy = float('inf')
        min_cell = None
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if not cell['collapsed']:
                    entropy = len(cell['possible'])
                    if entropy < min_entropy and entropy > 0:
                        min_entropy = entropy
                        min_cell = (x, y)
        return min_cell

    def collapse_cell(self, x, y):
        """坍缩一个单元格到特定状态"""
        cell = self.grid[y][x]
        if not cell['possible']:
            return False
        
        # 根据地形规则选择可能的地形
        weights = []
        for tile in cell['possible']:
            tile_cfg = self.tiles[tile]
            weight = 1.0
            
            # 考虑海拔因素
            if hasattr(self, 'elevation'):
                elev = self.elevation[y][x]
                if 'elevation' in tile_cfg:
                    if elev < tile_cfg['elevation']['min'] or elev > tile_cfg['elevation']['max']:
                        weight *= 0.1
            
            # 考虑温度因素
            if hasattr(self, 'temperature'):
                temp = self.temperature[y][x]
                if 'temperature' in tile_cfg:
                    if temp < tile_cfg['temperature']['min'] or temp > tile_cfg['temperature']['max']:
                        weight *= 0.1
            
            weights.append(weight)
        
        # 归一化权重
        total_weight = sum(weights)
        if total_weight == 0:
            return False
        weights = [w/total_weight for w in weights]
        
        # 随机选择地形
        chosen = np.random.choice(cell['possible'], p=weights)
        cell['possible'] = [chosen]
        cell['collapsed'] = True
        
        # 将相邻单元格加入传播队列
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                self.propagate_queue.append((nx, ny))
        
        return True

    def propagate(self):
        """传播约束"""
        while self.propagate_queue:
            x, y = self.propagate_queue.popleft()
            cell = self.grid[y][x]
            if cell['collapsed']:
                continue
            
            # 收集相邻单元格的约束
            valid_tiles = set(cell['possible'])
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbor = self.grid[ny][nx]
                    if neighbor['collapsed']:
                        neighbor_tile = neighbor['possible'][0]
                        # 检查相邻规则
                        for tile in list(valid_tiles):
                            if tile in self.tiles and 'conditional_rules' in self.tiles[tile]:
                                for rule in self.tiles[tile]['conditional_rules']:
                                    if rule['type'] == 'adjacent':
                                        if neighbor_tile not in rule['required']:
                                            valid_tiles.discard(tile)
            
            # 更新可能的地形
            old_possible = set(cell['possible'])
            cell['possible'] = list(valid_tiles)
            
            # 如果可能性发生变化，将相邻单元格加入队列
            if old_possible != valid_tiles:
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.propagate_queue.append((nx, ny))

    def generate(self):
        """生成地形"""
        backtrack_count = 0
        terrain = np.empty((self.height, self.width), dtype=object)
        
        while True:
            # 找到熵最小的单元格
            cell_pos = self.get_min_entropy_cell()
            if not cell_pos:
                break
                
            x, y = cell_pos
            success = self.collapse_cell(x, y)
            
            if not success:
                # 回溯
                backtrack_count += 1
                if backtrack_count > self.backtrack_limit:
                    print("Warning: Reached backtrack limit, resetting generation...")
                    self.__init__(self.config, self.width, self.height)
                    backtrack_count = 0
                continue
                
            self.propagate()
        
        # 构建最终地形
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell['collapsed'] and cell['possible']:
                    terrain[y][x] = cell['possible'][0]
                else:
                    terrain[y][x] = 'grass'  # 默认地形
        
        return terrain

class RiverGenerator:
    def __init__(self, elevation, terrain):
        self.elevation = elevation
        self.terrain = terrain
        self.graph = nx.DiGraph()

    def find_sources(self, terrain_type):
        """寻找水源点"""
        sources = []
        for y in range(self.terrain.shape[0]):
            for x in range(self.terrain.shape[1]):
                if self.terrain[y][x] == terrain_type:
                    sources.append((x, y))
        return sources

    def get_downhill_neighbors(self, pos):
        """获取低于当前位置的相邻点"""
        x, y = pos
        neighbors = []
        current_elev = self.elevation[y][x]
        
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.terrain.shape[1] and 0 <= ny < self.terrain.shape[0]:
                if self.elevation[ny][nx] < current_elev:
                    neighbors.append((nx, ny))
        return neighbors

    def generate_rivers(self, min_length=5, water_source='mountain', destination='water'):
        """生成河流系统"""
        sources = self.find_sources(water_source)
        rivers = []
        
        # 随机选择一些水源点
        np.random.shuffle(sources)
        selected_sources = sources[:min(len(sources), 5)]  # 最多选择5个水源点
        
        for source in selected_sources:
            path = self.find_river_path(source, destination)
            if len(path) >= min_length:
                rivers.append(path)
                self.apply_river_erosion(path)
        
        return rivers

    def find_river_path(self, start, destination_type):
        """寻找河流路径"""
        path = [start]
        current = start
        visited = set([start])
        
        while True:
            neighbors = self.get_downhill_neighbors(current)
            # 过滤已访问的点
            neighbors = [n for n in neighbors if n not in visited]
            
            if not neighbors:
                break
            
            # 选择最低的相邻点
            next_pos = min(neighbors, key=lambda p: self.elevation[p[1]][p[0]])
            path.append(next_pos)
            visited.add(next_pos)
            current = next_pos
            
            # 如果到达目标类型或形成环路，结束
            if self.terrain[current[1]][current[0]] == destination_type:
                break
        
        return path

    def apply_river_erosion(self, path):
        """应用河流侵蚀效果"""
        for x, y in path:
            # 降低河床高度
            self.elevation[y][x] *= 0.9
            # 标记为河流
            self.terrain[y][x] = 'river'
            
            # 侵蚀河岸
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.terrain.shape[1] and 0 <= ny < self.terrain.shape[0]:
                    self.elevation[ny][nx] *= 0.95

class CivilizationPlacer:
    def __init__(self, config, terrain):
        self.config = config
        self.terrain = terrain
        self.city_rules = config['civilization_rules']

    def check_resources(self, x, y):
        """检查位置周围是否有所需资源"""
        required_resources = self.city_rules['required_resources']
        search_radius = 3  # 搜索半径
        
        for resource in required_resources:
            found = False
            for dx in range(-search_radius, search_radius + 1):
                for dy in range(-search_radius, search_radius + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.terrain.shape[1] and 0 <= ny < self.terrain.shape[0]:
                        if self.terrain[ny][nx] == resource:
                            found = True
                            break
                if found:
                    break
            if not found:
                return False
        return True

    def check_distance_to_other_cities(self, x, y, placed_cities):
        """检查与其他城市的距离"""
        min_distance = self.city_rules['min_distance']
        
        for cx, cy in placed_cities:
            distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if distance < min_distance:
                return False
        return True

    def find_city_candidates(self):
        """寻找适合建城的位置"""
        candidates = []
        for y in range(self.terrain.shape[0]):
            for x in range(self.terrain.shape[1]):
                if self.terrain[y][x] == 'grass':  # 只在平原上建城
                    if self.check_resources(x, y):
                        candidates.append((x, y))
        return candidates

    def place_cities(self):
        """放置古代城市遗迹"""
        candidates = self.find_city_candidates()
        placed_cities = []
        
        # 随机打乱候选位置
        np.random.shuffle(candidates)
        
        # 尝试放置城市
        for candidate in candidates:
            x, y = candidate
            if self.check_distance_to_other_cities(x, y, placed_cities):
                self.terrain[y][x] = 'ancient_city'
                placed_cities.append((x, y))
                
                # 最多放置3个城市
                if len(placed_cities) >= 3:
                    break
        
        return self.terrain

def print_world(world, symbols):
    """增强版可视化输出"""
    border = "+" + "---" * world.shape[1] + "+"
    print(border)
    for row in world:
        print("|" + "".join(symbols.get(cell, "?") for cell in row) + "|")
    print(border)

# 示例配置文件（world_config.json）
"""
{
    "tiles": [
        {
            "name": "grass",
            "symbol": "🟩",
            "elevation": {"min": 0, "max": 0.3},
            "temperature": {"min": 10, "max": 35},
            "conditional_rules": [
                {"type": "adjacent", "required": ["water"], "min_count": 1}
            ]
        },
        {
            "name": "mountain",
            "symbol": "⛰️",
            "elevation": {"min": 0.3, "max": 1.0}
        },
        {
            "name": "river",
            "symbol": "🌊",
            "elevation": {"min": -0.2, "max": 0.5}
        },
        {
            "name": "ancient_city",
            "symbol": "🏛️",
            "placement_rules": {
                "required_adjacent": ["grass", "mountain"],
                "exclusion": ["swamp", 5]
            }
        }
    ],
    "civilization_rules": {
        "min_distance": 8,
        "required_resources": ["water", "stone"]
    },
    "global_rules": {
        "continent_shape": {
            "core_size": 5,
            "ring_layers": 3
        }
    }
}
"""

if __name__ == "__main__":
    generator = WorldGenerator("world_config.json", width=32, height=32)
    world = generator.generate_full_world()
    print_world(world.terrain, generator.symbol_map)