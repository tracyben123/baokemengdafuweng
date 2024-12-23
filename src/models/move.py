class Move:
    def __init__(self, name, type, power, pp):
        self.name = name
        self.type = type
        self.power = power
        self.pp = pp
        self.max_pp = pp
        
    def use(self):
        """使用技能，返回是否使用成功"""
        if self.pp > 0:
            self.pp -= 1
            return True
        return False
        
    def restore(self):
        """恢复PP值"""
        self.pp = self.max_pp