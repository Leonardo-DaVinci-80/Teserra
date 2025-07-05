import pygame
import random
import json
import os

SCORE_FILE = "score.json"

pygame.init()

WIDTH, HEIGHT = 300, 600 # screen size
enable_flash = True
ROWS, COLS = 20, 10 # the first tetris grid was 10 blocks wide and 20 blocks in length
BLOCK_SIZE = WIDTH // COLS # each block is 30x30 pixels
BLOCK_SIZE = 30
GRID_WIDTH = WIDTH // BLOCK_SIZE 
GRID_HEIGHT = HEIGHT // BLOCK_SIZE
# Colours
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
COLOURS = [(0, 255, 255), (255, 165, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255), (128, 0, 128), (255, 255, 0)]

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

# Window
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

def load_high_score():
    if os.path.exists(SCORE_FILE): 
        with open(SCORE_FILE, "r") as f:
            return json.load(f).get("high_score", 0)
    return 0

def save_high_score(score):
    with open(SCORE_FILE, "w") as f:
        json.dump({"high_score": score}, f)

def reset_high_score():
    if os.path.exists(SCORE_FILE):
        os.remove(SCORE_FILE)

# Grid
def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

    for (x, y), color in locked_positions.items():
        if y >= 0:
            grid[y][x] = color

    return grid

# Tetromino (shapes that can be split into 4 squares) class
class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.colour = random.choice(COLOURS)
        self.x = COLS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

# Convert the shape into positions
def convert_shape_format(shape):
    positions = []
    for i, row in enumerate(shape.shape):
        for j, val in enumerate(row):
            if val:
                positions.append((shape.x + j, shape.y + i))
    return positions

# Valid Move Checker
def valid_space(shape, grid):
    accepted = [[(j, i) for j in range(COLS) if grid[i][j] == BLACK] for i in range(ROWS)]
    accepted = [j for sub in accepted for j in sub]
    formatted = convert_shape_format(shape)
    for pos in formatted:
        if pos not in accepted:
            if pos[1] > -1:
                return False
    return True

# Clear Lines
def clear_rows(grid, locked):
    cleared_rows = []
    for y in range(len(grid) - 1, -1, -1):
        row = [locked.get((x, y)) for x in range(GRID_WIDTH)]
        if all(color != (0, 0, 0) and color is not None for color in row):
            cleared_rows.append(y)

    if enable_flash and cleared_rows:
        flash_rows(win, grid, cleared_rows)

    for y in cleared_rows:
        for x in range(GRID_WIDTH):
            try:
                del locked[(x, y)]
            except:
                continue

    if cleared_rows:
        for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
            x, y = key
            shift = sum(1 for row in cleared_rows if y < row)
            if shift:
                new_key = (x, y + shift)
                locked[new_key] = locked.pop(key)

    return len(cleared_rows)

# Draw grid
def draw_grid(surface, grid):
    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(surface, grid[i][j],
                             (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # Grid lines
    for i in range(ROWS):
        pygame.draw.line(surface, GREY, (0, i * BLOCK_SIZE), (WIDTH, i * BLOCK_SIZE))
    for j in range(COLS):
        pygame.draw.line(surface, GREY, (j * BLOCK_SIZE, 0), (j * BLOCK_SIZE, HEIGHT))

def draw_grid_lines(surface):
    # Horizontal lines
    for i in range(ROWS):
        pygame.draw.line(surface, GREY, (0, i * BLOCK_SIZE), (WIDTH, i * BLOCK_SIZE))
    # Vertical lines
    for j in range(COLS):
        pygame.draw.line(surface, GREY, (j * BLOCK_SIZE, 0), (j * BLOCK_SIZE, HEIGHT))

# Draw window
def draw_window(surface, grid, score, high_score):
    surface.fill(BLACK)

    # Draw each block from the grid (including locked ones)
    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(surface, grid[i][j],
                             (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    draw_grid_lines(surface)  # draw the grid lines

def get_random_shape():
    # Creates a new Tetromino object with a random shape.
    return Tetromino(random.choice(SHAPES))

def draw_falling_piece(surface, piece):
    # draws the current falling tetromino
    formatted_positions = convert_shape_format(piece)

    for x, y in formatted_positions:
        if y >= 0:
            rect = (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, piece.colour, rect, 0) # Fill
            pygame.draw.rect(surface, (0, 0, 0), rect, 1) # Border

def draw_game_over(surface, score):
    surface.fill(BLACK)

    high_score = load_high_score()

    title_font = pygame.font.SysFont("Consolas", 30, bold=True)
    small_font = pygame.font.SysFont("Consolas", 18)

    game_over = title_font.render("Game Over", True, (255, 0, 0))
    final_score = small_font.render(f"Your Score: {score}", True, (255, 255, 255))
    high_score_text = small_font.render(f"High Score: {high_score}", True, (255, 215, 0))
    restart_text = small_font.render("R: Restart", True, (255, 255, 255))
    quit_text = small_font.render("Q: Quit to Menu", True, (255, 255, 255))

    y = HEIGHT // 4
    surface.blit(game_over, (WIDTH // 2 - game_over.get_width() // 2, y))
    y += 40
    surface.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, y))
    y += 30
    surface.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, y))
    y += 40
    surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, y))
    y += 25
    surface.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, y))

    pygame.display.update()

