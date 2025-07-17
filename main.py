import json
from glob import glob
from os import path
from string import ascii_letters, digits

class MoveableObject:
    """
    Abstract base for movable game entities like Player and Crate.

    Attributes:
        _x (int): X-coordinate (private)
        _y (int): Y-coordinate (private)

    Properties:
        x (int): Returns current X-coordinate.
        y (int): Returns current Y-coordinate.
        position (tuple[int, int]): Returns current position.

    Methods:
        move(x, y): Attempts to move to (x, y) if the move is legal.
    """

    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def position(self) -> tuple[int, int]:
        return self._x, self._y

    def move(self, x: int, y: int) -> bool:
        dx = abs(x - self._x)
        dy = abs(y - self._y)

        if x < 0 or y < 0:
            print(f"Error: Setting negative coordinates is forbidden for {self.__class__.__name__}")
            return False

        if (dx > 1 or dy > 1) or (dx == 1 and dy == 1):
            print(f"Error: Illegal move - can only move one tile in one direction. Tried ({self._x},{self._y}) -> ({x},{y}) in {self.__class__.__name__}")
            return False

        self._x = x
        self._y = y

        return True



class Player(MoveableObject):
    """
    Represented by 'x'.
    Inherits from MoveableObject class

    Attributes:
        _x (int): X-coordinate (private)
        _y (int): Y-coordinate (private)

    Properties:
        x (int): Returns current X-coordinate.
        y (int): Returns current Y-coordinate.
        position (tuple[int, int]): Returns current position.

    Methods:
        move(x, y): Attempts to move to (x, y) if the move is legal.
    """

    def __str__(self):
        return "x"



class Crate(MoveableObject):
    """
    Represents a movable or fixed crate in the game level.
    
    Attributes:
        _x (int): X-coordinate (private)
        _y (int): Y-coordinate (private)

    Properties:
        x (int): Returns current X-coordinate.
        y (int): Returns current Y-coordinate.
        position (tuple[int, int]): Returns current position.

    Methods:
        move(x, y): Attempts to move to (x, y) if the move is legal.
    """
    
    def __init__(self, x: int, y: int, moveable: bool):
        super().__init__(x, y)
        self.moveable = moveable
    
    def __str__(self):
        if self.moveable:
            return "◻"
        else:
            return "◼"
        
    def clone(self):
        return Crate(self._x, self._y, self.moveable)



class GameLoader:
    """
    Handles loading and provision of level data.

    Automatically locates or prompts for a JSON level file,
    parses its content, and prepares the game state.

    Raises:
        ValueError: If the level file cannot be found or parsed.
    """

    def __init__(self):
        self.path = self.get_level_file()
        self.original_data = self.load_level()
        if self.original_data is None:
            raise ValueError("Failed to load level")

    def load_level(self) -> tuple | None:
        try:
            with open(self.path, "r") as f:
                level_data = json.load(f)
            return self.parse_level(level_data)
        except FileNotFoundError:
            print(f"ERROR: File not found. Path '{self.path}' doesn't exist.")
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON: {e}")
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
        return None

    def parse_level(self, data: json) -> tuple | None:
        try:
            player_pos = tuple(data["player"])
            crates = [Crate(x, y, movable) for x, y, movable in data["crates"]]
            goals = [tuple(g) for g in data["goals"]]
            width, height = data["dimensions"]
        except KeyError as e:
            print(f"ERROR: Missing field in level data: {e}")
            return None
        except Exception as e:
            print(f"ERROR: Failed to parse level structure: {e}")
            return None

        print(f"INFO: Successfully loaded level from {self.path}")
        return player_pos, crates, goals, (width, height), self
    
    def get_fresh_level(self) -> tuple[tuple[int, int], list[Crate], list[tuple[int, int]], tuple[int, int], "GameLoader"]:
        """
        Returns a fresh copy of the level data for a new game session.

        Returns:
            tuple: (player_position, cloned_crates, goals, dimensions, self_reference)
        """
        
        player, crates, goals, dimensions, self_ref = self.original_data
        crates_clone = [crate.clone() for crate in crates]
        return player, crates_clone, goals, dimensions, self_ref

    @staticmethod
    def get_level_file() -> str:
        """
        Handles game file extraction and file existance validation.

        Returns:
            string: Absolute path to valid game file.
        """

        potential_level_files = glob("*.json")
        files_count = len(potential_level_files)
        
        if files_count == 1:
            return path.abspath(potential_level_files[0])
        elif files_count > 1:
            print("INFO: Detected multiple potencial game files")
            for index, file in enumerate(potential_level_files):
                print(f"{index}: {file}")
            
            while True:
                try:
                    choice = int(input("Choose one file: "))
                    if 0 <= choice < files_count:
                        return path.abspath(potential_level_files[choice])
                    else:
                        raise IndexError("Choice index out of the range")
                except Exception as e:
                    print(f"ERROR: {e}")
        else:
            while True:
                file = input("INFO: No potential game files found. Enter file path manually:\n> ")
                if path.exists(file):
                    return path.abspath(file)
                else:
                    print("ERROR: File doesn't exist. Try again.")



