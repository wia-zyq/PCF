import pygame
import sys
import random
from pygame.locals import *

# 初始化pygame
pygame.init()

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
GRID_SIZE = 10
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# 创建窗口
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('墙间对决')
clock = pygame.time.Clock()

class Piece:
    def __init__(self, player, shape, row, col):
        self.player = player  # 1 或 2
        self.shape = shape    # 'circle' 或 'square'
        self.row = row
        self.col = col
        self.selected = False
    
    def draw(self):
        x = self.col * CELL_SIZE + CELL_SIZE // 2
        y = self.row * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 3
        
        if self.player == 1:
            color = RED
        else:
            color = BLUE
            
        if self.selected:
            pygame.draw.circle(window, YELLOW, (x, y), radius + 5)
            
        if self.shape == 'circle':
            pygame.draw.circle(window, color, (x, y), radius)
        else:
            rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
            pygame.draw.rect(window, color, rect)

class Game:
    def __init__(self):
        self.board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_player = 1
        self.selected_piece = None
        self.valid_moves = []
        self.dark_cells = self.generate_dark_cells()
        self.wall_positions = self.generate_wall()
        self.initialize_pieces()
        
    def generate_dark_cells(self):
        dark_cells = set()
        while len(dark_cells) < 10:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            # 确保不在第一行和最后一行（棋子初始位置）
            if row != 0 and row != GRID_SIZE - 1:
                dark_cells.add((row, col))
        return dark_cells
    
    def generate_wall(self):
        wall_positions = set()
        mid_col = GRID_SIZE // 2
        # 从第2行到第7行建墙
        for row in range(2, GRID_SIZE - 2):
            wall_positions.add((row, mid_col - 1))
            wall_positions.add((row, mid_col))
            wall_positions.add((row, mid_col + 1))
        
        # 在中间开一个豁口
        gap_row = GRID_SIZE // 2
        wall_positions.remove((gap_row, mid_col - 1))
        wall_positions.remove((gap_row, mid_col))
        wall_positions.remove((gap_row, mid_col + 1))
        
        return wall_positions
    
    def initialize_pieces(self):
        # 玩家1（红色）在顶部，圆形棋子
        for i in range(10):
            row = 0
            col = i
            self.board[row][col] = Piece(1, 'circle', row, col)
        
        # 玩家2（蓝色）在底部，方形棋子
        for i in range(10):
            row = GRID_SIZE - 1
            col = i
            self.board[row][col] = Piece(2, 'square', row, col)
    
    def draw_board(self):
        window.fill(WHITE)
        
        # 绘制格子
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (row, col) in self.dark_cells:
                    pygame.draw.rect(window, DARK_GRAY, rect)
                else:
                    pygame.draw.rect(window, GRAY, rect)
                pygame.draw.rect(window, BLACK, rect, 1)
        
        # 绘制墙
        for row, col in self.wall_positions:
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(window, BLACK, rect)
        
        # 绘制棋子
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col]:
                    self.board[row][col].draw()
        
        # 绘制有效移动位置
        for row, col in self.valid_moves:
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(window, GREEN, rect, 3)
        
        # 显示当前玩家
        font = pygame.font.SysFont(None, 36)
        if self.current_player == 1:
            text = font.render("当前玩家: 红方 (圆形)", True, RED)
        else:
            text = font.render("当前玩家: 蓝方 (方形)", True, BLUE)
        window.blit(text, (20, 20))
    
    def is_valid_position(self, row, col):
        return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE
    
    def is_wall(self, row, col):
        return (row, col) in self.wall_positions
    
    def get_valid_moves(self, piece):
        moves = []
        row, col = piece.row, piece.col
        
        # 检查所有可能的移动方向
        for dr in [-2, -1, 0, 1, 2]:
            for dc in [-2, -1, 0, 1, 2]:
                # 不能原地不动
                if dr == 0 and dc == 0:
                    continue
                
                new_row, new_col = row + dr, col + dc
                
                # 检查是否在棋盘内
                if not self.is_valid_position(new_row, new_col):
                    continue
                
                # 检查是否是墙
                if self.is_wall(new_row, new_col):
                    continue
                
                # 检查是否已经有自己的棋子
                if self.board[new_row][new_col] and self.board[new_row][new_col].player == piece.player:
                    continue
                
                # 计算曼哈顿距离
                distance = abs(dr) + abs(dc)
                
                # 如果是深色格子，只能走一格
                if (row, col) in self.dark_cells or (new_row, new_col) in self.dark_cells:
                    if distance > 1:
                        continue
                
                # 正常格子可以走1-2格
                if distance > 2:
                    continue
                
                # 如果是吃子，距离必须为1且斜方向
                if self.board[new_row][new_col] and self.board[new_row][new_col].player != piece.player:
                    if distance == 1 and dr != 0 and dc != 0:  # 斜方向
                        moves.append((new_row, new_col, True))  # True表示吃子
                else:
                    moves.append((new_row, new_col, False))
        
        return moves
    
    def select_piece(self, row, col):
        # 如果点击的是自己的棋子，选择它
        if self.board[row][col] and self.board[row][col].player == self.current_player:
            self.selected_piece = self.board[row][col]
            self.valid_moves = [ (r, c) for r, c, _ in self.get_valid_moves(self.selected_piece) ]
            return True
        return False
    
    def move_piece(self, row, col):
        if not self.selected_piece or (row, col) not in self.valid_moves:
            return False
        
        # 检查是否是吃子
        for r, c, is_capture in self.get_valid_moves(self.selected_piece):
            if r == row and c == col and is_capture:
                self.board[row][col] = None  # 吃掉对方棋子
        
        # 移动棋子
        self.board[self.selected_piece.row][self.selected_piece.col] = None
        self.selected_piece.row, self.selected_piece.col = row, col
        self.board[row][col] = self.selected_piece
        
        # 切换玩家
        self.current_player = 3 - self.current_player  # 在1和2之间切换
        self.selected_piece = None
        self.valid_moves = []
        
        # 检查游戏是否结束
        if self.check_game_over():
            self.show_game_over()
        
        return True
    
    def check_game_over(self):
        player1_exists = False
        player2_exists = False
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col]:
                    if self.board[row][col].player == 1:
                        player1_exists = True
                    else:
                        player2_exists = True
        
        return not player1_exists or not player2_exists
    
    def show_game_over(self):
        font = pygame.font.SysFont(None, 72)
        if not any(piece for row in self.board for piece in row if piece and piece.player == 1):
            text = font.render("蓝方胜利!", True, BLUE)
        else:
            text = font.render("红方胜利!", True, RED)
        
        window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 
                         WINDOW_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.update()
        pygame.time.wait(3000)
        
        # 重置游戏
        self.__init__()

def main():
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                
                if game.selected_piece:
                    if game.move_piece(row, col):
                        pass  # 移动成功
                    else:
                        game.select_piece(row, col)  # 尝试选择其他棋子
                else:
                    game.select_piece(row, col)
        
        game.draw_board()
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
