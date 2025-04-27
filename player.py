# player.py
import pygame
import random
from constants import *
from card import Hand

class ChipStack:
    """表示一堆筹码的类"""
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y
        self.chips = []  # 筹码面值列表
        self.calculate_chips()
        
    def calculate_chips(self):
        """将总值分解为各面值的筹码"""
        self.chips = []
        remaining = self.value
        
        # 从大到小使用筹码
        for chip_value in sorted([100, 50, 25, 5], reverse=True):
            while remaining >= chip_value:
                self.chips.append(chip_value)
                remaining -= chip_value
    
    def draw(self, screen):
        """绘制筹码堆"""
        if not self.chips:
            return
            
        # 绘制每个筹码，稍微错开堆叠
        for i, chip_value in enumerate(self.chips):
            y_offset = -i * 3  # 向上堆叠
            
            # 根据面值选择颜色
            color = SILVER  # 默认颜色
            if chip_value == 5:
                color = SILVER
            elif chip_value == 25:
                color = GOLD
            elif chip_value == 50:
                color = BRONZE
            elif chip_value == 100:
                color = BLUE
                
            pygame.draw.circle(screen, color, (self.x, self.y + y_offset), 20)
            pygame.draw.circle(screen, WHITE, (self.x, self.y + y_offset), 20, 2)
            
            # 添加筹码装饰
            pygame.draw.circle(screen, (color[0]//2, color[1]//2, color[2]//2), 
                              (self.x, self.y + y_offset), 15, 1)
            
            # 绘制筹码面值
            font = pygame.font.Font(None, 24)
            text = font.render(str(chip_value), True, BLACK)
            text_rect = text.get_rect(center=(self.x, self.y + y_offset))
            screen.blit(text, text_rect)
        
        # 绘制总值
        font = pygame.font.Font(None, 28)
        total_text = font.render(str(self.value), True, WHITE)
        screen.blit(total_text, (self.x - total_text.get_width()//2, self.y + 25))


class Player:
    def __init__(self, name, strategy=None, chips=1000, is_human=False):
        self.name = name
        self.hands = [Hand()]  # 初始有一手牌，支持分牌
        self.chips = chips
        self.bet_per_hand = 0  # 每手牌的下注金额
        self.is_human = is_human
        self.strategy = strategy
        self.position = (0, 0)  # 屏幕上的位置
        self.state = "waiting"  # waiting, betting, playing, done
        self.results = [""]  # 每手牌的结果: win, lose, push, blackjack, five_card
        self.current_hand_index = 0  # 当前正在玩的手牌索引
        self.chip_stacks = []  # 玩家的筹码堆
        self.animation_in_progress = False  # 动画标志
        
    def place_bet(self, amount):
        if amount > self.chips:
            amount = self.chips
            
        if amount <= 0:
            return 0
            
        self.bet_per_hand += amount  # 累加下注金额
        self.chips -= amount
        
        # 播放下注音效（简单声音）
        try:
            pygame.mixer.Sound.play(pygame.mixer.Sound(pygame.sndarray.array(pygame.Surface((1, 1)))))
        except:
            pass
                
        # 更新下注区域的筹码堆
        self.update_chip_stacks()
            
        return amount
    
    def update_chip_stacks(self):
        """更新下注区域的筹码堆显示"""
        self.chip_stacks = []
        
        # 为每手牌创建一个筹码堆
        for i, hand in enumerate(self.hands):
            # 计算筹码堆的位置
            x = self.position[0] + 400 
            y = self.position[1] - 70 + (i * 150)  
            
            # 创建筹码堆
            self.chip_stacks.append(ChipStack(self.bet_per_hand, x, y))
    
    def add_chips(self, amount):
        self.chips += amount
        
        # 播放获胜音效（简单声音）
        try:
            pygame.mixer.Sound.play(pygame.mixer.Sound(pygame.sndarray.array(pygame.Surface((1, 1)))))
        except:
            pass
        
    def auto_bet(self, min_bet=5, max_bet=100):
        if self.strategy:
            bet_amount = self.strategy.decide_bet(self.chips, min_bet, max_bet)
            return self.place_bet(bet_amount)
        return random.randint(5, 50)  # 简化的AI下注策略
    
    def decide_action(self, dealer_up_card_value, hand_index=0):
        # 简化的AI决策：点数<17则要牌，否则停牌
        hand_value = self.hands[hand_index].get_value()
        if hand_value < 17:
            return "hit"
        else:
            return "stand"
    
    def decide_split(self, hand_index=0):
        # 简化的分牌决策：只在特定情况下分牌
        if self.hands[hand_index].can_split():
            card_value = self.hands[hand_index].cards[0].get_card_value()
            # A和8总是分牌
            if card_value == 11 or card_value == 8:
                return True
        return False
    
    def split_hand(self, hand_index):
        # 确保手牌可以分牌
        if not self.hands[hand_index].can_split():
            return False
            
        # 检查玩家是否有足够的筹码进行分牌
        if self.chips < self.bet_per_hand:
            return False
            
        # 分牌并从玩家那里扣除额外的下注
        new_hand = self.hands[hand_index].split()
        if new_hand:
            self.hands.append(new_hand)
            self.results.append("")  # 为新手牌添加结果占位符
            self.chips -= self.bet_per_hand  # 为新手牌扣除相同的下注
            
            # 更新筹码堆
            self.update_chip_stacks()
            
            return True
        return False
    
    def reset(self):
        # 重置玩家状态
        self.hands = [Hand()]
        self.bet_per_hand = 0
        self.state = "waiting"
        self.results = [""]
        self.current_hand_index = 0
        self.chip_stacks = []
    
    def update(self):
        # 更新所有手牌
        for hand in self.hands:
            hand.update()
            
        # 检查是否有动画正在进行
        self.animation_in_progress = any(card.moving for hand in self.hands for card in hand.cards)
    
    def draw(self, screen, font):
        # 绘制玩家区域背景
        pygame.draw.rect(screen, (30, 60, 40), 
                       (self.position[0] - 20, self.position[1] - 90, 
                        450, 70 + len(self.hands) * 150), 
                       border_radius=15)
        
        # 绘制玩家名称和筹码
        name_text = font.render(self.name, True, WHITE)
        screen.blit(name_text, (self.position[0], self.position[1] - 40))
        
        # 绘制玩家筹码（使用金色突出显示）
        chips_text = font.render(f"Chip: {self.chips}", True, GOLD)
        screen.blit(chips_text, (self.position[0], self.position[1] - 80))
        
        # 绘制每手牌的下注金额
        if self.bet_per_hand > 0:
            bet_text = font.render(f"Bet: {self.bet_per_hand}/Hand", True, GOLD)
            screen.blit(bet_text, (self.position[0] + 200, self.position[1] - 80))
        
        # 绘制下注区域的筹码堆
        for stack in self.chip_stacks:
            stack.draw(screen)
        
        # 绘制所有手牌
        for i, hand in enumerate(self.hands):
            # 添加一个垂直偏移，使多个手牌可见
            y_offset = i * 150
            
            # 绘制手牌区域背景（当前手牌突出显示）
            if i == self.current_hand_index and self.state == "playing":
                # 当前正在玩的手牌区域用金色突出显示
                pygame.draw.rect(screen, (50, 50, 30), 
                               (self.position[0] - 10, self.position[1] + y_offset - 10, 
                                300, CARD_HEIGHT + 20), 
                               border_radius=10)
                # 绘制一个金色指示器
                pygame.draw.circle(screen, GOLD, 
                                  (self.position[0] - 25, self.position[1] + y_offset + CARD_HEIGHT // 2), 
                                  12)
            
            # 绘制手牌
            hand.draw(screen, self.position[0], self.position[1] + y_offset)
            
            # 绘制手牌点数
            value_text = font.render(f"Pts: {hand.get_value()}", True, WHITE)
            screen.blit(value_text, (self.position[0] + 250, self.position[1] - 40))
            
            # 绘制结果（如果有）
            if i < len(self.results) and self.results[i]:
                result_color = GOLD
                result_display = self.results[i].upper()
                
                if self.results[i] == "win":
                    result_color = GREEN
                    result_display = "Win"
                elif self.results[i] == "blackjack":
                    result_color = GREEN
                    result_display = "Blackjack!"
                elif self.results[i] == "five_card":
                    result_color = GREEN
                    result_display = "Five Dragon!"
                elif self.results[i] == "lose":
                    result_color = RED
                    result_display = "Lose"
                elif self.results[i] == "push":
                    result_color = GOLD
                    result_display = "Push"
                    
                result_text = font.render(result_display, True, result_color)
                screen.blit(result_text, (self.position[0] + 350, self.position[1] + y_offset))


class Dealer:
    def __init__(self):
        self.name = "Dealer"
        self.hand = Hand()
        self.position = (0, 0)  # 屏幕上的位置
    
    def update(self):
        # 更新手牌
        self.hand.update()
        
    def draw(self, screen, font, hide_first_card=False):
        # 绘制庄家区域背景
        pygame.draw.rect(screen, (40, 40, 40), 
                       (self.position[0] - 10, self.position[1] - 50, 
                        400, CARD_HEIGHT + 80), 
                       border_radius=15)
        
        # 绘制庄家名称
        name_text = font.render(self.name, True, WHITE)
        screen.blit(name_text, (self.position[0], self.position[1] - 30))
        
        # 绘制当前手牌
        self.hand.draw(screen, self.position[0], self.position[1], True, hide_first_card)
        
        # 如果不隐藏牌，绘制手牌点数
        if not hide_first_card:
            value_text = font.render(f"Pts: {self.hand.get_value()}", True, WHITE)
            screen.blit(value_text, (self.position[0] + 220, self.position[1] - 30))