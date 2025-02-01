# Licensing information in the LICENSE file
# From this code you might be able to tell that I don't use Python

import random
import time
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import sys
from collections import deque

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=64,
    height=32,
    bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13,
    latch_pin=board.D0,
    output_enable_pin=board.D1,
)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

palette = displayio.Palette(4)
palette[0] = 0x000000  # Empty
palette[1] = 0xFFFFFF  # Border
palette[2] = 0x00FF00  # Snake
palette[3] = 0xFF0000  # Apple

bmp = displayio.Bitmap(display.width, display.height, 4)

def draw_border():
    for i in range(display.width):
        bmp[i, 0] = 1
        bmp[i, display.height - 1] = 1
    for i in range(display.height):
        bmp[0, i] = 1
        bmp[display.width - 1, i] = 1

draw_border()

tg = displayio.TileGrid(bmp, pixel_shader=palette)
g = displayio.Group()
g.append(tg)
display.root_group = g

snake_body = [
    (15, 16),
    (14, 16),
    (13, 16),
    (12, 16),
    (11, 16),
    (10, 16),
    (9, 16),
    (8, 16),
    (7, 16),
    (6, 16),
    (5, 16),
    (4, 16),
    (3, 16),
]  # the coords of the snake, element 0 is the head


def game_over():
    time.sleep(1)
    print("GAME OVER")
    sys.exit()


def get_random_apple_pos():
    # If the snake somehow finished the game, reset
    if len(snake_body) == ((display.width - 1) * (display.height - 1)) - 2:
        game_over()
        return

    # Keep on looking for a possible apple position
    pos = (random.randint(1, display.width - 2), random.randint(1, display.height - 2))
    while pos in snake_body:
        pos = (
            random.randint(1, display.width - 2),
            random.randint(1, display.height - 2),
        )
    return pos


apple_coords = get_random_apple_pos()

# Basically all of the game logic
def next_move():
    global apple_coords

    # Breadth First Search
    # It is an algorithm that finds the shortest path

    queue = deque()

    # Struggling with python arrays, AI had to fix the array generation (list index out of range errors earlier)
    visited = [[False for _ in range(display.height)] for _ in range(display.width)]
    parents = [[None for _ in range(display.height)] for _ in range(display.width)]

    for xx in snake_body:
        # The path-finding BFS cannot go to boxes marked as visited
        # so this is an easy way to make sure the snake doesn't run into itself
        visited[xx[0]][xx[1]] = True

    queue.append(snake_body[0])

    while queue:
        thing = queue.popleft()

        neighbours = [
            (thing[0] - 1, thing[1]),
            (thing[0] + 1, thing[1]),
            (thing[0], thing[1] - 1),
            (thing[0], thing[1] + 1),
            # Uncomment the next four lines if you want diagonals!
            # (thing[0]+1, thing[1]+1),
            # (thing[0]+1, thing[1]-1),
            # (thing[0]-1, thing[1]-1),
            # (thing[0]-1, thing[1]+1),
        ]

        for neighbour in neighbours:
            if neighbour[0] < 1 or neighbour[0] >= (display.width - 1):
                continue
            if neighbour[1] < 1 or neighbour[1] >= (display.height - 1):
                continue

            if not visited[neighbour[0]][neighbour[1]]:
                visited[neighbour[0]][neighbour[1]] = True
                queue.append(neighbour)
                parents[neighbour[0]][neighbour[1]] = thing

                if neighbour == apple_coords:
                    # Going back and getting the whole path
                    path = []
                    current = neighbour
                    while current != snake_body[0]:
                        path.insert(0, current)
                        current = parents[current[0]][current[1]]

                    if path:
                        nextPos = path[0]
                        snake_body.insert(0, nextPos)
                        if snake_body[0] == apple_coords:
                            apple_coords = get_random_apple_pos()
                        else:
                            # This is in the `else` because the
                            # snake body should grow when an apple
                            # is eaten
                            snake_body.pop()

                        return

    # No path found
    game_over()


# Renders the current game state to the bitmap
def render_game():
    # Empty the screen
    for a in range(display.width):
        for b in range(display.height):
            bmp[a, b] = 0

    # Re-draw the border
    draw_border()

    # Draw the snake
    for coord in snake_body:
        bmp[coord[0], coord[1]] = 2

    # Draw the apple
    bmp[apple_coords[0], apple_coords[1]] = 3

while True:
    next_move()
    render_game()
    display.refresh(minimum_frames_per_second=0)
    time.sleep(0.05)
