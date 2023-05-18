#coding: utf-8
import sys
import math
import numpy as np
import string
from time import sleep
import random

# Initialisation des variables globales
PLAYER1 = 1
PLAYER2 = 2
CELL_CODE = [' ', 'x', 'o']

# Colors variables for text
RED = '\033[31m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
BLUE = '\033[34m'
RESET = '\033[0m'

# Colors variables for highlighting the background
VERY_DARK_CYAN_BG = '\033[46m'
PINK_BG = '\033[48;5;218m'
RESET_BG = '\033[0m'

# Colors variables for highlighting the color depending on the player
PLAYER_COLOR_CODE = [None,CYAN, MAGENTA]
PLAYER_VS_BOT_COLOR_CODE = [None, MAGENTA, CYAN]
BOT_BG_COLOR_CODE = [None, PINK_BG, VERY_DARK_CYAN_BG]
PLAYER_BG_COLOR_CODE = [None, VERY_DARK_CYAN_BG, PINK_BG]

# ## I. BOARD REPRESENTATION

# ### 1.1 Representation of information as a matrix

# Board mid-game example
board_mid_game = np.array([[0,0,0,0,0,0,0,0,0],
                        [0,2,2,0,0,0,0,0,0],
                        [0,0,2,1,1,0,0,0,1],
                        [0,0,0,2,0,0,0,0,0],
                        [0,0,2,1,0,0,2,0,0],
                        [0,1,0,0,0,0,0,2,0],
                        [0,0,0,0,0,2,0,2,0],
                        [0,2,2,1,0,0,2,0,0],
                        [0,0,0,0,0,1,0,0,0]] )
board_just_before_free_move =np.array([[0,0,0,0,0,0,1,0,0],
                                    [1,0,0,0,1,0,0,0,0],
                                    [0,0,0,0,0,0,0,2,0],
                                    [0,0,0,0,0,0,0,0,2],
                                    [0,0,0,0,0,2,0,0,2],
                                    [0,0,0,0,0,0,0,2,0],
                                    [1,2,0,0,0,0,0,0,0],
                                    [0,0,0,0,0,2,0,2,2],
                                    [1,0,1,0,0,0,0,0,0]] )
# - We will create 3 configurations: start, mid-game and end-game
def create_board(size, style=1):
    total_cells = size * size
    # create board
    board = np.zeros((size, size), dtype=int)
    cells = [(i, j) for i in range(size) for j in range(size)]
    # 1st choice: create a standard starting board
    if style == 1:
        third = size//3
        board[0:third] = 1
        board[-third:] = 2
    # 2nd choice: create a random mid-game board
    elif style == 2:
        # add player 1
        player_indices = np.random.choice(range(len(cells)), size=int(total_cells /2), replace=False)
        player_cells = [cells[i] for i in player_indices]
        for i, (row, col) in enumerate(player_cells):
            if i <= total_cells / 4:
                board[col, row] = 1
            else:
                board[col, row] = 2
    # 3rd choice: create a random (almost) end-game board
    elif style == 3:
        player_indices = np.random.choice(range(len(cells)), size=18, replace=False)
        player_cells = [cells[i] for i in player_indices]
        for i, (row, col) in enumerate(player_cells):
            if i <= 9:
                board[col, row] = 1
            else:
                board[col, row] = 2
    # 4th choice: create a board for deadlock situation
    elif style == 4:
        board = board_just_before_free_move
    return board

# ### 1.2 Function to print the board

# - We will create a function to highlight the current player's cells
def hightlight_cell(cell_value, cell, current_player, curr_cell=None, human=None, bot=None):
    # We will set the background color depending on the player
    if human != 2: 
        # human == 1 (player vs player)    --> Human colors = VERY_DARK_CYAN_BG, Bot color = PINK_BG
        # or human == None (player vs bot) --> Player 1 color = VERY_DARK_CYAN_BG, Player 2 color = PINK_BG
        # PLAYER_BG_COLOR_CODE = [None, VERY_DARK_CYAN_BG, PINK_BG]
        if cell_value == current_player and curr_cell == None:
            return PLAYER_BG_COLOR_CODE[current_player]+CELL_CODE[cell_value]+RESET_BG # 
        # If player has selected a cell, highlight the selected cell
        elif curr_cell != None and cell[0] == curr_cell[0] and cell[1] == curr_cell[1]:
            return PLAYER_BG_COLOR_CODE[current_player]+CELL_CODE[cell_value]+RESET_BG 
        return CELL_CODE[cell_value]
    elif human == 2:
        # BOT_BG_COLOR_CODE = [None, PINK_BG, VERY_DARK_CYAN_BG]
        # Human colors = VERY_DARK_CYAN_BG, Bot color = PINK_BG
        # If player hasn't selected a cell yet, highlight all the current player's cells
        if cell_value == current_player and curr_cell == None:
            return BOT_BG_COLOR_CODE[current_player]+CELL_CODE[cell_value]+RESET_BG # PLAYER_COLOR_CODE = [None, CYAN, MAGNETA]
        # If player has selected a cell, highlight the selected cell
        elif curr_cell != None and cell[0] == curr_cell[0] and cell[1] == curr_cell[1]:
            return BOT_BG_COLOR_CODE[current_player]+CELL_CODE[cell_value]+RESET_BG 
        return CELL_CODE[cell_value]

def print_board(board, current_player, human=None, bot=None, curr_cell=None):
    # Print players infos
    if human == 1:
        player_1, player_2 = "YOU:", "BOT:"
        color_1, color_2 = CYAN, MAGENTA
    elif human == 2:
        player_1, player_2 = "BOT:", "YOU:"
        color_1, color_2 = MAGENTA, CYAN
    else:
        player_1, player_2 = "PLAYER 1:", "PLAYER 2:"
        color_1, color_2 = CYAN, MAGENTA
    # print the line of index of column:
    print('    ' + '   '.join([str(i) for i in range(1,len(board)+1)]))    
    print('  +' + '---+' * len(board))
    # print the rest of the board:
    count = 0
    for row in range(board.shape[0]):
        each_row = ''
        # print each row with its index as letters
        for col in range(board.shape[1]):
            my_cell = (row, col)
            value = board[row, col]
            cell_to_print = hightlight_cell(value, my_cell, current_player, curr_cell, human, bot)
            each_row += cell_to_print + ' | '
        print(string.ascii_uppercase[count],'|', each_row)
        print('  +' + ('---+' * len(board) ))
        count += 1
    count_player1 = np.count_nonzero(board == 1)
    count_player2 = np.count_nonzero(board == 2)
    print(f"{color_1}{player_1}{RESET} {color_1}{count_player1}{RESET} x left            {color_2}{player_2}{RESET} {color_2}{count_player2}{RESET} o left")

