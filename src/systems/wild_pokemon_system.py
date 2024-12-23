from models.pokemon import Pokemon
from models.move import Move
import random

class WildPokemonSystem:
    def __init__(self):
        # 定义不同等级的宝可梦池
        self.common_pokemon_pool = [
            ("小拉达", [
                ("撞击", "NORMAL", 40, 35),
                ("电光一闪", "NORMAL", 40, 30)
            ], "NORMAL"),
            ("喇叭芽", [
                ("藤鞭", "GRASS", 40, 25),
                ("吸取", "GRASS", 35, 30)
            ], "GRASS"),
            ("走路草", [
                ("藤鞭", "GRASS", 40, 25),
                ("撞击", "NORMAL", 40, 35)
            ], "GRASS")
        ]
        
        self.medium_pokemon_pool = [
            ("皮卡丘", [
                ("电击", "ELECTRIC", 40, 30),
                ("电光一闪", "NORMAL", 40, 30),
                ("十万伏特", "ELECTRIC", 90, 15)
            ], "ELECTRIC"),
            ("小火马", [
                ("火花", "FIRE", 40, 25),
                ("踢", "NORMAL", 35, 35),
                ("火焰轮", "FIRE", 60, 25)
            ], "FIRE")
        ]
        
        self.rare_pokemon_pool = [
            ("海星星", [
                ("水枪", "WATER", 40, 25),
                ("高速旋转", "NORMAL", 35, 35),
                ("水炮", "WATER", 90, 15)
            ], "WATER"),
            ("六尾", [
                ("火花", "FIRE", 40, 25),
                ("电光一闪", "NORMAL", 40, 30),
                ("喷射火焰", "FIRE", 90, 15)
            ], "FIRE")
        ]

    def generate_wild_pokemon(self, player_level):
        """生成野生宝可梦"""
        # 降低遇到高等级宝可梦的概率
        level = max(1, random.randint(
            max(1, player_level - 3),
            player_level + (1 if random.random() < 0.2 else 0)
        ))
        
        # 根据等级调整宝可梦种类
        if level >= 15:
            pokemon_pool = self.rare_pokemon_pool
        elif level >= 8:
            pokemon_pool = self.medium_pokemon_pool
        else:
            pokemon_pool = self.common_pokemon_pool
        
        pokemon_data = random.choice(pokemon_pool)
        return self._create_pokemon(pokemon_data, level)
        
    def _create_pokemon(self, pokemon_data, level):
        name = pokemon_data[0]
        moves = pokemon_data[1]
        
        # 创建宝可梦实例
        pokemon = Pokemon(name, pokemon_data[2], level)
        
        # 添加技能
        for move_data in moves:
            name, move_type, power, pp = move_data
            pokemon.learn_new_move((name, move_type, power, pp))
            
        return pokemon 