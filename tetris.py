"""
Mini Tetris на Python.

Запуск:
    python tetris.py

Зависимости: только стандартная библиотека Python — используется tkinter.
Управление:
    ← / →  — движение
    ↓      — ускорить падение
    ↑ / X  — повернуть фигуру
    Space  — мгновенно сбросить фигуру
    P      — пауза
    R      — новая игра
"""

from __future__ import annotations

import random
import tkinter as tk


CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
SIDE_PANEL = 190
WIDTH = COLUMNS * CELL_SIZE + SIDE_PANEL
HEIGHT = ROWS * CELL_SIZE

# Новая палитра: neon sunset — темный фон, яркие фигуры и мягкая тень.
BOARD_COLOR = "#160f29"
PANEL_COLOR = "#0f172a"
GRID_COLOR = "#35284f"
TEXT_COLOR = "#fff7ed"
MUTED_TEXT_COLOR = "#c4b5fd"
GHOST_COLOR = "#5b4b8a"
EMPTY_CELL_COLOR = "#1f1638"
PAUSE_COLOR = "#fbbf24"
GAME_OVER_COLOR = "#fb7185"

COLORS = {
    "I": "#00f5d4",
    "J": "#4cc9f0",
    "L": "#ff8fab",
    "O": "#fee440",
    "S": "#80ed99",
    "T": "#c77dff",
    "Z": "#ff4d6d",
}

