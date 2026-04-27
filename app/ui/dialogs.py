import tkinter as tk
from tkinter import ttk
from app.utils import FENSetter

class NewGameDialog(tk.Toplevel):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
        self.title("새 대국 설정")
        self.geometry("450x580")
        self.resizable(False, False)
        
        # 선택 값 저장 (기본값: 상마상마)
        self.selected_han = tk.StringVar(value="상마상마")
        self.selected_cho = tk.StringVar(value="상마상마")
        
        # 모달 설정 (메인 윈도우 조작 방지)
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. 탭 컨트롤 (사용자가 초를 잡으면 초가 화면 아래, 한을 잡으면 한이 화면 아래쪽에 위치/ 항상 초가 먼저 둠)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # [탭 1] 사용자가 초(선수)로 시작할 때 - 화면상 위가 한(후수), 아래가 초(선수)
        self.tab_cho_start = tk.Frame(self.notebook, bg="#fcfcfc")
        self.notebook.add(self.tab_cho_start, text=" 초나라(선수) ")
        self._create_cho_first_layout(self.tab_cho_start)

        # [탭 2] 사용자가 한(후수)으로 시작할 때 - 화면상 위가 초(선수), 아래가 한(후수)
        self.tab_han_start = tk.Frame(self.notebook, bg="#fcfcfc")
        self.notebook.add(self.tab_han_start, text=" 한나라(후수) ")
        self._create_han_first_layout(self.tab_han_start)

        # 2. 확인/취소 버튼
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", side="bottom", pady=15)
        
        tk.Button(btn_frame, text="확인", width=12, command=self._on_confirm).pack(side="right", padx=20)
        tk.Button(btn_frame, text="취소", width=10, command=self.destroy).pack(side="right")

    def _create_cho_first_layout(self, parent):
        """초가 선수일 때: 위는 한나라, 아래는 초나라"""
        # 한나라(소문자) 영역 - 위에 배치
        han_frame = tk.LabelFrame(parent, text=" 한나라(Red) 상차림 ", padx=10, pady=10)
        han_frame.pack(fill="x", padx=10, pady=5)
        self._add_options(han_frame, self.selected_han, "han")

        # 초나라(대문자) 영역 - 아래에 배치
        cho_frame = tk.LabelFrame(parent, text=" 초나라(Blue) 상차림 ", padx=10, pady=10)
        cho_frame.pack(fill="x", padx=10, pady=5)
        self._add_options(cho_frame, self.selected_cho, "cho")

    def _create_han_first_layout(self, parent):
        """한이 선수일 때: 위는 초나라, 아래는 한나라"""
        # 초나라(대문자) 영역 - 위에 배치
        cho_frame = tk.LabelFrame(parent, text=" 초나라(Blue) 상차림 ", padx=10, pady=10)
        cho_frame.pack(fill="x", padx=10, pady=5)
        self._add_options(cho_frame, self.selected_cho, "cho")

        # 한나라(소문자) 영역 - 아래에 배치
        han_frame = tk.LabelFrame(parent, text=" 한나라(Red) 상차림 ", padx=10, pady=10)
        han_frame.pack(fill="x", padx=10, pady=5)
        self._add_options(han_frame, self.selected_han, "han")

    def _add_options(self, frame, var, side):
        """라디오 버튼과 미리보기 영역"""
        formations = ["상마상마", "마상마상", "상마마상", "마상상마"]
        for i, fmt in enumerate(formations):
            r, c = divmod(i, 2)
            # 라디오 버튼만 배치 (이미지는 추후 Canvas 미니맵 등으로 확장 가능)
            tk.Radiobutton(frame, text=fmt, variable=var, value=fmt).grid(row=r, column=c, sticky="w", padx=20, pady=5)

    def _on_confirm(self):
        """선택된 상차림으로 FEN을 생성하여 매니저에게 전달"""
        # 탭 인덱스에 따라 다른 FEN 생성 (선수는 항상 초)
        tab_index = self.notebook.index(self.notebook.select())
        
        if tab_index == 0:
            # 탭 1: 초나라(선수) - 초가 아래쪽에 보임
            new_fen = FENSetter.get_initial_fen_han_view(
                self.selected_han.get(),
                self.selected_cho.get()
            )
        else:
            # 탭 2: 한나라(선수로 보이나 실제 선수는 초) - 한이 아래쪽에 보임
            new_fen = FENSetter.get_initial_fen_cho_player(
                self.selected_han.get(),
                self.selected_cho.get()
            )
        
        # 매니저에게 FEN 데이터 전달하여 게임 초기화
        self.manager.request_new_game(new_fen)
        self.destroy()