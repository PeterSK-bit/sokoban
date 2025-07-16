# Sokoban Game

A simple terminal-based Sokoban-style puzzle game implemented in Python.  
Move the player (`x`) to push movable crates (`◻`) onto goal tiles (`+`).  
Immovable crates (`◼`) act as obstacles.

---

## Features

- Text-based ASCII rendering in terminal  
- Player and crate movement with validation  
- Recursive pushing of crates if movable  
- Level loading from JSON files  
- Reset and quit functionality  
- Win condition detection

---

## Installation

1. Clone this repository:

   ```bash
   https://github.com/PeterSK-bit/sokoban.git
   cd sokoban
   python main.py
   ```

---

## Controls

| Key              | Action        |
| ---------------- | ------------- |
| `w`              | Move Up       |
| `s`              | Move Down     |
| `a`              | Move Left     |
| `d`              | Move Right    |
| `r` or `restart` | Restart level |
| `q` or `quit`    | Quit game     |

---

## Future Improvements
- Implement level editor
- Add multiple levels and level selection
- Save and load game progress
- Add better error handling and UI polish

---

## License
This project is licensed under the **MIT** License.
