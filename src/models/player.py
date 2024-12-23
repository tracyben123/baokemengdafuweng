from models.pokemon import Pokemon
import random

class Player:
    def __init__(self, name):
        self.name = name
        self.game_loop = None  # 添加 game_loop 引用
        # 随机初始位置
        self.position = 0
        self.target_position = 0  # 目标位置
        self.steps_remaining = 0  # 剩余步数
        self.is_moving = False    # 是否正在移动
        self.move_speed = 0.3     # 每步移动时间（秒）
        self.move_timer = 0       # 移动计时器
        self.current_ring = "outer"
        self.coins = 1000  # 初始金币
        self.pokemons = []  # 宝可梦列表
        self.items = []    # 道具列表
        self.badges = []   # 徽章列表
        self.waiting_turns = 0  # 等待回合数，用于道馆失败等情况
        self.selected_pokemon_index = None  # 添加选中的宝可梦索引
        
        # 添加棋盘大小属性
        self.board_size = {
            "outer": 32,  # 外圈32格
            "inner": 24   # 内圈24格
        }
        
        # 添加初始宝可梦
        self.add_starter_pokemon()
        
        # 添加初始道具
        self.add_starter_items()
        
    def add_starter_pokemon(self):
        """添加初始宝可梦"""
        # 可选的属性
        types = ["NORMAL", "FIRE", "WATER", "GRASS", "ELECTRIC"]
        # 随机选择一个属性
        pokemon_type = random.choice(types)
        
        # 根据属性选择名字
        names = {
            "NORMAL": "小拉达",
            "FIRE": "小火龙",
            "WATER": "杰尼龟",
            "GRASS": "妙蛙种子",
            "ELECTRIC": "皮卡丘"
        }
        
        # 创建初始宝可梦
        starter = Pokemon(
            name=names[pokemon_type],
            type=pokemon_type,
            level=1,  # 初始级为1
            moves=[
                ("撞击", "NORMAL", 40, 35),  # 基础技能
                (self._get_type_move(pokemon_type), pokemon_type, 40, 25)  # 属性技能
            ]
        )
        self.pokemons.append(starter)
        
    def _get_type_move(self, pokemon_type):
        """获取对应属性的基础技能"""
        moves = {
            "NORMAL": "电光一闪",
            "FIRE": "火花",
            "WATER": "水枪",
            "GRASS": "藤鞭",
            "ELECTRIC": "电击"
        }
        return moves[pokemon_type]
        
    def start_move(self, steps):
        """开始移动"""
        self.target_steps = steps
        self.steps_moved = 0
        self.move_timer = 0
        self.is_moving = True
        print(f"[DEBUG] 开始移动，目标步数: {steps}")
        
    def update_movement(self, delta_time):
        """更新移动状态"""
        if not self.is_moving:
            return False
            
        # 累加时间
        self.move_timer += delta_time
        
        # 检查是否到达移动时间
        if self.move_timer >= self.move_speed:
            self.move_timer = 0  # 重置计时器
            
            # 移动一步
            if self.steps_moved < self.target_steps:
                current_size = self.board_size[self.current_ring]
                self.position = (self.position + 1) % current_size
                self.steps_moved += 1
                print(f"[DEBUG] 移动第{self.steps_moved}步，当前位置: {self.position}，当前环: {self.current_ring}")
                
                # 检查是否达到目标步数
                if self.steps_moved >= self.target_steps:
                    self.is_moving = False
                    print(f"[DEBUG] 移动完成，总共移动{self.steps_moved}步")
                    return False
                    
        return True
        
    def add_coins(self, amount):
        """增加金币"""
        self.coins += amount
        
    def spend_coins(self, amount):
        """花费金币"""
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
        
    def add_pokemon(self, pokemon):
        """添加宝可梦"""
        self.pokemons.append(pokemon)
        
    def remove_pokemon(self, index):
        """移除宝可梦"""
        if 0 <= index < len(self.pokemons):
            return self.pokemons.pop(index)
        return None
        
    def add_item(self, item):
        """添加道具"""
        self.items.append(item)
        
    def use_item(self, item_index, target):
        """使用道具"""
        if 0 <= item_index < len(self.items):
            item = self.items[item_index]
            success = item.use(target)
            if success:
                print(f"[DEBUG] 使用{item.name}成功")
                self.items.pop(item_index)
                if self.game_loop and hasattr(self.game_loop, 'last_message'):  # 添加 game_loop 检查
                    self.game_loop.last_message = f"使用{item.name}成功"
                    self.game_loop.message_display_time = 0
            return success
        return False
        
    def update_turn(self):
        """更新回合状态"""
        if self.waiting_turns > 0:
            self.waiting_turns -= 1
        
    def add_starter_items(self):
        """添加初始道具"""
        from src.models.item import Item
        
        # 添加初始恢复道具
        starter_items = [
            ("伤药", "HEAL", 50),         # 恢复50HP
            ("伤药", "HEAL", 50),         # 再来一个伤药
            ("PP恢复剂", "PP", 10),       # 恢复技能PP值
            ("全体恢复药", "HEAL_ALL", 100)  # 完全恢复
        ]
        
        for name, effect_type, effect_value in starter_items:
            item = Item(
                name=name,
                price=0,  # 初始道具不设置价格
                effect_type=effect_type,
                effect_value=effect_value
            )
            self.items.append(item)
        
    def select_pokemon(self, index):
        """选择宝可梦"""
        if 0 <= index < len(self.pokemons):
            if self.selected_pokemon_index == index:
                # 再次点击取消选择
                self.selected_pokemon_index = None
            elif self.selected_pokemon_index is not None:
                # 如果已经选中了一个宝可梦，则交换位置
                self.swap_pokemon(self.selected_pokemon_index, index)
                self.selected_pokemon_index = None
            else:
                # 选中宝可梦
                self.selected_pokemon_index = index
                
    def swap_pokemon(self, index1, index2):
        """交换两个宝可梦的位置"""
        if (0 <= index1 < len(self.pokemons) and 
            0 <= index2 < len(self.pokemons)):
            self.pokemons[index1], self.pokemons[index2] = \
                self.pokemons[index2], self.pokemons[index1]