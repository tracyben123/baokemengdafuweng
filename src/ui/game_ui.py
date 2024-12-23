import pygame
import os
from systems.map_system import TileType
import random
import math

class GameUI:
    def __init__(self, screen_width=1280, screen_height=720):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("宝可梦大富翁")
        self.game_loop = None  # 添加 game_loop 引用
        
        # 设置字体
        try:
            # 加载思源黑体，调整字体大小
            font_dir = os.path.join("assets", "fonts")
            self.font_bold = pygame.font.Font(
                os.path.join(font_dir, "SourceHanSansSC-Bold.otf"), 24)  # 从32改为24
            self.font = pygame.font.Font(
                os.path.join(font_dir, "SourceHanSansSC-Regular.otf"), 20)  # 从32改为20
            self.font_small = pygame.font.Font(
                os.path.join(font_dir, "SourceHanSansSC-Regular.otf"), 16)  # 从24改为16
            self.font_large = pygame.font.Font(
                os.path.join(font_dir, "SourceHanSansSC-Bold.otf"), 32)  # 从40改为32
        except Exception as e:
            print(f"警告：加载字体失败 - {str(e)}")
            # 使用系统默认字体作为后备
            self.font_bold = pygame.font.SysFont("microsoftyaheui", 24, bold=True)
            self.font = pygame.font.SysFont("microsoftyaheui", 20)
            self.font_small = pygame.font.SysFont("microsoftyaheui", 16)
            self.font_large = pygame.font.SysFont("microsoftyaheui", 32, bold=True)
        
        self.clock = pygame.time.Clock()
        
        # 加载骰子图片
        self.dice_images = []
        for i in range(1, 7):
            try:
                # 使用点数图案而不是数字
                image = pygame.Surface((100, 100))
                image.fill((255, 255, 255))  # 白色背景
                
                # 绘制骰子边框
                pygame.draw.rect(image, (0, 0, 0), (0, 0, 100, 100), 2)
                
                # 根据点数绘制圆点
                dots = self._get_dice_dots(i)
                for x, y in dots:
                    pygame.draw.circle(image, (0, 0, 0), (x, y), 8)
                    
                self.dice_images.append(image)
            except:
                print(f"创建骰子图像 {i} 失败")
        
        # 修改呼吸动画参数，进一步降低频率
        self.breath_animation_time = 0
        self.breath_animation_speed = 0.5  # 再降低呼吸速度1.0改为0.5）
        self.breath_scale_range = 0.1     # 保持呼吸幅度不变
        
        # 修改捕捉动画相关属性
        self.catch_animation_frame = 0
        self.catch_animation_length = 180  # 从90帧增加到180帧(3秒)
        self.catch_animation_state = None  # None, "throwing", "shaking", "caught", "failed"
        self.catch_shake_count = 0
        self.catch_success = False
        self.on_catch_animation_complete = None
        self.result_display_time = 120  # 结果显示时间(2秒)
        
    def draw_current_screen(self, game):
        """根据游戏状态绘制当前界面"""
        self.game_loop = game
        
        # 清空屏幕
        self.screen.fill((255, 255, 255))
        
        # 始终绘制游戏棋盘作为背景
        self.draw_game_board(game)
        
        # 根据游戏状态绘制额外的界面
        if game.game_state == "IN_TUTORIAL":
            self.draw_tutorial_screen(game.tutorial_system)
        elif game.game_state == "IN_BATTLE":
            self.draw_battle_screen(game.battle_system)
        elif game.game_state == "IN_SHOP":
            self.draw_shop_screen(game.shop_system, game.players[game.current_player_index])
        elif game.game_state == "IN_POKEMON_CENTER":
            self.draw_pokemon_center_screen(game.pokemon_center_system, game.players[game.current_player_index])
        elif game.game_state == "GAME_OVER":
            self.draw_game_over_screen(game)
        elif game.game_state == "ROLLING_DICE":
            self._draw_dice_animation(game.dice_animation_frame, game.dice_result)
        elif game.game_state == "IN_MENU":
            self.draw_menu_screen()
        
    def draw_game_board(self, game):
        """绘制游戏棋盘"""
        # 清空屏幕
        self.screen.fill((255, 255, 255))
        
        # 绘制外圈和内圈
        self._draw_outer_ring(game.map_system.outer_ring)
        self._draw_inner_ring(game.map_system.inner_ring)
        
        # 绘制玩家信息
        self._draw_player_info(game.players, game.current_player_index)
        
        # 绘制当前玩家的宝可梦列表和背包
        if game.game_state == "WAITING_FOR_ROLL":
            current_player = game.players[game.current_player_index]
            self._draw_inventory(current_player, 20, 100)      # 左侧显示背包
            self._draw_pokemon_list(current_player, 1000, 100) # 右侧显示宝可梦列表
        
        # 绘制控制按钮
        self._draw_control_buttons()
        
        # 如果正在投骰子，绘制骰子动画
        if game.game_state == "ROLLING_DICE":
            self._draw_dice_animation(game.dice_animation_frame, game.dice_result)
            
        # 绘制提示信息（如果有）
        if hasattr(game, 'last_message') and game.last_message:
            message_text = self.font.render(game.last_message, True, (255, 0, 0))
            message_rect = message_text.get_rect(center=(640, 50))
            self.screen.blit(message_text, message_rect)
        
    def _draw_outer_ring(self, tiles):
        """绘制外圈"""
        for i, tile in enumerate(tiles):
            pos = self.game_loop.map_system.get_tile_position(i, "outer")
            self._draw_tile(tile, pos, i, "outer")

    def _draw_inner_ring(self, tiles):
        """绘制内圈"""
        for i, tile in enumerate(tiles):
            pos = self.game_loop.map_system.get_tile_position(i, "inner")
            self._draw_tile(tile, pos, i, "inner")

    def _draw_tile(self, tile, pos, index, ring_type):
        """绘制单个格子"""
        tile_size = self.game_loop.map_system.TILE_SIZE
        
        # 绘制格子背景和颜色
        pygame.draw.rect(self.screen, (150, 150, 150), (*pos, tile_size, tile_size))
        color = self._get_tile_color(tile.type)
        pygame.draw.rect(self.screen, color, (*pos, tile_size, tile_size))
        
        # 绘制格子类型文字
        tile_text = self._get_tile_text(tile.type)
        text = self.font_small.render(tile_text, True, (0, 0, 0))
        text_rect = text.get_rect(center=(pos[0] + tile_size//2, pos[1] + tile_size//2))
        self.screen.blit(text, text_rect)
        
        # 绘制所有玩家的棋子
        for player in self.game_loop.players:
            if player.position == index and player.current_ring == ring_type:
                # 计算棋子大小和位置
                base_size = tile_size // 3
                center_x = pos[0] + tile_size // 2
                center_y = pos[1] + tile_size // 2
                
                # 判断是否是当前玩家
                is_current = player == self.game_loop.players[self.game_loop.current_player_index]
                
                # 只有当前玩家有呼吸效果和光晕
                if is_current:
                    breath_scale = 1.0 + math.sin(self.breath_animation_time * self.breath_animation_speed) * self.breath_scale_range
                    scaled_size = base_size * breath_scale
                    
                    # 绘制发光效果
                    glow_size = scaled_size + 4
                    glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (255, 215, 0, 100),  # 金色光晕
                                     (glow_size, glow_size), glow_size)
                    self.screen.blit(glow_surface, 
                                   (center_x - glow_size, center_y - glow_size))
                else:
                    scaled_size = base_size  # 非当前玩家使用固定大小
                
                # 绘制玩家棋子
                player_colors = {
                    0: (255, 50, 50),    # 玩家1：鲜红色
                    1: (50, 50, 255)     # 玩家2：鲜蓝色
                }
                player_index = self.game_loop.players.index(player)
                player_color = player_colors[player_index]
                
                # 绘制棋子边框（增加立体感）
                border_color = (min(player_color[0] + 30, 255),
                              min(player_color[1] + 30, 255),
                              min(player_color[2] + 30, 255))
                pygame.draw.circle(self.screen, border_color,
                                 (center_x, center_y), scaled_size + 2)
                
                # 绘制棋子主体
                pygame.draw.circle(self.screen, player_color,
                                 (center_x, center_y), scaled_size)
                
                # 绘制玩家编号（使用白色以增加对比度）
                player_num = "P1" if player == self.game_loop.players[0] else "P2"
                num_text = self.font_small.render(player_num, True, (255, 255, 255))
                num_rect = num_text.get_rect(center=(center_x, center_y))
                self.screen.blit(num_text, num_rect)
        
    def _get_tile_color(self, tile_type):
        """获取格子颜色"""
        colors = {
            "POKEMON_CENTER": (255, 100, 100),  # 红色：宝可梦中心
            "SHOP": (100, 255, 100),           # 绿色：商店
            "WILD": (150, 150, 150),           # 灰色：野生宝可梦
            "GYM": (255, 255, 100),            # 黄色：道馆
            "PORTAL": (100, 100, 255),         # 蓝色：传送门
            "NORMAL": (200, 200, 200)          # 浅灰色：普通格子
        }
        return colors.get(tile_type.name, (200, 200, 200))
        
    def _get_tile_text(self, tile_type):
        """获取格子类型的显示文字"""
        texts = {
            TileType.NORMAL: "普通",
            TileType.POKEMON_CENTER: "中心",
            TileType.SHOP: "商店",
            TileType.WILD: "野战",
            TileType.GYM: "道馆",
            TileType.PORTAL: "传送"
        }
        return texts.get(tile_type, "普通")
        
    def _draw_player_info(self, players, current_player_index):
        """绘制玩家信息"""
        # 更新呼吸动画时间
        self.breath_animation_time += 0.05  # 从0.1改为0.05，减慢更新速度
        breath_scale = 1.0 + math.sin(self.breath_animation_time * self.breath_animation_speed) * self.breath_scale_range
        
        for i, player in enumerate(players):
            # 玩家信息框位置
            x = 20 + i * 250
            y = 650
            base_width = 200
            base_height = 120
            
            # 如果是当前玩家，应用呼吸效果
            if i == current_player_index:
                # 计算缩放后的尺寸
                scaled_width = base_width * breath_scale
                scaled_height = base_height * breath_scale
                # 调整位置以保持中心点不变
                x = x - (scaled_width - base_width) / 2
                y = y - (scaled_height - base_height) / 2
                width = scaled_width
                height = scaled_height
                # 绘制发光效果
                glow_surface = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (255, 255, 0, 100), 
                               (0, 0, width + 10, height + 10), border_radius=10)
                self.screen.blit(glow_surface, (x - 5, y - 5))
            else:
                width = base_width
                height = base_height
            
            # 绘制背景
            color = (255, 255, 0) if i == current_player_index else (200, 200, 200)
            pygame.draw.rect(self.screen, color, (x, y, width, height))
            
            # 绘制玩家名字
            name_text = self.font_bold.render(player.name, True, (0, 0, 0))
            name_rect = name_text.get_rect(x=x + 10, y=y + 10)
            if i == current_player_index:
                name_rect.x = x + (width - name_text.get_width()) / 2
            self.screen.blit(name_text, name_rect)
            
            # 绘制金币
            coins_text = self.font.render(f"金币: {player.coins}", True, (0, 0, 0))
            coins_rect = coins_text.get_rect(x=x + 10, y=y + 40)
            if i == current_player_index:
                coins_rect.x = x + (width - coins_text.get_width()) / 2
            self.screen.blit(coins_text, coins_rect)
            
            # 绘制宝可梦信息
            if player.pokemons:
                pokemon = player.pokemons[0]
                pokemon_text = self.font_small.render(
                    f"{pokemon.name} Lv.{pokemon.level}", True, (0, 0, 0))
                pokemon_rect = pokemon_text.get_rect(x=x + 10, y=y + 70)
                if i == current_player_index:
                    pokemon_rect.x = x + (width - pokemon_text.get_width()) / 2
                self.screen.blit(pokemon_text, pokemon_rect)
                
                # 绘制HP条
                hp_percent = pokemon.hp / pokemon.max_hp
                hp_width = 180 * hp_percent
                if i == current_player_index:
                    hp_width *= breath_scale
                hp_x = x + (width - 180) / 2 if i == current_player_index else x + 10
                pygame.draw.rect(self.screen, (255, 0, 0), 
                               (hp_x, y + 95, hp_width, 15))
        
    def _draw_control_buttons(self):
        """绘制控制按钮"""
        # 投骰子按钮
        if self.game_loop.game_state == "WAITING_FOR_ROLL":
            pygame.draw.rect(self.screen, (100, 200, 100),  # 绿色
                            (560, 670, 120, 50))
            roll_text = self.font.render("投骰子", True, (0, 0, 0))
            self.screen.blit(roll_text, (580, 680))
            
            # 菜单按钮
            pygame.draw.rect(self.screen, (200, 200, 200),  # 灰色
                            (700, 670, 120, 50))
            menu_text = self.font.render("菜单", True, (0, 0, 0))
            self.screen.blit(menu_text, (730, 680))
        
    def draw_battle_screen(self, battle_system):
        """绘制战斗界面"""
        # 清空屏幕
        self.screen.fill((255, 255, 255))
        
        # 绘制攻击方宝可梦
        self._draw_pokemon(battle_system.current_attacker_pokemon, True)
        
        # 绘制防守方宝可梦
        self._draw_pokemon(battle_system.current_defender_pokemon, False)
        
        # 绘制技能按钮
        self._draw_skill_buttons(battle_system.current_attacker_pokemon.moves)
        
        # 绘制其他战斗选项（逃跑、捕获等）
        self._draw_battle_options(battle_system.is_pvp)
        
        # 添加提示信息
        hint_text = "必须完成战斗、成功逃跑或捕获宝可梦才能离开战斗"
        hint = self.font_small.render(hint_text, True, (255, 0, 0))
        hint_rect = hint.get_rect(center=(640, 50))
        self.screen.blit(hint, hint_rect)
        
        # 添加战斗回合数显示
        turn_text = self.font.render(f"回合: {battle_system.turn}", True, (0, 0, 0))
        self.screen.blit(turn_text, (600, 100))
        
        # 添加逃跑概率提示
        if not battle_system.is_pvp:
            escape_chance = 0.7 + 0.15 * battle_system.turn
            escape_text = self.font_small.render(
                f"逃跑成功率: {int(escape_chance * 100)}%", True, (0, 0, 0))
            self.screen.blit(escape_text, (850, 450))
        
        # 添加战斗提示
        if battle_system.current_defender_pokemon.hp < battle_system.current_defender_pokemon.max_hp * 0.3:
            hint = self.font_small.render(
                "可梦体力不足，现在是捕捉的好时机！", True, (255, 0, 0))
            hint_rect = hint.get_rect(center=(640, 80))
            self.screen.blit(hint, hint_rect)
        
        # 添加经验值提示
        exp_gain = battle_system.calculate_exp_gain()
        exp_text = self.font_small.render(
            f"击败后可获得经验值：{exp_gain}", True, (0, 0, 0))
        self.screen.blit(exp_text, (600, 130))
        
        # 显示双方HP
        attacker_hp_text = self.font.render(
            f"HP: {battle_system.current_attacker_pokemon.hp}/{battle_system.current_attacker_pokemon.max_hp}",
            True, (0, 0, 0))
        defender_hp_text = self.font.render(
            f"HP: {battle_system.current_defender_pokemon.hp}/{battle_system.current_defender_pokemon.max_hp}",
            True, (0, 0, 0))
        
        self.screen.blit(attacker_hp_text, (200, 350))
        self.screen.blit(defender_hp_text, (800, 350))
        
        # 显示属性克制信息
        if battle_system.current_attacker_pokemon and battle_system.current_defender_pokemon:
            type_text = self.font_small.render(
                f"属性克制: {battle_system.current_attacker_pokemon.type} vs {battle_system.current_defender_pokemon.type}",
                True, (0, 0, 0))
            self.screen.blit(type_text, (600, 150))
        
        # 绘制战斗选项
        if not battle_system.is_pvp:
            # 逃跑按钮
            pygame.draw.rect(self.screen, (200, 200, 200),
                            (900, 500, 100, 50))
            escape_text = self.font.render("逃跑", True, (0, 0, 0))
            self.screen.blit(escape_text, (920, 515))
            
            # 捕捉按钮
            pygame.draw.rect(self.screen, (200, 200, 200),
                            (900, 560, 100, 50))
            catch_text = self.font.render("捕捉", True, (0, 0, 0))
            self.screen.blit(catch_text, (920, 575))
            
            # 道具按钮
            pygame.draw.rect(self.screen, (100, 200, 100),
                            (900, 620, 100, 50))
            item_text = self.font.render("道具", True, (0, 0, 0))
            self.screen.blit(item_text, (920, 635))
            
            # 如果正在显示道具列表，绘制道具列表面板
            if battle_system.showing_items:
                self._draw_battle_items_panel(battle_system.current_attacker)
        
        # 如果正在播放捕捉动画，绘制动画
        if self.catch_animation_state:
            self._draw_catch_animation(battle_system.current_defender_pokemon)
        else:
            # 正常绘制战斗界面
            # 绘制捕捉按钮
            pygame.draw.rect(self.screen, (200, 200, 200),
                            (900, 560, 100, 50))
            catch_text = self.font.render("捕捉", True, (0, 0, 0))
            self.screen.blit(catch_text, (920, 575))
            
            # 道具按钮
            pygame.draw.rect(self.screen, (100, 200, 100),
                            (900, 620, 100, 50))
            item_text = self.font.render("道具", True, (0, 0, 0))
            self.screen.blit(item_text, (920, 635))
            
            # 如果正在显示道具列表，绘制道具列表面板
            if battle_system.showing_items:
                self._draw_battle_items_panel(battle_system.current_attacker)

    def _draw_pokemon(self, pokemon, is_attacker):
        """绘制宝可梦"""
        x = 200 if is_attacker else 800
        y = 300
        
        # 绘制名称
        text = self.font.render(pokemon.name, True, (0, 0, 0))
        self.screen.blit(text, (x, y))
        
        # 绘制血量条
        hp_percent = pokemon.hp / pokemon.max_hp
        pygame.draw.rect(self.screen, (255, 0, 0), 
                        (x, y + 30, 100 * hp_percent, 10))
        
        # 绘制等级
        text = self.font.render(f"Lv.{pokemon.level}", True, (0, 0, 0))
        self.screen.blit(text, (x, y + 50))
        
    def _draw_skill_buttons(self, moves):
        """绘制技能按钮"""
        for i, move in enumerate(moves):
            x = 100
            y = 500 + i * 50
            
            # 绘制按钮背景
            pygame.draw.rect(self.screen, (200, 200, 200), 
                           (x, y, 200, 40))
            
            # 绘制技能名称和PP
            text = self.font.render(f"{move.name} PP:{move.pp}/{move.max_pp}", 
                                  True, (0, 0, 0))
            self.screen.blit(text, (x + 10, y + 10))
            
    def _draw_battle_options(self, is_pvp):
        """绘制战斗选项"""
        options = []
        if not is_pvp:
            options.extend([
                ("逃跑", (900, 500)),
                ("捕捉", (900, 560)),
                ("道具", (900, 620))
            ])
        
        # 添加退出按钮
        options.append(("退出", (50, 650)))
        
        for option, (x, y) in options:
            width = 120 if option == "退出" else 100
            color = (255, 100, 100) if option == "退出" else (200, 200, 200)
            text_color = (255, 255, 255) if option == "退出" else (0, 0, 0)
            
            pygame.draw.rect(self.screen, color, (x, y, width, 50))
            text = self.font.render(option, True, text_color)
            self.screen.blit(text, (x + 20, y + 15))

    def _get_tile_position(self, index, start_x, start_y, width, height):
        """计算格子的位置"""
        tile_width = 40
        tile_height = 40
        total_tiles = 32
        
        # 计算每边格子数
        side_length = total_tiles // 4
        
        # 根据索引确定格子在哪一边
        if index < side_length:  # 上边
            x = start_x + (index * tile_width)
            y = start_y
        elif index < side_length * 2:  # 右边
            x = start_x + width - tile_width
            y = start_y + ((index - side_length) * tile_height)
        elif index < side_length * 3:  # 下边
            x = start_x + width - ((index - side_length * 2) * tile_width)
            y = start_y + height - tile_height
        else:  # 左边
            x = start_x
            y = start_y + height - ((index - side_length * 3) * tile_height)
        
        return x, y

    def draw_shop_screen(self, shop_system, player):
        """绘制商店界面"""
        # 清空屏幕
        self.screen.fill((255, 255, 255))
        
        # 使用大号粗体绘制标题
        title = self.font_large.render("商店", True, (0, 0, 0))
        self.screen.blit(title, (600, 50))
        
        # 使用常规字体绘制金币
        coins_text = self.font.render(f"金币: {player.coins}", True, (0, 0, 0))
        self.screen.blit(coins_text, (100, 50))
        
        # 绘制商品列表
        items = shop_system.get_item_list()
        for i, (item_name, price) in enumerate(items):
            # 绘制商品背景
            pygame.draw.rect(self.screen, (200, 200, 200),
                            (100, 100 + i * 60, 400, 50))
            
            # 使用小号字体绘制商品信息
            item_text = self.font_small.render(f"{item_name} - {price}币", True, (0, 0, 0))
            self.screen.blit(item_text, (120, 110 + i * 60))
            
            # 绘制购买按钮
            pygame.draw.rect(self.screen, (0, 255, 0),
                            (520, 100 + i * 60, 100, 50))
            buy_text = self.font.render("购买", True, (0, 0, 0))
            self.screen.blit(buy_text, (540, 110 + i * 60))
        
        # 绘制背包
        self._draw_inventory(player, 700, 100)
        
        # 绘制退出按钮
        pygame.draw.rect(self.screen, (255, 100, 100),  # 红色按钮
                        (50, 650, 120, 50))
        exit_text = self.font.render("退出", True, (255, 255, 255))  # 白色文字
        self.screen.blit(exit_text, (80, 660))

    def _draw_inventory(self, player, x, y):
        """绘制背包"""
        # 绘制标题
        title = self.font_bold.render("背包", True, (0, 0, 0))
        self.screen.blit(title, (x, y))
        
        # 绘制道具列表
        if not player.items:
            empty_text = self.font.render("背包是空的", True, (100, 100, 100))
            self.screen.blit(empty_text, (x + 10, y + 40))
        else:
            for i, item in enumerate(player.items):
                # 绘制背景（添加鼠标悬停效果）
                is_hovered = self._is_mouse_over((x, y + 40 + i * 50, 260, 40))
                bg_color = (230, 230, 230) if is_hovered else (220, 220, 220)
                pygame.draw.rect(self.screen, bg_color,
                               (x, y + 40 + i * 50, 260, 40))
                
                # 绘制道具名称
                item_text = self.font.render(item.name, True, (0, 0, 0))
                self.screen.blit(item_text, (x + 10, y + 50 + i * 50))
                
                # 如果鼠标悬停，显示提示文本
                if is_hovered:
                    hint_text = self.font_small.render("点击使用", True, (100, 100, 100))
                    self.screen.blit(hint_text, (x + 180, y + 55 + i * 50))

    def _is_mouse_over(self, rect):
        """检查鼠标是否悬停在指定区域"""
        mouse_pos = pygame.mouse.get_pos()
        return (rect[0] <= mouse_pos[0] <= rect[0] + rect[2] and 
                rect[1] <= mouse_pos[1] <= rect[1] + rect[3])

    def draw_pokemon_center_screen(self, pokemon_center_system, player):
        """绘制宝可梦中心界面"""
        # 清空屏幕
        self.screen.fill((255, 255, 255))
        
        # 绘制标题
        title = self.font.render("宝可梦中心", True, (0, 0, 0))
        self.screen.blit(title, (600, 50))
        
        # 绘制宝可梦列表
        for i, pokemon in enumerate(player.pokemons):
            # 绘宝可梦信息背景
            pygame.draw.rect(self.screen, (200, 200, 200),
                            (100, 100 + i * 100, 600, 90))
            
            # 绘制宝可梦名称
            name_text = self.font.render(pokemon.name, True, (0, 0, 0))
            self.screen.blit(name_text, (120, 110 + i * 100))
            
            # 绘制等级
            level_text = self.font.render(f"Lv.{pokemon.level}", True, (0, 0, 0))
            self.screen.blit(level_text, (300, 110 + i * 100))
            
            # 绘制HP
            hp_text = self.font.render(f"HP: {pokemon.hp}/{pokemon.max_hp}", True, (0, 0, 0))
            self.screen.blit(hp_text, (120, 150 + i * 100))
            
            # 绘制量条
            hp_percent = pokemon.hp / pokemon.max_hp
            pygame.draw.rect(self.screen, (255, 0, 0),
                            (300, 150 + i * 100, 200 * hp_percent, 20)) 
        
        # 绘制退出按钮
        pygame.draw.rect(self.screen, (255, 100, 100),  # 红色按钮
                        (50, 650, 120, 50))
        exit_text = self.font.render("退出", True, (255, 255, 255))
        self.screen.blit(exit_text, (80, 660))

    def draw_save_load_screen(self, save_system, is_saving=True):
        """绘制存档/读档界面"""
        self.screen.fill((255, 255, 255))
        
        # 绘制题
        title = self.font.render("保存游戏" if is_saving else "加载游戏", True, (0, 0, 0))
        self.screen.blit(title, (600, 50))
        
        # 获取存档列表
        saves = save_system.get_save_list()
        
        # 绘制存档列表
        for i, save in enumerate(saves):
            # 绘制存档背景
            pygame.draw.rect(self.screen, (200, 200, 200),
                            (100, 100 + i * 80, 800, 70))
            
            # 绘制存档信
            time_text = self.font.render(f"时间: {save['timestamp']}", True, (0, 0, 0))
            self.screen.blit(time_text, (120, 110 + i * 80))
            
            players_text = self.font.render(f"玩家: {', '.join(save['players'])}", True, (0, 0, 0))
            self.screen.blit(players_text, (120, 140 + i * 80))
            
            # 绘制操作按钮
            if not is_saving:
                pygame.draw.rect(self.screen, (0, 255, 0),
                               (920, 100 + i * 80, 100, 70))
                load_text = self.font.render("加载", True, (0, 0, 0))
                self.screen.blit(load_text, (940, 125 + i * 80))
        
        # 如果是保存界面，绘制新档按钮
        if is_saving:
            pygame.draw.rect(self.screen, (0, 255, 0),
                            (100, 600, 200, 50))
            new_save_text = self.font.render("新建存档", True, (0, 0, 0))
            self.screen.blit(new_save_text, (150, 615))

    def draw_settings_screen(self, settings_system):
        """绘制设置界面"""
        self.screen.fill((255, 255, 255))
        
        # 绘制标题
        title = self.font.render("游戏设置", True, (0, 0, 0))
        self.screen.blit(title, (600, 50))
        
        # 绘制设置分类
        categories = ["声音设置", "显示设置", "游戏设置", "控制设置"]
        for i, category in enumerate(categories):
            pygame.draw.rect(self.screen, (200, 200, 200),
                            (100, 100 + i * 150, 1080, 140))
            category_text = self.font.render(category, True, (0, 0, 0))
            self.screen.blit(category_text, (120, 110 + i * 150))
            
            # 根据分类绘制不同的设置项
            if category == "声音设置":
                self._draw_sound_settings(settings_system, 100, 140 + i * 150)
            elif category == "显示设置":
                self._draw_display_settings(settings_system, 100, 140 + i * 150)
            elif category == "游戏设置":
                self._draw_gameplay_settings(settings_system, 100, 140 + i * 150)
            elif category == "控制设置":
                self._draw_control_settings(settings_system, 100, 140 + i * 150)
            
        # 绘制置按钮
        pygame.draw.rect(self.screen, (255, 0, 0),
                        (100, 650, 200, 50))
        reset_text = self.font.render("重置默认", True, (255, 255, 255))
        self.screen.blit(reset_text, (150, 665))
        
    def _draw_sound_settings(self, settings_system, x, y):
        """绘制声音设置"""
        # 音效音量滑块
        sfx_text = self.font.render("音效音量", True, (0, 0, 0))
        self.screen.blit(sfx_text, (x + 20, y))
        sfx_volume = settings_system.get_setting("sound", "sfx_volume")
        pygame.draw.rect(self.screen, (150, 150, 150),
                        (x + 200, y + 10, 200, 20))
        pygame.draw.rect(self.screen, (0, 255, 0),
                        (x + 200, y + 10, 200 * sfx_volume, 20))
        
        # BGM音量滑块
        bgm_text = self.font.render("BGM音量", True, (0, 0, 0))
        self.screen.blit(bgm_text, (x + 500, y))
        bgm_volume = settings_system.get_setting("sound", "bgm_volume")
        pygame.draw.rect(self.screen, (150, 150, 150),
                        (x + 680, y + 10, 200, 20))
        pygame.draw.rect(self.screen, (0, 255, 0),
                        (x + 680, y + 10, 200 * bgm_volume, 20))
        
    def _draw_display_settings(self, settings_system, x, y):
        """绘制显示设置"""
        # 全屏切换
        fullscreen = settings_system.get_setting("display", "fullscreen")
        pygame.draw.rect(self.screen, (0, 255, 0) if fullscreen else (150, 150, 150),
                        (x + 20, y, 100, 40))
        fs_text = self.font.render("全屏", True, (0, 0, 0))
        self.screen.blit(fs_text, (x + 40, y + 10))
        
        # 分辨率选择
        res_text = self.font.render("分辨率", True, (0, 0, 0))
        self.screen.blit(res_text, (x + 200, y))
        current_res = settings_system.get_setting("display", "resolution")
        res_options = ["1280x720", "1920x1080"]
        for i, res in enumerate(res_options):
            pygame.draw.rect(self.screen, (0, 255, 0) if f"{current_res[0]}x{current_res[1]}" == res else (150, 150, 150),
                            (x + 300 + i * 150, y, 140, 40))
            res_opt_text = self.font.render(res, True, (0, 0, 0))
            self.screen.blit(res_opt_text, (x + 310 + i * 150, y + 10))

    def draw_tutorial_screen(self, tutorial_system):
        """绘制教程界面"""
        # 获取当前教程步骤
        step = tutorial_system.get_current_step()
        if not step:
            return
        
        # 绘制半透明背景
        s = pygame.Surface((1280, 720))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        
        # 绘制教程框
        pygame.draw.rect(self.screen, (255, 255, 255),
                        (200, 200, 880, 320))
        pygame.draw.rect(self.screen, (0, 0, 0),
                        (200, 200, 880, 320), 2)
        
        # 使用粗体绘制标题
        title = self.font_bold.render(step["title"], True, (0, 0, 0))
        self.screen.blit(title, (220, 220))
        
        # 使用常规字体绘制内容
        content_lines = step["content"].split("\n")
        for i, line in enumerate(content_lines):
            text = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (220, 270 + i * 30))
        
        # 绘制高亮区域（如果有）
        if step["highlight_area"]:
            x, y, w, h = step["highlight_area"]
            pygame.draw.rect(self.screen, (255, 255, 0),
                            (x, y, w, h), 3)
        
        # 绘制下一步按钮
        pygame.draw.rect(self.screen, (0, 255, 0),
                        (880, 450, 180, 50))
        next_text = self.font.render("下一步", True, (0, 0, 0))
        self.screen.blit(next_text, (920, 465))

    def draw_learn_move_screen(self, pokemon, learnable_moves):
        """绘制技能学习界面"""
        # 清空屏幕
        self.screen.fill((255, 255, 255))
        
        # 绘制题
        title = self.font_large.render("学习技能", True, (0, 0, 0))
        self.screen.blit(title, (600, 50))
        
        # 绘制宝可梦信息
        pokemon_info = f"{pokemon.name} Lv.{pokemon.level}"
        info_text = self.font.render(pokemon_info, True, (0, 0, 0))
        self.screen.blit(info_text, (100, 100))
        
        # 绘制当前技能
        self.font.render("当前技能:", True, (0, 0, 0))
        for i, move in enumerate(pokemon.moves):
            move_text = f"{move.name} ({move.type}) 威力:{move.power} PP:{move.pp}/{move.max_pp}"
            text = self.font.render(move_text, True, (0, 0, 0))
            self.screen.blit(text, (120, 160 + i * 40))
        
        # 绘制可学习的技能
        self.font.render("可学习的技能:", True, (0, 0, 0))
        for i, (name, move_type, power, pp) in enumerate(learnable_moves):
            move_text = f"{name} ({move_type}) 威力:{power} PP:{pp}"
            text = self.font.render(move_text, True, (0, 0, 0))
            self.screen.blit(text, (120, 360 + i * 40))
            
            # 绘制学习按钮
            pygame.draw.rect(self.screen, (0, 255, 0),
                            (500, 360 + i * 40, 100, 35))
            learn_text = self.font.render("学习", True, (0, 0, 0))
            self.screen.blit(learn_text, (520, 365 + i * 40))
        
        # 绘制退出按钮
        pygame.draw.rect(self.screen, (255, 100, 100),
                        (50, 650, 120, 50))
        exit_text = self.font.render("退出", True, (255, 255, 255))
        self.screen.blit(exit_text, (80, 660))

    def _draw_dice_animation(self, frame, final_number):
        """绘制骰子动画"""
        # 计算动画中心位置
        center_x = 640  # 屏幕中心x
        center_y = 360  # 屏幕中心y
        
        animation_length = self.game_loop.dice_animation_length
        total_frames = self.game_loop.dice_total_frames
        
        if frame < animation_length:  # 动画阶段
            # 减慢旋转度
            dice_number = random.randint(0, 5)
            angle = frame * 8  # 从12度减小到8度，使旋转更慢
            rotated_dice = pygame.transform.rotate(self.dice_images[dice_number], angle)
            
            # 调整弹跳效果
            bounce_height = abs(math.sin(frame * 0.1)) * 30  # 从0.15减小到0.1，使弹跳更慢
            center_y -= bounce_height
            
        else:  # 结束显示阶段
            rotated_dice = self.dice_images[final_number - 1]
            
            # 添加结果文本
            result_text = self.font_large.render(f"点数: {final_number}", True, (255, 255, 255))
            text_rect = result_text.get_rect(center=(center_x, center_y - 80))
            self.screen.blit(result_text, text_rect)
        
        # 获取旋转后图片的矩形
        dice_rect = rotated_dice.get_rect(center=(center_x, center_y))
        
        # 绘制半透明背景
        s = pygame.Surface((1280, 720))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        
        # 绘制骰子
        self.screen.blit(rotated_dice, dice_rect)

    def _get_dice_dots(self, number):
        """获取骰子点数的位置"""
        dots = {
            1: [(50, 50)],
            2: [(25, 25), (75, 75)],
            3: [(25, 25), (50, 50), (75, 75)],
            4: [(25, 25), (25, 75), (75, 25), (75, 75)],
            5: [(25, 25), (25, 75), (50, 50), (75, 25), (75, 75)],
            6: [(25, 25), (25, 50), (25, 75), (75, 25), (75, 50), (75, 75)]
        }
        return dots.get(number, [])

    def draw_menu_screen(self):
        """绘制菜单界面"""
        # 绘制半透明背景
        s = pygame.Surface((1280, 720))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        
        # 绘制菜单标题
        title = self.font_large.render("游戏菜单", True, (255, 255, 255))
        title_rect = title.get_rect(center=(640, 100))
        self.screen.blit(title, title_rect)
        
        # 绘制菜单按钮
        menu_items = [
            "保存游戏",
            "读取游戏",
            "设置",
            "返回游戏"
        ]
        
        for i, item in enumerate(menu_items):
            # 绘制按钮背景
            pygame.draw.rect(self.screen, (200, 200, 200),
                            (500, 200 + i * 100, 280, 50))
            # 绘制按钮文字
            text = self.font.render(item, True, (0, 0, 0))
            text_rect = text.get_rect(center=(640, 225 + i * 100))
            self.screen.blit(text, text_rect)

    def _draw_pokemon_list(self, player, x, y):
        """绘制宝可梦列表"""
        # 绘制标题
        title = self.font_bold.render("宝可梦列表", True, (0, 0, 0))
        self.screen.blit(title, (x, y))
        
        # 绘制宝可梦信息
        for i, pokemon in enumerate(player.pokemons):
            # 检查是否被选中
            is_selected = i == player.selected_pokemon_index
            is_hovered = self._is_mouse_over((x, y + 40 + i * 80, 260, 70))
            
            # 绘制背景（选中和悬停状态有不同颜色）
            if is_selected:
                bg_color = (255, 255, 150)  # 黄色背景表示选中
            elif is_hovered:
                bg_color = (230, 230, 230)  # 浅灰色表示悬停
            else:
                bg_color = (220, 220, 220)  # 默认背景色
            
            pygame.draw.rect(self.screen, bg_color,
                            (x, y + 40 + i * 80, 260, 70))
            
            # 绘制名称和等级
            name_text = self.font.render(f"{pokemon.name} Lv.{pokemon.level}", True, (0, 0, 0))
            self.screen.blit(name_text, (x + 10, y + 45 + i * 80))
            
            # 绘制HP条
            hp_text = self.font_small.render(f"HP: {pokemon.hp}/{pokemon.max_hp}", True, (0, 0, 0))
            self.screen.blit(hp_text, (x + 10, y + 70 + i * 80))
            
            hp_percent = pokemon.hp / pokemon.max_hp
            pygame.draw.rect(self.screen, (255, 0, 0),
                            (x + 100, y + 75 + i * 80, 150 * hp_percent, 15))
            pygame.draw.rect(self.screen, (0, 0, 0),
                            (x + 100, y + 75 + i * 80, 150, 15), 1)
            
            # 如果是选中状态，显示交换提示
            if is_selected and is_hovered:
                hint_text = self.font_small.render("点击其他宝可梦交换位置", True, (100, 100, 100))
                self.screen.blit(hint_text, (x + 10, y + 95 + i * 80))

    def _draw_battle_items_panel(self, player):
        """绘制战斗中的道具列表面板"""
        # 绘制半透明背景
        panel_surface = pygame.Surface((300, 400))
        panel_surface.fill((240, 240, 240))
        panel_surface.set_alpha(230)
        self.screen.blit(panel_surface, (580, 300))
        
        # 绘制标题
        title = self.font_bold.render("道具列表", True, (0, 0, 0))
        self.screen.blit(title, (680, 310))
        
        # 绘制道具列表
        if not player.items:
            empty_text = self.font.render("没有可用的道具", True, (100, 100, 100))
            self.screen.blit(empty_text, (650, 360))
        else:
            for i, item in enumerate(player.items):
                # 绘制道具背景
                is_hovered = self._is_mouse_over((600, 350 + i * 50, 260, 40))
                bg_color = (230, 230, 230) if is_hovered else (200, 200, 200)
                pygame.draw.rect(self.screen, bg_color,
                               (600, 350 + i * 50, 260, 40))
                
                # 绘制道具名称
                item_text = self.font.render(item.name, True, (0, 0, 0))
                self.screen.blit(item_text, (620, 360 + i * 50))

    def _draw_catch_animation(self, target_pokemon):
        """绘制捕捉动画"""
        center_x = 640  # 屏幕中心x
        center_y = 360  # 屏幕中心y
        
        # 绘制半透明背景
        s = pygame.Surface((1280, 720))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        
        if self.catch_animation_state == "throwing":
            # 延长投掷阶段到1秒
            progress = self.catch_animation_frame / 60  # 从30改为60
            if progress >= 1:
                self.catch_animation_state = "shaking"
                self.catch_animation_frame = 0
                return
            
            # 计算精灵球位置（抛物线轨迹）
            start_x = 200
            start_y = 500
            target_x = center_x
            target_y = center_y
            
            current_x = start_x + (target_x - start_x) * progress
            # 增加抛物线高度
            current_y = start_y + (target_y - start_y) * progress - 300 * math.sin(progress * math.pi)
            
            # 绘制精灵球
            ball_size = 30
            pygame.draw.circle(self.screen, (255, 0, 0), (int(current_x), int(current_y)), ball_size)
            pygame.draw.line(self.screen, (0, 0, 0), 
                            (int(current_x - ball_size), int(current_y)),
                            (int(current_x + ball_size), int(current_y)), 3)
        
        elif self.catch_animation_state == "shaking":
            # 延长每次摇晃时间到0.5秒
            shake_progress = self.catch_animation_frame / 30  # 从15改为30
            if shake_progress >= 1:
                self.catch_shake_count += 1
                self.catch_animation_frame = 0
                if self.catch_shake_count >= 3:
                    self.catch_animation_state = "caught" if self.catch_success else "failed"
                return
            
            # 计算摇晃角度
            angle = 30 * math.sin(shake_progress * math.pi * 2)
            
            # 绘制摇晃的精灵球
            ball_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(ball_surface, (255, 0, 0), (30, 30), 30)
            pygame.draw.line(ball_surface, (0, 0, 0), (0, 30), (60, 30), 3)
            
            # 旋转精灵球
            rotated_ball = pygame.transform.rotate(ball_surface, angle)
            ball_rect = rotated_ball.get_rect(center=(center_x, center_y))
            self.screen.blit(rotated_ball, ball_rect)
            
            # 添加特效
            effect_radius = 40 + abs(math.sin(shake_progress * math.pi * 2) * 10)
            pygame.draw.circle(self.screen, (255, 255, 0, 50), 
                             (center_x, center_y), int(effect_radius), 2)
        
        elif self.catch_animation_state in ["caught", "failed"]:
            # 延长结果显示时间到2秒
            if self.catch_animation_frame >= self.result_display_time:
                if self.on_catch_animation_complete:
                    self.on_catch_animation_complete()
                    self.on_catch_animation_complete = None
                self.catch_animation_state = None
                return
            
            # 绘制结果特效和文本
            if self.catch_success:
                # 成功特效
                effect_size = 50 + abs(math.sin(self.catch_animation_frame * 0.1) * 20)
                for i in range(8):
                    angle = i * math.pi / 4 + self.catch_animation_frame * 0.05
                    x = center_x + math.cos(angle) * effect_size
                    y = center_y + math.sin(angle) * effect_size
                    pygame.draw.circle(self.screen, (255, 255, 0), (int(x), int(y)), 5)
                
                # 成功文本
                success_text = self.font_large.render("捕获成功！", True, (0, 255, 0))
                text_rect = success_text.get_rect(center=(center_x, center_y - 100))
                self.screen.blit(success_text, text_rect)
                
                # 添加宝可梦名称
                pokemon_text = self.font.render(f"获得了{target_pokemon.name}！", True, (255, 255, 255))
                pokemon_rect = pokemon_text.get_rect(center=(center_x, center_y + 50))
                self.screen.blit(pokemon_text, pokemon_rect)
            else:
                # 失败特效
                pygame.draw.circle(self.screen, (255, 0, 0, 50),
                                 (center_x, center_y), 
                                 int(40 + self.catch_animation_frame * 0.5), 2)
                
                # 失败文本
                fail_text = self.font_large.render("捕获失败！", True, (255, 0, 0))
                text_rect = fail_text.get_rect(center=(center_x, center_y - 100))
                self.screen.blit(fail_text, text_rect)
                
                # 添加失败原因
                reason_text = self.font.render(f"{target_pokemon.name}挣脱了精灵球！", True, (255, 255, 255))
                reason_rect = reason_text.get_rect(center=(center_x, center_y + 50))
                self.screen.blit(reason_text, reason_rect)
            
        self.catch_animation_frame += 1

    def start_catch_animation(self, success):
        """开始捕捉动画"""
        self.catch_animation_frame = 0
        self.catch_animation_state = "throwing"
        self.catch_shake_count = 0
        self.catch_success = success