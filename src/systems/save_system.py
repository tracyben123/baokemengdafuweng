import json
import os
from datetime import datetime
from models.player import Player
from models.pokemon import Pokemon
from models.skill import Skill
from models.item import Item

class SaveSystem:
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
    def save_game(self, game_loop):
        """保存游戏状态"""
        save_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "turn_count": game_loop.turn_count,
            "current_player_index": game_loop.current_player_index,
            "players": [self._serialize_player(p) for p in game_loop.players]
        }
        
        filename = f"save_{int(datetime.now().timestamp())}.json"
        filepath = os.path.join(self.save_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
            
        return filename
        
    def load_game(self, filename):
        """加载游戏存档"""
        filepath = os.path.join(self.save_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError("存档文件不存在")
            
        with open(filepath, "r", encoding="utf-8") as f:
            save_data = json.load(f)
            
        return self._deserialize_save_data(save_data)
        
    def get_save_list(self):
        """获取所有存档文件列表"""
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.save_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    save_data = json.load(f)
                saves.append({
                    "filename": filename,
                    "timestamp": save_data["timestamp"],
                    "players": [p["name"] for p in save_data["players"]]
                })
        return saves
        
    def _serialize_player(self, player):
        """序列化玩家数据"""
        return {
            "name": player.name,
            "coins": player.coins,
            "position": player.position,
            "current_ring": player.current_ring,
            "waiting_turns": player.waiting_turns,
            "bankruptcy_support": player.bankruptcy_support,
            "badges": player.badges,
            "pokemons": [self._serialize_pokemon(p) for p in player.pokemons],
            "items": [self._serialize_item(i) for i in player.items]
        }
        
    def _serialize_pokemon(self, pokemon):
        """序列化宝可梦数��"""
        return {
            "name": pokemon.name,
            "type": pokemon.type,
            "level": pokemon.level,
            "hp": pokemon.hp,
            "max_hp": pokemon.max_hp,
            "attack": pokemon.attack,
            "defense": pokemon.defense,
            "speed": pokemon.speed,
            "exp": pokemon.exp,
            "exp_needed": pokemon.exp_needed,
            "skills": [self._serialize_skill(s) for s in pokemon.skills],
            "status": pokemon.status
        }
        
    def _serialize_skill(self, skill):
        """序列化技能数据"""
        return {
            "name": skill.name,
            "type": skill.type,
            "power": skill.power,
            "pp": skill.pp,
            "max_pp": skill.max_pp
        }
        
    def _serialize_item(self, item):
        """序列化道具数据"""
        return {
            "name": item.name,
            "price": item.price,
            "effect_type": item.effect_type,
            "effect_value": item.effect_value
        }
        
    def _deserialize_save_data(self, save_data):
        """反序列化存档数据"""
        from src.models.player import Player
        from src.models.pokemon import Pokemon
        from src.models.skill import Skill
        from src.models.item import Item
        
        players = []
        for player_data in save_data["players"]:
            player = Player(player_data["name"])
            player.coins = player_data["coins"]
            player.position = player_data["position"]
            player.current_ring = player_data["current_ring"]
            player.waiting_turns = player_data["waiting_turns"]
            player.bankruptcy_support = player_data["bankruptcy_support"]
            player.badges = player_data["badges"]
            
            # 恢复宝可梦
            for pokemon_data in player_data["pokemons"]:
                pokemon = Pokemon(pokemon_data["name"], pokemon_data["type"], pokemon_data["level"])
                pokemon.hp = pokemon_data["hp"]
                pokemon.max_hp = pokemon_data["max_hp"]
                pokemon.attack = pokemon_data["attack"]
                pokemon.defense = pokemon_data["defense"]
                pokemon.speed = pokemon_data["speed"]
                pokemon.exp = pokemon_data["exp"]
                pokemon.exp_needed = pokemon_data["exp_needed"]
                pokemon.status = pokemon_data["status"]
                
                # 恢复技能
                for skill_data in pokemon_data["skills"]:
                    skill = Skill(skill_data["name"], skill_data["type"], 
                                skill_data["power"], skill_data["max_pp"])
                    skill.pp = skill_data["pp"]
                    pokemon.learn_skill(skill)
                    
                player.add_pokemon(pokemon)
                
            # 恢复道具
            for item_data in player_data["items"]:
                item = Item(item_data["name"], item_data["price"],
                          item_data["effect_type"], item_data["effect_value"])
                player.items.append(item)
                
            players.append(player)
            
        return {
            "turn_count": save_data["turn_count"],
            "current_player_index": save_data["current_player_index"],
            "players": players
        } 