# - Function of waiting time for the bot
def print_bot_thinking(seconds=3):
    bot_phrase = ["Bot calculating its strategy", "Bot analyzing its next move","Bot planning its next move",
              "Bot contemplating its next strategy","Bot plotting its next move","Bot devising its master plan",
              "Bot strategizing for victory","Bot calculating its path to triumph","Bot: \"I'm thinking!\"",
              "Bot contemplating its winning moves","Bot mapping out its path to game triumph"]
    count = 0
    phrase = random.choice(bot_phrase)
    print( phrase,".", end="", flush=True)
    sleep(1)
    while count < seconds:
        print(".", end="", flush=True)
        count+=1
        sleep(1)
    print("")
    
def print_slow(text):
    for char in text:
        print(char, end='', flush=True)  # Print each character without a newline
        sleep(0.04)  # Adjust the sleep duration to control the speed

def print_loading():
    total_steps = 10
    for i in range(total_steps+1):
        progresss = i/total_steps*100
        filled_char = int(i/total_steps*20)
        empty_char = 20-filled_char
        print(f"\r{BLUE}LOADING: [{filled_char*'='}{empty_char*' '}] {progresss:.0f}%{RESET}", end="")
        sleep(0.3)
    print("")
    sleep(2)
       
def dot_moving(seconds):
    count = 0
    while count < seconds:
        sleep(1)
        print(".", end="", flush=True)
        count+=1
        sleep(1)
    print("")

# ##II. CHECKING THE VALIDITY OF A MOVE
# ### 2.1 Enter the coordinates and check if they are valid

# - Function to check if the format of the input is correct
def correct_formatting(cell): ## for example: a1, B2, C3, ...
    # split the cell into two parts: row and column
    if len(cell) != 2:
        return False
    else:
        row, col = cell[0], cell[1]  # split the string at the empty space
        #If the row index is an uppercase letter and the column index is a digit
        row_is_letter = row in string.ascii_letters
        col_is_digit = col in string.digits
        if row_is_letter and col_is_digit:
            return True
        else:
            return False   

def test_correct_formatting():
    assert correct_formatting('ABB') == False 
    assert correct_formatting('9B') == False
    assert correct_formatting('B8') == True
    assert correct_formatting('C*') == False
    assert correct_formatting('!8') == False
    assert correct_formatting('b5') == True
    print("Test 1. The cell is in the correct format")

# - Function to check if the cell is in the board
def cell_is_in_board(cell, board):
    size = len(board)
    # Check if the cell is in the board
    row, col = cell[0].lower(), cell[1]
    row = string.ascii_letters.index(row)
    col = int(col)-1
    if (row < size) & (col < size):
        return True
    else:
        return False
    
def test_cell_is_in_board():
    assert cell_is_in_board('E5', board_mid_game) == True
    assert cell_is_in_board('c9', board_mid_game) == True
    assert cell_is_in_board('C8', board_mid_game) == True
    assert cell_is_in_board('h8', board_mid_game) == True
    assert cell_is_in_board('Y9', board_mid_game) == False
    print('Test 2. The cell is in the board')

# - Function to get input of a cell from the user
def get_cell(board, which="start"):
    while True:
        cell = input(f"Enter {which} (ex: A1, b2, C3, ...) or {CYAN}'q'{RESET} to give up your turn or {MAGENTA}'e'{RESET} to exit\n")
        if cell == 'q': # if the user wants to quit or give up their turn
            return 'q'
        elif cell == 'e': # if the user wants to exit the game
            return 'e'
        else:
            good_format = correct_formatting(cell) and cell_is_in_board(cell, board)
            if good_format:
                row = string.ascii_letters.index(cell[0].lower()) 
                col = int(cell[1]) -1
                return (row, col)
            else:
                print('Invalid input. Try again.')           

# - Function to convert the cell into the index of the board (ex: (0,0) --> A1, (1,1) --> B2, ...)
def cell_to_code(cell):
    row, col = int(cell[0]), int(cell[1])
    row = string.ascii_letters[row].upper()
    col = col + 1
    return row+str(col)

def test_cell_to_code():
    assert cell_to_code((0,0)) == 'A1'
    assert cell_to_code((1,1)) == 'B2'
    assert cell_to_code((2,8)) == 'C9'
    assert cell_to_code((3,5)) == 'D6'
    assert cell_to_code((8,0)) == 'I1'
    print('Test 3. The cell is well converted to the code')

# - Function to get the value of a cell in the board (ex: (i,j) --> 0 or 1 or 2)
def get_value_from_pos(cell, board):
    row, col = cell[0], cell[1]
    return board[row, col]

def test_get_value_from_pos():
    assert get_value_from_pos((0,0), board_mid_game) == 0
    assert get_value_from_pos((1,1), board_mid_game) == 2
    assert get_value_from_pos((2,8), board_mid_game) == 1
    assert get_value_from_pos((3,5), board_mid_game) == 0
    assert get_value_from_pos((8,0), board_mid_game) == 0
    print('Test 4. The value of the cell is well retrieved')

# ### 2.2 Check some properties of the two cells:
# - Function to check if the two cells are different
def check_if_cells_are_different(cell1, cell2): 
    if cell1 == cell2:
        return False
    return True

def test_check_if_cells_are_different():
    assert check_if_cells_are_different((0,0), (0,0)) == False
    assert check_if_cells_are_different((1,1), (1,2)) == True
    print('Test 5. We can check if the two cells are different')
# - Function to check if the two cells are orthogonale
def check_if_cells_are_orthogonale (cell1, cell2): 
    if (cell1[0] == cell2[0]) or (cell1[1] == cell2[1]):
        return True
    return False

def test_check_if_cells_are_orthogonale():
    assert check_if_cells_are_orthogonale((0,0), (8,0)) == True
    assert check_if_cells_are_orthogonale((1,1), (1,2)) == True
    assert check_if_cells_are_orthogonale((1,1), (2,2)) == False
    assert check_if_cells_are_orthogonale((3,1), (2,4)) == False
    print('Test 6. We can check if the two cells are orthogonale')
# - Function to check if the two cells are diagonal
def check_if_cells_are_diagonal (cell1, cell2):
    if (abs(cell1[0] - cell2[0]) == abs(cell1[1] - cell2[1])):
        return True
    return False

def test_check_if_cells_are_diagonal():
    assert check_if_cells_are_diagonal((0,0), (8,8)) == True
    assert check_if_cells_are_diagonal((1,2), (4,5)) == True
    assert check_if_cells_are_diagonal((1,1), (1,2)) == False
    assert check_if_cells_are_diagonal((3,1), (2,4)) == False
    assert check_if_cells_are_diagonal((3,1), (2,2)) == True
    print('Test 7. We can check if the two cells are diagonal')