SHAPES = {
    "I": [[1, 1, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "Z": [[1, 1, 0], [0, 1, 1]],
}


class Tetris:
    """Простая реализация Тетриса на tkinter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Mini Tetris")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root,
            width=WIDTH,
            height=HEIGHT,
            bg=BOARD_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.after_id: str | None = None
        self.board: list[list[str | None]] = []
        self.current: dict[str, object] = {}
        self.next_piece: dict[str, object] = {}
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_delay = 600
        self.paused = False
        self.running = True

        self.bind_keys()
        self.new_game()

    def bind_keys(self) -> None:
        self.root.bind("<Left>", lambda _: self.move(-1, 0))
        self.root.bind("<Right>", lambda _: self.move(1, 0))
        self.root.bind("<Down>", lambda _: self.soft_drop())
        self.root.bind("<Up>", lambda _: self.rotate())
        self.root.bind("x", lambda _: self.rotate())
        self.root.bind("X", lambda _: self.rotate())
        self.root.bind("<space>", lambda _: self.hard_drop())
        self.root.bind("p", lambda _: self.toggle_pause())
        self.root.bind("P", lambda _: self.toggle_pause())
        self.root.bind("r", lambda _: self.new_game())
        self.root.bind("R", lambda _: self.new_game())

    def new_game(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.board = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_delay = 600
        self.paused = False
        self.running = True
        self.next_piece = self.create_piece()
        self.spawn_piece()
        self.draw()
        self.game_loop()

    def create_piece(self) -> dict[str, object]:
        name = random.choice(list(SHAPES))
        matrix = [row[:] for row in SHAPES[name]]
        return {
            "name": name,
            "matrix": matrix,
            "x": COLUMNS // 2 - len(matrix[0]) // 2,
            "y": -1,
        }

    def spawn_piece(self) -> None:
        self.current = self.next_piece
        self.current["x"] = COLUMNS // 2 - len(self.current["matrix"][0]) // 2  # type: ignore[index]
        self.current["y"] = -1
        self.next_piece = self.create_piece()

        if not self.is_valid(
            self.current["matrix"],  # type: ignore[arg-type]
            self.current["x"],  # type: ignore[arg-type]
            self.current["y"],  # type: ignore[arg-type]
        ):
            self.running = False

    @staticmethod
    def rotate_matrix(matrix: list[list[int]]) -> list[list[int]]:
        return [list(row) for row in zip(*matrix[::-1])]

    def is_valid(self, matrix: list[list[int]], x: int, y: int) -> bool:
        for row_index, row in enumerate(matrix):
            for col_index, filled in enumerate(row):
                if not filled:
                    continue

                board_x = x + col_index
                board_y = y + row_index

                if board_x < 0 or board_x >= COLUMNS or board_y >= ROWS:
                    return False

                if board_y >= 0 and self.board[board_y][board_x] is not None:
                    return False

        return True

    def move(self, dx: int, dy: int) -> bool:
        if not self.running or self.paused:
            return False

        matrix = self.current["matrix"]  # type: ignore[assignment]
        x = self.current["x"] + dx  # type: ignore[operator]
        y = self.current["y"] + dy  # type: ignore[operator]

        if self.is_valid(matrix, x, y):  # type: ignore[arg-type]
            self.current["x"] = x
            self.current["y"] = y
            self.draw()
            return True

        return False

    def rotate(self) -> None:
        if not self.running or self.paused:
            return

        name = self.current["name"]
        if name == "O":
            return

        current_matrix = self.current["matrix"]  # type: ignore[assignment]
        rotated = self.rotate_matrix(current_matrix)  # type: ignore[arg-type]
        current_x = self.current["x"]  # type: ignore[assignment]
        current_y = self.current["y"]  # type: ignore[assignment]

        for kick in (0, -1, 1, -2, 2):
            if self.is_valid(rotated, current_x + kick, current_y):  # type: ignore[arg-type]
                self.current["matrix"] = rotated
                self.current["x"] = current_x + kick  # type: ignore[operator]
                self.draw()
                return

    def soft_drop(self) -> None:
        if self.move(0, 1):
            self.score += 1
            self.draw()

    def hard_drop(self) -> None:
        if not self.running or self.paused:
            return

        distance = 0
        while self.move(0, 1):
            distance += 1

        self.score += distance * 2
        self.lock_piece()
        self.draw()

    def lock_piece(self) -> None:
        matrix = self.current["matrix"]  # type: ignore[assignment]
        x = self.current["x"]  # type: ignore[assignment]
        y = self.current["y"]  # type: ignore[assignment]
        name = self.current["name"]  # type: ignore[assignment]

        for row_index, row in enumerate(matrix):  # type: ignore[arg-type]
            for col_index, filled in enumerate(row):
                if not filled:
                    continue

                board_y = y + row_index  # type: ignore[operator]
                board_x = x + col_index  # type: ignore[operator]

                if board_y < 0:
                    self.running = False
                    return

                self.board[board_y][board_x] = name  # type: ignore[index]

        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self) -> None:
        remaining_rows = [row for row in self.board if any(cell is None for cell in row)]
        cleared = ROWS - len(remaining_rows)

        if cleared:
            empty_rows = [[None for _ in range(COLUMNS)] for _ in range(cleared)]
            self.board = empty_rows + remaining_rows
            self.lines += cleared
            self.level = self.lines // 10 + 1
            self.drop_delay = max(90, 600 - (self.level - 1) * 45)
            self.score += [0, 100, 300, 500, 800][cleared] * self.level

    def toggle_pause(self) -> None:
        if not self.running:
            return

        self.paused = not self.paused
        self.draw()

    def get_ghost_y(self) -> int:
        matrix = self.current["matrix"]  # type: ignore[assignment]
        x = self.current["x"]  # type: ignore[assignment]
        y = self.current["y"]  # type: ignore[assignment]

        while self.is_valid(matrix, x, y + 1):  # type: ignore[arg-type,operator]
            y += 1  # type: ignore[operator]

        return y  # type: ignore[return-value]

    def game_loop(self) -> None:
        if self.running and not self.paused:
            if not self.move(0, 1):
                self.lock_piece()
                self.draw()

        self.after_id = self.root.after(self.drop_delay, self.game_loop)

    def draw_cell(self, x: int, y: int, color: str, outline: str = GRID_COLOR) -> None:
        px = x * CELL_SIZE
        py = y * CELL_SIZE
        self.canvas.create_rectangle(
            px + 1,
            py + 1,
            px + CELL_SIZE - 1,
            py + CELL_SIZE - 1,
            fill=color,
            outline=outline,
        )
        self.canvas.create_line(px + 3, py + 3, px + CELL_SIZE - 5, py + 3, fill="#ffffff")
        self.canvas.create_line(px + 3, py + 3, px + 3, py + CELL_SIZE - 5, fill="#ffffff")

    def draw_board(self) -> None:
        for row in range(ROWS):
            for col in range(COLUMNS):
                color = COLORS.get(self.board[row][col], EMPTY_CELL_COLOR)
                self.draw_cell(col, row, color)

        for col in range(COLUMNS + 1):
            x = col * CELL_SIZE
            self.canvas.create_line(x, 0, x, HEIGHT, fill=GRID_COLOR)

        for row in range(ROWS + 1):
            y = row * CELL_SIZE
            self.canvas.create_line(0, y, COLUMNS * CELL_SIZE, y, fill=GRID_COLOR)

    def draw_piece(self, piece: dict[str, object], ghost: bool = False) -> None:
        matrix = piece["matrix"]  # type: ignore[assignment]
        x = piece["x"]  # type: ignore[assignment]
        y = piece["y"]  # type: ignore[assignment]
        name = piece["name"]  # type: ignore[assignment]
        color = GHOST_COLOR if ghost else COLORS[name]  # type: ignore[index]

        for row_index, row in enumerate(matrix):  # type: ignore[arg-type]
            for col_index, filled in enumerate(row):
                if not filled:
                    continue

                board_y = y + row_index  # type: ignore[operator]
                board_x = x + col_index  # type: ignore[operator]

                if board_y >= 0:
                    self.draw_cell(board_x, board_y, color)

    def draw_sidebar(self) -> None:
        x = COLUMNS * CELL_SIZE + 22
        self.canvas.create_text(x, 35, anchor="w", fill=TEXT_COLOR, font=("Arial", 18, "bold"), text="MINI TETRIS")
        self.canvas.create_text(x, 62, anchor="w", fill=MUTED_TEXT_COLOR, font=("Arial", 10), text="neon sunset")
        self.canvas.create_text(x, 100, anchor="w", fill=TEXT_COLOR, font=("Arial", 12), text=f"Очки: {self.score}")
        self.canvas.create_text(x, 130, anchor="w", fill=TEXT_COLOR, font=("Arial", 12), text=f"Линии: {self.lines}")
        self.canvas.create_text(x, 160, anchor="w", fill=TEXT_COLOR, font=("Arial", 12), text=f"Уровень: {self.level}")

        self.canvas.create_text(x, 210, anchor="w", fill=MUTED_TEXT_COLOR, font=("Arial", 12, "bold"), text="Следующая:")

        preview_origin_x = x
        preview_origin_y = 240
        matrix = self.next_piece["matrix"]  # type: ignore[assignment]
        name = self.next_piece["name"]  # type: ignore[assignment]

        for row_index, row in enumerate(matrix):  # type: ignore[arg-type]
            for col_index, filled in enumerate(row):
                if filled:
                    px = preview_origin_x + col_index * 22
                    py = preview_origin_y + row_index * 22
                    self.canvas.create_rectangle(
                        px,
                        py,
                        px + 20,
                        py + 20,
                        fill=COLORS[name],  # type: ignore[index]
                        outline=GRID_COLOR,
                    )

        controls = (
            "Управление:\n"
            "← →  движение\n"
            "↓    ускорить\n"
            "↑/X  поворот\n"
            "Space сброс\n"
            "P    пауза\n"
            "R    заново"
        )
        self.canvas.create_text(x, 365, anchor="w", fill=TEXT_COLOR, font=("Arial", 11), text=controls)

        if self.paused:
            self.canvas.create_text(x, 520, anchor="w", fill=PAUSE_COLOR, font=("Arial", 14, "bold"), text="ПАУЗА")

        if not self.running:
            self.canvas.create_text(x, 520, anchor="w", fill=GAME_OVER_COLOR, font=("Arial", 14, "bold"), text="ИГРА ОКОНЧЕНА")
            self.canvas.create_text(x, 550, anchor="w", fill=TEXT_COLOR, font=("Arial", 11), text="Нажмите R")

    def draw(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, COLUMNS * CELL_SIZE, HEIGHT, fill=BOARD_COLOR, outline=BOARD_COLOR)
        self.draw_board()

        if self.current:
            ghost_piece = dict(self.current)
            ghost_piece["y"] = self.get_ghost_y()
            self.draw_piece(ghost_piece, ghost=True)
            self.draw_piece(self.current)

        self.canvas.create_rectangle(COLUMNS * CELL_SIZE, 0, WIDTH, HEIGHT, fill=PANEL_COLOR, outline=PANEL_COLOR)
        self.draw_sidebar()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    Tetris().run()
