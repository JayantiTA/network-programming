# importing the required libraries
import logging
import pygame as pg
from pygame.locals import *
import sys
import socketio
import time


# init socketio client
sio = socketio.Client()

# set level logging
logging.getLogger().setLevel(logging.INFO)


# initiate all the variables and window screen
def initiate_var():
    # declaring the global variables
    global XO, winner, draw, board, turn, is_game_started, drawed, room # global variable for game
    global width, height, white, line_color, screen, cover_window, x_img, o_img, fps, CLOCK # global variable for gui

    # save the position that drawed on board
    drawed = set()
    # for storing the 'x' or 'o'
    # value as character
    XO = None
    turn = None

    # to store the current room of the game
    room = {}

    # as a flag when the game is started
    is_game_started = False

    # storing the winner's value at
    # any instant of code
    winner = None

    # to check if the game is a draw
    draw = None

    # to set width of the game window
    width = 400

    # to set height of the game window
    height = 400

    # to set background color of the
    # game window
    white = (255, 255, 255)

    # color of the straightlines on that
    # white game board, dividing board
    # into 9 parts
    line_color = (0, 0, 0)

    # setting up a 3 * 3 board in canvas
    board = [[None] * 3, [None] * 3, [None] * 3]

    # initializing the pygame window
    pg.init()

    # setting fps manually
    fps = 30

    # this is used to track time
    CLOCK = pg.time.Clock()

    # this method is used to build the
    # infrastructure of the display
    screen = pg.display.set_mode((width, height + 100), 0, 32)

    # setting up a nametag for the
    # game window
    pg.display.set_caption("My Tic Tac Toe")

    # loading the images as python object
    cover_window = pg.image.load("assets/modified_cover.png")
    x_img = pg.image.load("assets/X_modified.png")
    y_img = pg.image.load("assets/o_modified.png")

    # resizing images
    cover_window = pg.transform.scale(cover_window, (width, height + 100))
    x_img = pg.transform.scale(x_img, (80, 80))
    o_img = pg.transform.scale(y_img, (80, 80))
    display_message("Please wait...")


# show the message before the game started
def display_message(text_message):
    global screen, cover_window, width
    screen.blit(cover_window, (0, 0))
    # displaying over the screen
    text = pg.font.Font(None, 30).render(text_message, 1, (0, 0, 0))

    # copy the rendered message onto the board
    # creating a small block at the bottom of the main display
    text_rect = text.get_rect(center=(width / 2, 40))
    screen.blit(text, text_rect)


# show the initiate window (base column for X and O)
def initiate_game():
    # updating the display
    screen.fill(white)
    # drawing vertical lines
    pg.draw.line(screen, line_color, (width / 3, 0), (width / 3, height), 7)
    pg.draw.line(screen, line_color, (width / 3 * 2, 0), (width / 3 * 2, height), 7)

    # drawing horizontal lines
    pg.draw.line(screen, line_color, (0, height / 3), (width, height / 3), 7)
    pg.draw.line(screen, line_color, (0, height / 3 * 2), (width, height / 3 * 2), 7)
    draw_status()


# show the status of the game (turn, winner, and draw)
def draw_status():
    # getting the global variable draw
    # into action
    global draw, turn, XO, winner

    if winner is None:
        message = turn.upper() + "'s Turn || Your role: " + XO.upper()
    else:
        message = f"{winner.upper()} won ! || Click to play again"
        draw_win()
    if draw:
        message = "Game Draw !"

    # setting a font object
    font = pg.font.Font(None, 30)

    # setting the font properties like
    # color and width of the text
    text = font.render(message, 1, (255, 255, 255))

    # copy the rendered message onto the board
    # creating a small block at the bottom of the main display
    screen.fill((0, 0, 0), (0, 400, 500, 100))
    text_rect = text.get_rect(center=(width / 2, 500 - 50))
    screen.blit(text, text_rect)


# draw the line if there is a winner
def draw_win():
    global board
    # checking for winning rows
    for row in range(0, 3):
        if (board[row][0] == board[row][1] == board[row][2]) and (
            board[row][0] is not None
        ):
            pg.draw.line(
                screen,
                (250, 0, 0),
                (0, (row + 1) * height / 3 - height / 6),
                (width, (row + 1) * height / 3 - height / 6),
                4,
            )
            break

    # checking for winning columns
    for col in range(0, 3):
        if (board[0][col] == board[1][col] == board[2][col]) and (
            board[0][col] is not None
        ):
            pg.draw.line(
                screen,
                (250, 0, 0),
                ((col + 1) * width / 3 - width / 6, 0),
                ((col + 1) * width / 3 - width / 6, height),
                4,
            )
            break

    # check for diagonal winners
    if (board[0][0] == board[1][1] == board[2][2]) and (board[0][0] is not None):
        # game won diagonally left to right
        pg.draw.line(screen, (250, 70, 70), (50, 50), (350, 350), 4)

    if (board[0][2] == board[1][1] == board[2][0]) and (board[0][2] is not None):
        # game won diagonally right to left
        pg.draw.line(screen, (250, 70, 70), (350, 50), (50, 350), 4)


