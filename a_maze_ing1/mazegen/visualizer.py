import os


COLORS = [
    "\033[97m",  # White
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[94m",  # Blue
    "\033[93m",  # Yellow
]
RESET = "\033[0m"


class ConsoleVisualizer:
    def __init__(self, grid, entry, exit):
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.path_coords = set()  # Set of (x,y) tuples for the solution
        self.show_path = False
        self.color_idx = 0

    def set_path(self, path_str):
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
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen

        wall_color = COLORS[self.color_idx]
        print(f"MAZE VISUALIZATION ({self.grid.width}x{self.grid.height})")

        # Iterate through every row
        for y in range(self.grid.height):
            # Line 1: Top Walls (North)
            top_line = ""
            for x in range(self.grid.width):
                val = self.grid.get_value(x, y)
                # Corner
                top_line += f"{wall_color}+{RESET}"
                # North Wall (Bit 0)
                if val & 1:
                    top_line += f"{wall_color}---{RESET}"
                else:
                    top_line += "   "
            print(top_line + f"{wall_color}+{RESET}")  # Close row

            # Line 2: Side Walls (West) and Cell Body
            mid_line = ""
            for x in range(self.grid.width):
                val = self.grid.get_value(x, y)

                # West Wall (Bit 3)
                if val & 8:
                    mid_line += f"{wall_color}|{RESET}"
                else:
                    mid_line += " "

                # Cell Content
                if (x, y) == self.entry:
                    mid_line += " E "
                elif (x, y) == self.exit:
                    mid_line += " X "
                elif self.show_path and (x, y) in self.path_coords:
                    mid_line += " . "   # Path dot
                else:
                    mid_line += "   "

            # Close the rightmost wall (East of last cell)
            last_val = self.grid.get_value(self.grid.width - 1, y)
            if last_val & 2:  # East Bit
                mid_line += f"{wall_color}|{RESET}"
            else:
                mid_line += " "
            print(mid_line)

        # Bottom Line of the entire maze
        bot_line = ""
        for x in range(self.grid.width):
            val = self.grid.get_value(x, self.grid.height - 1)
            bot_line += f"{wall_color}+{RESET}"
            if val & 4:   # South Bit
                bot_line += f"{wall_color}---{RESET}"
            else:
                bot_line += "   "
        print(bot_line + f"{wall_color}+{RESET}")
