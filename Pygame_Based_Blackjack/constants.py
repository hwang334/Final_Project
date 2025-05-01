# constants.py
import pygame
import os
from enum import Enum

# 初始化pygame
pygame.init()

# 屏幕尺寸
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 100, 0)  # 深绿色，更像赌桌
DARK_GREEN = (0, 80, 0)
BRIGHT_GREEN = (0, 150, 0)
RED = (220, 20, 60)  # 更鲜艳的红色
BLUE = (25, 25, 112)  # 深蓝色
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)
DARK_RED = (139, 0, 0)
TABLE_GREEN = (53, 101, 77)  # 赌桌绿
FELT_GREEN = (34, 139, 34)
PURPLE = (128, 0, 128)
ORANGE = (255, 140, 0)
CREAM = (255, 253, 208)  # 米色，用于装饰

# 卡牌尺寸
CARD_WIDTH = 100
CARD_HEIGHT = 140

# 定义扑克牌花色
class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"