# - Function to check the valid direction of the move
def can_move_to(cell1, cell2):
    return check_if_cells_are_different(cell1, cell2) and (check_if_cells_are_orthogonale(cell1, cell2) or check_if_cells_are_diagonal(cell1, cell2))

def test_can_move_to():
    assert can_move_to((0,0), (8,0)) == True
    assert can_move_to((1,1), (1,2)) == True
    assert can_move_to((1,1), (2,2)) == True
    assert can_move_to((3,1), (2,4)) == False
    print('Test 8. We can check if the move is valid')
    
# - Function to get the step to loop through the cells in between (ex: get_step(1, 3) --> 1, get_step(3, 1) --> -1)
def get_step(number1, number2):
    diff = number2 - number1
    # we copy the sign of "diff" to 1 go get the step, if diff = 0, we return 0
    return int(math.copysign(1, diff) if diff != 0 else 0)

def test_get_step():
    assert get_step(1, 3) == 1
    assert get_step(3, 1) == -1
    print('Test 9. We can get the step to loop through the cells in between')
    
# - Function to get the coordinates of cells in between the two cells, and the cells of the opponent in between (jump-over move)
def get_interested_segment_and_cell(cell1, cell2, board):
    #get the cell of the two cells
    row1, col1 = cell1[0], cell1[1]
    row2, col2 = cell2[0], cell2[1]
    #get the step to loop through the cells in between
    row_step = get_step(row1, row2)
    col_step = get_step(col1, col2)
    
    # get the lists of row and col indices of the cells in between
    row_indices = list(range(row1, row2+row_step, row_step) if row_step != 0 else [row1]*(abs(col1-col2)+1))
    col_indices = list(range(col1, col2+col_step, col_step) if col_step != 0 else [col1]*(abs(row1-row2)+1))
    
    # return the segment and the cell of the opponent in between
    segment = []
    for i, j in zip(row_indices, col_indices):
        segment.append(board[i, j])
        
    prior_end_cell = (row_indices[-2], col_indices[-2])
    return np.array(segment), prior_end_cell

# - Function to count the number of occupied cells in a segment
def count_occupied_cells(segment):
    return sum([1 for cell in segment if cell != 0])

# - Function to get input of the player you want to play 
def ask_for_player():
    while True:
        player = input(f"Let's select your pawn ({BLUE}1{RESET} for {BLUE}'x'{RESET} or {BLUE}2{RESET} for {BLUE}'o'{RESET}): \n")
        if player.isdigit() and int(player) in [1, 2]:
            return int(player)
        else:
            print("Number should be 1 or 2. Please try again.")

# - Function to get input of the size of the board
def ask_for_size_of_board():
    while True:
        size = input(f"Enter the size of the board (size > 5), for example, {CYAN}9{RESET} for a {CYAN}9x9{RESET} board: \n")
        if size.isdigit() and int(size) > 5:
            return int(size)
        else:
            print("The size should be a number, or the number is too small. Please try again.")

# - Function to get input of the style of the board: 1 for standard starting board, 2 for random mid-game board, 3 for random (almost) end-game board
def ask_for_style_of_board():
    while True:
        style = input(f"Enter the style of the board:\n    {CYAN}1{RESET} for standard starting board \n    {CYAN}2{RESET} for random mid-game board \n    {CYAN}3{RESET} for random (almost) end-game board \n    {CYAN}4{RESET} for a 9x9 board to check deadlock situation \n")
        if style.isdigit() and int(style) in [1, 2, 3, 4]:
            return int(style)
        else:
            print("The style should be 1, 2, 3 or 4. Please try again.")

#- Function to get input of the style of the game: 1 for "Player vs Player", 2 for "Player vs Bot"
def introduction():
    # Introduction dialog
    print(f"{MAGENTA}*{RESET}"*50)
    print_slow(f"{BLUE}Welcome to the NAURU game!\n{RESET}")   
    print_slow(f"{BLUE}In this game you will be:\n{RESET}")
    print_slow(f"{BLUE}- engaging in a thrilling{RESET} {CYAN}Player versus Player{RESET} {BLUE}battle\n{RESET}")
    print_slow(f"{BLUE}- Or testing your skills against{RESET} {MAGENTA}a challenging bot{RESET}{BLUE}! \n{RESET}")
    print_slow(f"{BLUE}Let's get started!\n{RESET}")

def ask_for_style_of_game():
    while True:
        style = input(f"Enter the style: {CYAN}1{RESET} for {CYAN}\"Player vs Player\"{RESET}, {MAGENTA}2{RESET} for {MAGENTA}\"Player vs NAIVE Bot\"{RESET}, {RED}3{RESET} for {RED}\"Player vs BRAINY Bot\"{RESET} \n")
        if style.isdigit() and int(style) in [1, 2, 3]:
            return int(style)
        else:
            print("The style should be 1, 2, or 3. Please try again.")
# 2.3 Check if each type of move is valid:
## 2.3.1 Check if jump-on-top is valid:

# - Function to return the opponent of the current player
def return_opponent(player):
    return 1 if player == 2 else 2

# - Function to check if the elimination move is valid
def can_eliminate(cell1, cell2, board, player):
    # if the destination cell is empty or occupied by the player, return False
    if get_value_from_pos(cell2, board) in [0,player]:
        return False
    else:
        opponent = return_opponent(player)
        segment, prior_cell = get_interested_segment_and_cell(cell1, cell2, board)
        # If there is no empty cell in between, return False
        if len(segment) < 3:
            return False
        else:
            occupied_cell_count  = count_occupied_cells(segment)
            correct_player_cell = (segment[0] == player)
            correct_opponent_cell = (segment[-1] == opponent)
            return (occupied_cell_count == 2) and correct_opponent_cell and correct_player_cell

def test_can_eliminate():
    assert can_eliminate((4,2), (4,4), board_mid_game, 1) == False
    assert can_eliminate((4,2), (4,4), board_mid_game, 2) == False
    assert can_eliminate((6,5), (4,3), board_mid_game, 2) == True
    assert can_eliminate((6,5), (4,3), board_mid_game, 1) == False
    print('Test 10. We can check if the elimination move is valid')
    
## 2.3.2 Check if jump-over is valid:
# - Function to check if the jump-over move is valid
def can_jump_over(cell1, cell2, board, player):
    # if the destination cell is not empty, return False
    if get_value_from_pos(cell2, board) != 0:
        return False
    else:
        opponent = return_opponent(player)
        segment, prior_cell = get_interested_segment_and_cell(cell1, cell2, board)
        # If the pawn you want to jump over is not the opponent's, return False
        if board[prior_cell]!= opponent:
            return False
        else:
            occupied_cell_count  = count_occupied_cells(segment)
            # If the condition of the jump-over move i.e. only one cell in between, is not satisfied, return False
            if (len(segment) < 3) or occupied_cell_count != 2:
                return False
            else:
                # return the pawn you want to jump over if True, return False otherwise
                return (segment[0] == player) and (segment[-2] == opponent) and prior_cell 

