# card.py
import pygame
import os
import random
from constants import *

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.face_up = True
        self.position = (0, 0)
        self.target_position = (0, 0)
        self.moving = False
        self.move_speed = 20  # 每帧移动的像素数
        self.image = None
        self.load_image()
        
    def load_image(self):
        # 将花色和点数转换为对应的图片文件名
        suit_letter = ""
        if self.suit == Suit.HEARTS:
            suit_letter = "H"
        elif self.suit == Suit.DIAMONDS:
            suit_letter = "D"
        elif self.suit == Suit.CLUBS:
            suit_letter = "C"
        elif self.suit == Suit.SPADES:
            suit_letter = "S"
            
        value_letter = ""
        if self.value == 1:
            value_letter = "A"
        elif self.value == 11:
            value_letter = "J"
        elif self.value == 12:
            value_letter = "Q"
        elif self.value == 13:
            value_letter = "K"
        else:
            value_letter = str(self.value)
            
        # 加载图片
        image_path = os.path.join("assets", "cards", f"{value_letter}{suit_letter}.png")
        try:
            self.image = pygame.image.load(image_path)
            # 调整图片大小以匹配游戏中的卡牌尺寸
            self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))
        except Exception as e:
            print(f"无法加载卡牌图片: {image_path}, 错误: {e}")
            self.image = None
        
    def __str__(self):
        if self.value == 1:
            rank = "A"
        elif self.value == 11:
            rank = "J"
        elif self.value == 12:
            rank = "Q"
        elif self.value == 13:
            rank = "K"
        else:
            rank = str(self.value)
            
        suit_symbol = ""
        if self.suit == Suit.HEARTS:
            suit_symbol = "♥"
        elif self.suit == Suit.DIAMONDS:
            suit_symbol = "♦"
        elif self.suit == Suit.CLUBS:
            suit_symbol = "♣"
        elif self.suit == Suit.SPADES:
            suit_symbol = "♠"
            
        return f"{rank}{suit_symbol}"
    
    def get_card_value(self):
        if self.value == 1:
            return 11  # Ace默认为11，需要时会变为1
        elif self.value > 10:
            return 10  # 面值卡为10
        else:
            return self.value
    
    def set_target_position(self, x, y):
        """设置卡牌的目标位置，启动移动动画"""
        self.target_position = (x, y)
        self.moving = True
        
    def update(self):
        """更新卡牌位置，处理移动动画"""
        if self.moving:
            dx = self.target_position[0] - self.position[0]
            dy = self.target_position[1] - self.position[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance <= self.move_speed:
                self.position = self.target_position
                self.moving = False
            else:
                # 计算移动向量
                factor = self.move_speed / distance
                self.position = (
                    self.position[0] + dx * factor,
                    self.position[1] + dy * factor
                )
    
    def draw(self, screen, x=None, y=None):
        # 如果提供了新坐标，则更新位置
        if x is not None and y is not None:
            self.position = (x, y)
            self.target_position = (x, y)
            self.moving = False
        
        # 绘制卡牌
        if self.face_up and self.image:
            screen.blit(self.image, self.position)
        elif not self.face_up and hasattr(pygame, 'game') and hasattr(pygame.game, 'card_back_image') and pygame.game.card_back_image is not None:
            # 使用全局卡背图片
            screen.blit(pygame.game.card_back_image, self.position)
        else:
            # 备用绘制方法
            x, y = self.position
            # 绘制卡片轮廓
            pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
            pygame.draw.rect(screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=10)
            
            if self.face_up:
                # 绘制卡片花色和点数
                font = pygame.font.Font(None, 36)
                
                # 获取卡片文本和颜色
                card_text = self.__str__()
                text_color = BLACK
                if self.suit == Suit.HEARTS or self.suit == Suit.DIAMONDS:
                    text_color = RED
                
                # 在左上角和右下角绘制文本
                text = font.render(card_text, True, text_color)
                screen.blit(text, (x + 8, y + 8))
                screen.blit(pygame.transform.rotate(text, 180), (x + CARD_WIDTH - 32, y + CARD_HEIGHT - 32))
                
                # 在中间绘制更大的符号
                font_big = pygame.font.Font(None, 60)
                if self.suit == Suit.HEARTS:
                    symbol = font_big.render("♥", True, text_color)
                elif self.suit == Suit.DIAMONDS:
                    symbol = font_big.render("♦", True, text_color)
                elif self.suit == Suit.CLUBS:
                    symbol = font_big.render("♣", True, text_color)
                else:  # SPADES
                    symbol = font_big.render("♠", True, text_color)
                
                symbol_rect = symbol.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
                screen.blit(symbol, symbol_rect)
            else:
                # 绘制卡片背面
                pygame.draw.rect(screen, BLUE, (x + 5, y + 5, CARD_WIDTH - 10, CARD_HEIGHT - 10), border_radius=8)
                pygame.draw.rect(screen, DARK_RED, (x + 15, y + 15, CARD_WIDTH - 30, CARD_HEIGHT - 30), 2, border_radius=5)
                
                # 添加背面花纹
                for i in range(5):
                    for j in range(7):
                        pygame.draw.circle(screen, DARK_RED, 
                                          (x + 20 + i * 15, y + 20 + j * 15), 
                                          2)


class Deck:
    def __init__(self):
        self.cards = []
        self.position = (SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2)
        self.create_deck()
        
    def create_deck(self):
        self.cards = []
        for suit in Suit:
            for value in range(1, 14):  # 1 = Ace, 11 = Jack, 12 = Queen, 13 = King
                card = Card(suit, value)
                card.position = self.position
                card.target_position = self.position
                self.cards.append(card)
        
    def shuffle(self):
        random.shuffle(self.cards)
        # 将所有卡牌位置重置到牌堆位置
        for card in self.cards:
            card.position = self.position
            card.target_position = self.position
        
    def deal_card(self, target_position=None):
        if len(self.cards) > 0:
            card = self.cards.pop()
            if target_position:
                card.set_target_position(*target_position)
            # 添加发牌音效（这里用简单的声音替代）
            try:
                pygame.mixer.Sound.play(pygame.mixer.Sound(pygame.sndarray.array(pygame.Surface((1, 1)))))
            except:
                pass
            return card
        else:
            self.create_deck()
            self.shuffle()
            return self.deal_card(target_position)
    
    def draw(self, screen):
        # 绘制牌堆
        if len(self.cards) > 0:
            x, y = self.position
            pygame.draw.rect(screen, BLUE, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
            pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=10)
            
            # 绘制牌堆图案
            font = pygame.font.Font(None, 24)
            text = font.render(f"剩余: {len(self.cards)}", True, WHITE)
            screen.blit(text, (x + 10, y + CARD_HEIGHT - 30))
            
            # 添加装饰
            for i in range(4):
                offset = i * 2
                pygame.draw.rect(screen, (0, 0, 150) if i % 2 == 0 else BLUE, 
                              (x - offset, y - offset, CARD_WIDTH, CARD_HEIGHT), 
                              1, border_radius=10)


class Hand:
    def __init__(self):
        self.cards = []
        self.is_splitted = False  # 标记是否为分牌后的手牌
        
    def add_card(self, card):
        self.cards.append(card)
        
    def get_value(self):
        value = 0
        aces = 0
        
        for card in self.cards:
            card_value = card.get_card_value()
            if card_value == 11:
                aces += 1
            value += card_value
        
        # 如果总值超过21，将A从11转为1
        while value > 21 and aces > 0:
            value -= 10  # 将一个A从11转为1
            aces -= 1
            
        return value
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21
    
    def is_five_card_charlie(self):
        # 五小龙规则：5张牌且点数不超过21点自动获胜
        return len(self.cards) >= 5 and self.get_value() <= 21
    
    def can_split(self):
        # 判断是否可以分牌：两张牌且点数相同
        if len(self.cards) != 2:
            return False
        # 判断两张牌的点数是否相同（注意：10、J、Q、K都算作10点）
        card1_value = self.cards[0].get_card_value()
        card2_value = self.cards[1].get_card_value()
        return card1_value == card2_value
    
    def split(self):
        # 分牌操作，返回一个新的手牌
        if not self.can_split():
            return None
        
        new_hand = Hand()
        new_hand.add_card(self.cards.pop())  # 移除一张牌到新手牌
        new_hand.is_splitted = True
        self.is_splitted = True
        return new_hand
    
    def clear(self):
        self.cards = []
        self.is_splitted = False
    
    def update(self):
        # 更新所有卡牌的位置
        for card in self.cards:
            card.update()
    
    def draw(self, screen, x, y, is_dealer=False, hide_first_card=False):
        for i, card in enumerate(self.cards):
            # 增加间距，从原来的30像素增加到60像素
            card_x = x + i * 60
            
            # 如果需要，隐藏庄家的第一张牌
            if is_dealer and i == 0 and hide_first_card:
                card.face_up = False
            else:
                card.face_up = True
                
            card.draw(screen, card_x, y)
