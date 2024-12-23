from src.models.item import Item

class ShopSystem:
    def __init__(self):
        self.items = {
            "精灵球": {"price": 200, "effect": "CATCH", "value": 1.2},
            "高级球": {"price": 600, "effect": "CATCH", "value": 1.5},
            "超级球": {"price": 1200, "effect": "CATCH", "value": 2.0},
            "伤药": {"price": 300, "effect": "HEAL", "value": 50},
            "好伤药": {"price": 700, "effect": "HEAL", "value": 200},
            "全满药": {"price": 2500, "effect": "HEAL", "value": 999},
            "PP恢复剂": {"price": 1000, "effect": "PP", "value": 10},
            "全体恢复药": {"price": 3000, "effect": "HEAL_ALL", "value": 100}
        }
        
    def get_item_list(self):
        """获取商品列表"""
        return [(name, info["price"]) for name, info in self.items.items()]
        
    def buy_item(self, player, item_name):
        """购买道具"""
        item_info = self.items.get(item_name)
        if not item_info:
            return False, "无效的道具"
        
        if player.coins < item_info["price"]:
            return False, "金币不足"
        
        # 限制道具数量
        if len(player.items) >= 10:
            return False, "道具栏已满"
        
        # 添加购买确认
        if not self.game_loop.ui.show_confirm_dialog(
            f"确定要购买{item_name}吗？\n价格：{item_info['price']}金币"):
            return False, "取消购买"
        
        # 创建物品实例
        item = Item(
            name=item_name,
            price=item_info["price"],
            effect_type=item_info["effect"],
            effect_value=item_info["value"]
        )
        
        # 扣除金币并添加物品
        player.coins -= item_info["price"]
        player.items.append(item)
        return True, f"购买{item_name}成功"
    
    def sell_item(self, player, item_index):
        return player.sell_item(item_index)