def test_can_jump_over():
    assert can_jump_over((4,2), (4,4), board_mid_game, 2) == (4,3)
    assert can_jump_over((4,2), (4,4), board_mid_game, 1) == False
    assert can_jump_over((6,5), (3,2), board_mid_game, 2) == (4,3)
    print('Test 11. We can check if the jump-over move is valid')
    
def can_move_freely(cell1, cell2, board):
    # We already had the valid cell1, only need to check if cell2 and the cells between are empty
    segment, prior_cell = get_interested_segment_and_cell(cell1, cell2, board)
    count = np.count_nonzero(segment)
    return (count == 1)

def test_can_move_freely():
    assert can_move_freely((1,1), (4,1), board_mid_game ) == True
    assert can_move_freely((2,3), (5,6), board_mid_game) == True
    assert can_move_freely((4,2), (7,2), board_mid_game) == False
    assert can_move_freely((7,6), (3,6), board_mid_game) == False
    print('Test 12. We can check if the free move is valid')

# ## III. APPLYING A MOVE 
#- Function to update the board after a move is applied
def update_cell(board, curr_cell, end_cell):
    current_player = board[curr_cell[0], curr_cell[1]]
    board[curr_cell[0], curr_cell[1]] = 0
    board[end_cell[0], end_cell[1]] = current_player
    return board

# - Function to update the board after a jump-on-top move is applied
def update_opponent(board, cell):
    board[cell[0], cell[1]] = PLAYER1 if board[cell[0], cell[1]] == PLAYER2 else PLAYER2
    return board

# ## IV. GAME!
# ### 4.1 Functions auxiliaries to the game:

# - Function to check if the game is over
def check_game_over(board, human=None, bot=None):
    # player 1: x, pplayer 2 o
    if human == None and bot == None:
        player_1, player_2 = 'PLAYER 1', 'PLAYER 2'
    elif human == 1:
        player_1, player_2 = 'YOU', 'BOT'    
    elif human == 2:
        player_1, player_2 = 'BOT', 'YOU'
    count_player1 = np.count_nonzero(board == 1)
    count_player2 = np.count_nonzero(board == 2)
    if (count_player1 <= 5) or (count_player2 <=5):
        # Announce the winner
        print(f"{PLAYER_COLOR_CODE[1]}x{RESET} pawns: {count_player1}")
        print(f"{PLAYER_COLOR_CODE[2]}o{RESET} pawns: {count_player2}")
        print(f"{PLAYER_COLOR_CODE[1]}{player_1}{RESET} WON!") if count_player1 > count_player2 else print(f"{PLAYER_COLOR_CODE[2]}{player_2}{RESET} WON!")
        choice = input("Play again? (y/n)\n")
        while choice not in ['y', 'n']:
            print("Please enter 'y' or 'n'.")
            choice = input("Play again? (y/n)\n")
        if choice == 'y':
            return nauru()
        else:
            print_slow(f"{BLUE}Thanks for playing!{RESET}")
            sys.exit()

# 4.2 Functions auxiliaries to Player vs Bot version::
# - Function to get a list of all the cells in a correct direction of a cell in a board
def return_list_movable_cells(cell, board):
    row = cell[0]
    col = cell[1]
    list_movable_cells = []
    board_size = len(board)
    #get the cells in the same column
    for r in range(board_size):
        if r != row:
            list_movable_cells.append((r, col))
    #get the cells in the same row
    for c in range(board_size):
        if c != cell[1]:
            list_movable_cells.append((cell[0], c))
    # get the cells in the diagonal right down
    for r in range(board_size):
        for c in range(board_size):
            if (row -r == col -c) and (r,c) != cell:
                list_movable_cells.append((r, c))
    # get the cells in the diagonal left down
    for r in range(board_size):
        for c in range(board_size):
            if (row -r == -(col -c)) and (r,c) != cell:
                list_movable_cells.append((r, c))
    return list_movable_cells

# - Functions to get all the possible moves for a player with the celll selected

# - Function to get valid cells for a jump-over strategy
def list_for_jump_over(board, current_player, current_cell): 
    movable_cells_list = return_list_movable_cells(current_cell, board)
    list_to_return = []
    for cell in movable_cells_list:
        if can_jump_over(current_cell, cell, board, current_player):
            list_to_return.append(cell)
    return list_to_return

# - Function to get valid cells for the elimination strategy
def list_for_eliminate(board, current_player, current_cell): 
    movable_cells_list = return_list_movable_cells(current_cell, board)
    list_to_return = []
    for cell in movable_cells_list:
        if can_eliminate(current_cell, cell, board, current_player):
            list_to_return.append(cell)
    return list_to_return

# - Function to get valid cells for free move strategy
def list_for_move_freely(board, current_cell):
    movable_cells_list = return_list_movable_cells(current_cell, board)
    list_to_return = []
    for cell in movable_cells_list:
        if can_move_freely(current_cell, cell, board):
            list_to_return.append(cell)
    return list_to_return

# - Function to get all the choice of cells possible for a player at the beginning of his/her turn
def get_list_cells_to_choose(board, player):
    list_cells = []
    len_board = len(board)
    for row in range(len_board):
        for col in range(len_board):
            if board[row, col] == player:
                list_cells.append((row, col))
    return list_cells

# - Function to see if a cell is able to jump over another cell:

def get_two_lists_of_strategies(board, player):
    cells_to_choose = get_list_cells_to_choose(board, player)
    strategy_jump_over = []
    strategy_eliminate = []
    for cell in cells_to_choose:
        movable_list = return_list_movable_cells(cell, board)
        loop_next_destination = True
        check_eliminate = True
        check_jump_over = True
        while loop_next_destination:
        # Loop through each destination
            for destination in movable_list:
                # See if it is needed to check for elimination or jump over
                if check_eliminate or check_jump_over: #(if still needed)
                    if check_eliminate and can_eliminate(cell, destination, board, player):
                        strategy_eliminate.append(cell)
                        check_eliminate = False # No need to check for elimination anymore
                    elif check_jump_over and can_jump_over(cell, destination, board, player):
                        strategy_jump_over.append(cell)
                        check_jump_over = False # No need to check for jump over anymore
                else:
                    loop_next_destination = False
            loop_next_destination = False
    return strategy_jump_over, strategy_eliminate

