import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import json
import os
from datetime import datetime


class Minesweeper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Морской Сапер")

        # Морская цветовая палитра (мягкие оттенки)
        self.colors = {
            'primary': '#E3F2FD',  # Очень светлый голубой (фон)
            'secondary': '#BBDEFB',  # Светлый голубой (панели)
            'accent': '#90CAF9',  # Мягкий голубой (акценты)
            'light': '#E1F5FE',  # Светлый аквамарин
            'dark': '#0288D1',  # Морская синь (темный акцент)
            'success': '#4CAF50',  # Морская зелень
            'danger': '#F44336',  # Коралловый красный
            'warning': '#FF9800',  # Песочный оранжевый
            'text': '#01579B',  # Темно-синий текст
            'text_secondary': '#0277BD',  # Средний синий текст
            'button': '#29B6F6',  # Небесно-голубой кнопки
            'button_hover': '#039BE5',  # Голубой при наведении
            'cell_hidden': '#81D4FA',  # Светло-голубой скрытых клеток
            'cell_revealed': '#E1F5FE',  # Очень светлый голубой открытых
            'cell_mine': '#EF9A9A',  # Мягкий красный мин
            'cell_flag': '#FFCC80',  # Песочный желтый флагов
            'panel': '#B3E5FC',  # Панель управления
            'records_bg': '#E1F5FE',  # Фон таблицы рекордов
            'records_header': '#81D4FA',  # Заголовок таблицы
            'records_row1': '#E1F5FE',  # Первая строка
            'records_row2': '#B3E5FC',  # Вторая строка
            'border': '#4FC3F7',  # Цвет границ
            'input_bg': '#FFFFFF',  # Фон поля ввода
            'input_border': '#29B6F6',  # Граница поля ввода
        }

        self.root.configure(bg=self.colors['primary'])

        # Имя игрока
        self.player_name = self.get_player_name()

        # Параметры по умолчанию
        self.width = 9
        self.height = 9
        self.mine_count = 10
        self.MAX_WIDTH = 16  # Максимальная ширина поля

        # Игровые переменные
        self.board = []
        self.buttons = []
        self.mines = []
        self.game_over = False
        self.game_won = False
        self.first_move = True
        self.start_time = None
        self.flags_placed = 0
        self.revealed_count = 0

        # Таблица рекордов
        self.records_file = "minesweeper_records.json"
        self.records = self.load_records()

        # Цвета для чисел (мягкие оттенки)
        self.number_colors = {
            1: '#0277BD',  # Темно-синий
            2: '#0288D1',  # Морская синь
            3: '#039BE5',  # Ярко-синий
            4: '#29B6F6',  # Небесно-голубой
            5: '#4FC3F7',  # Светло-голубой
            6: '#81D4FA',  # Очень светлый голубой
            7: '#B3E5FC',  # Почти белый
            8: '#E1F5FE',  # Белый с голубым оттенком
        }

        # Размер клетки (адаптивный)
        self.cell_size = self.calculate_cell_size()

        # Создание интерфейса
        self.create_menu()
        self.create_info_panel()
        self.create_game_frame()

        self.new_game()

    def calculate_cell_size(self):
        """Рассчитать размер клетки в зависимости от ширины поля"""
        base_size = 40
        if self.width > 12:
            return 35
        elif self.width > 15:
            return 30
        return base_size

    def get_player_name(self):
        """Получить имя игрока"""
        # Попробуем загрузить сохраненное имя
        if os.path.exists("player_name.txt"):
            try:
                with open("player_name.txt", "r", encoding="utf-8") as f:
                    saved_name = f.read().strip()
                    if saved_name:
                        return saved_name
            except:
                pass

        # Если нет сохраненного имени, запросим
        name_window = tk.Toplevel(self.root)
        name_window.title("Введите ваше имя")
        name_window.configure(bg=self.colors['primary'])
        name_window.resizable(False, False)
        name_window.transient(self.root)
        name_window.grab_set()

        # Центрирование окна
        name_window.update_idletasks()
        x = (name_window.winfo_screenwidth() // 2) - 200
        y = (name_window.winfo_screenheight() // 2) - 100
        name_window.geometry(f"400x200+{x}+{y}")

        tk.Label(
            name_window,
            text="👤 ДОБРО ПОЖАЛОВАТЬ В САПЕР!",
            font=("Arial", 14, "bold"),
            bg=self.colors['primary'],
            fg=self.colors['text'],
            pady=20
        ).pack()

        tk.Label(
            name_window,
            text="Введите ваше имя для таблицы рекордов:",
            font=("Arial", 10),
            bg=self.colors['primary'],
            fg=self.colors['text_secondary'],
            pady=10
        ).pack()

        name_var = tk.StringVar(value="Игрок")
        name_entry = tk.Entry(
            name_window,
            textvariable=name_var,
            font=("Arial", 12),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            relief=tk.SOLID,
            bd=2,
            width=30
        )
        name_entry.pack(pady=10)
        name_entry.select_range(0, tk.END)
        name_entry.focus()

        def save_name():
            name = name_var.get().strip()
            if not name:
                name = "Игрок"

            # Сохраняем имя в файл
            try:
                with open("player_name.txt", "w", encoding="utf-8") as f:
                    f.write(name)
            except:
                pass

            self.player_name = name
            name_window.destroy()

        tk.Button(
            name_window,
            text="Сохранить",
            command=save_name,
            font=("Arial", 11, "bold"),
            bg=self.colors['button'],
            fg="white",
            activebackground=self.colors['button_hover'],
            padx=30,
            pady=8
        ).pack(pady=15)

        # Привязка Enter для сохранения
        name_window.bind('<Return>', lambda e: save_name())

        # Ждем закрытия окна
        self.root.wait_window(name_window)

        return self.player_name if hasattr(self, 'player_name') else "Игрок"

    def change_player_name(self):
        """Изменить имя игрока"""
        new_name = simpledialog.askstring(
            "Смена имени",
            "Введите новое имя для таблицы рекордов:",
            initialvalue=self.player_name,
            parent=self.root
        )

        if new_name and new_name.strip():
            self.player_name = new_name.strip()

            # Сохраняем имя в файл
            try:
                with open("player_name.txt", "w", encoding="utf-8") as f:
                    f.write(self.player_name)
            except:
                pass

            messagebox.showinfo("Успех", f"Имя изменено на: {self.player_name}")
            self.player_label.config(text=f" {self.player_name}")

    def load_records(self):
        """Загрузка таблицы рекордов из файла"""
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        # Создаем пустую таблицу рекордов
        return {
            "easy": [],
            "medium": [],
            "hard": [],
            "custom": []
        }

    def save_records(self):
        """Сохранение таблицы рекордов в файл"""
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, indent=2, ensure_ascii=False)
        except:
            pass

    def add_record(self, difficulty, time_seconds):
        """Добавление нового рекорда с именем текущего игрока"""
        record = {
            "name": self.player_name,
            "time": time_seconds,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "difficulty": difficulty
        }

        # Добавляем запись и сортируем по времени
        self.records[difficulty].append(record)
        self.records[difficulty] = sorted(
            self.records[difficulty],
            key=lambda x: x["time"]
        )[:10]  # Оставляем только 10 лучших

        self.save_records()

        # Показываем сообщение о новом рекорде
        messagebox.showinfo(
            "Новый рекорд! 🏆",
            f"🎉 {self.player_name}, вы установили новый рекорд!\n\n"
            f"Уровень: {self.get_difficulty_name(difficulty)}\n"
            f"Время: {time_seconds} секунд\n\n"
            f"Рекорд сохранен в таблице!"
        )

        return True

    def get_difficulty_name(self, difficulty):
        """Получить отображаемое имя уровня сложности"""
        names = {
            "easy": "🌊 Новичок",
            "medium": "⚓ Любитель",
            "hard": "🚢 Профессионал",
            "custom": "🧭 Пользовательский"
        }
        return names.get(difficulty, difficulty)

    def show_records(self):
        """Показать таблицу рекордов в морской цветовой гамме"""
        records_window = tk.Toplevel(self.root)
        records_window.title("🏆 Таблица рекордов")
        records_window.configure(bg=self.colors['records_bg'])
        records_window.resizable(False, False)

        # Центрирование окна
        records_window.update_idletasks()
        x = (records_window.winfo_screenwidth() // 2) - 250
        y = (records_window.winfo_screenheight() // 2) - 300
        records_window.geometry(f"500x600+{x}+{y}")

        # Заголовок
        title_frame = tk.Frame(records_window, bg=self.colors['records_bg'])
        title_frame.pack(fill=tk.X, pady=(15, 10))

        tk.Label(
            title_frame,
            text="🏆 ТАБЛИЦА РЕКОРДОВ 🏆",
            font=("Arial", 18, "bold"),
            bg=self.colors['records_bg'],
            fg=self.colors['text']
        ).pack()

        # Имя текущего игрока
        tk.Label(
            title_frame,
            text=f"Текущий игрок: {self.player_name}",
            font=("Arial", 10, "italic"),
            bg=self.colors['records_bg'],
            fg=self.colors['text_secondary'],
            pady=5
        ).pack()

        # Кнопка смены имени
        tk.Button(
            title_frame,
            text="✏️ Сменить имя",
            command=lambda: [self.change_player_name(), records_window.destroy(), self.show_records()],
            font=("Arial", 9),
            bg=self.colors['accent'],
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=2,
            cursor="hand2"
        ).pack(pady=5)

        # Создаем Notebook (вкладки) для разных уровней сложности
        notebook = tk.ttk.Notebook(records_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Стили для notebook
        style = tk.ttk.Style()
        style.theme_create("marine_theme", parent="alt", settings={
            "TNotebook": {"configure": {"background": self.colors['records_bg']}},
            "TNotebook.Tab": {
                "configure": {
                    "background": self.colors['records_header'],
                    "foreground": self.colors['text'],
                    "padding": [10, 5],
                    "font": ('Arial', 10, 'bold')
                },
                "map": {
                    "background": [("selected", self.colors['button'])],
                    "expand": [("selected", [1, 1, 1, 0])]
                }
            }
        })
        style.theme_use("marine_theme")

        # Вкладки для каждого уровня сложности
        difficulties = [
            ("easy", "🌊 Новичок (9x9, 10 мин)"),
            ("medium", "⚓ Любитель (16x16, 40 мин)"),
            ("hard", "🚢 Профессионал (16x30, 99 мин)"),
            ("custom", "🧭 Пользовательский")
        ]

        for diff_key, diff_name in difficulties:
            frame = tk.Frame(notebook, bg=self.colors['records_bg'])
            notebook.add(frame, text=diff_name)

            # Создаем Frame для заголовков таблицы
            header_frame = tk.Frame(frame, bg=self.colors['records_header'])
            header_frame.pack(fill=tk.X, pady=(0, 5))

            # Заголовки колонок
            headers = ["Место", "Имя", "Время", "Дата"]
            widths = [8, 15, 8, 12]

            for i, (header, width) in enumerate(zip(headers, widths)):
                tk.Label(
                    header_frame,
                    text=header,
                    font=("Arial", 10, "bold"),
                    bg=self.colors['records_header'],
                    fg=self.colors['text'],
                    width=width,
                    relief=tk.RAISED,
                    bd=1
                ).grid(row=0, column=i, padx=1, pady=1, sticky="nsew")

            # Данные рекордов
            canvas = tk.Canvas(
                frame,
                bg=self.colors['records_bg'],
                highlightthickness=0,
                bd=0
            )
            scrollbar = tk.Scrollbar(
                frame,
                orient="vertical",
                command=canvas.yview,
                bg=self.colors['records_bg']
            )
            scrollable_frame = tk.Frame(canvas, bg=self.colors['records_bg'])

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            records = self.records.get(diff_key, [])
            if not records:
                empty_frame = tk.Frame(
                    scrollable_frame,
                    bg=self.colors['records_bg'],
                    height=200
                )
                empty_frame.pack(fill=tk.BOTH, expand=True)

                tk.Label(
                    empty_frame,
                    text="📭 Пока нет рекордов!",
                    font=("Arial", 14),
                    bg=self.colors['records_bg'],
                    fg=self.colors['text_secondary']
                ).pack(pady=20)

                tk.Label(
                    empty_frame,
                    text="Сыграйте и станьте первым! 🎮",
                    font=("Arial", 11),
                    bg=self.colors['records_bg'],
                    fg=self.colors['accent']
                ).pack()
            else:
                for i, record in enumerate(records[:10], 1):
                    # Чередуем цвета строк для лучшей читаемости
                    if i % 2 == 0:
                        row_color = self.colors['records_row1']
                    else:
                        row_color = self.colors['records_row2']

                    # Подсвечиваем записи текущего игрока
                    if record["name"] == self.player_name:
                        row_color = self.colors['accent']

                    row_frame = tk.Frame(
                        scrollable_frame,
                        bg=row_color,
                        relief=tk.FLAT,
                        bd=1
                    )
                    row_frame.pack(fill=tk.X, pady=1)

                    # Место с иконкой для первых трех мест
                    if i == 1:
                        place_text = "🥇"
                        place_color = "#FFD700"  # Золотой
                    elif i == 2:
                        place_text = "🥈"
                        place_color = "#C0C0C0"  # Серебряный
                    elif i == 3:
                        place_text = "🥉"
                        place_color = "#CD7F32"  # Бронзовый
                    else:
                        place_text = f"{i}"
                        place_color = self.colors['text']

                    tk.Label(
                        row_frame,
                        text=place_text,
                        font=("Arial", 11, "bold"),
                        bg=row_color,
                        fg=place_color,
                        width=6
                    ).grid(row=0, column=0, padx=5)

                    # Имя (выделяем жирным, если это текущий игрок)
                    name_font = ("Arial", 11, "bold" if record["name"] == self.player_name else "normal")
                    tk.Label(
                        row_frame,
                        text=record["name"][:15],
                        font=name_font,
                        bg=row_color,
                        fg=self.colors['text'],
                        width=15
                    ).grid(row=0, column=1, padx=5)

                    tk.Label(
                        row_frame,
                        text=f"{record['time']} сек",
                        font=("Arial", 11, "bold"),
                        bg=row_color,
                        fg=self.colors['success'],
                        width=8
                    ).grid(row=0, column=2, padx=5)

                    tk.Label(
                        row_frame,
                        text=record["date"][:10],
                        font=("Arial", 9),
                        bg=row_color,
                        fg=self.colors['text_secondary'],
                        width=12
                    ).grid(row=0, column=3, padx=5)

            canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
            scrollbar.pack(side="right", fill="y")

        # Кнопка закрытия
        close_frame = tk.Frame(records_window, bg=self.colors['records_bg'])
        close_frame.pack(pady=10)

        tk.Button(
            close_frame,
            text="Закрыть",
            command=records_window.destroy,
            font=("Arial", 11, "bold"),
            bg=self.colors['button'],
            fg="white",
            activebackground=self.colors['button_hover'],
            relief=tk.RAISED,
            bd=2,
            padx=25,
            pady=8,
            cursor="hand2"
        ).pack()

        # Привязка колесика мыши для прокрутки
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def clear_records(self):
        """Очистить таблицу рекордов"""
        if messagebox.askyesno(
                "Очистка рекордов 🗑️",
                "Вы уверены, что хотите очистить всю таблицу рекордов?\n\n"
                "Это действие нельзя отменить!",
                parent=self.root
        ):
            self.records = {
                "easy": [],
                "medium": [],
                "hard": [],
                "custom": []
            }
            self.save_records()
            messagebox.showinfo("Успех ✅", "Таблица рекордов очищена!")

    def create_menu(self):
        """Создание меню в морской гамме"""
        menubar = tk.Menu(self.root,
                          bg=self.colors['panel'],
                          fg=self.colors['text'],
                          activebackground=self.colors['accent'],
                          activeforeground="white")
        self.root.config(menu=menubar)

        # Меню "Игра"
        game_menu = tk.Menu(menubar, tearoff=0,
                            bg=self.colors['panel'],
                            fg=self.colors['text'],
                            activebackground=self.colors['accent'],
                            activeforeground="white")
        menubar.add_cascade(label="🌊 Игра", menu=game_menu)
        game_menu.add_command(label="🔄 Новая игра", command=self.new_game, accelerator="Ctrl+N")
        game_menu.add_separator()

        # Меню "Сложность"
        difficulty_menu = tk.Menu(game_menu, tearoff=0,
                                  bg=self.colors['panel'],
                                  fg=self.colors['text'],
                                  activebackground=self.colors['accent'],
                                  activeforeground="white")
        game_menu.add_cascade(label="⚙️ Сложность", menu=difficulty_menu)
        difficulty_menu.add_command(label="🌊 Новичок (9x9, 10 мин)",
                                    command=lambda: self.set_difficulty(9, 9, 10, "easy"))
        difficulty_menu.add_command(label="⚓ Любитель (16x16, 40 мин)",
                                    command=lambda: self.set_difficulty(16, 16, 40, "medium"))
        difficulty_menu.add_command(label="🚢 Профессионал (16x30, 99 мин)",
                                    command=lambda: self.set_difficulty(16, 30, 99, "hard"))
        difficulty_menu.add_command(label="🧭 Пользовательский",
                                    command=self.custom_difficulty)
        game_menu.add_separator()
        game_menu.add_command(label="👤 Сменить имя игрока", command=self.change_player_name)
        game_menu.add_separator()
        game_menu.add_command(label="🏆 Таблица рекордов", command=self.show_records, accelerator="F2")
        game_menu.add_command(label="🗑️ Очистить рекорды", command=self.clear_records)
        game_menu.add_separator()
        game_menu.add_command(label="🚪 Выход", command=self.root.quit, accelerator="Ctrl+Q")

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0,
                            bg=self.colors['panel'],
                            fg=self.colors['text'],
                            activebackground=self.colors['accent'],
                            activeforeground="white")
        menubar.add_cascade(label="❓ Справка", menu=help_menu)
        help_menu.add_command(label="📖 Как играть", command=self.show_help)
        help_menu.add_command(label="ℹ️ О программе", command=self.show_about)

        # Привязка горячих клавиш
        self.root.bind('<Control-n>', lambda e: self.new_game())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<F2>', lambda e: self.show_records())

    def create_game_frame(self):
        """Создание игрового поля"""
        self.game_frame = tk.Frame(self.root,
                                   bg=self.colors['primary'],
                                   padx=10,
                                   pady=10)
        self.game_frame.pack()

    def create_info_panel(self):
        """Создание панели информации"""
        # Верхняя панель
        top_panel = tk.Frame(self.root,
                             bg=self.colors['secondary'],
                             relief=tk.RAISED,
                             bd=2,
                             padx=15,
                             pady=10)
        top_panel.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Имя игрока слева
        player_frame = tk.Frame(top_panel, bg=self.colors['secondary'])
        player_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(
            player_frame,
            text="👤",
            font=("Arial", 14),
            bg=self.colors['secondary'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)

        self.player_label = tk.Label(
            player_frame,
            text=f" {self.player_name}",
            font=("Arial", 12, "bold"),
            bg=self.colors['secondary'],
            fg=self.colors['text']
        )
        self.player_label.pack(side=tk.LEFT, padx=5)

        # Кнопка смены имени
        tk.Button(
            player_frame,
            text="✏️",
            command=self.change_player_name,
            font=("Arial", 9),
            bg=self.colors['accent'],
            fg="white",
            relief=tk.FLAT,
            padx=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        # Счетчик мин в центре
        center_frame = tk.Frame(top_panel, bg=self.colors['secondary'])
        center_frame.pack(side=tk.LEFT, expand=True)

        mines_frame = tk.Frame(center_frame, bg=self.colors['secondary'])
        mines_frame.pack()

        tk.Label(
            mines_frame,
            text="💣",
            font=("Arial", 16),
            bg=self.colors['secondary'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)

        self.mines_label = tk.Label(
            mines_frame,
            text=f" {self.mine_count}",
            font=("Arial", 16, "bold"),
            bg=self.colors['secondary'],
            fg=self.colors['warning']
        )
        self.mines_label.pack(side=tk.LEFT, padx=5)

        # Кнопка новой игры в центре
        self.new_game_btn = tk.Button(
            center_frame,
            text="🌊 НОВАЯ ИГРА",
            font=("Arial", 12, "bold"),
            command=self.new_game,
            bg=self.colors['button'],
            fg="white",
            activebackground=self.colors['button_hover'],
            activeforeground="white",
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=6,
            cursor="hand2"
        )
        self.new_game_btn.pack(pady=5)

        # Таймер справа
        time_frame = tk.Frame(top_panel, bg=self.colors['secondary'])
        time_frame.pack(side=tk.RIGHT, padx=10)

        tk.Label(
            time_frame,
            text="⏱️",
            font=("Arial", 16),
            bg=self.colors['secondary'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)

        self.time_label = tk.Label(
            time_frame,
            text=" 0 сек",
            font=("Arial", 16, "bold"),
            bg=self.colors['secondary'],
            fg=self.colors['success']
        )
        self.time_label.pack(side=tk.LEFT, padx=5)

        # Нижняя панель с инструкциями
        bottom_panel = tk.Frame(self.root,
                                bg=self.colors['accent'],
                                relief=tk.FLAT,
                                padx=10,
                                pady=8)
        bottom_panel.pack(fill=tk.X, padx=10, pady=(0, 10))

        instructions = [
            ("ЛКМ", "открыть клетку", self.colors['primary']),
            ("ПКМ", "поставить флаг", self.colors['warning']),
            ("СКМ", "быстрое открытие", self.colors['success']),
            ("F2", "таблица рекордов", self.colors['light'])
        ]

        for key, desc, color in instructions:
            frame = tk.Frame(bottom_panel, bg=self.colors['accent'])
            frame.pack(side=tk.LEFT, padx=15)

            tk.Label(
                frame,
                text=key,
                font=("Arial", 10, "bold"),
                bg=self.colors['accent'],
                fg=color
            ).pack(side=tk.LEFT)

            tk.Label(
                frame,
                text=f" - {desc}",
                font=("Arial", 10),
                bg=self.colors['accent'],
                fg="white"
            ).pack(side=tk.LEFT)

    def new_game(self):
        """Начать новую игру"""
        # Сброс состояния
        self.game_over = False
        self.game_won = False
        self.first_move = True
        self.flags_placed = 0
        self.revealed_count = 0
        self.start_time = None
        self.current_difficulty = "easy"  # По умолчанию

        # Пересчитываем размер клетки
        self.cell_size = self.calculate_cell_size()

        # Очистка поля
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        # Создание кнопок
        self.buttons = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                btn = tk.Button(
                    self.game_frame,
                    width=2 if self.width > 12 else 3,
                    height=1,
                    font=("Arial", 10 if self.width > 12 else 11),
                    relief=tk.RAISED,
                    bd=2,
                    bg=self.colors['cell_hidden'],
                    fg=self.colors['text'],
                    activebackground=self.colors['accent'],
                    cursor="hand2"
                )
                btn.grid(row=y, column=x, padx=1, pady=1)

                # Привязка событий
                btn.bind("<Button-1>", lambda e, x=x, y=y: self.left_click(x, y))
                btn.bind("<Button-3>", lambda e, x=x, y=y: self.right_click(x, y))
                btn.bind("<Button-2>", lambda e, x=x, y=y: self.middle_click(x, y))

                # Эффект наведения
                btn.bind("<Enter>", lambda e, b=btn: b.config(
                    bg=self.colors['accent'],
                    relief=tk.RAISED
                ))
                btn.bind("<Leave>", lambda e, b=btn, x=x, y=y:
                b.config(
                    bg=self.colors['cell_hidden'] if not self.board or not self.board[y][x]['revealed'] else
                    self.colors['cell_revealed'],
                    relief=tk.RAISED
                ))

                row.append(btn)
            self.buttons.append(row)

        # Инициализация игрового поля
        self.board = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append({
                    'is_mine': False,
                    'neighbors': 0,
                    'revealed': False,
                    'flagged': False
                })
            self.board.append(row)

        self.mines = []

        # Обновление информации
        self.update_info()

        # Запуск таймера
        self.update_timer()

        # Центрирование окна после создания поля
        self.center_window()

    def center_window(self):
        """Центрировать окно после изменения размера поля"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def set_difficulty(self, width, height, mines, difficulty):
        """Установить уровень сложности"""
        self.width = min(width, self.MAX_WIDTH)  # Ограничиваем ширину
        self.height = height
        self.mine_count = mines
        self.current_difficulty = difficulty
        self.new_game()

    def custom_difficulty(self):
        """Настройка пользовательской сложности"""
        try:
            width = simpledialog.askinteger(
                "Пользовательские настройки ⚙️",
                f"Введите ширину поля (5-{self.MAX_WIDTH}):",
                minvalue=5,
                maxvalue=self.MAX_WIDTH,
                initialvalue=min(self.width, self.MAX_WIDTH),
                parent=self.root
            )
            if not width:
                return

            height = simpledialog.askinteger(
                "Пользовательские настройки ⚙️",
                "Введите высоту поля (5-30):",
                minvalue=5,
                maxvalue=30,
                initialvalue=self.height,
                parent=self.root
            )
            if not height:
                return

            max_mines = width * height - 9
            mines = simpledialog.askinteger(
                "Пользовательские настройки ⚙️",
                f"Введите количество мин (1-{max_mines}):",
                minvalue=1,
                maxvalue=max_mines,
                initialvalue=min(self.mine_count, max_mines),
                parent=self.root
            )
            if not mines:
                return

            self.width = width
            self.height = height
            self.mine_count = mines
            self.current_difficulty = "custom"
            self.new_game()
        except:
            pass

    def generate_mines(self, safe_x, safe_y):
        """Сгенерировать мины, избегая безопасных клеток"""
        safe_cells = set()

        # Добавляем первую клетку и соседей в безопасные
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = safe_x + dx, safe_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    safe_cells.add((nx, ny))

        # Генерация мин
        self.mines = []
        while len(self.mines) < self.mine_count:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in safe_cells and (x, y) not in self.mines:
                self.mines.append((x, y))
                self.board[y][x]['is_mine'] = True

        # Подсчет соседей-мин для каждой клетки
        for y in range(self.height):
            for x in range(self.width):
                if not self.board[y][x]['is_mine']:
                    count = 0
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                if self.board[ny][nx]['is_mine']:
                                    count += 1
                    self.board[y][x]['neighbors'] = count

    def left_click(self, x, y):
        """Обработка левого клика (открытие клетки)"""
        if self.game_over or self.board[y][x]['revealed'] or self.board[y][x]['flagged']:
            return

        # Первый ход - генерация мин
        if self.first_move:
            self.generate_mines(x, y)
            self.first_move = False
            self.start_time = time.time()

        # Открываем клетку
        self.board[y][x]['revealed'] = True
        self.revealed_count += 1
        self.update_button(x, y)

        # Если мина - поражение
        if self.board[y][x]['is_mine']:
            self.game_over = True
            self.reveal_all_mines()
            self.show_game_over_message(False)
            return

        # Если пустая клетка - открываем соседей
        if self.board[y][x]['neighbors'] == 0:
            self.reveal_neighbors(x, y)

        # Проверка победы
        self.check_win()

    def show_game_over_message(self, is_win):
        """Показать сообщение о конце игры"""
        if is_win:
            elapsed_time = int(time.time() - self.start_time) if self.start_time else 0
            messagebox.showinfo(
                "Победа! 🎉",
                f"🏆 {self.player_name}, ПОЗДРАВЛЯЕМ! ВЫ ВЫИГРАЛИ! 🏆\n\n"
                f"Время: {elapsed_time} секунд\n"
                f"Уровень: {self.get_difficulty_name(self.current_difficulty)}\n"
                f"Размер поля: {self.width}×{self.height}\n\n"
                f"Нажмите OK чтобы продолжить"
            )
        else:
            messagebox.showinfo(
                "Поражение 💥",
                f"💣 {self.player_name}, ВЫ НАТУПИЛИ НА МИНУ! 💣\n\n"
                f"Игра окончена.\n"
                f"Попробуйте еще раз!"
            )

    def right_click(self, x, y):
        """Обработка правого клика (флаг)"""
        if self.game_over or self.board[y][x]['revealed']:
            return

        # Переключаем флаг
        self.board[y][x]['flagged'] = not self.board[y][x]['flagged']

        if self.board[y][x]['flagged']:
            self.flags_placed += 1
            self.buttons[y][x].config(
                text="🚩",
                fg=self.colors['warning'],
                bg=self.colors['cell_flag']
            )
        else:
            self.flags_placed -= 1
            self.buttons[y][x].config(
                text="",
                bg=self.colors['cell_hidden']
            )

        self.update_info()
        self.check_win()

    def middle_click(self, x, y):
        """Обработка среднего клика (быстрое открытие)"""
        if not self.board[y][x]['revealed'] or self.board[y][x]['neighbors'] == 0:
            return

        # Подсчет флагов вокруг
        flag_count = 0
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.board[ny][nx]['flagged']:
                        flag_count += 1

        # Если флагов столько же, сколько соседей-мин
        if flag_count == self.board[y][x]['neighbors']:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if not self.board[ny][nx]['revealed'] and not self.board[ny][nx]['flagged']:
                            self.left_click(nx, ny)

    def reveal_neighbors(self, x, y):
        """Рекурсивно открыть соседей"""
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not self.board[ny][nx]['revealed'] and not self.board[ny][nx]['flagged']:
                        self.board[ny][nx]['revealed'] = True
                        self.revealed_count += 1
                        self.update_button(nx, ny)
                        if self.board[ny][nx]['neighbors'] == 0:
                            self.reveal_neighbors(nx, ny)

    def update_button(self, x, y):
        """Обновить внешний вид кнопки"""
        cell = self.board[y][x]
        btn = self.buttons[y][x]

        if cell['revealed']:
            btn.config(
                relief=tk.SUNKEN,
                bg=self.colors['cell_revealed'],
                state=tk.DISABLED
            )
            if cell['is_mine']:
                btn.config(
                    text="💣",
                    fg=self.colors['danger'],
                    bg=self.colors['cell_mine']
                )
            elif cell['neighbors'] > 0:
                color = self.number_colors.get(cell['neighbors'], self.colors['text'])
                btn.config(text=str(cell['neighbors']), fg=color)
            else:
                btn.config(text="")
        else:
            btn.config(
                relief=tk.RAISED,
                state=tk.NORMAL,
                bg=self.colors['cell_hidden'] if not cell['flagged'] else self.colors['cell_flag']
            )

    def reveal_all_mines(self):
        """Показать все мины при поражении"""
        for y, x in self.mines:
            self.board[x][y]['revealed'] = True
            self.update_button(y, x)

    def check_win(self):
        """Проверить условия победы"""
        # Все не-мины открыты
        all_safe_revealed = True
        for y in range(self.height):
            for x in range(self.width):
                if not self.board[y][x]['is_mine'] and not self.board[y][x]['revealed']:
                    all_safe_revealed = False
                    break
            if not all_safe_revealed:
                break

        # Или все мины помечены флагами
        if not all_safe_revealed:
            all_mines_flagged = True
            for y, x in self.mines:
                if not self.board[x][y]['flagged']:
                    all_mines_flagged = False
                    break
            if all_mines_flagged:
                # Проверяем, что нет лишних флагов
                flag_count = 0
                for y in range(self.height):
                    for x in range(self.width):
                        if self.board[y][x]['flagged']:
                            flag_count += 1
                all_safe_revealed = (flag_count == self.mine_count)

        if all_safe_revealed and not self.game_won:
            self.game_won = True
            self.game_over = True
            elapsed_time = int(time.time() - self.start_time) if self.start_time else 0

            # Показываем сообщение о победе
            self.show_game_over_message(True)

            # Проверяем, является ли результат рекордом
            if self.current_difficulty in ["easy", "medium", "hard", "custom"]:
                records_for_diff = self.records.get(self.current_difficulty, [])
                is_record = True

                if records_for_diff:
                    # Проверяем, входит ли время в топ-10
                    if len(records_for_diff) >= 10:
                        worst_time = max(r["time"] for r in records_for_diff)
                        if elapsed_time > worst_time:
                            is_record = False

                if is_record:
                    self.add_record(self.current_difficulty, elapsed_time)

    def update_info(self):
        """Обновить информацию на панели"""
        mines_left = self.mine_count - self.flags_placed
        self.mines_label.config(
            text=f" {mines_left}",
            fg=self.colors['warning'] if mines_left > 0 else self.colors['success']
        )

        # Обновляем имя игрока
        self.player_label.config(text=f" {self.player_name}")

    def update_timer(self):
        """Обновить таймер"""
        if self.start_time and not self.game_over:
            elapsed_time = int(time.time() - self.start_time)
            self.time_label.config(
                text=f" {elapsed_time} сек",
                fg=self.colors['success'] if elapsed_time < 100 else
                (self.colors['warning'] if elapsed_time < 300 else self.colors['danger'])
            )

        # Планируем следующее обновление через 1 секунду
        self.root.after(1000, self.update_timer)

    def show_help(self):
        """Показать справку в морском стиле"""
        help_window = tk.Toplevel(self.root)
        help_window.title("📖 Справка")
        help_window.configure(bg=self.colors['primary'])
        help_window.resizable(False, False)

        # Центрирование окна
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - 300
        y = (help_window.winfo_screenheight() // 2) - 250
        help_window.geometry(f"600x500+{x}+{y}")

        # Заголовок
        header_frame = tk.Frame(help_window, bg=self.colors['primary'])
        header_frame.pack(fill=tk.X, pady=(15, 10))

        tk.Label(
            header_frame,
            text="📖 КАК ИГРАТЬ В МОРСКОЙ САПЕР",
            font=("Arial", 18, "bold"),
            bg=self.colors['primary'],
            fg=self.colors['text']
        ).pack()

        # Основное содержание
        canvas = tk.Canvas(help_window, bg=self.colors['primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(help_window, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=self.colors['primary'])

        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        sections = [
            ("🌊 ЦЕЛЬ ИГРЫ",
             "Открыть все клетки, не содержащие морских мин.\n"
             "Используйте логику и внимательность, чтобы избежать взрыва!",
             self.colors['text']),

            ("📏 ОГРАНИЧЕНИЯ",
             f"• Максимальная ширина поля: {self.MAX_WIDTH} клеток\n"
             "• Максимальная высота поля: 30 клеток\n"
             "• Размер клеток автоматически адаптируется\n"
             "• Окно игры центрируется на экране",
             self.colors['accent']),

            ("🖱️ УПРАВЛЕНИЕ",
             "• Левый клик - открыть клетку\n"
             "• Правый клик - поставить/убрать флаг 🚩\n"
             "• Средний клик - быстрое открытие соседей\n"
             "• F2 - открыть таблицу рекордов",
             self.colors['accent']),

            ("📋 ПРАВИЛА",
             "1. Число в клетке показывает количество мин в соседних клетках\n"
             "2. Используйте флаги 🚩 для отметки предполагаемых мин\n"
             "3. Игра закангрывается при открытии мины 💣\n"
             "4. Быстрое открытие работает, когда флагов достаточно",
             self.colors['text_secondary']),

            ("⚙️ УРОВНИ СЛОЖНОСТИ",
             f"• 🌊 Новичок: 9×9 поле, 10 мин (макс. ширина {self.MAX_WIDTH})\n"
             f"• ⚓ Любитель: 16×16 поле, 40 мин (макс. ширина {self.MAX_WIDTH})\n"
             f"• 🚢 Профессионал: 16×30 поле, 99 мин (макс. ширина {self.MAX_WIDTH})\n"
             f"• 🧭 Пользовательский: настройте размер до {self.MAX_WIDTH}×30",
             self.colors['text']),

            ("👤 СИСТЕМА ИМЕН",
             f"• Ваше текущее имя: {self.player_name}\n"
             "• Имя сохраняется между играми\n"
             "• Можно изменить имя в меню Игра → Сменить имя игрока\n"
             "• Все рекорды привязываются к имени игрока",
             self.colors['accent']),

            ("🏆 СИСТЕМА РЕКОРДОВ",
             "• Таблица рекордов сохраняется автоматически\n"
             "• Топ-10 результатов для каждого уровня сложности\n"
             "• Ваши рекорды подсвечиваются в таблице\n"
             "• Имя игрока отображается рядом с каждым рекордом",
             self.colors['success']),

            ("🎯 СТРАТЕГИЯ",
             "• Начинайте с углов и краев поля\n"
             "• Если число равно количеству закрытых клеток вокруг - все они мины\n"
             "• Если число равно количеству флагов вокруг - остальные клетки безопасны\n"
             "• Используйте логику, а не удачу!",
             self.colors['warning']),

            ("⌨️ ГОРЯЧИЕ КЛАВИШИ",
             "• Ctrl+N - Новая игра\n"
             "• Ctrl+Q - Выход\n"
             "• F2 - Таблица рекордов",
             self.colors['text']),
        ]

        for title, content, color in sections:
            section_frame = tk.Frame(content_frame, bg=self.colors['primary'])
            section_frame.pack(fill=tk.X, pady=12, padx=20)

            tk.Label(
                section_frame,
                text=title,
                font=("Arial", 13, "bold"),
                bg=self.colors['primary'],
                fg=color,
                anchor="w"
            ).pack(fill=tk.X, pady=(0, 5))

            tk.Label(
                section_frame,
                text=content,
                font=("Arial", 10),
                bg=self.colors['primary'],
                fg=self.colors['text_secondary'],
                justify=tk.LEFT,
                anchor="w",
                wraplength=550
            ).pack(fill=tk.X)

        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        scrollbar.pack(side="right", fill="y")

        # Кнопка закрытия
        button_frame = tk.Frame(help_window, bg=self.colors['primary'])
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Закрыть",
            command=help_window.destroy,
            font=("Arial", 11, "bold"),
            bg=self.colors['button'],
            fg="white",
            activebackground=self.colors['button_hover'],
            relief=tk.RAISED,
            bd=2,
            padx=30,
            pady=8,
            cursor="hand2"
        ).pack()

        # Привязка колесика мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def show_about(self):
        """Показать информацию о программе"""
        about_text = f"""
{'=' * 50}
🌊 МОРСКОЙ САПЕР - ВЕРСИЯ 5.0
{'=' * 50}

📏 ОГРАНИЧЕНИЯ РАЗМЕРА:
• Максимальная ширина поля: {self.MAX_WIDTH} клеток
• Максимальная высота поля: 30 клеток
• Автоматическая адаптация размера клеток

🎨 ДИЗАЙН:
Игра выполнена в морской цветовой гамме с мягкими,
не режущими глаз оттенками синего и голубого.

👤 СИСТЕМА ИМЕН:
• Текущий игрок: {self.player_name}
• Имя сохраняется между сеансами игры
• Все рекорды привязываются к имени

🏆 ТАБЛИЦА РЕКОРДОВ:
• Автоматическое сохранение в JSON формате
• Отдельные таблицы для каждого уровня сложности
• Подсветка ваших рекордов в таблице

⚙️ ТЕХНОЛОГИИ:
• Python 3.x с графическим интерфейсом Tkinter
• JSON для хранения данных
• Адаптивный дизайн под разные размеры поля

📁 СОХРАНЕНИЕ ДАННЫХ:
• Рекорды: minesweeper_records.json
• Имя игрока: player_name.txt

🎯 ЦЕЛЬ ПРОЕКТА:
Создание классической игры "Сапер" с современным
дизайном, системой рекордов и персонализацией.

👨‍💻 РАЗРАБОТКА:
Игра разработана с акцентом на удобство
и эстетическое удовольствие от игрового процесса.

🌊 УДАЧИ В ОСВОЕНИИ МОРСКИХ ГЛУБИН!
"""
        messagebox.showinfo("ℹ️ О программе", about_text)

    def run(self):
        """Запустить игру"""
        # Центрирование окна
        self.center_window()

        # Запуск главного цикла
        self.root.mainloop()


def main():
    """Точка входа в программу"""
    print("=" * 70)
    print("🌊 МОРСКОЙ САПЕР - ВЕРСИЯ С ОГРАНИЧЕНИЕМ ШИРИНЫ 🌊".center(70))
    print("=" * 70)
    print("\n📏 ОГРАНИЧЕНИЯ РАЗМЕРА:")
    print(f"  • Максимальная ширина поля: 16 клеток")
    print("  • Максимальная высота поля: 30 клеток")
    print("  • Автоматическая адаптация размера клеток")
    print("\n👤 СИСТЕМА ИМЕН:")
    print("  • Имя сохраняется между играми")
    print("  • Все рекорды привязываются к имени")
    print("  • Можно сменить имя в любой момент")
    print("\n🎯 Уровни сложности:")
    print("  1. 🌊 Новичок: 9x9, 10 мин")
    print("  2. ⚓ Любитель: 16x16, 40 мин")
    print("  3. 🚢 Профессионал: 16x30, 99 мин")
    print("  4. 🧭 Пользовательский: настройте сами (до 16x30)")
    print("\n🖱️ Управление:")
    print("  ЛКМ - открыть клетку")
    print("  ПКМ - поставить/убрать флаг 🚩")
    print("  СКМ - быстрое открытие соседей")
    print("  F2 - таблица рекордов 🏆")
    print("\n💾 Сохранение:")
    print("  Рекорды: minesweeper_records.json")
    print("  Имя игрока: player_name.txt")
    print("=" * 70)

    try:
        # Проверяем, установлен ли tkinter
        import tkinter
        print("\n✅ Запуск игры...")

        # Создаем и запускаем игру
        game = Minesweeper()
        game.run()

    except ImportError:
        print("\n❌ ОШИБКА: Tkinter не найден!")
        print("\nДля установки Tkinter:")
        print("Windows: Обычно идет в составе Python")
        print("Linux: sudo apt-get install python3-tk")
        print("Mac: brew install python-tk")

        input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    # Необходимо для работы notebook (вкладок) в tkinter
    try:
        from tkinter import ttk

        main()
    except ImportError:
        print("❌ Ошибка: не удалось импортировать ttk из tkinter")