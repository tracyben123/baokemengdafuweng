import pygame

class TutorialSystem:
    def __init__(self):
        self.current_step = 0
        self.tutorial_steps = [
            {
                "title": "游戏基础",
                "content": "欢迎来到宝可梦大富翁！在这里你将扮演一名宝可梦训练师，环游世界收服宝可梦。",
                "highlight_area": None
            },
            {
                "title": "移动规则",
                "content": "按空格键投掷骰子，你的角色将根据点数在棋盘上移动。",
                "highlight_area": (100, 650, 200, 50)  # 骰子按钮区域
            },
            {
                "title": "格子类型",
                "content": "棋盘上有不同类型的格子：\n红色-宝可梦中心\n绿色-商店\n灰色-野生宝可梦\n黄色-道馆\n蓝色-传送门",
                "highlight_area": None
            },
            {
                "title": "战斗系统",
                "content": "遇到野生宝可梦或其他训练师时，将进入战斗。选择技能进行攻击，或尝试捕获野生宝可梦。",
                "highlight_area": None
            },
            {
                "title": "商店系统",
                "content": "在商店可以购买各种道具，如精灵球、恢复药等。使用金币进行购买。",
                "highlight_area": None
            }
        ]
        
    def get_current_step(self):
        """获取当前教程步骤"""
        if self.current_step >= len(self.tutorial_steps):
            return None
        return self.tutorial_steps[self.current_step]
        
    def next_step(self):
        """进入下一步教程"""
        self.current_step += 1
        return self.get_current_step()
        
    def reset(self):
        """重置教程进度"""
        self.current_step = 0 