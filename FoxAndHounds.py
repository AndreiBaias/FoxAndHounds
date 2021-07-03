import pygame
from copy import deepcopy
import time


#constante
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = HEIGHT//ROWS

#culori
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
INDIGO = (75, 0, 130)
GOLD = (255,215,0)

#fereastra
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Baias Bogdan-Andrei Vulpea si Cainii')





#tabla
class Board:
    #constructor
    def __init__(self):
        self.board = []
        self.board_debug = []
        self.create_board()
        self.foxPos = (7, 0)
        self.prevFoxPos = (0,0)


    #creare gui tabla de joc
    def draw_board(self, window):
        window.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(window, WHITE, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


    #functie de calculare a scorului
    #daca o miscare duce la o stare in care cainii castiga atunci ofer un "incentive" sa se ia acea ruta
    #starea este mai avantajoasa pentru jucator cu cat:
    #vulpea e mai aproape de linia 0 - incerc sa blochez drumurile vulpii
    #vulpea are mai multe miscari valabile - incerc sa inconjor vulpea, eventual folosindu-ma de linia 7 si coloanele 0 si 7
    #distanta adunata de la toti cainii la vulpe e mai mare - incerc sa ma deplasez catre vulpe cu cainii
    #distantele dintre cel mai de sus si cel mai de jos caine, respectiv dintre cel mai din dreapta si cel mai din stanga caine sunt mai mari - incerc sa tin cainii cat mai apropiati pentru a putea inconjura vulpea
    #o mutare duce la victorie pentru jucator - prioritizez miscari care nu duc la victoria vulpii
    def evaluate(self):
        if len(self.get_valid_moves(self.get_piece(self.foxPos[0], self.foxPos[1]))) == 0 :
            return 10000000
        return -(7 - self.foxPos[0]) * 10 - len(self.get_valid_moves(self.get_piece(self.foxPos[0], self.foxPos[1]))) * 4 - self.distance_to_fox() * 8 - self.distance_between_blacks() * 6 - self.will_win()


    #functia a doua de calculare a scorului
    #o miscare a vulpii are scor mai mare daca e mai aproape de linia 0, daca e mai departe de piesele negre si daca are cat mai multe miscari posibile la un punct
    #folosesc si prima functie de evuluare pentru a face vulpea sa foloseasca miscarile care duc la o victorie cat mai rapida
    def alternate_evaluate(self):

        return 8**abs(self.foxPos[0] - 7) + self.distance_to_fox() * 2 + 4 ** abs(4 - self.foxPos[1]) - self.evaluate()


    #functie pentru a obtine o lista cu toate piesele de o culoare - folosita in special pentru a returna cainii si a vedea pozitiile lor
    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        # print(pieces)
        return pieces

    #functie pentru suma distantelor dintre caini si vulpe
    def distance_to_fox(self):
        distance = 0
        for piece in self.get_all_pieces(BLACK):
            distance = distance + abs(self.foxPos[0] - piece.row) + abs(self.foxPos[1] - piece.col)
        return distance

    #functie pentru a calcula cat de "deschis" sunt pozitionati cainii
    def distance_between_blacks(self):
        distance = 0
        minX = 8
        maxX = 0
        minY = 8
        maxY = 0
        for piece in self.get_all_pieces(BLACK):
            if piece.row > maxY :
                maxY = piece.row
            if piece.col > maxX :
                maxX = piece.col
            if piece.row < minY :
                minY = piece.row
            if piece.col < minX :
                minX = piece.row
        return (maxX - minX) * 2 + (maxY - minY) * 3 + maxX *2

    #functie care verifica daca urmeaza ca vulpea sa castige
    #"simulez" o stare succesor fara sa o calculez
    def will_win(self):
        for move in self.get_valid_moves(self.get_piece(self.foxPos[0], self.foxPos[1])):
            if move[0] == 0:
                return 1000000
        return 0

    #functie care numara cate piese negre sunt in jurul vulpii
    #am renuntat la ea
    # def blacks_close(self):
    #     number_blacks = 0
    #     if self.foxPos[0] < 7 and self.foxPos[1] < 7 and self.foxPos[1] > 0 :
    #         if self.get_piece(self.foxPos[0]-1, self.foxPos[1]-1) != 0:
    #             number_blacks = number_blacks + 1
    #         elif self.get_piece(self.foxPos[0]-1, self.foxPos[1]+1) != 0:
    #             number_blacks = number_blacks + 1
    #         elif self.get_piece(self.foxPos[0]+1, self.foxPos[1]-1) != 0:
    #             number_blacks = number_blacks + 1
    #         elif self.get_piece(self.foxPos[0]+1, self.foxPos[1]+1) != 0:
    #             number_blacks = number_blacks + 1
    #     return number_blacks


    #miscarea unei piese pe tabla - piece e piesa, row si col sunt indicii noii pozitii
    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        self.board_debug[piece.row][piece.col], self.board_debug[row][col] = self.board_debug[row][col], self.board_debug[piece.row][piece.col]
        if piece.color == RED:
            self.foxPos = (row, col)
            self.prevFoxPos = (piece.row, piece.col)
        piece.move(row, col)


    #functie pentru verificarea starii finale
    def winner(self):
            piece = self.get_piece(self.foxPos[0], self.foxPos[1])
            if self.foxPos[0] == 0:
                return 'Fox'
            elif not self.get_valid_moves(piece) :
                return 'Hounds'
            else:
                return None


    #getter piesa pe tabla - folosita in special pentru debug pe parcursul realizarii temei
    def get_piece(self, row, col):
        return self.board[row][col]

    #tabla in memorie - 0 unde nu am piese, obiect Piece unde am piesa
    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 1 :
                        self.board[row].append(Piece(row, col, BLACK))
                    elif row == 7 and col == 0:
                        self.board[row].append(Piece(row,col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
            # print(self.board[row][0].__repr__)


    #construire matricea tabla sub forma necesara pentru debug - unde am piese afisez tipul ei, in rest afisez culoarea de pe tabla
    def _init_board_debug(self):
        for row in range(ROWS):
            self.board_debug.append([])
            for col in range(COLS):
                if isinstance(self.board[row][col], Piece):
                    if str(self.board[row][col]) == str(RED) :
                        self.board_debug[row].append("Fox")
                    else:
                        self.board_debug[row].append("Hound")
                else:
                    if row%2 == 0:
                        if col%2 == 1:
                            self.board_debug[row].append("BLACK")
                        else:
                            self.board_debug[row].append("WHITE")
                    else:
                        if col%2 == 0:
                            self.board_debug[row].append("BLACK")
                        else:
                            self.board_debug[row].append("WHITE")
        return self.board_debug

    #afisarea tablei memorate pentru debug
    def debug_print(self):
        if self.board_debug == []:
            self._init_board_debug()
        for row in range(ROWS):
            print(self.board_debug[row])


    #functie pentru desenarea pieselor pe tabla
    def draw(self, window):
        self.draw_board(window)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0 :
                    piece.draw_piece(window)

    #functie pentru aflarea pozitiilor in care se poate muta o piesa la un anumit moment
    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED:
            moves.update(self._traverse_left(row-1, max(row-3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row-1, max(row-3, -1), -1, piece.color, right))
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        if piece.color == BLACK:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
        return moves

    #functie pentru mutare pe diagonala a unei piese
    #pozitia de plecare, pozitia finala, directia, culoarea piesei, coloana din stanga
    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0 :
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r + 3, ROWS)

                break
            elif current.color == RED or current.color == BLACK:
                break
            else:
                last = [current]

            left -= 1

        return moves

    #analog cu functia anterioara, dar pentru mutari in dreapta
    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)


                break
            elif current.color == RED or current.color == BLACK:
                break
            else:
                last = [current]

            right += 1

        return moves

    def __repr__(self):
        return self.board

#piese
class Piece:
    PADDING = 10
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color

        self.x = 0
        self.y = 0
        self.pos()

    #pozitia pe ecran a unei piese
    def pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    #modificare pozitie dupa mutare
    def move(self, row, col):
        self.row = row
        self.col = col
        self.pos()

    #desenare piesa
    def draw_piece(self, window):
        radius = SQUARE_SIZE//2 - self.PADDING
        pygame.draw.circle(window, INDIGO, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(window, self.color, (self.x, self.y), radius)

    def __repr__(self):
        return str(self.color)


class Game:
    def __init__(self, window):
        self.selected = None
        self._init()
        self.window = window

    #functia de update pentru joc
    #fac update la tabla si verific conditia de win
    def update(self):
        self.board.draw(self.window)
        if self.selected:
            self.draw_valid_moves(self.valid_moves)
        if self.board.winner() == 'Fox':
            pygame.draw.circle(self.window, GOLD, (self.board.foxPos[1]* SQUARE_SIZE + SQUARE_SIZE // 2, self.board.foxPos[0] * SQUARE_SIZE + SQUARE_SIZE // 2 ), 50)
            pygame.display.update()
            time.sleep(3)
            pygame.draw.rect(window, RED, (0,0, 800, 800))
            pygame.init()
            font = pygame.font.Font('freesansbold.ttf', 64)
            text = font.render(' !!!         FOX WON         !!!', True, GOLD)
            window.blit(text, (0, 350))
            pygame.display.update()
            time.sleep(3)

        elif self.board.winner() == 'Hounds':
            for piece in self.board.get_all_pieces(BLACK):
                pygame.draw.circle(self.window, GOLD, (piece.col * SQUARE_SIZE + SQUARE_SIZE // 2, piece.row * SQUARE_SIZE + SQUARE_SIZE // 2), 50)
                pygame.display.update()
            time.sleep(3)
            pygame.draw.rect(window, INDIGO, (0, 0, 800, 800))
            pygame.init()
            font = pygame.font.Font('freesansbold.ttf', 64)
            text = font.render('!!!      HOUNDS WON      !!!', True, GOLD)
            window.blit(text, (0, 350))
            pygame.display.update()
            time.sleep(3)

        else:
            pass
        pygame.display.update()

    def _init(self):
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}
        self.board.debug_print()

    #daca vreau sa resetez tabla
    def reset(self):
        self._init(self)

    #functie care selecteaza o piesa si arata miscarile valide
    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            #miscare invalida => reiau incercarea de mutare
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        #daca schimb piesa - folosita la debug
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        return False

    #functie pentru miscarea in game
    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            self.board.debug_print()
            self.change_turn()
        else:
            return False
        return True

    #functie pentru desenarea mutarilor posibile pentru o piesa
    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.window, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 20)

    #functie de alternare a jucatorilor
    def change_turn(self):
        self.valid_moves = []
        if self.turn == RED:
            self.turn = BLACK
            print("Hounds to move")
        else:
            print("Fox to move")
            self.turn = RED

    def get_board(self):
        return self.board

    #functie pentru mutari facute de calculator
    def ai_move(self, board):
        self.board = board
        self.change_turn()

#algoritmul minimax - position este starea ca tabla de joc, depth este adancimea arborelui, max_player - bool care verifica daca se alege min sau max
def minmax(position, depth, max_player):
    if depth == 0 or position.winner() != None:
        return position.evaluate(), position

    if max_player:
        maxEval = float('-inf')
        best_move = None
        for move in get_all_moves(position, BLACK):
            evaluation = minmax(move, depth-1, False)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move

        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(position, RED):
            evaluation = minmax(move, depth - 1, True)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move

        return minEval, best_move



#algoritmul alpha-beta aplicat pentru vulpe, analog celui anterior dar cu functia de evaluare schimbata si cu verificari aditionale pentru alpha si beta  + retezari
def alpha_beta_fox(alpha, beta, position, depth, max_player):
    if depth == 0 or position.winner() != None:
        return position.alternate_evaluate(), position

    if alpha > beta:
        return position.alternate_evaluate(), position

    if max_player:
        maxEval = float('-inf')
        best_move = None
        for move in get_all_moves(position, RED):
            evaluation = alpha_beta_fox(alpha, beta, move, depth-1, False)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
            alpha = max(alpha, evaluation)
            if alpha == evaluation and alpha >= beta:
                break

        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(position, BLACK):
            evaluation = alpha_beta_fox(alpha, beta, move, depth - 1, True)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
            beta = min(beta, evaluation)
            if beta == evaluation and alpha >= beta:
                break


        return minEval, best_move


#functie auxiliara de simulare mutari pentru minimax
def simulate_move(piece, move, board):
    board.move(piece, move[0], move[1])
    return board

#functie care returneaza toate mutarile posibile pentru o categorie de piese
#functia succesor care memoreaza starile in care duc mutarile posibile simulate
def get_all_moves(board, color):
    moves = []
    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move in valid_moves.keys():
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board)
            moves.append(new_board)

    return moves

#functie care imi da pozitia in matrice a mouse-ului
def get_pos_mouse(pos):
    x,y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

#menu mod joc
def game_intro():
    intro = True
    # pygame.init()
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # intro = False
                quit()

        window.fill(INDIGO)

        title = pygame.image.load("title.png")
        titleText = window.blit(title, title.get_rect())    # title is an image
        titleText.center = ((WIDTH / 2), (HEIGHT / 2))

        playerVSplayer = pygame.image.load("playerVSplayer.png")
        playerVSai = pygame.image.load("playerVSai.png")
        aiVSai = pygame.image.load("aiVSai.png")

        # button(100, 350, 195, 80, aiVSai, playerVSai, main_players)
        # button(x, y, w, h, inactive, active, action=None)
        button(0, 200, 195, 80, playerVSplayer, main_players)
        button(0, 300, 195, 80, playerVSai, depth_selector_player_ai)
        button(0, 400, 195, 80, aiVSai, depth_selector_ai_ai)

        pygame.display.update()
        pygame.time.Clock().tick(15)

#butoane
def button(x, y, w, h, inactive, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        window.blit(inactive, (x, y))
        if click[0] == 1 and action is not None:
            action()
    else:
        window.blit(inactive, (x, y))

#menu selectare adancime arbore player vs ai
def depth_selector_player_ai():
    intro1 = True
    pygame.init()
    while intro1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                intro1 = False
                quit()

        window.fill(INDIGO)

        title = pygame.image.load("title.png")
        titleText = window.blit(title, title.get_rect())
        titleText.center = ((WIDTH / 2), (HEIGHT / 2))

        depth3 = pygame.image.load("depth3.png")
        depth5 = pygame.image.load("depth5.png")
        depth7 = pygame.image.load("depth7.png")

        button(0, 200, 195, 80, depth3, main3)
        button(0, 300, 195, 80, depth5, main5)
        button(0, 400, 195, 80, depth7, main7)

        pygame.display.update()
        pygame.time.Clock().tick(15)


#menu selectare adancime arbore ai vs ai
def depth_selector_ai_ai():
    intro2 = True
    pygame.init()
    while intro2:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                intro2 = False
                quit()

        window.fill(INDIGO)

        title = pygame.image.load("title.png")
        titleText = window.blit(title, title.get_rect())
        titleText.center = ((WIDTH / 2), (HEIGHT / 2))

        depth3 = pygame.image.load("depth3.png")
        depth5 = pygame.image.load("depth5.png")
        depth7 = pygame.image.load("depth7.png")

        button(0, 200, 195, 80, depth3, main_ai3)
        button(0, 300, 195, 80, depth5, main_ai5)
        button(0, 400, 195, 80, depth7, main_ai7)

        pygame.display.update()
        pygame.time.Clock().tick(15)


#main pentru 2 playeri
def main_players():
    run = True
    clock = pygame.time.Clock()
    game = Game(window)
    pygame.init()
    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_pos_mouse(pos)
                game.select(row, col)

        game.update()

    pygame.quit()

#main default pentru player vs ai
def main(depth):
    running = True
    clock = pygame.time.Clock()
    game = Game(window)
    pygame.init()
    while running:
        clock.tick(60)

        if game.turn == BLACK:
            value, new_board = minmax(game.get_board(), depth, True)
            game.ai_move(new_board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:

                pos = pygame.mouse.get_pos()
                row, col = get_pos_mouse(pos)
                game.select(row, col)
        game.update()
    pygame.quit()

#wrappere pentru main
def main3():
    main(3)

def main5():
    main(5)

def main7():
    main(7)

#main pentru ai vs ai
def main_ai(depth):
    running = True
    clock = pygame.time.Clock()
    game = Game(window)
    pygame.init()
    while running:
        clock.tick(60)

        if game.turn == BLACK:
            value, new_board = minmax(game.get_board(), depth, True)
            game.ai_move(new_board)
        else:
            value, new_board = alpha_beta_fox(0, 0, game.get_board(), depth, True)
            game.ai_move(new_board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:

                pos = pygame.mouse.get_pos()
                row, col = get_pos_mouse(pos)
                game.select(row, col)
        game.update()
    pygame.quit()

#wrappere pentru ai vs ai
def main_ai3():
    main_ai(3)

def main_ai5():
    main_ai(5)

def main_ai7():
    main_ai(7)

#run
game_intro()