#- Function to check if two players are stuck
def are_players_stuck(board, player1, player2=None): # PLAYER1 = 1, PLAYER2 = 2
    player1_is_stuck = True
    player2_is_stuck = True
    cells_of_player1 = get_list_cells_to_choose(board, player1) # an array of tuples [(0,0) ,(0,1), ...]
    # Player 1's situation
    while player1_is_stuck == True:
        for cell in cells_of_player1:
            if len(list_for_jump_over(board, player1, cell)) !=0 or len(list_for_eliminate(board, player1, cell)) !=0:
                player1_is_stuck = False
                break
        break
    if player2 != None:
    # Player 2's situation
        cells_of_player2 = get_list_cells_to_choose(board, player2) # an array of tuples [(1,0) ,(2,1), ...]
        while player2_is_stuck == True:
            for cell in  cells_of_player2:
                if len(list_for_jump_over(board, player2, cell)) !=0 or len(list_for_eliminate(board, player2, cell)) !=0:
                    player2_is_stuck = False
                    break
            break
    return player1_is_stuck and player2_is_stuck
# - Deadlock situation

def human_do_if_deadlock(board, current_player, human, bot, curr_cell=None, end_cell=None,strategy=None):
    if human == None or human == 1:
        COLOR_CODE = PLAYER_COLOR_CODE
    elif human == 2:
        COLOR_CODE = PLAYER_VS_BOT_COLOR_CODE
    opponent = return_opponent(current_player)
    if strategy == "jump":
        pass
    else:
        print("===========================================")
        header = ["{}YOUR TURN{}", "{}PLAYER{}'S TURN{}" ]
        print(header[0].format(CYAN, RESET) if human != None else header[1].format(PLAYER_COLOR_CODE[current_player], current_player, RESET))
        print_board(board, current_player, human, bot, curr_cell)
        print(f"{BLUE}Hmm{RESET}", end="", flush=True)
        dot_moving(3)
        print_slow(f"{BLUE}Looks like we've reached a deadlock! Nowhere to move.{RESET}\n")
        sleep(2)
        print_slow(f"{BLUE}Now you can move any of your pieces to any empty cell, but you can't jump over any piece.{RESET}\n")
        sleep(2)
        curr_cell = get_cell(board, which="a cell to begin")
        if curr_cell == 'e':
            sys.exit()
        elif curr_cell == 'q':
            return board, opponent
        else:
            while board[curr_cell] != current_player:
                wrong_cell = cell_to_code(curr_cell)
                curr_cell = None
                print_board(board, current_player, human, bot, curr_cell)
                phrase_header = ["You are {}Player {}.", "Your pawn is {}{}{}"]
                print(phrase_header[0].format(COLOR_CODE[current_player], current_player, RESET) if human == None else phrase_header[1].format(COLOR_CODE[current_player], CELL_CODE[current_player], RESET), end="", flush=True)
                print(f" The cell {RED}{wrong_cell}{RESET} you chose is not occupied by {COLOR_CODE[current_player]}{CELL_CODE[current_player]}{RESET}. Please try again.\n")
                curr_cell = get_cell(board, which="start cell")
                if curr_cell == 'e':
                    sys.exit()
                elif curr_cell == 'q':
                    return board, opponent
        print_board(board, current_player, human, bot, curr_cell)
        print(f"You chose the pawn {COLOR_CODE[current_player]}{cell_to_code(curr_cell)}{RESET}.")
        end_cell = get_cell(board, which="destination cell")
        if end_cell == 'e':
            sys.exit()
        elif end_cell == 'q':
            return board, opponent
        else:
            move_valid = can_move_to(curr_cell, end_cell) and can_move_freely(curr_cell, end_cell, board)
            while move_valid != True:
                end_cell = get_cell(board, which="destination cell")
                if end_cell == 'e':
                    sys.exit()
                elif end_cell == 'q':
                    return board, opponent
                move_valid = can_move_to(curr_cell, end_cell) and can_move_freely(curr_cell, end_cell, board)
        # update the board2
        board = update_cell(board, curr_cell, end_cell)
        curr_cell = end_cell
        print_board(board, current_player, human, bot, curr_cell)
        print(f"Nice move! You've just move your pawn to {COLOR_CODE[current_player]}{cell_to_code(curr_cell)}{RESET}!")
        print("Next player's turn...")
        sleep(3)
        return board, opponent
     
def bot_do_if_deadlock(board, current_player, human, bot, curr_cell=None, end_cell=None, strategy=None, bot_guided=False):
    BOT_NAME = "BOT" if bot_guided == False else "BRAINY BOT"
    print("=====================================")
    print(f"{MAGENTA}{BOT_NAME}'S TURN{RESET}")
    print_board(board, current_player, human, bot, curr_cell=None)
    print_slow(f"{BLUE}Hmm...{RESET}\n")
    sleep(2)
    print_slow(f"{BLUE}Looks like we've reached a deadlock! Nowhere to move.{RESET}\n")
    sleep(2)
    print_slow(f"{BLUE}{BOT_NAME} will now be allowed to make a free move.{RESET}\n")
    sleep(1)
    print_bot_thinking()
    list_valid_cells_for_bot = get_list_cells_to_choose(board, bot)
    cell = random.choice(list_valid_cells_for_bot)
    possible_moves = list_for_move_freely(board, cell)
    curr_cell = cell
    print_board(board, current_player, human, bot, curr_cell)
    print(f"{MAGENTA}{BOT_NAME}{RESET}: \"I am now at {MAGENTA}{cell_to_code(curr_cell)}{RESET}.\"")
    print_bot_thinking(2)
    end_cell = random.choice(possible_moves)
    board = update_cell(board, curr_cell, end_cell)
    print_board(board, current_player, human, bot, end_cell)
    print(f"{MAGENTA}{BOT_NAME}{RESET}: \"I made a free move from {MAGENTA}{cell_to_code(curr_cell)}{RESET} to {MAGENTA}{cell_to_code(end_cell)}{RESET}!\"\n")
    sleep(3)
    return board, human
    
    
    
# - Guided strategy for the bot

def guided_strategy(board, bot, strategy=None):
    # Get two lists of cells which are valid for each strategy
    jumpable_cells, eliminatable_cells = get_two_lists_of_strategies(board, bot)
    # count the number of cells left for bot
    number_cells_left = np.count_nonzero(board == bot)
    if number_cells_left > 10:
        proba = random.random()
        if proba >= 0.3 and len(eliminatable_cells) > 0: # 70% of the time, bot will eliminate
            cell = random.choice(eliminatable_cells)
            strategy = "eliminate"
        else:
            cell = random.choice(jumpable_cells) # 30% of the time, bot will jump
            strategy = "jump"
    else:
        proba = random.random()
        if proba >= 0.1 and len(jumpable_cells) > 0: # 90% of the time, bot will jump
            cell = random.choice(jumpable_cells)
            strategy = "jump"
        else:
            cell = random.choice(eliminatable_cells) # 10% of the time, bot will eliminate
            strategy = "eliminate"  
    return cell, strategy
    
