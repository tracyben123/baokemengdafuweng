class TypeChart:
    def __init__(self):
        # 属性相克表
        self.type_chart = {
            "NORMAL": {
                "effective": [],
                "not_effective": ["ROCK", "STEEL"],
                "immune": ["GHOST"]
            },
            "FIRE": {
                "effective": ["GRASS", "ICE", "BUG", "STEEL"],
                "not_effective": ["FIRE", "WATER", "ROCK", "DRAGON"],
                "immune": []
            },
            "WATER": {
                "effective": ["FIRE", "GROUND", "ROCK"],
                "not_effective": ["WATER", "GRASS", "DRAGON"],
                "immune": []
            },
            "ELECTRIC": {
                "effective": ["WATER", "FLYING"],
                "not_effective": ["ELECTRIC", "GRASS", "DRAGON"],
                "immune": ["GROUND"]
            },
            "GRASS": {
                "effective": ["WATER", "GROUND", "ROCK"],
                "not_effective": ["FIRE", "GRASS", "POISON", "FLYING", "BUG", "DRAGON", "STEEL"],
                "immune": []
            }
        }
        
    def get_multiplier(self, move_type, target_type):
        """计算属性克制倍率"""
        if target_type in self.type_chart.get(move_type, {}).get("immune", []):
            return 0
        elif target_type in self.type_chart.get(move_type, {}).get("effective", []):
            return 2
        elif target_type in self.type_chart.get(move_type, {}).get("not_effective", []):
            return 0.5
        return 1 