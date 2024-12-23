class Item:
    def __init__(self, name, price, effect_type, effect_value):
        self.name = name
        self.price = price
        self.effect_type = effect_type  # "hp", "pp", "attack", "defense"
        self.effect_value = effect_value
    
    def use(self, target):
        """使用道具"""
        if self.effect_type == "HEAL":
            old_hp = target.hp
            target.heal(self.effect_value)
            print(f"[DEBUG] 使用{self.name}，恢复HP: {target.hp - old_hp}")
            return True
        
        elif self.effect_type == "PP":
            restored = False
            for move in target.moves:
                if move.pp < move.max_pp:
                    old_pp = move.pp
                    move.pp = min(move.pp + self.effect_value, move.max_pp)
                    print(f"[DEBUG] 恢复技能{move.name} PP: {move.pp - old_pp}")
                    restored = True
            return restored
        
        elif self.effect_type == "HEAL_ALL":
            target.restore_all()
            print(f"[DEBUG] 使用{self.name}，完全恢复")
            return True
        
        return False