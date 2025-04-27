# effects.py
import pygame
import random
from constants import *

class Particle:
    def __init__(self, x, y, color, size=5, life=30):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -1)
        self.color = color
        self.size = size
        self.life = life
        self.original_life = life
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # 添加重力
        self.life -= 1
        
    def draw(self, screen):
        alpha = int(255 * (self.life / self.original_life))
        radius = int(self.size * (self.life / self.original_life))
        
        # 创建一个临时表面来绘制半透明粒子
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            s, 
            (self.color[0], self.color[1], self.color[2], alpha), 
            (self.size, self.size), 
            radius
        )
        screen.blit(s, (self.x - self.size, self.y - self.size))