class PlayerEncounterSystem:
    def __init__(self, battle_system):
        self.battle_system = battle_system
    
    def check_player_encounter(self, players):
        """检查玩家是否相遇"""
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                if self._is_same_position(players[i], players[j]):
                    return players[i], players[j]
        return None, None
    
    def _is_same_position(self, player1, player2):
        """检查两个玩家是否在同一位置"""
        return (player1.position == player2.position and 
                player1.current_ring == player2.current_ring)
    
    def handle_player_encounter(self, player1, player2):
        """处理玩家相遇事件"""
        # 强制PVP战斗
        self.battle_system.start_battle(player1, player2, is_pvp=True)
        return "IN_PVP_BATTLE" 