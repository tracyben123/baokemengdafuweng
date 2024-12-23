import pygame
from ui.game_ui import GameUI
from models.player import Player
from game_loop import GameLoop

def main():
    # 初始化pygame
    pygame.init()
    
    # 创建游戏实例
    game = GameLoop()
    
    # 创建UI实例
    game.ui = GameUI()
    
    # 开始新游戏
    game.start_new_game()
    
    # 游戏主循环
    running = True
    while running:
        # 处理事件
        running = game.event_system.handle_events()
        
        # 更新游戏状态
        game.update()
        
        # 绘制当前界面
        game.ui.draw_current_screen(game)
        
        # 更新显示
        pygame.display.flip()
    
    # 退出游戏
    pygame.quit()

if __name__ == "__main__":
    main() 