# - Game flow for the computer bot
def bot_turn(board, current_player, human, bot, curr_cell=None, end_cell=None,strategy=None, bot_guided=False):
    # check deadlock
    BOT_NAME = "BOT" if bot_guided == False else "BRAINY BOT"
    dead_lock = are_players_stuck(board, current_player, human)
    if dead_lock:
        if strategy == "jump":
            pass
        else:
            if bot_guided == False:
                board, human = bot_do_if_deadlock(board, current_player, human, bot, curr_cell=None, end_cell=None, strategy=None, bot_guided=False)
            else:
                board, human = bot_do_if_deadlock(board, current_player, human, bot, curr_cell=None, end_cell=None, strategy=None, bot_guided=True)
            return board, human
    # check if bot is at a deadlock but its opponent is not
    bot_dead_lock = are_players_stuck(board, bot)
    if bot_dead_lock and strategy != "jump":
        print("=====================================")
        print(f"{MAGENTA}{BOT_NAME}'S TURN{RESET}")
        print_board(board, current_player, human, bot, curr_cell=None)
        print(f"{MAGENTA}Hmm{RESET}", end="", flush=True)
        dot_moving(3)
        print(f"{MAGENTA}{BOT_NAME}{RESET}: \"I'm at a dead end! Now it is your turn!\"")
        sleep(4)
        return board, human
    
    # Step 1: If the bot has not selected a cell yet, it selects one randomly, else it uses the cell it has selected
    if curr_cell == None:
        # select a random cell to begin with
        if bot_guided == False: # if bot is not guided, it will select a random cell
            list_cells_to_choose = get_list_cells_to_choose(board, bot)
            cell = random.choice(list_cells_to_choose)
            possible_moves = list_for_jump_over(board, bot, cell) + list_for_eliminate(board, bot, cell)
            while len(possible_moves) == 0:
                list_cells_to_choose.remove(cell)
                cell = random.choice(list_cells_to_choose)
                possible_moves = list_for_jump_over(board, bot, cell) + list_for_eliminate(board, bot, cell)     
            curr_cell = cell
        elif bot_guided == True: # if bot is guided, it will select a cell based on the guided strategy
            curr_cell, strategy = guided_strategy(board, bot, strategy=None)
            if strategy == "jump":
                possible_moves = list_for_jump_over(board, bot, curr_cell)
            elif strategy == "eliminate":
                possible_moves = list_for_eliminate(board, bot, curr_cell)
        print("=====================================")
        print(f"{MAGENTA}{BOT_NAME}'S TURN{RESET}")
        print_bot_thinking(3)
        print("=====================================")
        print_board(board, current_player, human, bot, curr_cell)
        print(f"{MAGENTA}{BOT_NAME}{RESET} is now at {MAGENTA}{cell_to_code(curr_cell)}{RESET}.")
        # select a random destination cell
        end_cell = random.choice(possible_moves)
        print_bot_thinking(4)
    else:
        # Bot has already has a cell to begin with, then choose randomly a destination cell
        possible_moves = list_for_jump_over(board, bot, curr_cell)
        if len(possible_moves) == 0:
            print(f"{MAGENTA}{BOT_NAME}{RESET} has given up its turn to you.")
            sleep(4)
            return board, human
        else:
            end_cell = random.choice(possible_moves)
            print_bot_thinking(4)
    
    # Step 2: Check if the move is valid and update the board
    # - Check which strategy bot has used
    strategy_eliminate = can_eliminate(curr_cell, end_cell, board, current_player) # True or False
    strategy_jump = can_jump_over(curr_cell, end_cell, board, current_player) # False or return prior cell if True

    ### Case 1: Eliminate
    if strategy_eliminate:
        strategy = "eliminate"
        board = update_cell(board, curr_cell, end_cell)
        print_board(board, current_player, human, bot, end_cell)
        print(f"{BOT_NAME} has eliminated your pawn at {CYAN}{cell_to_code(end_cell)}{RESET}. Now it is your turn!")
        check_game_over(board, human, bot)
        sleep(4)
        return board, human
    ### Case 2: Jump
    elif strategy_jump!=False:
        prior_cell = strategy_jump
        strategy = "jump"
        board = update_cell(board, curr_cell, end_cell)
        board = update_opponent(board, prior_cell)
        curr_cell = end_cell
        end_cell = None
        print_board(board, current_player, human, bot, curr_cell)
        print(f"{BOT_NAME} has jumped over your pawn at {CYAN}{cell_to_code(prior_cell)}{RESET} and is now at {MAGENTA}{cell_to_code(curr_cell)}{RESET}.")
        check_game_over(board, human, bot)
        return bot_turn(board, current_player, human,bot, curr_cell, end_cell=None, strategy="jump")

