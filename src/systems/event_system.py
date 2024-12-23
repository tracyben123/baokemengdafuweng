import pygame
from pygame.locals import *

class EventSystem:
    def __init__(self, game_loop):
        self.game_loop = game_loop
        
    def handle_events(self):
        """处理所有游戏事件"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
                
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.game_loop.game_state == "WAITING_FOR_ROLL":
                        self.game_loop.roll_dice()
                        
            if event.type == MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)
                
        return True
        
    def _handle_mouse_click(self, pos):
        """处理鼠标点击事件"""
        print(f"[DEBUG] 鼠标点击位置: {pos}")
        
        # 检查当前游戏状态
        if self.game_loop.game_state == "WAITING_FOR_ROLL":
            current_player = self.game_loop.players[self.game_loop.current_player_index]
            
            # 检查宝可梦列表点击
            for i in range(len(current_player.pokemons)):
                if self._is_in_rect(pos, (1000, 140 + i * 80, 260, 70)):
                    current_player.select_pokemon(i)
                    return
                
            # 检查背包道具点击
            for i, item in enumerate(current_player.items):
                if self._is_in_rect(pos, (20, 140 + i * 50, 260, 40)):
                    if current_player.selected_pokemon_index is not None:
                        # 使用道具在选中的宝可梦上
                        target_pokemon = current_player.pokemons[current_player.selected_pokemon_index]
                        if current_player.use_item(i, target_pokemon):
                            print(f"[DEBUG] 对{target_pokemon.name}使用{item.name}成功")
                        current_player.selected_pokemon_index = None
                    else:
                        print("[DEBUG] 请先选择要使用道具的宝可梦")
                    return
            
            # 投骰子按钮区域 (约560-680, 670-720)
            if 560 <= pos[0] <= 680 and 670 <= pos[1] <= 720:
                print("[DEBUG] 点击投骰子按钮")
                self.game_loop.roll_dice()
                return
            
            # 菜单按钮区域 (约700-820, 670-720)
            if 700 <= pos[0] <= 820 and 670 <= pos[1] <= 720:
                print("[DEBUG] 点击菜单按钮")
                self.game_loop.game_state = "IN_MENU"
                return
            
        elif self.game_loop.game_state == "IN_MENU":
            self._handle_menu_click(pos)
        elif self.game_loop.game_state == "IN_BATTLE":
            self._handle_battle_click(pos)
        elif self.game_loop.game_state == "IN_SHOP":
            self._handle_shop_click(pos)
        elif self.game_loop.game_state == "IN_POKEMON_CENTER":
            self._handle_pokemon_center_click(pos)
        elif self.game_loop.game_state == "IN_TUTORIAL":
            self._handle_tutorial_click(pos)
        elif self.game_loop.game_state == "IN_BATTLE_ITEM":
            self._handle_battle_item_click(pos)
            
    def _handle_menu_click(self, pos):
        """处理菜单界面的点击"""
        # 保存游戏按钮
        if self._is_in_rect(pos, (500, 200, 280, 50)):
            success, message = self.game_loop.save_game()
            print(f"[DEBUG] 保存游戏: {message}")
            return
        
        # 读取游戏按钮
        if self._is_in_rect(pos, (500, 300, 280, 50)):
            # TODO: 添加读取游戏对话框
            return
        
        # 设置按钮
        if self._is_in_rect(pos, (500, 400, 280, 50)):
            # TODO: 添加设置界面
            return
        
        # 返回游戏按钮
        if self._is_in_rect(pos, (500, 500, 280, 50)):
            self.game_loop.game_state = "WAITING_FOR_ROLL"
            return
        
    def _handle_battle_click(self, pos):
        """处理战斗界面的点击"""
        battle_system = self.game_loop.battle_system
        
        # 如果正在播放捕捉动画，不处理任何点击
        if hasattr(self.game_loop.ui, 'catch_animation_state') and \
           self.game_loop.ui.catch_animation_state is not None:
            return
        
        # 如果正在显示道具列表，处理道具点击
        if battle_system.showing_items:
            current_player = self.game_loop.players[self.game_loop.current_player_index]
            for i, item in enumerate(current_player.items):
                if self._is_in_rect(pos, (600, 350 + i * 50, 260, 40)):
                    result = battle_system.use_item(i)
                    battle_system.showing_items = False  # 使用后关闭道具列表
                    return
            # 点击道具列表外的区域关闭道具列表
            if not self._is_in_rect(pos, (580, 300, 300, 400)):
                battle_system.showing_items = False
            return
        
        print(f"[DEBUG] 处理战斗界面点击")
        
        # 检查退出按钮
        if self._is_in_rect(pos, (50, 650, 120, 50)):
            print("[DEBUG] 点击战斗退出按钮 - 必须完成战斗或成功逃跑才能离开")
            return  # 不允许直接退出
        
        # 检查技能按钮
        for i in range(4):
            if self._is_in_rect(pos, (100, 500 + i * 50, 200, 40)):
                print(f"[DEBUG] 点击技能按钮 {i}")
                result = self.game_loop.battle_system.execute_turn(i)
                print(f"[DEBUG] 战斗回合结果: {result}")
                if result in ["ATTACKER_WIN", "ESCAPED"]:
                    self.game_loop.end_turn()  # 战斗结束时切换玩家
                return
            
        if not self.game_loop.battle_system.is_pvp:
            # 检查逃跑按钮
            if self._is_in_rect(pos, (900, 500, 100, 50)):
                print("[DEBUG] 点击逃跑按钮")
                result = self.game_loop.battle_system.execute_turn(0, is_trying_escape=True)
                if result == "ESCAPED":
                    self.game_loop.end_turn()
                return
            
            # 检查捕捉按钮
            if self._is_in_rect(pos, (900, 560, 100, 50)):
                print("[DEBUG] 点击捕捉按钮")
                success, message = self.game_loop.battle_system.try_catch_pokemon()
                print(f"[DEBUG] 捕捉结果: {message}")
                if success:
                    # 等待动画完成后再结束战斗
                    def end_battle():
                        self.game_loop.game_state = "WAITING_FOR_ROLL"
                        self.game_loop.end_turn()
                    self.game_loop.ui.on_catch_animation_complete = end_battle
                return
            
            # 检查道具按钮
            if self._is_in_rect(pos, (900, 620, 100, 50)):
                print("[DEBUG] 点击道具按钮")
                battle_system.toggle_items_panel()
                return

    def _handle_shop_click(self, pos):
        """处理商店界面的点击"""
        current_player = self.game_loop.players[self.game_loop.current_player_index]
        
        # 检查退出按钮点击
        if self._is_in_rect(pos, (50, 650, 120, 50)):
            print("[DEBUG] 离开商店")
            self.game_loop.game_state = "WAITING_FOR_ROLL"
            self.game_loop.end_turn()  # 离开商店时结束回合
            return
        
        # 检查购买按钮点击
        items = self.game_loop.shop_system.get_item_list()
        for i, (item_name, price) in enumerate(items):
            if self._is_in_rect(pos, (520, 100 + i * 60, 100, 50)):
                success, message = self.game_loop.shop_system.buy_item(current_player, item_name)
                if success:
                    self.game_loop.sound_system.play_sound("buy_success")
                else:
                    self.game_loop.sound_system.play_sound("buy_fail")
                return
                
    def _handle_tutorial_click(self, pos):
        """处理教程界面的点击"""
        # 检查是否点击了下一步按钮
        if self._is_in_rect(pos, (880, 450, 180, 50)):
            next_step = self.game_loop.tutorial_system.next_step()
            if not next_step:
                self.game_loop.game_state = "WAITING_FOR_ROLL"
                
    def _handle_pokemon_center_click(self, pos):
        """处理宝可梦中心界面的点击"""
        # 检查退出按钮
        if self._is_in_rect(pos, (50, 650, 120, 50)):
            self.game_loop.game_state = "WAITING_FOR_ROLL"
            return
        
    def _handle_learn_move_click(self, pos):
        """处理技能学习界面的点击"""
        current_pokemon = self.game_loop.current_learning_pokemon
        learnable_moves = self.game_loop.skill_system.get_learnable_moves(current_pokemon)
        
        # 检查退出按钮
        if self._is_in_rect(pos, (50, 650, 120, 50)):
            self.game_loop.game_state = "WAITING_FOR_ROLL"
            return
        
        # 检查学习按钮
        for i, move_data in enumerate(learnable_moves):
            if self._is_in_rect(pos, (500, 360 + i * 40, 100, 35)):
                success, message = current_pokemon.learn_new_move(move_data)
                if success:
                    self.game_loop.sound_system.play_sound("learn_move")
                self.game_loop.game_state = "WAITING_FOR_ROLL"
                return
        
    def _handle_battle_item_click(self, pos):
        """处理战斗道具界面的点击"""
        current_player = self.game_loop.players[self.game_loop.current_player_index]
        
        # 检查退出按钮
        if self._is_in_rect(pos, (50, 650, 120, 50)):
            self.game_loop.game_state = "IN_BATTLE"
            return
        
        # 检查道具使用按钮
        for i, item in enumerate(current_player.items):
            if self._is_in_rect(pos, (700, 100 + i * 60, 100, 50)):
                result = self.game_loop.battle_system.use_item(i)
                self.game_loop.game_state = "IN_BATTLE"
                return
        
    def _is_in_rect(self, pos, rect):
        """检查点击位置是否在矩形区域内"""
        x, y = pos
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def _use_item_from_inventory(self, item_index):
        """从背包使用道具"""
        current_player = self.game_loop.players[self.game_loop.current_player_index]
        if item_index >= len(current_player.items):
            return False
        
        # 获���玩家的第一个宝可梦作为道具使用目标
        if not current_player.pokemons:
            return False
        
        target_pokemon = current_player.pokemons[0]
        return current_player.use_item(item_index, target_pokemon)
