from src.models.pokemon import Pokemon
from src.models.move import Move
import random

class GymSystem:
    def __init__(self):
        self.game_loop = None
        self.gym_leaders = {
            "FIRE": {
                "name": "小茂",
                "pokemon": ["喷火龙", "九尾", "快泳蜥"],
                "badge": "火焰徽章",
                "reward_coins": 5000
            },
            "WATER": {
                "name": "小霞",
                "pokemon": ["暴鲤龙", "水箭龟", "宝石海星"],
                "badge": "水滴徽章",
                "reward_coins": 5000
            },
            "GRASS": {
                "name": "小菊儿",
                "pokemon": ["妙蛙花", "大食花", "蘑菇王"],
                "badge": "森林徽章",
                "reward_coins": 5000
            },
            "ELECTRIC": {
                "name": "马志士",
                "pokemon": ["雷丘", "电击兽", "顽皮雷弹"],
                "badge": "雷电徽章",
                "reward_coins": 5000
            }
        }
        
    def challenge_gym(self, player, gym_type):
        """挑战道馆"""
        # 检查是否已获得该徽章
        if gym_type in player.badges:
            if self.game_loop:
                self.game_loop.last_message = "已获得此徽章"
            return False, {"error": "已获得此徽章"}
            
        # 检查玩家宝可梦等级是否达标
        min_level = 20  # 可以根据道馆调整
        if not any(p.level >= min_level for p in player.pokemons):
            if self.game_loop:
                self.game_loop.last_message = f"需要至少一只{min_level}级宝可梦才能挑战道馆"
            return False, {"error": f"需要至少一只{min_level}级宝可梦"}
            
        # 获取道馆信息
        gym_info = self.gym_leaders.get(gym_type)
        if not gym_info:
            return False, {"error": "无效的道馆类型"}
            
        # 生成道馆宝可梦
        max_player_level = max(p.level for p in player.pokemons)
        gym_pokemon = self._generate_gym_pokemon(gym_type, max_player_level)
        
        return True, {
            "pokemon": gym_pokemon,
            "leader_name": gym_info["name"],
            "badge": gym_info["badge"],
            "reward_coins": gym_info["reward_coins"]
        }
        
    def _generate_gym_pokemon(self, gym_type, player_level):
        """生成道馆宝可梦"""
        gym_info = self.gym_leaders[gym_type]
        
        # 选择一只道馆宝可梦
        pokemon_name = random.choice(gym_info["pokemon"])
        
        # 设置等级（略高于玩家最高等级）
        level = min(player_level + 2, 50)
        
        # 创建宝可梦实例
        pokemon = Pokemon(pokemon_name, gym_type, level)
        
        # 添加技能
        moves = self._get_gym_moves(gym_type)
        for move_data in moves:
            pokemon.learn_skill(Move(*move_data))
            
        return pokemon
        
    def _get_gym_moves(self, gym_type):
        """获取道馆宝可梦的技能列表"""
        # 基础技能
        moves = [("撞击", "NORMAL", 40, 35)]
        
        # 属性技能
        if gym_type == "FIRE":
            moves.extend([
                ("火花", "FIRE", 40, 25),
                ("火焰轮", "FIRE", 60, 25),
                ("喷射火焰", "FIRE", 90, 15)
            ])
        elif gym_type == "WATER":
            moves.extend([
                ("水枪", "WATER", 40, 25),
                ("水流喷射", "WATER", 60, 25),
                ("水炮", "WATER", 90, 15)
            ])
        elif gym_type == "GRASS":
            moves.extend([
                ("藤鞭", "GRASS", 40, 25),
                ("飞叶快刀", "GRASS", 60, 25),
                ("日光束", "GRASS", 90, 15)
            ])
        elif gym_type == "ELECTRIC":
            moves.extend([
                ("电击", "ELECTRIC", 40, 25),
                ("雷电拳", "ELECTRIC", 60, 25),
                ("十万伏特", "ELECTRIC", 90, 15)
            ])
            
        # 随机选择3个技能
        return [moves[0]] + random.sample(moves[1:], 2)
        
    def award_badge(self, player, gym_type):
        """授予徽章"""
        gym_info = self.gym_leaders.get(gym_type)
        if gym_info and gym_type not in player.badges:
            player.badges.append(gym_type)
            player.add_coins(gym_info["reward_coins"])
            return True, f"获得{gym_info['badge']}和{gym_info['reward_coins']}金币！"
        return False, "无法获得徽章"