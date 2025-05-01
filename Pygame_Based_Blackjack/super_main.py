# main.py
import pygame
import sys
import os
from game import AdvancedBlackjackGame

def main():
    """游戏主函数"""
    # 确保assets目录存在
    os.makedirs(os.path.join("assets", "cards"), exist_ok=True)
    
    # 创建并运行游戏
    game = AdvancedBlackjackGame()
    game.run()
    
    # 退出pygame并关闭程序
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
