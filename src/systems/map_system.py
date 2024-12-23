import random
from enum import Enum

class TileType(Enum):
    NORMAL = "NORMAL"
    POKEMON_CENTER = "POKEMON_CENTER"
    SHOP = "SHOP"
    WILD = "WILD"
    GYM = "GYM"
    PORTAL = "PORTAL"

class Tile:
    def __init__(self, type=TileType.NORMAL, gym_type=None):
        self.type = type
        self.gym_type = gym_type  # 道馆类型（只有道馆格子才有）

class MapSystem:
    # 棋盘布局常量
    BOARD_LEFT = 300     # 左边界保持不变
    BOARD_TOP = 100      # 上边界保持不变
    BOARD_WIDTH = 655    # 总宽度再减小10（665 -> 655）
    BOARD_HEIGHT = 410   # 总高度保持不变
    TILE_SIZE = 40       # 格子大小保持不变
    
    # 外环和内环的间距
    OUTER_SPACING = 20   # 外环格子间距
    INNER_SPACING = 15   # 内环格子间距
    
    # 内圈布局常量（保持不变）
    INNER_LEFT = 405     # 内圈左边界
    INNER_TOP = 170      # 内圈上边界
    INNER_WIDTH = 480    # 内圈宽度
    INNER_HEIGHT = 275   # 内圈高度
    
    # 每边格子数量（长方形布局）
    OUTER_HORIZONTAL = 10  # 外环水平边格子数
    OUTER_VERTICAL = 6    # 外环垂直边格子数
    INNER_HORIZONTAL = 8  # 内环水平边格子数
    INNER_VERTICAL = 4    # 内环垂直边格子数
    
    def __init__(self):
        # 外圈32格
        self.outer_ring = self._generate_ring(32, is_outer=True)
        # 内圈24格
        self.inner_ring = self._generate_ring(24, is_outer=False)
        
    def _generate_ring(self, size, is_outer=True):
        """生成一个环的格子"""
        tiles = []
        
        if is_outer:
            # 外环特殊格子数量
            special_tiles = {
                TileType.POKEMON_CENTER: 4,  # 4个宝可梦中心
                TileType.SHOP: 4,           # 4个商店
                TileType.WILD: 8,           # 减少野战格子数量（从12改为8）
                TileType.GYM: 4,            # 4个道馆
                TileType.PORTAL: 2,         # 2个传送门
            }
        else:
            # 内环特殊格子数量
            special_tiles = {
                TileType.POKEMON_CENTER: 1,  # 1个宝可梦中心
                TileType.SHOP: 1,           # 1个商店
                TileType.WILD: 16,          # 减少野战格子数量（从20改为16）
                TileType.GYM: 1,            # 1个道馆
                TileType.PORTAL: 1,         # 1个传送点
            }
        
        # 可用的道馆类型
        gym_types = ["FIRE", "WATER", "GRASS", "ELECTRIC"]
        
        # 先填充所有格子为普通格子
        tiles = [Tile(TileType.NORMAL) for _ in range(size)]
        
        # 随机放置特殊格子
        available_positions = list(range(size))
        for tile_type, count in special_tiles.items():
            positions = random.sample(available_positions, count)
            for pos in positions:
                # 如果是道馆格子，随机分配一个道馆类型
                if tile_type == TileType.GYM:
                    gym_type = random.choice(gym_types)
                    tiles[pos] = Tile(tile_type, gym_type)
                else:
                    tiles[pos] = Tile(tile_type)
                available_positions.remove(pos)
                
        return tiles
        
    def get_tile(self, position, ring):
        """获取指定位置的格子"""
        ring_tiles = self.outer_ring if ring == "outer" else self.inner_ring
        return ring_tiles[position % len(ring_tiles)]
        
    def get_random_start_position(self):
        """获取随机起始位置"""
        ring = random.choice(["outer", "inner"])
        position = random.randint(0, 31)
        return position, ring
        
    def get_tile_position(self, index, ring_type):
        """计算格子的实际显示位置"""
        if ring_type == "outer":
            return self._get_outer_ring_position(index)
        else:
            return self._get_inner_ring_position(index)
            
    def _get_outer_ring_position(self, index):
        """计算外圈格子位置"""
        total = 2 * (self.OUTER_HORIZONTAL + self.OUTER_VERTICAL)  # 32格
        
        # 上边（从左到右）
        if index < self.OUTER_HORIZONTAL:
            x = self.BOARD_LEFT + index * (self.TILE_SIZE + self.OUTER_SPACING)
            y = self.BOARD_TOP
            
        # 右边（从上到下）
        elif index < self.OUTER_HORIZONTAL + self.OUTER_VERTICAL:
            x = self.BOARD_LEFT + self.BOARD_WIDTH - self.TILE_SIZE
            y = self.BOARD_TOP + (index - self.OUTER_HORIZONTAL) * (self.TILE_SIZE + self.OUTER_SPACING)
            
        # 下边（从右到左）
        elif index < 2 * self.OUTER_HORIZONTAL + self.OUTER_VERTICAL:
            x = self.BOARD_LEFT + self.BOARD_WIDTH - ((index - (self.OUTER_HORIZONTAL + self.OUTER_VERTICAL) + 1) * (self.TILE_SIZE + self.OUTER_SPACING))
            y = self.BOARD_TOP + self.BOARD_HEIGHT - self.TILE_SIZE
            
        # 左边（从下到上）
        else:
            x = self.BOARD_LEFT
            y = self.BOARD_TOP + self.BOARD_HEIGHT - ((index - (2 * self.OUTER_HORIZONTAL + self.OUTER_VERTICAL) + 1) * (self.TILE_SIZE + self.OUTER_SPACING))
            
        return x, y
        
    def _get_inner_ring_position(self, index):
        """计算内圈格子位置"""
        total = 2 * (self.INNER_HORIZONTAL + self.INNER_VERTICAL)  # 24格
        
        # 上边（从左到右）
        if index < self.INNER_HORIZONTAL:
            x = self.INNER_LEFT + index * (self.TILE_SIZE + self.INNER_SPACING)
            y = self.INNER_TOP
            
        # 右边（从上到下）
        elif index < self.INNER_HORIZONTAL + self.INNER_VERTICAL:
            x = self.INNER_LEFT + self.INNER_WIDTH - self.TILE_SIZE
            y = self.INNER_TOP + (index - self.INNER_HORIZONTAL) * (self.TILE_SIZE + self.INNER_SPACING)
            
        # 下边（从右到左）
        elif index < 2 * self.INNER_HORIZONTAL + self.INNER_VERTICAL:
            x = self.INNER_LEFT + self.INNER_WIDTH - ((index - (self.INNER_HORIZONTAL + self.INNER_VERTICAL) + 1) * (self.TILE_SIZE + self.INNER_SPACING))
            y = self.INNER_TOP + self.INNER_HEIGHT - self.TILE_SIZE
            
        # 左��（从下到上）
        else:
            x = self.INNER_LEFT
            y = self.INNER_TOP + self.INNER_HEIGHT - ((index - (2 * self.INNER_HORIZONTAL + self.INNER_VERTICAL) + 1) * (self.TILE_SIZE + self.INNER_SPACING))
            
        return x, y