# gui.py
import pygame
import math
from constants import *

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, border_radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.visible = True
        self.border_radius = border_radius
        self.pulse = 0  # 用于脉冲效果
        self.pulse_direction = 1
        
    def update(self):
        # 更新脉冲效果
        if self.is_hovered:
            self.pulse += 0.1 * self.pulse_direction
            if self.pulse >= 1.0:
                self.pulse = 1.0
                self.pulse_direction = -1
            elif self.pulse <= 0.0:
                self.pulse = 0.0
                self.pulse_direction = 1
        
    def draw(self, screen, font):
        if not self.visible:
            return
            
        # 计算当前颜色（考虑脉冲效果）
        if self.is_hovered:
            # 在基础颜色和悬停颜色之间脉动
            factor = 0.5 + 0.5 * self.pulse
            r = int(self.color[0] + (self.hover_color[0] - self.color[0]) * factor)
            g = int(self.color[1] + (self.hover_color[1] - self.color[1]) * factor)
            b = int(self.color[2] + (self.hover_color[2] - self.color[2]) * factor)
            color = (r, g, b)
        else:
            color = self.color
            
        # 绘制按钮背景
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        
        # 绘制按钮边框
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=self.border_radius)
        
        # 绘制按钮文本
        text = font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
        
    def check_hover(self, mouse_pos):
        if self.visible:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.visible:
            return self.is_hovered
        return False


class ChipButton:
    def __init__(self, x, y, value, color, radius=35):
        self.x = x
        self.y = y
        self.radius = radius
        self.value = value
        self.color = color
        self.is_hovered = False
        self.visible = True
        self.animation_scale = 1.0
        self.animation_dir = 0
        
    def update(self):
        # 悬停时的动画效果
        if self.is_hovered:
            if self.animation_dir == 0:
                self.animation_scale += 0.02
                if self.animation_scale >= 1.1:
                    self.animation_dir = 1
            else:
                self.animation_scale -= 0.02
                if self.animation_scale <= 1.0:
                    self.animation_dir = 0
        else:
            self.animation_scale = 1.0
            self.animation_dir = 0
        
    def draw(self, screen, font):
        if not self.visible:
            return
            
        display_radius = int(self.radius * self.animation_scale)
        
        # 绘制筹码
        color = self.color
        if self.is_hovered:
            # 悬停时亮度增加
            color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
            
        # 绘制筹码基础
        pygame.draw.circle(screen, color, (self.x, self.y), display_radius)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), display_radius, 2)
        
        # 添加金色边缘
        pygame.draw.circle(screen, GOLD, (self.x, self.y), display_radius - 2, 1)
        
        # 添加筹码纹理
        for i in range(8):
            angle = i * math.pi / 4
            x1 = self.x + int(math.cos(angle) * (display_radius - 8))
            y1 = self.y + int(math.sin(angle) * (display_radius - 8))
            pygame.draw.circle(screen, WHITE, (x1, y1), 2)
        
        # 绘制筹码面值
        text = font.render(str(self.value), True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
        
    def check_hover(self, mouse_pos):
        if not self.visible:
            return False
            
        distance = ((mouse_pos[0] - self.x) ** 2 + (mouse_pos[1] - self.y) ** 2) ** 0.5
        self.is_hovered = distance <= self.radius
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.visible:
            return self.is_hovered
        return False