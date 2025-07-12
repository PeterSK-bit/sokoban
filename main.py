from os import system, name
from sys import exit

class Player:
    def __init__(self):
        self.x = -1
        self.y = -1
    
    def __str__(self):
        return "x"

    def move_valid(self, x:int, y:int, board:list) -> bool:
        if x >= 0 and y >= 0 and x < len(board[0]) and y < len(board):
            if abs(x-self.x) <= 1 and y == self.y or abs(y-self.y) <= 1 and x == self.x:
                if not(isinstance(board[y][x],Crate)) or board[y][x].move_valid(x+(x-self.x), y+(y-self.y), board):
                    self.x = x
                    self.y = y
                    return True
        return False

    def input_move(self) -> bool:
        direction_input = input()
        direction = {
            "w":(0,-1),
            "s":(0,1),
            "a":(-1,0),
            "d":(1,0)
        }
        if direction_input in ["w","a","s","d"]:
            return self.move_valid(self.x+direction[direction_input][0], self.y+direction[direction_input][1], board.array)
        elif direction_input in ["restart","r","reset"]:
            return None
        else:
            print("Wrong input")
            return self.input_move()

class Crate(Player):
    def __init__(self, x:int, y:int, moveable:bool):
        self.x = x
        self.y = y
        self.moveable = moveable

    def __str__(self):
        if self.moveable:
            return "◻"
        else:
            return "◼"
    
    def move_valid(self, x:int, y:int, board:list) -> bool:
        if self.moveable:
            return super().move_valid(x, y, board)
        else:
            return False

class Board:
    EMPTY_SPACE="·"
    def __init__(self, levels_path:str, player:Player):
        self.levels_path = levels_path
        self.player = player
        self.array = []
        self.points = []
        self.level = 0
        self.levels = self.get_levels()
    
    def clear_screen() -> None:
        if name == 'nt':  # Windows
            system('cls')
        else:
            system('clear')
    
    def get_levels(self) -> list:
        levels = []
        if not(self.levels_path.endswith(".txt")):
            exit(f"Invalid file type: cannot load levels.\nExpected file.txt not file.{self.levels_path[-self.levels_path[::-1].find('.') :]}")
        try:
            with open(self.levels_path, "r") as f:
                temp = f.readlines()
            
            for level in temp:
                if level.count(";") == 1:
                    levels.append(level.strip(";\n").replace(" ",""))
                else:
                    levels+=level.strip(";").replace(" ", "").split(";")

        except FileNotFoundError:
            exit(f"File Not Found:\nPath {self.levels_path} doesn't exist or name of file is incorrect: unable to load levels.")
        return levels
    
    def set_board_size(self) -> list[list]:
        x = int(self.current_level[-(self.current_level[::-1].find(":")) : self.current_level.find("x")])#getting number between : and x
        y = int(self.current_level[self.current_level.find("x")+1 : ])#getting number between x and end of string
        return [[self.EMPTY_SPACE for _ in range(x)] for _ in range(y)]#returning 2D list of "·"
    
    def set_winning_cords(self) -> list[tuple]:
        level_data = self.current_level
        
        winning_coords_data = level_data[level_data.find(":") +1 : -(level_data[::-1].find(":") +1)]
        coords_strings = winning_coords_data.split("),(")

        winning_coords = []
        for coord_str in coords_strings:
            coord_values = coord_str.replace("(", "").replace(")", "").split(',')
            coord_tuple = tuple(map(int, coord_values))
            winning_coords.append(coord_tuple)

        return winning_coords
    
    def get_player_cords(self) -> None:
        player.x,player.y = map(int,self.current_level[:self.current_level.find("),")].replace("(","").split(","))
    
    def get_crates_cords(self) -> list[tuple]:
        x=self.current_level
        list_of_strings=x[x.find("),(")+2 : x.find(":")].split("),(")
        return [tuple(map(int, val.replace(")","").replace("(","").split(','))) for val in list_of_strings]
    
    def set_player(self) -> None:
        self.get_player_cords()
        if not(isinstance(self.array[self.player.y][self.player.x],Crate)):
            self.array[self.player.y][self.player.x]=self.player
        else:
            exit(f"Unable to place player: Coordinates are occupied by other object.\nCheck level data it's possible defect. Path to file: {self.levels_path}")
    
    def set_crates(self) -> None:
        crates=self.get_crates_cords()
        for x, y, moveable in crates:
            if not(isinstance(self.array[y][x],Crate)) or not(isinstance(self.array[y][x],Player)):
                self.array[y][x] = Crate(x, y, bool(moveable))
            else:
                exit(f"Unable to place player: Coordinates are occupied by other object.\nCheck level data it's possible defect. Path to file: {self.levels_path}")

    def load_level(self) -> None:
        self.current_level = self.levels[self.level]
        if self.level > len(self.levels):
            exit("No more levels for load.")
        self.array = self.set_board_size()
        self.points = self.set_winning_cords()
        self.set_player()
        self.set_crates()
        self.level+=1
    
    def restart_level(self):
        self.array = self.set_board_size()
        self.points = self.set_winning_cords()
        self.set_player()
        self.set_crates()


    def show_board(self) -> None:
        for y, array in enumerate(self.array):
            for x, val in enumerate(array):
                if ((x, y) in self.points or (x, y) == self.points) and self.array[y][x] == self.EMPTY_SPACE:
                    print("¤", end="")
                else:
                    print(val, end="")
            print()
    
    def win_check(self) -> bool:
        for x,y in self.points:
            if not(isinstance(self.array[y][x],Crate)):
                return False
        return True

    def move(self, x:int, y:int) -> None:
        if isinstance(self.array[self.array[y][x].y][self.array[y][x].x], Crate):
            self.move(self.array[y][x].x, self.array[y][x].y)
        self.array[self.array[y][x].y][self.array[y][x].x] = self.array[y][x]
        self.array[y][x] = self.EMPTY_SPACE

    def update(self) -> bool:
        for y,array in enumerate(self.array):
            for x,val in enumerate(array):
                if isinstance(val,Player) or isinstance(val,Crate):
                    if x != val.x or y != val.y:
                        self.move(x, y)
        if self.win_check():
            return True
        return False
    
player=Player()
board=Board(input("Insert path to levels file: "),player)

#for _ in board.levels:
#    board.load_level()
#    
#    while not(board.update()):
#        Board.clear_screen()
#        print(f"LEVEL: {board.level}")
#        board.show_board()
#        if player.input_move() is None:
#            board.restart_level()
#
#    Board.clear_screen()
#    print("NEXT LEVEL")    
#    board.show_board()
#else:
#    print("WIN")