import pygame
from systems.map_system import MapSystem, TileType
from systems.battle_system import BattleSystem
from systems.shop_system import ShopSystem
from systems.gym_system import GymSystem
from systems.wild_pokemon_system import WildPokemonSystem
from systems.pokemon_center_system import PokemonCenterSystem
from systems.player_encounter_system import PlayerEncounterSystem
from systems.save_system import SaveSystem
from systems.sound_system import SoundSystem
from systems.settings_system import SettingsSystem
from systems.tutorial_system import TutorialSystem
from systems.event_system import EventSystem
from systems.skill_system import SkillSystem
from models.player import Player

class GameLoop:
    def __init__(self):
        self.map_system = MapSystem()
        self.battle_system = BattleSystem(self)
        self.shop_system = ShopSystem()
        self.gym_system = GymSystem()
        self.gym_system.game_loop = self
        self.wild_pokemon_system = WildPokemonSystem()
        self.pokemon_center_system = PokemonCenterSystem()
        self.player_encounter_system = PlayerEncounterSystem(self.battle_system)
        self.event_system = EventSystem(self)
        self.players = []
        self.current_player_index = 0
        self.turn_count = 0
        self.game_state = "WAITING_FOR_ROLL"  # 游戏状态机
        self.save_system = SaveSystem()
        self.sound_system = SoundSystem()
        self.settings_system = SettingsSystem()
        self.settings_system.apply_settings(self)
        # 播放主界面BGM
        self.sound_system.play_bgm("main_theme")
        self.tutorial_system = TutorialSystem()
        self.auto_save = True
        self.auto_save_interval = 10
        self.screen = None  # 将由settings_system设置
        self.game_states = [
            "WAITING_FOR_ROLL",  # 等待投骰子
            "ROLLING_DICE",      # 正在投骰子动画
            "MOVING",           # 玩家移动中
            "IN_BATTLE",        # 战斗界面
            "IN_SHOP",          # 商店界面
            "IN_POKEMON_CENTER", # 宝可梦中心
            "IN_TUTORIAL",      # 教程界面
            "IN_BATTLE_ITEM",   # 添加战斗道具界面状态
            "LEARNING_MOVE",    # 添加学习技能界面状态
            "IN_MENU",          # 添加菜单状态
            "GAME_OVER"         # 游戏结束
        ]
        self.skill_system = SkillSystem()
        self.current_learning_pokemon = None
        self.last_time = pygame.time.get_ticks()
        self.dice_animation_frame = 0
        self.dice_result = 0
        self.dice_animation_length = 60  # 从45帧增加到60帧
        self.dice_show_result_time = 120  # 从90帧增加到120帧
        self.dice_total_frames = self.dice_animation_length + self.dice_show_result_time
        self.last_message = None  # 添加这行
        self.message_display_time = 0  # 添加这行
        
        # 确保所有系统都有对 game_loop 的引用
        self.shop_system.game_loop = self
        self.wild_pokemon_system.game_loop = self
        self.pokemon_center_system.game_loop = self
        self.tutorial_system.game_loop = self
        self.skill_system.game_loop = self
        
    def add_player(self, player):
        if len(self.players) < 2:
            self.players.append(player)
            return True
        return False
        
    def roll_dice(self):
        """投骰子"""
        print(f"[DEBUG] 当前游戏状态: {self.game_state}")
        print(f"[DEBUG] 当前玩家: {self.players[self.current_player_index].name}")
        
        # 检查游戏状态和玩家
        if self.game_state != "WAITING_FOR_ROLL" or not self.players:
            print(f"[DEBUG] 无法投骰子: 游戏状态={self.game_state}, 玩家数={len(self.players)}")
            return False
            
        # 开始骰子动画
        self.dice_animation_frame = 0
        from random import randint
        self.dice_result = randint(1, 6)
        print(f"[DEBUG] 投出点数: {self.dice_result}")
        self.game_state = "ROLLING_DICE"
        return True
        
    def handle_tile_event(self, tile):
        """处理玩家踩到不同类型格子的事件"""
        current_player = self.players[self.current_player_index]
        print(f"[DEBUG] 处理格子事件: 类型={tile.type.name}, 位置={current_player.position}")
        
        # 先检查玩家相遇
        other_player, _ = self.player_encounter_system.check_player_encounter(self.players)
        if other_player and other_player != current_player:
            print(f"[DEBUG] 玩家相遇: {current_player.name} vs {other_player.name}")
            self.game_state = self.player_encounter_system.handle_player_encounter(
                current_player, other_player)
            return
        
        # 处理格子事件
        if tile.type == TileType.POKEMON_CENTER:
            print("[DEBUG] 进入宝可梦中心")
            self.game_state = "IN_POKEMON_CENTER"
            if self.pokemon_center_system.heal_all_pokemon(current_player):
                self.end_turn()
            return
        
        elif tile.type == TileType.SHOP:
            print("[DEBUG] 进入商店")
            self.game_state = "IN_SHOP"
            return
        
        elif tile.type == TileType.WILD:
            print("[DEBUG] 遇到野生宝可梦")
            wild_pokemon = self.generate_wild_pokemon(current_player)
            print(f"[DEBUG] 野生宝可梦: {wild_pokemon.name} Lv.{wild_pokemon.level}")
            self.battle_system.start_battle(current_player, wild_pokemon)
            self.game_state = "IN_BATTLE"
            return
        
        elif tile.type == TileType.GYM:
            print("[DEBUG] 进入道馆")
            success, gym_data = self.gym_system.challenge_gym(current_player, tile.gym_type)
            if success:
                print(f"[DEBUG] 道馆挑战开始: {gym_data['leader_name']}")
                self.battle_system.start_battle(current_player, gym_data["pokemon"])
                self.game_state = "IN_BATTLE"
                return
            else:
                print(f"[DEBUG] 道馆挑战失败: {gym_data.get('error', '未知错误')}")
                self.end_turn()
                return
        
        elif tile.type == TileType.PORTAL:
            print("[DEBUG] 使用传送门")
            current_player.current_ring = "inner" if current_player.current_ring == "outer" else "outer"
            print(f"[DEBUG] 传送至: {current_player.current_ring}")
            self.end_turn()
            return
        
        # 普通格子直接结束回合
        elif tile.type == TileType.NORMAL:
            print("[DEBUG] 普通格子，结束回合")
            self.end_turn()
            return
        
    def end_turn(self):
        """结束当前玩家的回合"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.current_player_index == 0:
            self.turn_count += 1
            
        # 检查游戏是否结束
        if self.turn_count >= 100:
            self.end_game()
            return
            
        # 更新玩家状态
        current_player = self.players[self.current_player_index]
        current_player.update_turn()
        
        self.game_state = "WAITING_FOR_ROLL"
        
    def end_game(self):
        """游戏结束处理"""
        # 找出金币最多的玩家
        winner = max(self.players, key=lambda p: p.coins)
        self.game_state = "GAME_OVER"
        return winner
        
    def generate_wild_pokemon(self, player):
        """生成野生宝可梦"""
        # 获取玩家最高等级宝可梦
        max_level = max(pokemon.level for pokemon in player.pokemons) if player.pokemons else 1
        return self.wild_pokemon_system.generate_wild_pokemon(max_level)
        
    def save_game(self):
        """保存当前游戏状态"""
        try:
            filename = self.save_system.save_game(self)
            return True, f"游戏已保存至: {filename}"
        except Exception as e:
            return False, f"保存游戏失败: {str(e)}"
        
    def load_game(self, filename):
        """加载游戏存档"""
        try:
            save_data = self.save_system.load_game(filename)
            self.turn_count = save_data["turn_count"]
            self.current_player_index = save_data["current_player_index"]
            self.players = save_data["players"]
            self.game_state = "WAITING_FOR_ROLL"
            return True, "游戏加载成功"
        except Exception as e:
            return False, f"加载游戏失败: {str(e)}"
        
    def update(self):
        """游戏主循环更新"""
        # 计算时间增量
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_time) / 1000.0  # 转换为秒
        self.last_time = current_time
        
        # 更新骰子动画
        if self.game_state == "ROLLING_DICE":
            self.dice_animation_frame += 1
            if self.dice_animation_frame >= self.dice_total_frames:
                print(f"[DEBUG] 骰子动画结束，开始移动")
                current_player = self.players[self.current_player_index]
                current_player.start_move(self.dice_result)
                self.game_state = "MOVING"
                
        # 更新玩家移动
        elif self.game_state == "MOVING":
            current_player = self.players[self.current_player_index]
            if not current_player.update_movement(delta_time):
                print(f"[DEBUG] 移动结束，当前位置: {current_player.position}")
                # 移动结束，处理格子事件
                tile = self.map_system.get_tile(current_player.position, current_player.current_ring)
                self.handle_tile_event(tile)
        
        # 检查是否需要自动保存
        if (self.settings_system.get_setting("gameplay", "auto_save") and
            self.turn_count % self.settings_system.get_setting("gameplay", "auto_save_interval") == 0):
            self.save_game()
        
        # 绘制当前界面
        if self.game_state == "IN_TUTORIAL":
            self.ui.draw_tutorial_screen(self.tutorial_system)
        
        # 添加状态检查
        if self.game_state not in self.game_states:
            print(f"[WARNING] 无的游戏状态: {self.game_state}")
            self.game_state = "WAITING_FOR_ROLL"
        
        # 更新提示信息显示时间
        if self.last_message:
            self.message_display_time += 1
            if self.message_display_time > 180:  # 3秒后消失
                self.last_message = None
                self.message_display_time = 0
        
    def start_new_game(self):
        """开始新游戏"""
        # 创建两个玩家
        player1 = Player("玩家1")
        player2 = Player("玩家2")
        
        # 设置 game_loop 引用
        player1.game_loop = self
        player2.game_loop = self
        
        # 设置随机起始位置
        for player in [player1, player2]:
            pos, ring = self.map_system.get_random_start_position()
            player.position = pos
            player.current_ring = ring
        
        self.players = [player1, player2]
        self.current_player_index = 0
        self.turn_count = 0  # 重置回合数
        self.game_state = "WAITING_FOR_ROLL"
        
    def check_level_up_skills(self, pokemon):
        """检查是否可以学习新技能"""
        if self.skill_system.can_learn_new_move(pokemon):
            self.current_learning_pokemon = pokemon
            self.game_state = "LEARNING_MOVE"
        