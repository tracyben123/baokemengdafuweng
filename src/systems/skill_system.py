class SkillSystem:
    def __init__(self):
        # 技能数据库
        self.skill_database = {
            "NORMAL": {
                "基础": [
                    ("撞击", 40, 35, {"desc": "普通的撞击攻击"}),
                    ("电光一闪", 40, 30, {"desc": "快速的攻击，容易命中", "priority": 1}),
                    ("猛撞", 85, 15, {"desc": "强力的撞击，可能会受到反伤", "recoil": 0.25})
                ],
                "进阶": [
                    ("破坏死光", 150, 5, {"desc": "需要蓄力的超强光线", "charge": 1}),
                    ("终极冲击", 120, 10, {"desc": "全力的撞击，有反伤", "recoil": 0.33})
                ]
            },
            "FIRE": {
                "基础": [
                    ("火花", 40, 25, {"desc": "小型火焰攻击", "burn_chance": 0.1}),
                    ("火焰轮", 60, 25, {"desc": "火焰包裹的冲撞", "burn_chance": 0.1})
                ],
                "进阶": [
                    ("喷射火焰", 90, 15, {"desc": "强力的火焰喷射", "burn_chance": 0.2}),
                    ("大字爆炎", 110, 5, {"desc": "爆炸性的火焰攻击", "burn_chance": 0.3})
                ]
            },
            "WATER": {
                "基础": [
                    ("水枪", 40, 25),
                    ("水流喷射", 60, 25)
                ],
                "进阶": [
                    ("水炮", 90, 15),
                    ("冲浪", 110, 5)
                ]
            },
            "GRASS": {
                "基础": [
                    ("藤鞭", 40, 25),
                    ("飞叶快刀", 60, 25)
                ],
                "进阶": [
                    ("日光束", 90, 15),
                    ("飞叶风暴", 110, 5)
                ]
            },
            "ELECTRIC": {
                "基础": [
                    ("电击", 40, 25),
                    ("雷电拳", 60, 25)
                ],
                "进阶": [
                    ("十万伏特", 90, 15),
                    ("打雷", 110, 5)
                ]
            },
            "PSYCHIC": {
                "基础": [
                    ("念力", 40, 25),
                    ("精神波", 60, 25)
                ],
                "进阶": [
                    ("精神强念", 90, 15),
                    ("精神冲击", 110, 5)
                ]
            },
            "FIGHTING": {
                "基础": [
                    ("空手劈", 40, 25),
                    ("连续拳", 60, 25)
                ],
                "进阶": [
                    ("爆裂拳", 90, 15),
                    ("真气拳", 110, 5)
                ]
            },
            "FLYING": {
                "基础": [
                    ("啄", 40, 25),
                    ("翅膀攻击", 60, 25)
                ],
                "进阶": [
                    ("空气斩", 90, 15),
                    ("暴风", 110, 5)
                ]
            },
            "GROUND": {
                "基础": [
                    ("泥巴射击", 40, 25),
                    ("震级", 60, 25)
                ],
                "进阶": [
                    ("地震", 90, 15),
                    ("裂地", 110, 5)
                ]
            },
            "ROCK": {
                "基础": [
                    ("落石", 40, 25),
                    ("岩石封锁", 60, 25)
                ],
                "进阶": [
                    ("岩崩", 90, 15),
                    ("尖石攻击", 110, 5)
                ]
            },
            "BUG": {
                "基础": [
                    ("虫咬", 40, 25),
                    ("银色旋风", 60, 25)
                ],
                "进阶": [
                    ("虫鸣", 90, 15),
                    ("超级角击", 110, 5)
                ]
            },
            "GHOST": {
                "基础": [
                    ("舌舔", 40, 25),
                    ("暗影拳", 60, 25)
                ],
                "进阶": [
                    ("暗影球", 90, 15),
                    ("暗影潜袭", 110, 5)
                ]
            },
            "ICE": {
                "基础": [
                    ("冰砾", 40, 25),
                    ("冰冻之风", 60, 25)
                ],
                "进阶": [
                    ("冰冻光束", 90, 15),
                    ("暴风雪", 110, 5)
                ]
            },
            "DRAGON": {
                "基础": [
                    ("龙爪", 40, 25),
                    ("龙息", 60, 25)
                ],
                "进阶": [
                    ("龙之波动", 90, 15),
                    ("流星群", 110, 5)
                ]
            },
            "DARK": {
                "基础": [
                    ("咬住", 40, 25),
                    ("恶意追��", 60, 25)
                ],
                "进阶": [
                    ("恶之波动", 90, 15),
                    ("恶之遗传", 110, 5)
                ]
            },
            "STEEL": {
                "基础": [
                    ("金属爪", 40, 25),
                    ("铁头", 60, 25)
                ],
                "进阶": [
                    ("铁尾", 90, 15),
                    ("陨石光束", 110, 5)
                ]
            },
            "FAIRY": {
                "基础": [
                    ("妖精之风", 40, 25),
                    ("魅惑之声", 60, 25)
                ],
                "进阶": [
                    ("月亮之力", 90, 15),
                    ("破灭之光", 110, 5)
                ]
            },
            "POISON": {
                "基础": [
                    ("毒针", 40, 25),
                    ("溶解液", 60, 25)
                ],
                "进阶": [
                    ("污泥炸弹", 90, 15),
                    ("垃圾射击", 110, 5)
                ]
            },
            "STATUS": {
                "基础": [
                    ("生长", 0, 20, {"desc": "提升特攻", "boost": {"sp_atk": 1}}),
                    ("剑舞", 0, 20, {"desc": "大幅提升攻击", "boost": {"atk": 2}}),
                    ("变圆", 0, 20, {"desc": "提升防御", "boost": {"def": 1}}),
                    ("高速移动", 0, 20, {"desc": "提升速度", "boost": {"speed": 2}})
                ],
                "进阶": [
                    ("健美", 0, 10, {"desc": "提升攻击和防御", "boost": {"atk": 1, "def": 1}}),
                    ("冥想", 0, 10, {"desc": "提升特攻和特防", "boost": {"sp_atk": 1, "sp_def": 1}}),
                    ("龙之舞", 0, 10, {"desc": "提升攻击和速度", "boost": {"atk": 1, "speed": 1}})
                ]
            },
            "DEBUFF": {
                "基础": [
                    ("瞪眼", 0, 20, {"desc": "降低防御", "debuff": {"def": -1}}),
                    ("叫声", 0, 20, {"desc": "降低攻击", "debuff": {"atk": -1}}),
                    ("烟幕", 0, 20, {"desc": "降低命中率", "debuff": {"accuracy": -1}})
                ],
                "进阶": [
                    ("诡异光线", 0, 10, {"desc": "降低特防", "debuff": {"sp_def": -1}}),
                    ("影子偷袭", 0, 10, {"desc": "降低速度", "debuff": {"speed": -1}})
                ]
            }
        }
        
    def get_learnable_moves(self, pokemon):
        """获取宝可梦可以学习的技能列表"""
        moves = []
        
        # 添加同属性技能
        if pokemon.type in self.skill_database:
            # 基础技能
            moves.extend([
                (name, pokemon.type, power, pp, effects)
                for name, power, pp, effects in self.skill_database[pokemon.type]["基础"]
            ])
            
            # 进阶技能（需要达到一定等级）
            if pokemon.level >= 35:
                moves.extend([
                    (name, pokemon.type, power, pp, effects)
                    for name, power, pp, effects in self.skill_database[pokemon.type]["进阶"]
                ])
                
        # 添加一般属性技能
        moves.extend([
            (name, "NORMAL", power, pp, effects)
            for name, power, pp, effects in self.skill_database["NORMAL"]["基础"]
        ])
        
        # 添加状态技能（根据等级）
        if pokemon.level >= 20:
            moves.extend([
                (name, "STATUS", 0, pp, effects)
                for name, power, pp, effects in self.skill_database["STATUS"]["基础"]
            ])
            
        if pokemon.level >= 40:
            moves.extend([
                (name, "STATUS", 0, pp, effects)
                for name, power, pp, effects in self.skill_database["STATUS"]["进阶"]
            ])
        
        return moves
        
    def can_learn_new_move(self, pokemon):
        """检查是否可以学习新技能"""
        # 每5级可以学习一个新技能
        return pokemon.level % 5 == 0 and len(pokemon.moves) < 4 