class Skill:
    def __init__(self, name, type, power, pp):
        self.name = name
        self.type = type
        self.power = power
        self.pp = pp
        self.max_pp = pp

    def use(self):
        if self.pp > 0:
            self.pp -= 1
            return True
        return False

    def restore(self):
        self.pp = self.max_pp 