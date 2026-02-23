import os
import sys
from mazegen.grid import Grid


COLORS = [
    "\033[97m",  # White
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[94m",  # Blue
    "\033[93m",  # Yellow
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
    "\033[97m"
]
RESET = "\033[0m"


class ConsoleVisualizer:
    def __init__(self, grid: Grid, entry: tuple, exit: tuple):
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.path_coords = set()
        self.show_path = True
        self.color_idx = 0
        self.imprint_42 = set()

    def set_path(self, path_str: str):
        """Converts NNSSWE string to coordinates for display"""
        x, y = self.entry
        self.path_coords = {(x, y)}
        for move in path_str:
            if move == 'N':
                y -= 1
            elif move == 'S':
                y += 1
            elif move == 'E':
                x += 1
            elif move == 'W':
                x -= 1
            self.path_coords.add((x, y))

    def render(self):
        """Draws the maze using ASCII characters"""
        # os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.write("\033[H")

        wall_color = COLORS[self.color_idx]
        print(f"MAZE VISUALIZATION ({self.grid.width}x{self.grid.height})")

        for y in range(self.grid.height):
            top_line = ""
            for x in range(self.grid.width):
                val = self.grid.get_value(x, y)
                top_line += f"{wall_color}+{RESET}"
                if val & 1:
                    top_line += f"{wall_color}---{RESET}"
                elif (self.show_path and (x, y) in self.path_coords and
                      (x, y - 1) in self.path_coords):
                    top_line += f"{COLORS[len(COLORS) - 2 - self.color_idx]}"
                    top_line += f"███{RESET}"
                else:
                    top_line += "   "
            print(top_line + f"{wall_color}+{RESET}")

            mid_line = ""
            for x in range(self.grid.width):
                val = self.grid.get_value(x, y)

                if val & 8:
                    mid_line += f"{wall_color}|{RESET}"
                elif (self.show_path and (x, y) in self.path_coords and
                      (x - 1, y) in self.path_coords):
                    mid_line += f"{COLORS[len(COLORS) - 2 - self.color_idx]}"
                    mid_line += f"█{RESET}"
                else:
                    mid_line += " "

                if (x, y) == self.entry:
                    mid_line += " E "
                elif (x, y) == self.exit:
                    mid_line += " X "
                elif self.show_path and (x, y) in self.path_coords:
                    mid_line += f"{COLORS[len(COLORS) - 2 - self.color_idx]}"
                    mid_line += f"███{RESET}"
                elif (x, y) in self.imprint_42:
                    mid_line += f"{COLORS[len(COLORS) - 1 - self.color_idx]}"
                    mid_line += f"███{RESET}"
                else:
                    mid_line += "   "

            last_val = self.grid.get_value(self.grid.width - 1, y)
            if last_val & 2:
                mid_line += f"{wall_color}|{RESET}"
            else:
                mid_line += " "
            print(mid_line)

        bot_line = ""
        for x in range(self.grid.width):
            val = self.grid.get_value(x, self.grid.height - 1)
            bot_line += f"{wall_color}+{RESET}"
            if val & 4:
                bot_line += f"{wall_color}---{RESET}"
            else:
                bot_line += "   "
        print(bot_line + f"{wall_color}+{RESET}")
        sys.stdout.flush()
