import pygame
import random
import os

# Constants
WIDTH, HEIGHT = 300, 600
ROWS, COLS = 20, 10
BLOCK_SIZE = WIDTH // COLS

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 240, 240),  # I
    (0, 0, 240),    # J
    (240, 160, 0),  # L
    (240, 240, 0),  # O
    (0, 240, 0),    # S
    (160, 0, 240),  # T
    (240, 0, 0),    # Z
]

SHAPES = [
    [['.....',
      '.....',
      '..O..',
      '..O..',
      '..O..'],
     ['.....',
      '.....',
      'OOO..',
      '..O..',
      '.....']],
    [['.....',
      '.O...',
      '.OOO.',
      '.....',
      '.....'],
     ['.....',
      '..OO.',
      '..O..',
      '..O..',
      '.....'],
     ['.....',
      '.....',
      '.OOO.',
      '...O.',
      '.....'],
     ['.....',
      '..O..',
      '..O..',
      '.OO..',
      '.....']],
    [['.....',
      '...O.',
      '.OOO.',
      '.....',
      '.....'],
     ['.....',
      '..O..',
      '..O..',
      '..OO.',
      '.....'],
     ['.....',
      '.....',
      '.OOO.',
      '.O...',
      '.....'],
     ['.....',
      '.OO..',
      '..O..',
      '..O..',
      '.....']],
    [['.....',
      '..OO.',
      '..OO.',
      '.....',
      '.....']],
    [['.....',
      '..OO.',
      '.OO..',
      '.....',
      '.....'],
     ['.....',
      '.O..',
      '.OO.',
      '..O.',
      '.....']],
    [['.....',
      '..O..',
      '.OOO.',
      '.....',
      '.....'],
     ['.....',
      '..O..',
      '..OO.',
      '..O..',
      '.....'],
     ['.....',
      '.....',
      '.OOO.',
      '..O..',
      '.....'],
     ['.....',
      '..O..',
      '.OO..',
      '..O..',
      '.....']],
    [['.....',
      '.OO..',
      '..OO.',
      '.....',
      '.....'],
     ['.....',
      '..O..',
      '.OO..',
      '.O...',
      '.....']]
]

HIGHSCORE_FILE = 'highscores.txt'

class Piece:
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.shape_idx = shape_idx
        self.rotation = 0

    @property
    def shape(self):
        return SHAPES[self.shape_idx][self.rotation % len(SHAPES[self.shape_idx])]

    @property
    def color(self):
        return COLORS[self.shape_idx]


def create_grid(locked):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked.items():
        if y >= 0:
            grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    shape = piece.shape
    for i, line in enumerate(shape):
        for j, char in enumerate(line):
            if char == 'O':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece, grid):
    accepted = [[(j, i) for j in range(COLS) if grid[i][j] == BLACK] for i in range(ROWS)]
    accepted = [j for sub in accepted for j in sub]
    formatted = convert_shape_format(piece)
    for pos in formatted:
        if pos not in accepted:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for (x, y) in positions:
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(COLS // 2 - 2, 0, random.randrange(len(SHAPES)))


def draw_text_middle(surface, text, size, color, y_offset=0):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (WIDTH/2 - label.get_width()/2, HEIGHT/2 - label.get_height()/2 + y_offset))


def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(surface, grid[y][x], (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y*BLOCK_SIZE), (WIDTH, y*BLOCK_SIZE))
    for x in range(COLS):
        pygame.draw.line(surface, GRAY, (x*BLOCK_SIZE, 0), (x*BLOCK_SIZE, HEIGHT))


def clear_rows(grid, locked):
    cleared = 0
    for y in range(ROWS-1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            ind = y
            for x in range(COLS):
                try:
                    del locked[(x, y)]
                except:
                    continue
    if cleared > 0:
        for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + cleared)
                locked[newKey] = locked.pop(key)
    return cleared


def load_highscores():
    scores = []
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                name, s = line.strip().split(',', 1)
                scores.append((name, int(s)))
    return scores


def save_highscores(scores):
    scores.sort(key=lambda x: x[1], reverse=True)
    with open(HIGHSCORE_FILE, 'w', encoding='utf-8') as f:
        for name, s in scores[:5]:
            f.write(f"{name},{s}\n")


def draw_window(surface, grid, score=0):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f"Score: {score}", True, WHITE)
    surface.blit(label, (10, 10))


def draw_next_shape(surface, piece):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next:', True, WHITE)
    sx = WIDTH + 30
    sy = 50
    surface.blit(label, (sx + 10, sy - 30))
    format = piece.shape
    for i, line in enumerate(format):
        for j, char in enumerate(line):
            if char == 'O':
                pygame.draw.rect(surface, piece.color, (sx + j*BLOCK_SIZE, sy + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)


def main(stdscr):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return score
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not valid_space(current_piece, grid):
                        current_piece.rotation -= 1
                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True

        shape_pos = convert_shape_format(current_piece)

        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            cleared = clear_rows(grid, locked_positions)
            score += cleared * 100
            change_piece = False

        draw_window(stdscr, grid, score)
        draw_next_shape(stdscr, next_piece)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(stdscr, "GAME OVER", 40, WHITE)
            pygame.display.update()
            pygame.time.delay(1500)
            run = False

    return score


def get_name(screen):
    name = ""
    font = pygame.font.SysFont('comicsans', 30)
    while True:
        screen.fill(BLACK)
        draw_text_middle(screen, "Enter your name:", 30, WHITE, -30)
        label = font.render(name, True, WHITE)
        screen.blit(label, (WIDTH/2 - label.get_width()/2, HEIGHT/2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name if name else "Anon"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10 and event.unicode.isprintable():
                        name += event.unicode


def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 150, HEIGHT))
    pygame.display.set_caption('Tetris')

    scores = load_highscores()

    run = True
    while run:
        screen.fill(BLACK)
        draw_text_middle(screen, 'Press any key to play', 30, WHITE, -50)
        font = pygame.font.SysFont('comicsans', 24)
        y = HEIGHT/2
        screen.blit(font.render('High Scores:', True, WHITE), (WIDTH + 10, 10))
        for i, (n, s) in enumerate(scores[:5]):
            text = font.render(f"{i+1}. {n} - {s}", True, WHITE)
            screen.blit(text, (WIDTH + 10, 40 + i*30))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                score = main(screen)
                name = get_name(screen)
                if name is not None:
                    scores.append((name, score))
                    save_highscores(scores)
                scores = load_highscores()
    pygame.quit()


if __name__ == '__main__':
    main_menu()