# - Game flow for the human player
def human_turn(board, current_player, human, bot, curr_cell=None, end_cell=None,strategy=None):
    opponent = bot
    # Step 1: Get input for the player (current cell) if it has not been selected yet, else use the cell it has selected
    dead_lock = are_players_stuck(board, current_player, opponent)
    if dead_lock:
        if strategy == "jump":
            pass
        else:
            board, current_player = human_do_if_deadlock(board, current_player, human, bot, curr_cell, end_cell, strategy)
            return board, current_player 
    print("*"*40)
    print(f"{CYAN}YOUR TURN{RESET}")
    print_board(board, current_player, human, bot, curr_cell)
    # If the player has not selected a cell yet, get input for the current cell
    if curr_cell == None:
        print(f"It's your turn, please choose a cell to move from. It must be occupied by {CYAN}{CELL_CODE[human]}{RESET}\n ")
        curr_cell = get_cell(board, which="start cell")
    if curr_cell == 'q':
        return board, bot
    elif curr_cell == 'e':
        sys.exit()
    ##`Check if the cell is occupied by the current player`
    else:
        while curr_cell in ['q', 'e'] or board[curr_cell] != human:
            wrong_cell = cell_to_code(curr_cell)
            curr_cell = None
            print_board(board, current_player, human, bot, curr_cell)
            print(f"The cell {RED}{wrong_cell}{RESET} you chose is not occupied by {CYAN}{CELL_CODE[human]}{RESET}. Please try again.\n")
            curr_cell = get_cell(board, which="start cell")
            if curr_cell == 'q':
                return board, bot
            elif curr_cell == 'e':
                sys.exit()
    print_board(board, human, human, bot, curr_cell)
    print(f"You are at {CYAN}{cell_to_code(curr_cell)}{RESET}.")
    # Step 2: Get input for the destination cell:
    if end_cell == None:
        end_cell = get_cell(board, which="destination cell")
        ## Step 2.1: Check if the player want to proceed with the move or quit
    if end_cell ==  'e':
        sys.exit()
    elif end_cell == "q": # give up the turn
        strategy_eliminate = False
        strategy_jump = False
        strategy = "quit"
    else:               # proceed with the move 
        # Check if the move is valid
        move_valid = can_move_to(curr_cell, end_cell) and (can_eliminate(curr_cell, end_cell, board, current_player) or (can_jump_over(curr_cell, end_cell, board, current_player)!= False))
        while move_valid != True: # if the move is not valid, ask for another destination cell
            print_board(board, current_player, human, bot, curr_cell)
            print(f"You are at {CYAN}{cell_to_code(curr_cell)}{RESET}.")
            print(f"The move {RED}{cell_to_code(end_cell)}{RESET} you chose is not valid.")
            end_cell = get_cell(board, which="destination cell")
            if end_cell == "q": # No move is possible, chose to give up the turn
                strategy_eliminate = False
                strategy_jump = False
                strategy = "quit"
                print(f"You gave the turn to Bot.\n")
                print("***************************************")
                sleep(2)
                return board, bot
            elif end_cell == 'e':
                sys.exit()
            else:              # found a move 
                move_valid = can_move_to(curr_cell, end_cell) and (can_eliminate(curr_cell, end_cell, board, current_player) or (can_jump_over(curr_cell, end_cell, board, current_player)!= False))
        strategy_eliminate = can_eliminate(curr_cell, end_cell, board, current_player)                    # strategy_jump = False or prior_cell if True
        strategy_jump = can_jump_over(curr_cell, end_cell, board, current_player)

    # Step 3: Update the board: according to the strategy (eliminate, jump, quit)
    ## Case 1: Eliminate
    if strategy_eliminate and (strategy != "jump"): # can jump on top but not after a jump over
        strategy = "eliminate"
        board = update_cell(board, curr_cell, end_cell)
        print_board(board, current_player, human, bot, end_cell)
        print(f"Good move from {CYAN}{cell_to_code(curr_cell)}{RESET} to {CYAN}{cell_to_code(end_cell)}{RESET}! You eliminated a pawn at {MAGENTA}{cell_to_code(end_cell)}{RESET}!\n")
        check_game_over(board, human, bot)
        sleep(2)
        return board, opponent
    ## Case 2: Jump 
    elif strategy_jump!= False: # can jump over (stategy_jump is the prior cell)
        strategy = "jump"
        prior_cell = strategy_jump
        board = update_cell(board, curr_cell, end_cell)
        board = update_opponent(board, prior_cell)
        print_board(board, current_player, human, bot, end_cell)
        print(f"Good move from {CYAN}{cell_to_code(curr_cell)}{RESET} to {CYAN}{cell_to_code(end_cell)}{RESET}! The pawn at {MAGENTA}{cell_to_code(prior_cell)}{RESET} is now yours! \n")
        check_game_over(board, human, bot)
        print("========================================")
        curr_cell = end_cell # update the current cell
        end_cell = None      # reset the destination cell
        end_cell = get_cell(board, which="destination cell")
        if end_cell == 'e':
            sys.exit()
        elif end_cell == 'q':  
            strategy = "quit"
            print(f"You gave the turn to Bot.\n")
            print("***************************************")
            sleep(2)
            return board, bot
        else:
            return human_turn(board, current_player, human, bot, curr_cell, end_cell, strategy="jump")
            
    # Case 3:  cannot eliminate after a jump 
    elif strategy_eliminate and strategy == "jump":
        print("OOPS! You cannot eliminate an opponent cell if you have already jumped over a cell\n. Try again\n")
        sleep(3)
        return human_turn(board, current_player, human, bot, curr_cell, end_cell=None, strategy = "jump")
    # Case 4: Quit
    elif strategy == "quit":
        print(f"You gave the turn to Bot.\n")
        sleep(2)
        return board, bot

def game_bot(board, current_player, human, bot, curr_cell=None, end_cell=None,strategy=None, bot_guided=False): 
    if current_player == bot: # human = 1 -> bot = 2; human = 2 -> bot = 1
        # run the game flow for the bot
        board, current_player = bot_turn(board, current_player, human, bot, curr_cell=None, end_cell=None, strategy=None, bot_guided=False)
        return board, current_player
    elif current_player == human:
        # run the game flow for the human
        board, current_player = human_turn(board, current_player, human, bot, curr_cell=None, end_cell=None, strategy=None)
        return board, current_player

def game_bot_guided(board, current_player, human, bot, curr_cell=None, end_cell=None,strategy=None, bot_guided=True):
    if current_player == bot: # human = 1 -> bot = 2; human = 2 -> bot = 1
        # run the game flow for the bot
        board, current_player = bot_turn(board, current_player, human, bot, curr_cell=None, end_cell=None, strategy=None, bot_guided=True)
        return board, current_player
    elif current_player == human:
        # run the game flow for the human
        board, current_player = human_turn(board, current_player, human, bot, curr_cell=None, end_cell=None, strategy=None)
        return board, current_player
    
