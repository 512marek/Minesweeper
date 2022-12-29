import pygame
from pygame.locals import *
import sys
import time
import numpy as np
from scipy.signal import convolve2d

class Board:
    def __init__(self):
        self.n_rows = 10
        self.n_cols = 10
        self.tile_size = 50
        self.n_bombs = 10
        self.grid = np.zeros((self.n_rows, self.n_cols), dtype = np.int8)
        self.revealed = np.zeros((self.n_rows, self.n_cols), dtype = np.int8)
        self.flagged = np.zeros((self.n_rows, self.n_cols), dtype = np.int8)
        self.WHITE = pygame.Color(255, 255, 255)
        self.GREEN = pygame.Color(0, 255, 0)
        self.BLACK = pygame.Color(0, 0, 0)
        self.get_height_and_width()
        pygame.display.set_caption("Minesweeper")
        self.game_display = pygame.display.set_mode((self.x, self.y))
        
    def get_height_and_width(self):
        n_lines_height = self.n_rows + 1
        n_lines_width = self.n_cols + 1
        self.x, self.y = self.n_cols * self.tile_size + n_lines_width, self.n_rows * self.tile_size + n_lines_height

    def draw_grid(self):
        for i in range(self.n_cols + 1):
            pygame.draw.line(self.game_display, self.WHITE, (i * self.tile_size + i, 0), (i * self.tile_size + i, self.y), 1)
        for i in range(self.n_rows + 1):
            pygame.draw.line(self.game_display, self.WHITE, (0, i * self.tile_size + i), (self.x, i * self.tile_size + i), 1)

    def place_bombs(self):
        bombs_set = set()
        while len(bombs_set) < self.n_bombs:
            bombs_set.add((np.random.randint(0, self.n_cols), np.random.randint(0, self.n_rows)))
        for bomb_position in bombs_set:
            self.grid[bomb_position[1]][bomb_position[0]] = 10

    def compute_board(self):
        kernel = np.array([[1,1,1],[1,0,1],[1,1,1]])
        grid_ = convolve2d(self.grid, kernel, 'same')
        self.count_grid =  grid_//10 + self.grid

    def print_numbers(self):
            number_font = pygame.font.SysFont(None, 32)
            for row in range(self.count_grid.shape[0]):
                for col in range(self.count_grid.shape[1]):
                    if self.revealed[row][col]:
                        if self.flagged[row][col] == 1:
                            number_text = "<>"
                        elif self.count_grid[row][col] > 9:
                            number_text = "*"
                        else:
                            number_text  = str(self.count_grid[row][col] )
                        number_image = number_font.render( number_text, True, self.WHITE, self.BLACK )
                        font_size_x, font_size_y = number_image.get_size()
                        position_x = (col * self.tile_size + col) + self.tile_size//2 - font_size_x//2 
                        position_y = (row * self.tile_size + row) + self.tile_size//2 - font_size_y//2
                        self.game_display.blit(number_image, (position_x, position_y))
            
            #visible grid
            self.visible_grid = self.revealed * self.count_grid


    global visited
    visited = []

    def reveal_tiles(self, row, col):

        if (row, col) not in visited:
            visited.append((row, col))
            if not (row < 0 or col < 0 or col >= self.n_cols or row >= self.n_rows or self.flagged[row][col] == 1):
                if self.count_grid[row][col] == 0:
                    for i in range(row - 1, row + 2):
                        for j in range(col - 1, col + 2):
                            try:
                                if self.count_grid[i][j] != '*' and i + j >= 0 and i * j >= 0 and not self.flagged[i][j] == 1:
                                    self.revealed[i][j] = 1
                                    self.reveal_tiles(i, j)
                            except:
                                continue
                else:
                    self.revealed[row][col] = 1
            else:
                return

    def user_click(self):
            x, y = pygame.mouse.get_pos()
            n_row, n_col = (y - (y)//self.tile_size)//self.tile_size, (x - (x)//self.tile_size)//self.tile_size
            return (n_row, n_col)

    def check_bomb(self, row, col):
        if self.count_grid[row][col] > 9:
            self.print_numbers()
            position_x = self.x//2
            position_y = self.y//2
            fontObj = pygame.font.Font('freesansbold.ttf', 60)
            textSurfaceObj = fontObj.render(":(", True, self.GREEN)
            textRectObj = textSurfaceObj.get_rect()
            textRectObj.center = (position_x, position_y)
            self.game_display.blit(textSurfaceObj, textRectObj)
            pygame.display.update()   
            time.sleep(3)
            pygame.quit()
            sys.exit()

    def right_click(self, row, col):
        if self.revealed[row][col] == 0:
            self.revealed[row][col] = 1
            self.flagged[row][col] = 1
        elif self.flagged[row][col] == 1:
            self.revealed[row][col] = 0
            self.flagged[row][col] = 0
            self.print_blank(row, col)

    def print_blank(self, row, col):
        position_x = (col * self.tile_size + col) + 1
        position_y = (row * self.tile_size + row) + 1
        fill_rect = pygame.Rect(position_x, position_y, self.tile_size, self.tile_size)
        pygame.draw.rect(self.game_display, self.BLACK, fill_rect)

    def check_win(self):
        if (self.revealed > 0).all() and ((self.flagged == 1) == (self.count_grid > 9)).all():
            position_x = self.x//2
            position_y = self.y//2
            fontObj = pygame.font.Font('freesansbold.ttf', 40)
            textSurfaceObj = fontObj.render("You have won!", True, self.GREEN)
            textRectObj = textSurfaceObj.get_rect()
            textRectObj.center = (position_x, position_y)
            self.game_display.blit(textSurfaceObj, textRectObj)
            self.print_numbers()
            pygame.display.update()
            time.sleep(5)  
            pygame.quit()
            sys.exit()

def main():
    pygame.init()
    b = Board()
    b.get_height_and_width()
    b.draw_grid()
    b.place_bombs()
    b.compute_board()
    b.print_numbers()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                    row, col = b.user_click()
                    if event.button == 1:
                        if not b.flagged[row][col] == 1:                    
                            b.reveal_tiles(row, col)
                            b.check_bomb(row, col)
                    if event.button == 3:
                        b.right_click(row, col)
                    b.check_win()
                    
            b.print_numbers()
            pygame.display.update()

if __name__ == "__main__":
    main()