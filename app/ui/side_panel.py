import tkinter as tk
from tkinter import ttk
import config

class SidePanel(tk.Frame):
    def __init__(self, parent, manager):
        """
        사이드 패널 클래스.
        :param parent: 부모 위젯 (MainWindow의 프레임)
        :param manager: GameManager 객체 (명령 전달용)
        """
        # 부모(MainWindow)의 설정값을 참조하기 위해 manager.cfg 사용
        super().__init__(parent, width=300, relief="flat", bg="#f0f0f0")
        self.manager = manager
        self.cfg = manager.cfg
        
        # 1. 각 레이어(층)를 순서대로 조립
        self._create_layer_1_engine_info()
        self._create_layer_2_scoreboard()
        self._create_layer_3_commands()
        self._create_layer_3_5_navigation()  # 수순 이동 버튼 층
        self._create_layer_4_notebook()      # 기보/분석 탭

        self.reset_history()

    # --- 1층: 엔진 정보 ---
    def _create_layer_1_engine_info(self):
        self.engine_frame = tk.LabelFrame(self, text=" 엔진 정보 ", padx=5, pady=5, bg="#f0f0f0")
        self.engine_frame.pack(fill="x", padx=10, pady=5)
        
        # 엔진 이름 (config에서 가져오거나 고정)
        engine_name = self.cfg.ENGINE_NAME.split('-')[0].capitalize()
        self.lbl_engine_name = tk.Label(self.engine_frame, text=f"{engine_name}", fg="blue", bg="#f0f0f0")
        self.lbl_engine_name.pack(side="left")
        
        self.lbl_status = tk.Label(self.engine_frame, text="● Ready", fg="green", bg="#f0f0f0")
        self.lbl_status.pack(side="right")

    # --- 2층: 스코어보드 ---
    def _create_layer_2_scoreboard(self):
        self.score_frame = tk.Frame(self, pady=10, bg="#f0f0f0")
        self.score_frame.pack(fill="x", padx=10)
        
        # 초나라 점수 (왼쪽)
        self.lbl_cho_score = tk.Label(self.score_frame, text="초: 0.0", 
                                      font=("Malgun Gothic", 12, "bold"), 
                                      fg=self.cfg.COLOR_CHO, bg="#f0f0f0")
        self.lbl_cho_score.pack(side="left", expand=True)
        
        # 한나라 점수 (오른쪽)
        self.lbl_han_score = tk.Label(self.score_frame, text=f"한: {self.cfg.DOM_SCORE}", 
                                      font=("Malgun Gothic", 12, "bold"), 
                                      fg=self.cfg.COLOR_HAN, bg="#f0f0f0")
        self.lbl_han_score.pack(side="right", expand=True)

    # --- 3층: 주요 명령 버튼 (새대국, 무르기 등) ---
    def _create_layer_3_commands(self):
        self.cmd_frame = tk.Frame(self, bg="#f0f0f0")
        self.cmd_frame.pack(fill="x", padx=10, pady=5)
        
        self.cmd_frame.columnconfigure(0, weight=1)
        self.cmd_frame.columnconfigure(1, weight=1)
        self.cmd_frame.columnconfigure(2, weight=1)

        # 버튼 생성 및 GameManager 함수 연결
        self.btn_analysis_start = tk.Button(self.cmd_frame, text="분석 시작", height=2, command=self._on_analysis_start)
        self.btn_game_start     = tk.Button(self.cmd_frame, text="대국 시작", height=2, command=self._on_game_start)
        self.btn_auto_game_start = tk.Button(self.cmd_frame, text="자동 대국", height=2, command=self._on_auto_game_start)
        self.btn_surrender  = tk.Button(self.cmd_frame, text="기권", height=2, command=self._on_surrender) # 기권 버튼 복원
        self.btn_pass  = tk.Button(self.cmd_frame, text="한수쉼", bg="#36f720",command=self._on_pass) # 한수쉼 버튼 복원
        self.btn_stop           = tk.Button(self.cmd_frame, text="중단",     height=2, command=self._on_stop)

        self.btn_analysis_start.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.btn_game_start.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.btn_auto_game_start.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
        self.btn_surrender.grid(row=1, column=0, sticky="nsew", padx=2, pady=2) # 기권 버튼 그리드 위치
        self.btn_pass.grid(row=1, column=1, sticky="nsew", padx=2, pady=2) # 한수쉼 버튼 그리드 위치
        self.btn_stop.grid(row=1, column=2, sticky="nsew", padx=2, pady=2)

    # --- 3.5층: 수순 네비게이션 ( <<  <  15/42  >  >> ) ---
    def _create_layer_3_5_navigation(self):
        self.nav_frame = tk.Frame(self, bg="#f0f0f0")
        self.nav_frame.pack(fill="x", padx=10, pady=10)
        
        for i in range(5):
            self.nav_frame.columnconfigure(i, weight=1)

        self.btn_first = tk.Button(self.nav_frame, text=" << ", command=self.manager.go_to_first)
        self.btn_prev  = tk.Button(self.nav_frame, text=" < ", command=self.manager.go_to_prev)
        
        self.move_count_var = tk.StringVar(value="0 / 0")
        self.lbl_move_count = tk.Label(self.nav_frame, textvariable=self.move_count_var, 
                                       font=("Consolas", 11, "bold"), width=8, 
                                       relief="sunken", bg="white")
        
        self.btn_next = tk.Button(self.nav_frame, text=" > ", command=self.manager.go_to_next)
        self.btn_last = tk.Button(self.nav_frame, text=" >> ", command=self.manager.go_to_last)

        self.btn_first.grid(row=0, column=0, sticky="nsew", padx=1)
        self.btn_prev.grid(row=0, column=1, sticky="nsew", padx=1)
        self.lbl_move_count.grid(row=0, column=2, sticky="nsew", padx=3)
        self.btn_next.grid(row=0, column=3, sticky="nsew", padx=1)
        self.btn_last.grid(row=0, column=4, sticky="nsew", padx=1)

    # --- 4층: 기보 및 분석 데이터 (Notebook 탭) ---
    def _create_layer_4_notebook(self):
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=5)

        # 1번 탭: 기보 수순 리스트
        self.tab_history = tk.Frame(self.tabs, bg="white")
        self.tabs.add(self.tab_history, text=" 기보 ")
        
        self.txt_history = tk.Text(self.tab_history, font=("Consolas", 10), 
                                   undo=True, bd=0, padx=5, pady=5)
        self.txt_history.pack(fill="both", expand=True)

        # 2번 탭: 엔진 분석 정보
        self.tab_analysis = tk.Frame(self.tabs, bg="white")
        self.tabs.add(self.tab_analysis, text=" 분석 ")
        
        self.txt_analysis = tk.Text(self.tab_analysis, font=("Consolas", 10), 
                                    bg="#f9f9f9", bd=0, padx=5, pady=5)
        self.txt_analysis.pack(fill="both", expand=True)

    # --- 내부 이벤트 핸들러 (Manager와 연결) ---
    def _on_analysis_start(self):
        print("SidePanel: 분석 모드 시작 요청")
        self.lbl_status.config(text="● Analyzing", fg="orange")
        self.manager.start_analysis_mode()

    def _on_game_start(self):
        print("SidePanel: 대국 모드 시작 요청")
        self.lbl_status.config(text="● Playing", fg="blue")
        self.manager.start_game_mode()

    def _on_auto_game_start(self):
        print("SidePanel: 자동 대국 모드 시작 요청")
        self.lbl_status.config(text="● Auto Play", fg="purple")
        self.manager.start_auto_game_mode()

    def _on_surrender(self):
        print("SidePanel: 기권 요청")
        # self.manager.surrender() # GameManager에 구현 필요

    def _on_pass(self):
        """한수쉼 실행"""
        # 대국 모드에서 플레이어 턴이 아니면 무시
        if self.manager.current_mode == "game" and self.manager.current_turn != self.manager.player_side:
            return
        self.manager.pass_turn()

    def _on_stop(self):
        print("SidePanel: 중단 요청")
        self.lbl_status.config(text="● Ready", fg="green")
        self.manager.stop_current_mode()
    
    def reset_history(self):
        """기보창을 초기 FEN 헤더 상태로 리셋"""
        self.txt_history.config(state="normal")
        self.txt_history.delete("1.0", tk.END)
        
        initial_header = f'[FEN "{self.cfg.INITIAL_FEN}"]\n\n'
        self.txt_history.insert(tk.END, initial_header)
        
        self.txt_history.config(state="disabled")
    
    def set_history_text(self, text):
        """텍스트 위젯 내용 교체 (상태 제어 포함)"""
        self.txt_history.config(state="normal")   # 편집 가능 모드
        self.txt_history.delete("1.0", tk.END)
        self.txt_history.insert(tk.END, text)
        self.txt_history.see(tk.END)              # 자동 스크롤
        self.txt_history.config(state="disabled") # 읽기 전용 모드

    # --- 외부 상태 업데이트용 메서드 (MainWindow가 호출) ---
    def update_status(self, turn, history, fen=None):
        """턴 정보와 기보 리스트를 받아 UI를 갱신합니다."""
        # FEN이 제공되지 않으면 기본값 사용
        if fen is None:
            fen = self.cfg.INITIAL_FEN
            
        # 1. 수순 표시 업데이트
        total_moves = len(history)
        current_step = self.manager.current_step  # 직접 접근
        self.update_move_count(current_step, total_moves)
        
        # 2. 기보 텍스트 업데이트
        """
        데이터(UCI 리스트)를 화면용 좌표(PGN)로 변환하여 기보창 전체를 다시 그립니다.
        """
        from app.utils import PGNManager
        
        # FEN을 포함한 전체 텍스트 생성
        full_text = PGNManager.format_moves(fen, history)
        self.set_history_text(full_text)

    def update_scores(self, cho, han):
        self.lbl_cho_score.config(text=f"초: {cho:.1f}")
        self.lbl_han_score.config(text=f"한: {han:.1f}")

    def update_move_count(self, current, total):
        self.move_count_var.set(f"{current} / {total}")
        # game/auto_game 모드에서 네비게이션 비활성화
        mode = self.manager.current_mode
        state = "disabled" if mode in ("game", "auto_game") else "normal"
        for btn in (self.btn_first, self.btn_prev, self.btn_next, self.btn_last):
            btn.config(state=state)

    def log_analysis(self, text):
        """엔진 분석 로그를 출력합니다."""
        self.txt_analysis.insert(tk.END, text + "\n")
        self.txt_analysis.see(tk.END)