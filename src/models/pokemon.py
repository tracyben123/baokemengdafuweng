from src.models.type_chart import TypeChart
from src.models.move import Move
from random import random, uniform

class Pokemon:
    def __init__(self, name, type, level=5, moves=None):
        self.name = name
        self.type = type
        self.level = level
        
        # 基础属性
        self.max_hp = 20 + level * 5
        self.hp = self.max_hp
        self.attack = 10 + level * 2
        self.defense = 10 + level * 2
        self.speed = 10 + level * 2
        
        # 经验值
        self.exp = 0
        self.exp_needed = level * 100
        
        # 技能列表
        self.moves = []
        if moves:
            for move_data in moves:
                name, move_type, power, pp = move_data
                self.moves.append(Move(name, move_type, power, pp))
                
        # 状态
        self.status = None
        
        # 属性相克表
        self.type_chart = TypeChart()
        
    def restore_all(self):
        """完全恢复状态"""
        # 恢复HP
        self.hp = self.max_hp
        # 恢复所有技能的PP
        for move in self.moves:
            move.restore()
        # 清除异常状态
        self.status = None
        
    def heal(self, amount):
        """恢复指定数值的HP"""
        self.hp = min(self.hp + amount, self.max_hp)
        
    def take_damage(self, damage):
        """受到伤害"""
        self.hp = max(0, self.hp - damage)
        return self.is_fainted()
        
    def is_fainted(self):
        """检查是否失去战斗能力"""
        return self.hp <= 0
        
    def gain_exp(self, exp_amount):
        """获得经验值"""
        # 计算升级所需经验值
        exp_needed = self.level * 100  # 每级需要的经验值随等级增加
        
        # 累加经验值并检查是否升级
        self.exp += exp_amount
        while self.exp >= exp_needed:
            self.level_up()
            self.exp -= exp_needed
            exp_needed = self.level * 100  # 更新下一级所需经验值
        
    def level_up(self):
        """升级"""
        self.level += 1
        # 属性提升
        self.max_hp += 5
        self.hp = self.max_hp  # 升级时恢复满血
        self.attack += 2
        self.defense += 2
        self.speed += 2
        
    def calculate_damage(self, move, target):
        """计算技能伤害"""
        # 基础伤害公式调整
        base_damage = (2 * self.level / 5 + 2) * move.power * self.attack / target.defense / 40 + 2
        
        # 属性相克加成
        type_multiplier = self.type_chart.get_multiplier(move.type, target.type)
        
        # 随机波动（0.85-1.0）
        random_factor = uniform(0.85, 1.0)
        
        # 添加暴击机制
        crit_chance = 0.1  # 10%暴击率
        crit_multiplier = 1.5  # 暴击伤害1.5倍
        if random() < crit_chance:
            print("[DEBUG] 暴击！")
            return int(base_damage * type_multiplier * random_factor * crit_multiplier)
        
        return int(base_damage * type_multiplier * random_factor)
        
    def learn_new_move(self, move_data):
        """学习新技能"""
        name, move_type, power, pp = move_data
        
        # 如果技能栏已满，需要先遗忘一个技能
        if len(self.moves) >= 4:
            return False, "技能栏已满"
        
        # 创建新技能
        new_move = Move(name, move_type, power, pp)
        self.moves.append(new_move)
        return True, f"学会了{name}！"
        
    def forget_move(self, move_index):
        """遗忘技能"""
        if 0 <= move_index < len(self.moves):
            forgotten_move = self.moves.pop(move_index)
            return True, f"遗忘了{forgotten_move.name}"
        return False, "无效的技能索引"