def draw_start_screen(surface):
    surface.fill(BLACK)
    title_font = pygame.font.SysFont("Consolas", 30, bold=True)
    small_font = pygame.font.SysFont("Consolas", 18)

    title = title_font.render("TETRIS", True, (0, 255, 255))
    high_score = load_high_score()
    high_score_text = small_font.render(f"High Score: {high_score}", True, (255, 255, 0))

    play_text = small_font.render("P: Play", True, (255, 255, 255))
    quit_text = small_font.render("Q: Quit", True, (255, 255, 255))
    delete_text = small_font.render("D: Delete High Score", True, (180, 0, 0))

    flash_status = "ON" if enable_flash else "OFF"
    flash_warning = small_font.render(f"F: Toggle Flash [{flash_status}]", True, (255, 100, 100))
    epilepsy_warning = small_font.render("⚠ Flashing effect warning", True, (255, 0, 0))

    y = HEIGHT // 5
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, y))
    y += 50
    surface.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, y))
    y += 50
    surface.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, y))
    y += 30
    surface.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, y))
    y += 30
    surface.blit(delete_text, (WIDTH // 2 - delete_text.get_width() // 2, y))
    y += 30
    surface.blit(flash_warning, (WIDTH // 2 - flash_warning.get_width() // 2, y))
    y += 30
    surface.blit(epilepsy_warning, (WIDTH // 2 - epilepsy_warning.get_width() // 2, y))

    pygame.display.update()

def start_screen():
    draw_start_screen(win)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_d:
                    reset_high_score()
                    draw_start_screen(win)  # refresh with updated high score
                elif event.key == pygame.K_f:
                    global enable_flash
                    enable_flash = not enable_flash
                    draw_start_screen(win)

def clear_rows(grid, locked):
    cleared_rows = []
    for y in range(len(grid) - 1, -1, -1):
        row = [locked.get((x, y)) for x in range(GRID_WIDTH)]
        if all(color != (0, 0, 0) and color is not None for color in row):
            cleared_rows.append(y)

    if enable_flash and cleared_rows:
        flash_rows(win, grid, cleared_rows)

    for y in cleared_rows:
        for x in range(GRID_WIDTH):
            try:
                del locked[(x, y)]
            except:
                continue

    if cleared_rows:
        for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
            x, y = key
            shift = sum(1 for row in cleared_rows if y < row)
            if shift:
                new_key = (x, y + shift)
                locked[new_key] = locked.pop(key)

    return len(cleared_rows)


def get_ghost_piece(piece, grid):
    ghost = Tetromino(piece.shape)
    ghost.x = piece.x
    ghost.y = piece.y
    ghost.shape = [row[:] for row in piece.shape]
    ghost.colour = (100,100,100)

    while valid_space(ghost, grid):
        ghost.y += 1
    ghost.y -= 1

    return ghost

def pause_menu(surface):
    font = pygame.font.SysFont("Consolas", 25)
    surface.fill(BLACK)

    paused_text = font.render("Game Paused", True, (255, 255, 255))
    resume_text = font.render("P: Resume", True, (200, 200, 200))
    quit_text = font.render("Q: Quit to Menu", True, (200, 200, 200))

    surface.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 3))
    surface.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2))
    surface.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 40))
    pygame.display.update()

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
                elif event.key == pygame.K_q:
                    return "quit"

def flash_rows(surface, grid, rows):
    flash_duration = 150  # milliseconds
    flash_times = 2

    for _ in range(flash_times):
        # Draw all cleared rows as white
        for row in rows:
            for col in range(COLS):
                pygame.draw.rect(surface, (255, 255, 255),
                                 (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        pygame.display.update()
        pygame.time.delay(flash_duration)

        # Redraw original grid
        draw_window(surface, grid, 0, load_high_score())  # 0 for score
        draw_grid_lines(surface)
        pygame.display.update()
        pygame.time.delay(flash_duration)

def main():
    score = 0
    run = True
    current_piece = get_random_shape()
    locked_positions = {}
    grid = create_grid()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 500  # milliseconds

    while run:
        dt = clock.tick(60)
        fall_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

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
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotate()
                        current_piece.rotate()
                        current_piece.rotate()
                
                elif event.key == pygame.K_p:
                    result = pause_menu(win)
                    if result == "quit":
                        return # exits main() and returns to the start screen

        if fall_time >= fall_speed:
            current_piece.y += 1

            if not valid_space(current_piece, grid):
                current_piece.y -= 1

                for x, y in convert_shape_format(current_piece):
                    if y >= 0:
                        locked_positions[(x, y)] = current_piece.colour

                rows = clear_rows(grid, locked_positions)
                score += rows * 100  

                current_piece = get_random_shape()

                if not valid_space(current_piece, grid):
                    draw_game_over(win, score)
                    high_score = load_high_score()
                    if score > high_score:
                        save_high_score(score)

                    waiting = True
                    while waiting:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                waiting = False
                                run = False
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_r:
                                    main()
                                    return
                                elif event.key == pygame.K_q:
                                    return

            fall_time = 0  # Reset fall timer

        grid = create_grid(locked_positions)
        draw_window(win, grid, score, load_high_score())
        ghost_piece = get_ghost_piece(current_piece, grid)
        draw_falling_piece(win, ghost_piece)  # ghost piece first (drawn behind)
        draw_falling_piece(win, current_piece)

        pygame.display.update()

if __name__ == "__main__":
    while True:
        start_screen()
        main()
    pygame.quit()
