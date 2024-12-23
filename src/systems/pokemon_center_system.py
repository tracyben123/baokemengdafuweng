class PokemonCenterSystem:
    def __init__(self):
        pass
        
    def heal_all_pokemon(self, player):
        """恢复玩家所有宝可梦的状态"""
        for pokemon in player.pokemons:
            pokemon.restore_all()
        return True 