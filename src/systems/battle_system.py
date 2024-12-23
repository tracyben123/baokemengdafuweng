from random import random, choice

class BattleSystem:
    def __init__(self, game_loop=None):
        self.game_loop = game_loop
        self.current_attacker = None
        self.current_defender = None
        self.current_attacker_pokemon = None
        self.current_defender_pokemon = None
        self.is_pvp = False
        self.turn = 0
        self.showing_items = False  # 添加道具列表显示状态
        
    def start_battle(self, attacker, defender, is_pvp=False):
        """开始战斗"""
        self.current_attacker = attacker
        self.current_defender = defender
        self.is_pvp = is_pvp
        
        # 选择第一个未失去战斗能力的宝可梦
        self.current_attacker_pokemon = next(
            (p for p in attacker.pokemons if not p.is_fainted()), None)
        if not self.current_attacker_pokemon:
            raise ValueError("攻击方没有可用的宝可梦")
            
        if is_pvp:
            self.current_defender_pokemon = next(
                (p for p in defender.pokemons if not p.is_fainted()), None)
            if not self.current_defender_pokemon:
                raise ValueError("防守方没有可用的宝可梦")
        else:
            self.current_defender_pokemon = defender  # 野生宝可梦
            
        self.turn = 0
        print("[DEBUG] 战斗开始")  # 添加调试信息
        
    def try_catch_pokemon(self):
        """尝试捕获宝可梦"""
        if self.is_pvp:
            return False, "不能捕获训练师的宝可梦"
            
        # 计算捕获率
        base_catch_rate = 0.3
        hp_factor = 1 - (self.current_defender_pokemon.hp / self.current_defender_pokemon.max_hp)
        catch_rate = base_catch_rate * (1 + hp_factor)
        
        success = random() < catch_rate
        
        # 启动捕捉动画
        if hasattr(self.game_loop, 'ui'):
            self.game_loop.ui.start_catch_animation(success)
            # 等待动画完成后再处理结果
            if success:
                # 将宝可梦添加到玩家的队伍中，但暂不改变游戏状态
                self.current_attacker.add_pokemon(self.current_defender_pokemon)
                return True, f"成功捕获了{self.current_defender_pokemon.name}！"
            else:
                return False, f"{self.current_defender_pokemon.name}挣脱了精灵球！"
        
    def execute_turn(self, move_index, is_trying_escape=False):
        """执行回合"""
        print(f"[DEBUG] 执行战斗回合: move_index={move_index}, is_trying_escape={is_trying_escape}")
        print(f"[DEBUG] 我方HP: {self.current_attacker_pokemon.hp}/{self.current_attacker_pokemon.max_hp}")
        print(f"[DEBUG] 敌方HP: {self.current_defender_pokemon.hp}/{self.current_defender_pokemon.max_hp}")
        self.turn += 1
        
        if is_trying_escape and not self.is_pvp:
            # 尝试逃跑
            escape_chance = 0.7 + 0.15 * self.turn
            if random() < escape_chance:
                print("[DEBUG] 逃跑成功")
                self.game_loop.game_state = "WAITING_FOR_ROLL"
                return "ESCAPED"
            else:
                print("[DEBUG] 逃跑失败")
                # 逃跑失败后，野生宝可梦会反击
                return self._enemy_counter_attack()
        
        # 使用技能
        if 0 <= move_index < len(self.current_attacker_pokemon.moves):
            move = self.current_attacker_pokemon.moves[move_index]
            if move.use():  # 检查PP
                # 我方攻击
                damage = self.current_attacker_pokemon.calculate_damage(
                    move, self.current_defender_pokemon)
                print(f"[DEBUG] 我方造成伤害: {damage}")
                
                if self.current_defender_pokemon.take_damage(damage):
                    print("[DEBUG] 目标失去战斗能力")
                    # 计算并给予经验值
                    exp_gain = self.calculate_exp_gain()
                    print(f"[DEBUG] 获得经验值: {exp_gain}")
                    self.current_attacker_pokemon.gain_exp(exp_gain)
                    
                    if self.is_pvp:
                        next_pokemon = next(
                            (p for p in self.current_defender.pokemons if not p.is_fainted()),
                            None)
                        if not next_pokemon:
                            self.game_loop.game_state = "WAITING_FOR_ROLL"
                            return "ATTACKER_WIN"
                        self.current_defender_pokemon = next_pokemon
                    else:
                        self.game_loop.game_state = "WAITING_FOR_ROLL"
                        return "ATTACKER_WIN"
                
                # 如果是PVP战斗，交换攻守方
                if self.is_pvp:
                    self.current_attacker, self.current_defender = (
                        self.current_defender, self.current_attacker)
                    self.current_attacker_pokemon, self.current_defender_pokemon = (
                        self.current_defender_pokemon, self.current_attacker_pokemon)
                else:
                    # 野生宝可梦反击
                    return self._enemy_counter_attack()
                
        return "CONTINUE"
    
    def _enemy_counter_attack(self):
        """敌方宝可梦反击"""
        # 降低敌方伤害
        damage_multiplier = 0.7  # 敌方伤害降低30%
        
        # 随机选择一个可用的技能
        available_moves = [m for m in self.current_defender_pokemon.moves if m.pp > 0]
        if not available_moves:
            print("[DEBUG] 敌方无可用技能")
            return "CONTINUE"
        
        enemy_move = choice(available_moves)
        enemy_move.use()
        
        # 计算伤害时应用降低系数
        damage = int(self.current_defender_pokemon.calculate_damage(
            enemy_move, self.current_attacker_pokemon) * damage_multiplier)
        print(f"[DEBUG] 敌方使用{enemy_move.name}造成伤害: {damage}")
        
        # 造成伤害
        if self.current_attacker_pokemon.take_damage(damage):
            print("[DEBUG] 我方宝可梦失去战斗能力")
            if self.is_pvp:
                next_pokemon = next(
                    (p for p in self.current_attacker.pokemons if not p.is_fainted()),
                    None)
                if not next_pokemon:
                    self.game_loop.game_state = "WAITING_FOR_ROLL"
                    return "DEFENDER_WIN"
                self.current_attacker_pokemon = next_pokemon
            else:
                self.game_loop.game_state = "WAITING_FOR_ROLL"
                return "DEFENDER_WIN"
            
        return "CONTINUE"
    
    def calculate_exp_gain(self):
        """计算战斗胜利后获得的经验值"""
        if self.is_pvp:
            # PVP战斗经验值计算
            level_diff = self.current_defender_pokemon.level - self.current_attacker_pokemon.level
            base_exp = 50  # 基础经验值
            return base_exp * (1 + max(0, level_diff) * 0.1)  # 每高1级增加10%经验值
        else:
            # 野生宝可梦战斗经验值计算
            wild_level = self.current_defender_pokemon.level
            base_exp = 30  # 野战基础经验值较低
            hp_percent = self.current_defender_pokemon.hp / self.current_defender_pokemon.max_hp
            # 剩余血量越少，经验值越高
            return base_exp * (1 + wild_level * 0.1) * (2 - hp_percent)
    
    def use_item(self, item_index):
        """在战斗中使用道具"""
        if self.is_pvp:
            return False, "对战中不能使用道具"
        
        success = self.current_attacker.use_item(
            item_index, 
            self.current_attacker_pokemon
        )
        
        if success:
            # 使用道具后，敌方会进行反击
            return self._enemy_counter_attack()
        
        return "CONTINUE"
    
    def toggle_items_panel(self):
        """切换道具列表显示状态"""
        self.showing_items = not self.showing_items