# 4.3 Function auxiliar for Player vs Player version
def game_human(board, current_player, curr_cell=None, end_cell=None,strategy=None):
    # Initialize the variables human and bot to reuse the function print_board
    human = None
    bot = None
    opponent = return_opponent(current_player)  
    dead_lock = are_players_stuck(board, current_player, opponent)
    if dead_lock:
        if strategy == "jump":
            pass
        else:
            board, current_player = human_do_if_deadlock(board, current_player, human, bot, curr_cell, end_cell, strategy)
            return board, current_player 
    # Step 1: Get input for the player (current cell): 
    if curr_cell == None:
        print(f"{PLAYER_COLOR_CODE[current_player]}PLAYER {current_player}'S TURN{RESET}")
        print_board(board, current_player, human, bot, curr_cell)
        print(f"{PLAYER_COLOR_CODE[current_player]}Player {current_player}{RESET}, please choose a cell to move from. It must be occupied by {PLAYER_COLOR_CODE[current_player]}{CELL_CODE[current_player]}{RESET}\n ")
        curr_cell = get_cell(board, which="start cell")
    ##`Check if the cell is occupied by the current player`
    if curr_cell == 'e':
        sys.exit()
    elif curr_cell == 'q':
        return board, opponent
    else:
        while board[curr_cell] != current_player:
            wrong_cell = cell_to_code(curr_cell)
            curr_cell = None
            print_board(board, current_player, human, bot, curr_cell)
            print(f"You are {PLAYER_COLOR_CODE[current_player]}Player {current_player}{RESET}. The cell {RED}{wrong_cell}{RESET} you chose is not occupied by {PLAYER_COLOR_CODE[current_player]}{CELL_CODE[current_player]}{RESET}. Please try again.\n")
            curr_cell = get_cell(board, which="start cell")
            if curr_cell == 'e':
                sys.exit()
            elif curr_cell == 'q':
                return board, opponent
    # Step 2: Get input for the next cell ( cell):
    print_board(board, current_player, human, bot,  curr_cell)
    print(f"You are at {PLAYER_COLOR_CODE[current_player]}{cell_to_code(curr_cell)}{RESET}.")
    if end_cell == None:
        end_cell = get_cell(board, which="destination cell")
        ## Step 2.1: Check if the player want to proceed with the move or quit
    if end_cell == 'e':
        sys.exit()
    elif end_cell == "q":
        strategy_eliminate = False
        strategy_jump = False
        strategy = "quit"
    else:
        move_valid = can_move_to(curr_cell, end_cell) and (can_eliminate(curr_cell, end_cell, board, current_player) or (can_jump_over(curr_cell, end_cell, board, current_player)!= False))
        while move_valid != True:
            print_board(board, current_player, human, bot, curr_cell)
            print(f"You are at {PLAYER_COLOR_CODE[current_player]}{cell_to_code(curr_cell)}{RESET}.")
            print(f"The move {RED}{cell_to_code(end_cell)}{RESET} you chose is not valid. Try again.\n")
            end_cell = get_cell(board, which="destination cell")
            if end_cell == 'e':
                sys.exit()
            elif end_cell == "q":
                strategy_eliminate = False
                strategy_jump = False
                strategy = "quit"
                print(f"You gave the turn to {PLAYER_COLOR_CODE[opponent]}Player {opponent}{RESET}.\n")
                sleep(2)
                return board, opponent
            else:
                move_valid = can_move_to(curr_cell, end_cell) and (can_eliminate(curr_cell, end_cell, board, current_player) or (can_jump_over(curr_cell, end_cell, board, current_player)!= False))
        strategy_eliminate = can_eliminate(curr_cell, end_cell, board, current_player)                    # strategy_jump = False or prior_cell if True
        strategy_jump = can_jump_over(curr_cell, end_cell, board, current_player)

         
    # Step 3: Update the board: according to the strategy (eliminate, jump, quit)
    ## Case 1: Jump on top
    if strategy_eliminate and (strategy != "jump"): # can jump on top but not after a jump over
        strategy = "eliminate"
        board = update_cell(board, curr_cell, end_cell)
        print_board(board, current_player, human, bot, end_cell)
        print(f"Good move from {PLAYER_COLOR_CODE[current_player]}{cell_to_code(curr_cell)}{RESET} to {PLAYER_COLOR_CODE[opponent]}{cell_to_code(end_cell)}{RESET}! You eliminated a pawn at {PLAYER_COLOR_CODE[opponent]}{cell_to_code(end_cell)}{RESET}!\n")
        check_game_over(board)
        sleep(2)
        print(f"{PLAYER_COLOR_CODE[opponent]}PLAYER {opponent}'S TURN{RESET}\n")
        return board, opponent
    ## Case 2: Jump over
    elif strategy_jump!= False: # can jump over (stategy_jump is the prior cell)
        strategy = "jump"
        prior_cell = strategy_jump
        board = update_cell(board, curr_cell, end_cell)
        board = update_opponent(board, prior_cell)
        print_board(board, current_player, human, bot, end_cell)
        print(f"Good move from {PLAYER_COLOR_CODE[current_player]}{cell_to_code(curr_cell)}{RESET} to {PLAYER_COLOR_CODE[current_player]}{cell_to_code(end_cell)}{RESET}! The pawn at {PLAYER_COLOR_CODE[opponent]}{cell_to_code(prior_cell)}{RESET} is now yours! \n")
        check_game_over(board)
        print(f"You are now at {PLAYER_COLOR_CODE[current_player]}{cell_to_code(end_cell)}{RESET}.\n")
        curr_cell = end_cell
        end_cell = None
        end_cell = get_cell(board, which="destination cell")
        if end_cell == 'e':
            sys.exit()
        # save the chosen strategy
        elif end_cell == 'q':  
            strategy = "quit"
            print(f"You gave the turn to {PLAYER_COLOR_CODE[opponent]}Player {opponent}{RESET}.\n")
            sleep(2)
            return board, opponent
        else:
            return game_human(board, current_player, curr_cell, end_cell, strategy="jump")
            
    # Case 3 cannot jump on top after a jump over
    elif strategy_eliminate and strategy == "jump":
        print("Oops! You cannot eliminate an opponent cell if you have already jumped over a cell\n. Try again\n")
        sleep(3)
        return game_human(board, current_player, curr_cell, end_cell=None, strategy = "jump")
    # Case 4: Quit
    elif strategy == "quit":
        print(f"You gave the turn to {PLAYER_COLOR_CODE[opponent]}Player {opponent}{RESET}.\n")
        sleep(2)
        return board, opponent
def test():
    test_correct_formatting()
    test_cell_is_in_board()
    test_cell_to_code()
    test_get_value_from_pos()
    test_check_if_cells_are_different()
    test_check_if_cells_are_orthogonale()
    test_check_if_cells_are_diagonal()
    test_can_move_to()
    test_get_step()
    test_can_eliminate()
    test_can_jump_over()
    test_can_move_freely()
    sleep(1)
    print_slow(f"{MAGENTA}All tests passed! Game is ready!{RESET}\n")
    sleep(1)
    
# 4.5 Main funtion Player vs Player
def player_vs_player():
    size_board = ask_for_size_of_board()
    style_board = ask_for_style_of_board()
    board = create_board(size_board, style=style_board)
    current_player = ask_for_player()
    while True:
        board, current_player = game_human(board, current_player, curr_cell=None, end_cell=None)

# 4.6 Main funtion Player vs Bot
def player_vs_bot():
    size_board = ask_for_size_of_board()
    style_board = ask_for_style_of_board()
    board = create_board(size_board, style=style_board)
    human = ask_for_player()
    bot = return_opponent(human)
    current_player = human
    while True:
        board, current_player = game_bot(board, current_player, human, bot, curr_cell=None, end_cell=None, strategy=None)

#  4.7 Main funtion of the game Player vs Bot guided
def player_vs_bot_guided():
    size_board = ask_for_size_of_board()
    style_board = ask_for_style_of_board()
    board = create_board(size_board, style=style_board)
    human = ask_for_player()
    bot = return_opponent(human)
    current_player = human
    while True:
        board, current_player = game_bot_guided(board, current_player, human, bot, curr_cell=None, end_cell=None, strategy=None, bot_guided=True)

# 4.8 Main funtion of the game
def nauru():
    game_style = ask_for_style_of_game() # 1 for player vs player, 2 for player vs bot
    if game_style == 1: # player vs player
        player_vs_player()
    elif game_style == 2: # player vs bot
        player_vs_bot()
    elif game_style == 3: # player vs bot guided
        player_vs_bot_guided()

def game():
    test()
    print_loading()
    introduction()
    nauru()
if __name__ == '__main__':  
    game()