class Game:
    """
    Handles core game loop, state management, and board rendering.

    The Game class is responsible for:
    - Tracking player, crates, goals, and level dimensions.
    - Handling movement input, including push mechanics for crates.
    - Checking for win conditions.
    - Rendering the board to the console.
    - Resetting the game from original data.

    Attributes:
        DIRECTIONS (dict): Allowed movement directions mapped to (dx, dy).
        width (int): Width of the game board.
        height (int): Height of the game board.
        player (Player): Instance representing the player.
        crates (list[Crate]): List of crate instances (some may be fixed).
        goals (list[tuple[int, int]]): Coordinates where crates must be moved.
        board (list[list[object]]): 2D board representation.
        game_loader (GameLoader): Reference to the GameLoader to enable reset.

    Methods:
        run(): Starts the game loop, handles user input.
        handle_move(x, y, direction): Attempts to move a player and possibly push a crate.
        check_win(): Returns True if all movable crates are on goals.
        render(): Renders the current board state in the console.
        rebuild_board(): Refreshes the 2D board from object positions.
        reset(): Restarts the level from original data.
    """

    # Maps direction keys to coordinate offsets
    DIRECTIONS = {
        "w": (0, -1),
        "s": (0, 1),
        "a": (-1, 0),
        "d": (1, 0)
    }

    def __init__(self, player_pos: tuple[int, int], crates: list[Crate], goals: list, dimensions: tuple[int, int], game_loader: GameLoader):
        self.width, self.height = dimensions
        self.player = Player(*player_pos)
        self.crates = crates
        self.goals = goals
        self.game_loader = game_loader

        # Assemble the board
        self.rebuild_board()

    def run(self):
        while True:
            self.render()
            user_input = input("Move: ").lower()

            if user_input in self.DIRECTIONS:
                self.handle_move(*self.player.position, self.DIRECTIONS[user_input])
                self.rebuild_board()
            elif user_input in ("r", "restart"):
                self.reset()
            elif user_input in ("q", "quit"):
                print("INFO: Game closed")
                break
            elif user_input in ("s", "save"):
                self.save()
            else:
                print("INFO: Invalid input.")

            if self.check_win():
                print("YOU WON!")
                self.render()
                break

    # Check if move is valid and handle crate pushing if necessary
    def handle_move(self, x, y, direction: tuple[int, int]) -> bool:
        """
        Handles the logic for attempting to move the player (or pushing a crate).

        Args:
            x (int): Player's current X position.
            y (int): Player's current Y position.
            direction (tuple[int, int]): The (dx, dy) movement vector.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        dx, dy = direction
        x2, y2 = x + dx, y + dy

        if not (0 <= x2 < self.width and 0 <= y2 < self.height):
            return False
        
        destination = self.board[y2][x2]

        if destination in (" ", "+"):
            self.board[y][x].move(x2, y2)
            return True
        elif isinstance(destination, Crate):
            if not destination.moveable:
                return False
            elif self.handle_move(x2, y2, direction):
                self.board[y][x].move(x2, y2)
                return True
        else:
            print("Error: While moving, encoutered unknown object")

        return False

    # True if every goal has a movable crate on it
    def check_win(self):
        return all(goal in [crate.position for crate in self.crates if crate.moveable]  for goal in self.goals)

    # Render the board including player, crates, and goals
    def render(self):
        print("-" * (self.width + 2))
        for row in self.board:
            print("|", end="")
            for char in row:
                print(char, end="")
            print("|")
        print("-" * (self.width + 2))

    def rebuild_board(self):
        self.board = [[" " for _ in range(self.width)] for _ in range(self.height)]
        occupied = set()

        for x, y in self.goals:
            self.board[y][x] = "+"

        for obj in self.crates + [self.player]:
            pos = (obj.x, obj.y)
            if pos in occupied:
                raise ValueError(f"ERROR: Conflict at {pos}: multiple objects on one tile!")
            occupied.add(pos)
            self.board[obj.y][obj.x] = obj
    
    # Reset the game state by reloading the original data
    def reset(self):
        self.__init__(*self.game_loader.get_fresh_level())
        print(f"INFO: Level from {self.game_loader.path} reset")

    def save(self):
        while True:
            filename = input("Enter filename: ")
            safe_chars = ascii_letters + digits + "-_."
            filename = "".join(c for c in filename if c in safe_chars)
            if filename: break
            print("INFO: After file name sanitasion filename end up empty, try again")


        data = {
            "player": list(self.player.position),
            "crates": [(crate.x, crate.y, crate.moveable) for crate in self.crates],
            "goals": self.goals,
            "dimensions": [self.width, self.height]
        }

        # custom data writing because json.dump makes file hard to read
        with open(filename + ".json", "w") as f:
            f.write('{\n')
            f.write(f'  "player": {data["player"]},\n')

            crates = ', '.join(json.dumps(crate) for crate in data["crates"])
            f.write(f'  "crates": [\n    {crates}\n  ],\n')

            goals = ', '.join(json.dumps(goal) for goal in data["goals"])
            f.write(f'  "goals": [\n    {goals}\n  ],\n')

            f.write(f'  "dimensions": {data["dimensions"]}\n')
            f.write('}')

        print(f"INFO: Game state saved to {filename}.json")



def main():
    try:
        game_loader = GameLoader()
    except ValueError as e:
        print(f"ERROR: {e}")
        return
    game = Game(*game_loader.get_fresh_level())
    game.run()

if __name__ == "__main__":
    main()