# draw X and O
def draw_xo(row, col, send):
    global board, turn

    # for the first row, the image
    # should be pasted at a x coordinate
    # of 30 from the left margin
    if row == 1:
        posx = 30

    # for the second row, the image
    # should be pasted at a x coordinate
    # of 30 from the game line
    if row == 2:
        # margin or width / 3 + 30 from
        # the left margin of the window
        posx = width / 3 + 30

    if row == 3:
        posx = width / 3 * 2 + 30

    if col == 1:
        posy = 30

    if col == 2:
        posy = height / 3 + 30

    if col == 3:
        posy = height / 3 * 2 + 30

    if tuple([row, col]) in drawed:
        return

    if send:
        sio.emit("turn", [row, col])

        if XO == 'x':
            screen.blit(x_img, (posy, posx))
        else:
            screen.blit(o_img, (posy, posx))
    else:
        if XO == 'x':
            screen.blit(o_img, (posy, posx))
        else:
            screen.blit(x_img, (posy, posx))

    drawed.add(tuple([row, col]))


def event_click():
    # get coordinates of mouse click
    x, y = pg.mouse.get_pos()

    # get column of mouse click (1-3)
    if x < width / 3:
        col = 1
    elif x < width / 3 * 2:
        col = 2
    elif x < width:
        col = 3
    else:
        col = None

    # get row of mouse click (1-3)
    if y < height / 3:
        row = 1
    elif y < height / 3 * 2:
        row = 2
    elif y < height:
        row = 3
    else:
        row = None

    # after getting the row and col,
    # we need to draw the images at
    # the desired positions
    if row and col and board[row - 1][col - 1] is None:
        draw_xo(row, col, True)
        draw_status()


# Event handler for connecting to the server
@sio.on("connect")
def connect():
    logging.warning("Connected to server")


# Event handler for receiving messages
@sio.on("message")
def receive_message(data):
    global is_game_started
    logging.info("Received message:", data)

    if data["player"] == 2:
        is_game_started = True
    elif "disconnected" not in data:
        display_message("Waiting for another player to join...")
        is_game_started = False
    elif "disconnected" in data and not winner and not draw:
        display_message("Enemy disconnected || Click to restart")
        is_game_started = False


# Event handler for receiving role
@sio.on("role")
def receive_role(data):
    global XO, room, turn, board
    logging.info("role: ", data["role"])

    XO = data["role"]
    room = data["room"]
    turn = room["turn"]
    board = room["board"]


# Event handler for receiving messages
@sio.on("turn")
def handle_turn(data):
    global XO, room, turn, board, winner, draw
    logging.info("Received message:", data)

    if data["room"] is not None:
        room = data["room"]
        current_position = room["turn_pos"]
        draw_xo(current_position[0], current_position[1], False) # draw before set new turn
        board = room["board"]
        draw = room["draw"]
        winner = room["winner"]
        turn = room["turn"]
        draw_status()


# quit the game
def quit_game():
    logging.warning("Game exited")
    sio.disconnect()
    pg.quit()
    pg.display.quit()
    sys.exit()


# start the game
def start_game():
    logging.warning("Game started")
    sio.emit("start_game")
    time.sleep(2)
    initiate_game()


if __name__ == "__main__":
    while True: # main game loop
        initiate_var()
        # Connect to the server
        sio.connect("http://localhost:8000")
        while True: # waiting for another player
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_game()
            pg.display.update()
            CLOCK.tick(fps)
            if is_game_started:
                start_game()
                break

        while is_game_started: # game loop
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_game()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if turn is not XO:
                        continue
                    if turn is not None and XO == turn:
                        event_click()

            pg.display.update()
            CLOCK.tick(fps)
            if winner or draw:
                break

        is_new_game_started = False
        is_game_started = False
        sio.disconnect()

        while not is_new_game_started: # game finished or enemy disconnected
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    pg.display.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    is_new_game_started = True

            pg.display.update()
            CLOCK.tick(fps)
