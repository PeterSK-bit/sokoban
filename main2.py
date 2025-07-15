import json

class MoveableObject:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def position(self) -> tuple[int, int]:
        return self._x, self._y

    def move(self, x: int, y: int) -> None:
        dx = abs(x - self._x)
        dy = abs(y - self._y)

        if x < 0 or y < 0:
            print(f"Error: Setting negative coordinates is forbidden for {self.__class__.__name__}")
            return

        if (dx > 1 or dy > 1) or (dx == 1 and dy == 1):
            print(f"Error: Illegal move - can only move one tile in one direction. Tried ({self._x},{self._y}) -> ({x},{y}) in {self.__class__.__name__}")
            return

        self._x = x
        self._y = y




class Player(MoveableObject):
    def __str__(self):
        return "x"



class Crate(MoveableObject):
    def __init__(self, x: int, y: int, moveable: bool):
        super().__init__(x, y)
        self.moveable = moveable
    
    def __str__(self):
        if self.moveable:
            return "◻"
        else:
            return "◼"



class GameLoader:
    def __init__(self, path: str):
        self.path = path

    def load_level(self) -> tuple | None:
        try:
            with open(self.path, "r") as f:
                level_data = json.load(f)
        except FileNotFoundError:
            print(f"ERROR: File not found. Path '{self.path}' doesn't exist.")
            return None
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON: {e}")
            return None
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            return None

        return self.parse_level(level_data)

    def parse_level(self, data: json) -> tuple:
        player_pos = tuple(data["player"])
        crates = [Crate(x, y, movable) for x, y, movable in data["crates"]]
        goals = [tuple(g) for g in data["goals"]]
        width, height = data["dimensions"]

        return player_pos, crates, goals, (width, height)



class Game:
    DIRECTIONS = {
        "w": (0, -1),
        "s": (0, 1),
        "a": (-1, 0),
        "d": (1, 0)
    }

    def __init__(self, player_pos: tuple[int, int], crates: list, goals: list, dimensions: tuple[int, int]):
        self.width, self.height = dimensions
        self.player = Player(*player_pos)
        self.crates = crates
        self.goals = goals

        # assemble of board
        self.board = [[" " for _ in range(self.width)] for _ in range(self.height)]
        for x, y in self.goals:
            self.board[y][x] = "+"
        for crate in self.crates:
            self.board[crate.y][crate.x] = crate

        self.board[self.player.y][self.player.x] = self.player

    def run(self):
        while True:
            self.render()
            user_input = input("Move: ").lower()

            if user_input in self.DIRECTIONS:
                self.hadnle_move(self.DIRECTIONS[user_input])
            elif user_input in ("r", "restart"):
                print("Restart not yet implemented.")
            elif user_input in ("q", "quit"):
                print("quit isnt implemented")
            else:
                print("Invalid input.")

            if self.check_win():
                print("You won!")
                break

    def hadnle_move(self, direction: tuple[int, int]) -> bool:
        dx, dy = direction
        x, y = self.player.x + dx, self.player.y + dy

        while 0 <= x < self.width and 0 <= y < self.height:
            destination = self.board[y][x]

            if destination in (" ", "+"):
                print("move possbile")
                return True
            elif isinstance(destination, Crate):
                if not destination.moveable:
                    break
            else:
                print("Error: While moving, encoutered unknown object")
                break

            x += dx
            y += dy

        return False

    def check_win(self):
        return all((crate.x, crate.y) in self.goals for crate in self.crates)

    def render(self):
        print("-" * (self.width + 2))
        for row in self.board:
            print("|", end="")
            for char in row:
                print(char, end="")
            print("|")
        print("-" * (self.width + 2))



def main():
    game_loader = GameLoader("lvl.json")
    game = Game(*game_loader.load_level())
    game.run()

if __name__ == "__main__":
    main()