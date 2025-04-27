# game.py
import pygame
import sys
import random
import math
import os
from constants import *
from card import Deck, Hand
from player import Player, Dealer
from gui import Button, ChipButton
from effects import Particle

class AdvancedBlackjackGame:
    def __init__(self):
        # 创建屏幕并设置窗口标题
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Luxury Casino Blackjack")
            
        self.clock = pygame.time.Clock()
        
        # 尝试加载卡背图片
        self.card_back_image = None
        try:
            back_path = os.path.join("assets", "cards", "red_back.png")
            self.card_back_image = pygame.image.load(back_path)
            self.card_back_image = pygame.transform.scale(self.card_back_image, (CARD_WIDTH, CARD_HEIGHT))
        except Exception as e:
            print(f"Cannot load card back image: {e}")
            print(f"Trying from current path: {os.getcwd()}")
        
        # 创建牌堆并设置位置
        self.deck = Deck()
        self.deck.position = (SCREEN_WIDTH // 2 - 345, SCREEN_HEIGHT -185)
        
        # 创建庄家和玩家
        self.dealer = Dealer()
        self.human_player = Player("You", None, 1000, True)
        self.ai_players = [
            Player("Basic Strategy AI", None, 1000),
            Player("Conservative AI", None, 1000),
            Player("Aggressive AI", None, 1000),
            Player("Card Counter AI", None, 1000)
        ]
        self.players = [self.human_player] + self.ai_players
        
        # 设置字体
        self.font_small = pygame.font.Font(None, 24)
        self.font = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        self.font_title = pygame.font.Font(None, 72)
        
        # 设置各个游戏元素的位置
        self.setup_positions()
        
        # 创建按钮 - 更现代的样式和位置
        self.create_buttons()
        
        # 筹码按钮 - 使用更直观的布局
        self.create_chip_buttons()
        
        # 设置游戏状态
        self.game_state = "betting"  # betting, player_turns, dealer_turn, game_over
        self.current_player_index = 0
        self.message = "Place your bet!"
        self.round_over = False
        
        # 特效相关变量
        self.particles = []  # 粒子效果
        self.flash_timer = 0  # 闪烁效果
        
        # 建立游戏实例引用供卡牌类使用
        pygame.game = self
        
        # 洗牌开始
        self.deck.shuffle()
    
    def setup_positions(self):
        """设置游戏元素的位置"""
        # 庄家位置 - 屏幕中上方
        self.dealer.position = (SCREEN_WIDTH // 2 - 165, 160)
        
        # 人类玩家位置 - 屏幕正中间底部
        self.human_player.position = (SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT - 350)
        
        # AI player positions - 2 on left side, 2 on right side
        if len(self.ai_players) >= 1:
            # Left top position
            self.ai_players[0].position = (100, 200)
        
        if len(self.ai_players) >= 2:
            # Left bottom position 
            self.ai_players[1].position = (100, 450)
        
        if len(self.ai_players) >= 3:
            # Right top position
            self.ai_players[2].position = (SCREEN_WIDTH - 450, 200)
        
        if len(self.ai_players) >= 4:
            # Right bottom position
            self.ai_players[3].position = (SCREEN_WIDTH - 450, 450)
    
    def create_buttons(self):
        """创建游戏按钮"""
        # 主游戏按钮 - 放在右侧面板
        panel_x = SCREEN_WIDTH - 200
        panel_y = SCREEN_HEIGHT // 2 + 50
        
        self.hit_button = Button(panel_x, panel_y + 160, 200, 60, "Hit", GREEN, BRIGHT_GREEN, 15)
        self.stand_button = Button(panel_x, panel_y + 240, 200, 60, "Stand", RED, (255, 50, 50), 15)
        self.deal_button = Button(panel_x, panel_y + 160, 200, 60, "Deal", BLUE, (50, 50, 255), 15)
        self.reset_bet_button = Button(panel_x, panel_y + 240, 200, 60, "Reset Bet", ORANGE, (255, 180, 0), 15)
        self.split_button = Button(panel_x, panel_y + 80, 200, 60, "Split", PURPLE, (180, 0, 180), 15)
    
    def create_chip_buttons(self):
        """创建筹码按钮"""
        # 筹码按钮 - 放在左侧面板，垂直排列
        panel_x = 39
        panel_y = SCREEN_HEIGHT // 2
        
        self.chip_buttons = [
            ChipButton(panel_x, panel_y - 150, 5, SILVER),
            ChipButton(panel_x, panel_y - 50, 25, GOLD),
            ChipButton(panel_x, panel_y + 50, 50, BRONZE),
            ChipButton(panel_x, panel_y + 150, 100, BLUE)
        ]
    
    def start_new_game(self):
        """开始新一局游戏，重置所有状态"""
        # 重置游戏状态
        self.game_state = "betting"
        self.current_player_index = 0
        self.message = "Place your bet!"
        self.round_over = False
        self.particles = []
        self.flash_timer = 0
        
        # 清除所有手牌
        self.dealer.hand.clear()
        for player in self.players:
            player.reset()
        
        # 确保牌组已经洗牌
        if len(self.deck.cards) < 20:
            self.deck = Deck()
            self.deck.position = (SCREEN_WIDTH // 2 - 345, SCREEN_HEIGHT -185)
            self.deck.shuffle()
    
    def handle_ai_bets(self):
        """处理AI玩家的下注"""
        # AI玩家下注
        for player in self.ai_players:
            bet_amount = random.randint(5, 50)  # 简化的AI下注策略
            if bet_amount <= player.chips:
                player.place_bet(bet_amount)
                player.state = "betting"
    
    def deal_initial_cards(self):
        """发初始牌给所有玩家和庄家"""
        # 给所有玩家和庄家发两张牌
        for _ in range(2):
            for player in self.players:
                if player.bet_per_hand > 0:  # 只给下注的玩家发牌
                    target_pos = (player.position[0] + len(player.hands[0].cards) * 60, 
                         player.position[1])
                    card = self.deck.deal_card(target_pos)
                    player.hands[0].add_card(card)
            
            # 给庄家发牌
            target_pos = (self.dealer.position[0] + len(self.dealer.hand.cards) * 60,
                 self.dealer.position[1])
            card = self.deck.deal_card(target_pos)
            self.dealer.hand.add_card(card)
        
        # 检查是否有黑杰克
        for player in self.players:
            if player.bet_per_hand > 0:
                # 检查第一手牌是否为黑杰克
                if player.hands[0].is_blackjack():
                    player.state = "done"
                    if self.dealer.hand.is_blackjack():
                        player.results[0] = "push"
                        player.add_chips(player.bet_per_hand)  # 返还下注
                    else:
                        player.results[0] = "blackjack"
                        player.add_chips(int(player.bet_per_hand * 2.5))  # 支付3:2
                        self.create_win_effect(player)  # 添加获胜特效
                else:
                    player.state = "playing"
        
        # 进入玩家回合状态
        self.game_state = "player_turns"
        self.current_player_index = 0
        
        # 找到第一个需要玩的玩家
        self.find_next_player_turn()
        
        if self.current_player_index < len(self.players):
            current_player = self.players[self.current_player_index]
            self.message = f"{current_player.name}'s turn"
        else:
            # 没有玩家需要玩，进入庄家回合
            self.game_state = "dealer_turn"
    
    def find_next_player_turn(self):
        """找到下一个需要玩的玩家或手牌"""
        while self.current_player_index < len(self.players):
            player = self.players[self.current_player_index]
            
            # 如果玩家没有下注或已经完成，跳到下一个玩家
            if player.bet_per_hand <= 0 or player.state != "playing":
                self.current_player_index += 1
                continue
                
            # 找到玩家的下一个需要玩的手牌
            while player.current_hand_index < len(player.hands):
                hand_result = player.results[player.current_hand_index]
                
                # 如果这手牌没有结果，可以继续玩
                if not hand_result:
                    return
                    
                # 否则，移动到下一手牌
                player.current_hand_index += 1
            
            # 如果所有手牌都已完成，玩家完成
            player.state = "done"
            self.current_player_index += 1
            
        # 如果没有找到下一个玩家，进入庄家回合
        self.game_state = "dealer_turn"
    
    def handle_player_turn(self):
        """处理当前玩家的回合"""
        # 检查是否所有玩家都已完成
        if self.current_player_index >= len(self.players):
            # 所有玩家都已完成，进入庄家回合
            self.game_state = "dealer_turn"
            return
        
        current_player = self.players[self.current_player_index]
        
        # 跳过未玩或未下注的玩家
        if current_player.state != "playing" or current_player.bet_per_hand <= 0:
            self.current_player_index += 1
            return
            
        # 检查是否有动画正在进行
        any_animation = False
        for player in self.players:
            player.update()
            if hasattr(player, 'animation_in_progress') and player.animation_in_progress:
                any_animation = True
                
        self.dealer.update()
        
        if any_animation:
            return  # 等待动画完成
        
        # 当前玩家的当前手牌
        current_hand_index = current_player.current_hand_index
        if current_hand_index >= len(current_player.hands):
            # 已经完成所有手牌，移动到下一个玩家
            current_player.state = "done"
            self.current_player_index += 1
            return
            
        current_hand = current_player.hands[current_hand_index]
        
        # 检查五小龙
        if current_hand.is_five_card_charlie():
            current_player.results[current_hand_index] = "five_card"
            winnings = current_player.bet_per_hand * 2
            current_player.add_chips(winnings)  # 支付获胜
            self.create_win_effect(current_player)  # 添加获胜特效
            current_player.current_hand_index += 1
            
            # 寻找下一个需要玩的手牌/玩家
            self.find_next_player_turn()
            return
        
        # 如果是AI玩家的回合
        if not current_player.is_human:
            # 添加延迟以使其可见
            pygame.time.delay(500)
            
            # AI的简化决策：点数<17则要牌，否则停牌
            if current_hand.get_value() < 17:
                # AI选择要牌
                target_pos = (current_player.position[0] + len(current_hand.cards) * 60,
                              current_player.position[1] + current_hand_index * 150)
                card = self.deck.deal_card(target_pos)
                current_hand.add_card(card)
                
                # 检查玩家是否爆牌
                if current_hand.get_value() > 21:
                    current_player.results[current_hand_index] = "lose"
                    self.create_lose_effect(current_player)  # 添加失败特效
                    current_player.current_hand_index += 1
                    
                    # 寻找下一个需要玩的手牌/玩家
                    self.find_next_player_turn()
                
            else:
                # AI选择停牌
                current_player.current_hand_index += 1
                
                # 寻找下一个需要玩的手牌/玩家
                self.find_next_player_turn()
    
    def handle_split(self, player, hand_index):
        """处理分牌操作"""
        # 确保玩家有足够的筹码
        if player.chips < player.bet_per_hand:
            return False
            
        # 分牌
        if player.split_hand(hand_index):
            # 给两手牌各发一张牌
            for i in range(2):
                hand_idx = hand_index + i
                if hand_idx < len(player.hands):
                    target_pos = (player.position[0] + len(player.hands[hand_idx].cards) * 60,
                                  player.position[1] + hand_idx * 150)
                    card = self.deck.deal_card(target_pos)
                    player.hands[hand_idx].add_card(card)
                    
            return True
            
        return False
    
    def handle_dealer_turn(self):
        """处理庄家的回合"""
        # 检查是否有动画正在进行
        self.dealer.update()
        if any(card.moving for card in self.dealer.hand.cards):
            return  # 等待动画完成
            
        # 庄家摸牌直到17或更高
        if self.dealer.hand.get_value() < 17:
            # 添加延迟以产生视觉效果
            pygame.time.delay(500)
            
            # 发一张牌给庄家
            target_pos = (self.dealer.position[0] + len(self.dealer.hand.cards) * 60,
                          self.dealer.position[1])
            card = self.deck.deal_card(target_pos)
            self.dealer.hand.add_card(card)
            
        else:
            # 确定胜负
            self.determine_winners()
            self.game_state = "game_over"
    
    def determine_winners(self):
        """确定所有玩家的胜负"""
        dealer_value = self.dealer.hand.get_value()
        dealer_bust = dealer_value > 21
        
        for player in self.players:
            if player.bet_per_hand <= 0:  # 跳过未下注的玩家
                continue
                
            for hand_index, hand in enumerate(player.hands):
                # 跳过已有结果的手牌
                if player.results[hand_index]:
                    continue
                    
                player_value = hand.get_value()
                
                # 检查五小龙规则
                if hand.is_five_card_charlie():
                    player.results[hand_index] = "five_card"
                    player.add_chips(player.bet_per_hand * 2)  # 赢得下注
                    self.create_win_effect(player)  # 添加获胜特效
                    continue
                
                if player_value > 21:  # 玩家已经爆牌
                    player.results[hand_index] = "lose"
                    self.create_lose_effect(player)  # 添加失败特效
                elif dealer_bust:
                    player.results[hand_index] = "win"
                    player.add_chips(player.bet_per_hand * 2)  # 返还下注 + 赢钱
                    self.create_win_effect(player)  # 添加获胜特效
                elif player_value > dealer_value:
                    player.results[hand_index] = "win"
                    player.add_chips(player.bet_per_hand * 2)  # 返还下注 + 赢钱
                    self.create_win_effect(player)  # 添加获胜特效
                elif player_value < dealer_value:
                    player.results[hand_index] = "lose"
                    self.create_lose_effect(player)  # 添加失败特效
                else:
                    player.results[hand_index] = "push"
                    player.add_chips(player.bet_per_hand)  # 返还下注
        
        # 更新游戏消息
        if dealer_bust:
            self.message = "Dealer busts! Click \"Deal\" to start a new round."
        else:
            self.message = f"Dealer's points: {dealer_value}. Click \"Deal\" to start a new round."
    
    def create_win_effect(self, player):
        """为玩家获胜创建特效"""
        # 添加粒子效果
        for _ in range(50):
            particle = Particle(
                player.position[0] + random.randint(0, 200),
                player.position[1] + random.randint(-50, 50),
                GOLD,
                random.randint(3, 8),
                random.randint(30, 60)
            )
            self.particles.append(particle)
    
    def create_lose_effect(self, player):
        """为玩家失败创建特效"""
        # 添加红色闪烁效果
        self.flash_timer = 10
    
    def update_particles(self):
        """更新粒子效果"""
        # 更新所有粒子
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()
        
        # 更新闪烁计时器
        if self.flash_timer > 0:
            self.flash_timer -= 1
    
    def handle_event(self, event):
        """处理用户输入事件"""
        if event.type == pygame.QUIT:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新按钮悬停状态
        for button in [self.hit_button, self.stand_button, self.deal_button, self.reset_bet_button, self.split_button]:
            button.check_hover(mouse_pos)
            button.update()  # 更新按钮动画
        
        for chip in self.chip_buttons:
            chip.check_hover(mouse_pos)
            chip.update()  # 更新筹码按钮动画
        
        # 根据游戏状态处理按钮点击
        if self.game_state == "betting":
            # 筹码按钮（仅限人类玩家）
            for chip in self.chip_buttons:
                if chip.is_clicked(event):
                    if self.human_player.chips >= chip.value:
                        self.human_player.place_bet(chip.value)
            
            # 重置下注按钮
            if self.reset_bet_button.is_clicked(event) and self.human_player.bet_per_hand > 0:
                # 返还已下注的筹码
                self.human_player.chips += self.human_player.bet_per_hand
                self.human_player.bet_per_hand = 0
                self.human_player.chip_stacks = []
                    
            # Deal按钮开始游戏
            if self.deal_button.is_clicked(event) and self.human_player.bet_per_hand > 0:
                self.handle_ai_bets()
                self.deal_initial_cards()
                
        elif self.game_state == "player_turns":
            # 只有在人类玩家回合时处理点击
            if (self.current_player_index < len(self.players) and 
                self.players[self.current_player_index].is_human):
                
                current_hand_index = self.human_player.current_hand_index
                
                # 分牌按钮只在可以分牌时可用
                if (current_hand_index < len(self.human_player.hands) and
                    self.human_player.hands[current_hand_index].can_split() and
                    self.human_player.chips >= self.human_player.bet_per_hand and
                    self.split_button.is_clicked(event)):
                    
                    self.handle_split(self.human_player, current_hand_index)
                
                # Hit按钮
                elif self.hit_button.is_clicked(event):
                    if current_hand_index < len(self.human_player.hands):
                        current_hand = self.human_player.hands[current_hand_index]
                        
                        # 发一张牌给玩家
                        target_pos = (self.human_player.position[0] + len(current_hand.cards) * 60,
                                     self.human_player.position[1] + current_hand_index * 150)
                        card = self.deck.deal_card(target_pos)
                        current_hand.add_card(card)
                        
                        # 检查是否为五小龙
                        if current_hand.is_five_card_charlie():
                            self.human_player.results[current_hand_index] = "five_card"
                            winnings = self.human_player.bet_per_hand * 2
                            self.human_player.add_chips(winnings)
                            self.create_win_effect(self.human_player)
                            self.human_player.current_hand_index += 1
                            
                            # 寻找下一个需要玩的手牌/玩家
                            self.find_next_player_turn()
                        # 检查是否爆牌
                        elif current_hand.get_value() > 21:
                            self.human_player.results[current_hand_index] = "lose"
                            self.create_lose_effect(self.human_player)
                            self.human_player.current_hand_index += 1
                            
                            # 寻找下一个需要玩的手牌/玩家
                            self.find_next_player_turn()
                
                # Stand按钮
                elif self.stand_button.is_clicked(event):
                    self.human_player.current_hand_index += 1
                    
                    # 寻找下一个需要玩的手牌/玩家
                    self.find_next_player_turn()
        
        elif self.game_state == "game_over":
            # Deal按钮开始新游戏
            if self.deal_button.is_clicked(event):
                self.start_new_game()
        
        return True
    
    def draw(self):
        """绘制游戏界面"""
        # 绘制背景 - 渐变效果
        for y in range(SCREEN_HEIGHT):
            shade = int(y / SCREEN_HEIGHT * 80)  # 从深到浅渐变
            color = (0, 100 - shade, 50 - shade // 2)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # 绘制桌面
        pygame.draw.ellipse(self.screen, TABLE_GREEN, 
                          (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100),
                          width=20)
        
        # 绘制桌面花纹
        pygame.draw.ellipse(self.screen, FELT_GREEN, 
                          (100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200),
                          width=2)
        
        # 绘制标题和装饰
        title = self.font_title.render("Luxury Blackjack", True, GOLD)
        shadow = self.font_title.render("Luxury Blackjack", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        
        # 绘制标题阴影和文本
        self.screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
        # 绘制装饰线
        pygame.draw.line(self.screen, GOLD, 
                        (title_rect.left - 50, title_rect.centery),
                        (title_rect.left - 10, title_rect.centery), 5)
        pygame.draw.line(self.screen, GOLD, 
                        (title_rect.right + 10, title_rect.centery),
                        (title_rect.right + 50, title_rect.centery), 5)
        
        # 绘制消息
        message_text = self.font.render(self.message, True, WHITE)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(message_text, message_rect)
        
        # 绘制牌堆
        self.deck.draw(self.screen)
        
        # 绘制庄家
        hide_dealer_card = self.game_state in ["betting", "player_turns"]
        self.dealer.draw(self.screen, self.font, hide_dealer_card)
        
        # 绘制所有玩家
        for player in self.players:
            player.draw(self.screen, self.font)
        
        # 更新分牌按钮可见性
        self.split_button.visible = False
        # 只有在人类玩家回合，且当前手牌可以分牌时显示分牌按钮
        if (self.game_state == "player_turns" and 
            self.current_player_index < len(self.players) and 
            self.players[self.current_player_index].is_human):
            
            current_hand_index = self.human_player.current_hand_index
            if (current_hand_index < len(self.human_player.hands) and
                self.human_player.hands[current_hand_index].can_split() and
                self.human_player.chips >= self.human_player.bet_per_hand):
                
                self.split_button.visible = True
        
        # 根据游戏状态绘制按钮
        if self.game_state == "betting":
            # 绘制人类玩家的筹码按钮
            for chip in self.chip_buttons:
                chip.draw(self.screen, self.font)
                
            # 绘制Deal按钮和重置下注按钮
            self.deal_button.draw(self.screen, self.font)
            self.reset_bet_button.draw(self.screen, self.font)
                
        elif self.game_state == "player_turns":
            # 只有在人类玩家回合时显示Hit/Stand按钮
            if (self.current_player_index < len(self.players) and 
                self.players[self.current_player_index].is_human):
                
                self.hit_button.draw(self.screen, self.font)
                self.stand_button.draw(self.screen, self.font)
                
                # 如果可以分牌，显示分牌按钮
                if self.split_button.visible:
                    self.split_button.draw(self.screen, self.font)
                
        elif self.game_state == "game_over":
            self.deal_button.draw(self.screen, self.font)
        
        # 绘制粒子效果
        for particle in self.particles:
            particle.draw(self.screen)
        
        # 绘制闪烁效果
        if self.flash_timer > 0:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(self.flash_timer * 10)
            s.fill((255, 0, 0, alpha))
            self.screen.blit(s, (0, 0))
        
        # 绘制游戏规则说明
        rules_bg = pygame.Rect(10, SCREEN_HEIGHT - 70, 380, 60)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), rules_bg, border_radius=10)
        
        rules_text1 = self.font_small.render("Rules: Five Card Charlie (5 cards ≤ 21) wins", True, GOLD)
        rules_text2 = self.font_small.render("Same value cards can be split (extra bet required)", True, GOLD)
        self.screen.blit(rules_text1, (20, SCREEN_HEIGHT - 60))
        self.screen.blit(rules_text2, (20, SCREEN_HEIGHT - 35))
        
        # 绘制版本信息
        version_text = self.font_small.render("Luxury Blackjack v1.0", True, WHITE)
        self.screen.blit(version_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 30))
        
        # 更新显示
        pygame.display.flip()
    
    def run(self):
        """运行游戏主循环"""
        running = True
        while running:
            # 处理事件
            for event in pygame.event.get():
                running = self.handle_event(event)
                if not running:
                    break
            
            # 更新游戏状态
            self.update_particles()
            
            # 处理AI玩家回合和庄家回合
            if self.game_state == "player_turns":
                self.handle_player_turn()
            elif self.game_state == "dealer_turn":
                self.handle_dealer_turn()
            
            # 绘制所有内容
            self.draw()
            
            # 限制帧率
            self.clock.tick(60)
            
            # 检查是否有玩家破产
            bankrupt_players = [p for p in self.players if p.chips <= 0]
            if self.human_player in bankrupt_players:
                self.message = "Game Over! You've run out of chips."
                # 允许再进行一轮以查看最终状态
                if self.game_state == "game_over" and not self.round_over:
                    self.round_over = True
                elif self.round_over and self.game_state == "game_over":
                    pygame.time.delay(3000)  # 显示最终状态3秒
                    running = False