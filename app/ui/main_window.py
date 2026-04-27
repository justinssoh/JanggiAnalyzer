import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from app.ui.canvas import JanggiCanvas
from app.ui.side_panel import SidePanel

class JanggiApp:
    def __init__(self, root, config, game_manager):
        """
        메인 윈도우 UI 클래스.
        :param root: Tkinter root 객체
        :param config: config 모듈
        :param game_manager: GameManager 인스턴스
        """
        self.root = root
        self.cfg = config
        self.game_manager = game_manager

        # 1. 윈도우 기본 설정
        self.root.title(self.cfg.WINDOW_TITLE)
        self.root.geometry(f"{self.cfg.WINDOW_WIDTH}x{self.cfg.WINDOW_HEIGHT}")
        self.root.configure(bg="#e0e0e0")

        # 2. 게임 매니저에 UI 갱신 콜백 등록
        # 매니저가 데이터 처리를 끝내면 이 클래스의 refresh_ui를 호출하게 됩니다.
        self.game_manager.set_ui_callback(self.refresh_ui)

        # 3. 레이아웃 조립
        self._setup_status_bar()
        self._setup_menu()
        self._setup_ui()
        
        # 4. 종료 프로토콜 설정 (엔진 프로세스 정리)
        self.game_manager.set_ui_callback(self.refresh_ui)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_ui(self):
        """좌우 배치를 담당하는 메인 프레임 설정"""
        # 전체를 감싸는 컨테이너
        self.main_container = tk.Frame(self.root, bg="#e0e0e0")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # [좌측] 장기판 영역 (Canvas)
        self.canvas_frame = tk.Frame(self.main_container, bd=2, relief="sunken")
        self.canvas_frame.pack(side="left", fill="both", expand=True)

        # 실제 장기판 캔버스 생성 (모델 데이터를 넘겨줌)
        self.canvas = JanggiCanvas(
            self.canvas_frame, 
            self.game_manager.model, 
            self.game_manager
        )
        self.canvas.grid(row=0, column=0)

        # [우측] 세로 좌표 프레임 (9 ~ 0)
        self.v_coord_frame = tk.Frame(self.canvas_frame, bg="#ffffff")
        self.v_coord_frame.grid(row=0, column=1, sticky="ns")
        self._create_v_labels()

        # [하단] 가로 좌표 프레임 (a ~ i)
        self.h_coord_frame = tk.Frame(self.canvas_frame, bg="#ffffff")
        self.h_coord_frame.grid(row=1, column=0, sticky="ew")
        self._create_h_labels()
    
        # [우측] 사이드 패널 영역 (SidePanel)
        # 각종 버튼과 엔진 분석 결과가 들어감
        self.side_panel = SidePanel(
            self.main_container, 
            self.game_manager
        )
        self.side_panel.pack(side="right", fill="y", padx=(10, 0))

    print("UI: 화면 갱신 완료")
    
    def _create_v_labels(self):
        """세로 좌표 9~0을 생성하여 v_coord_frame에 배치"""
        # 시작점(OFFSET) 맞추기용 빈 칸
        # tk.Frame(self.v_coord_frame, height=self.cfg.OFFSET, bg="white").pack()
        
        for i in range(10):
            # 각 숫자마다 격자 크기(CELL_SIZE)만큼의 영역을 할당
            f = tk.Frame(self.v_coord_frame, height=self.cfg.CELL_SIZE, width=30)
            f.pack(fill="x")
            f.pack_propagate(False) # 내부 라벨 크기에 프레임이 변하지 않게 고정
            
            lbl = tk.Label(f, text=str(9-i), font=("Consolas", 10))
            lbl.place(relx=0.5, rely=0.5, anchor="center")

    def _create_h_labels(self):
        """가로 좌표 a~i 생성 (장기판 아래)"""
        # 1. 가로 레이블 전체를 감싸는 프레임의 높이를 명시 (최소 30~40px)
        self.h_coord_frame.config(height=40, bg="#ffffff") 
        self.h_coord_frame.pack_propagate(False) # 내부 요소 때문에 크기가 줄어들지 않게 고정

        # 2. 시작점(OFFSET) 맞추기용 왼쪽 여백 프레임
        # 장기판의 첫 번째 줄이 OFFSET만큼 떨어져 있으므로 똑같이 맞춰줍니다.
        # tk.Frame(self.h_coord_frame, width=self.cfg.OFFSET, bg="#ffffff").pack(side="left")
    
        for i in range(9):
            # 3. 각 알파벳을 담을 칸(Container) 생성
            # 너비는 정확히 CELL_SIZE와 일치해야 격자 선과 숫자가 맞습니다.
            cell_container = tk.Frame(self.h_coord_frame, width=self.cfg.CELL_SIZE, height=40, bg="#ffffff")
            cell_container.pack(side="left")
            cell_container.pack_propagate(False) # 크기 고정
            
            # 4. 실제 알파벳 레이블 배치
            lbl = tk.Label(cell_container, text=chr(ord('a')+i), 
                        font=("Consolas", 11, "bold"), bg="#ffffff", fg="#555555")
            lbl.place(relx=0.5, rely=0.5, anchor="center") # 컨테이너의 정중앙

    def on_closing(self):
        """프로그램 종료 시 엔진 프로세스를 안전하게 닫습니다."""
        if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
            if self.game_manager.engine:
                self.game_manager.engine.quit_engine()
            self.root.destroy()

# -------------------------------------------------------------------------
# 참고: 이 클래스는 main.py에서 다음과 같이 생성됩니다.
# app = JanggiApp(root, config, game_manager)

    def _setup_menu(self):
        """상단 메뉴바 설정"""
        self.menubar = tk.Menu(self.root)

        # [파일] 메뉴
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="새 대국", command=self._open_new_game_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.on_closing)
        self.menubar.add_cascade(label="파일", menu=file_menu)

        # [PGN] 메뉴
        pgn_menu = tk.Menu(self.menubar, tearoff=0)
        pgn_menu.add_command(label="Save PGN", command=self._on_pgn_save)
        pgn_menu.add_command(label="Load PGN", command=self._on_pgn_load)
        self.menubar.add_cascade(label="PGN", menu=pgn_menu)

        # [설정] 메뉴
        settings_menu = tk.Menu(self.menubar, tearoff=0)
        settings_menu.add_command(label="엔진 설정", command=lambda: print("Engine Settings"))
        self.menubar.add_cascade(label="설정", menu=settings_menu)

        # [도움말] 메뉴
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="정보", command=lambda: messagebox.showinfo("정보", "Python 장기 분석기 v1.0"))
        self.menubar.add_cascade(label="도움말", menu=help_menu)

        self.root.config(menu=self.menubar) 

    def _setup_status_bar(self):
        """최하단 상태 표시줄 설정"""
        # bd=1, relief="sunken"으로 경계선을 줍니다.
        self.status_var = tk.StringVar(value=" 준비됨 ")
        self.status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            bd=1, 
            relief="sunken", 
            anchor="w",  # 텍스트 왼쪽 정렬
            padx=10,
            pady=3,
            bg="#f0f0f0"
        )
        self.status_bar.pack(side="bottom", fill="x")

    def set_status(self, message):
        """외부(Manager 등)에서 상태 메시지를 변경할 때 사용"""
        self.status_var.set(f" {message} ")

    def refresh_ui(self):
        """
        GameManager로부터 신호를 받아 화면을 통째로 새로 고칩니다.
        리셋 버튼, 기물 이동, PGN 로드 등 모든 상황에서 호출됩니다.
        """
        # 1. 캔버스 기물 위치 다시 그리기
        self.canvas.draw_all()
        
        # 2. 캔버스에 포커스 설정 및 이벤트 강제 발생 (키보드 조작 등을 위함)
        self.canvas.focus_set()
        self.canvas.event_generate("<FocusIn>")
        
        # 3. 사이드 패널의 기보창이나 상태 갱신
        self.side_panel.update_status(
            turn=self.game_manager.current_turn,
            history=self.game_manager.move_history,
            fen=self.game_manager.current_fen
        )
        
        # 4. 하단 상태바 정보 업데이트
        turn_text = "초(Blue) 차례" if self.game_manager.current_turn == "w" else "한(Red) 차례"
        self.set_status(f"현재 턴: {turn_text} | 수순: {self.game_manager.current_step}/{len(self.game_manager.move_history)}수")
        
        # 5. 윈도우 업데이트 강제 실행
        # self.root.update_idletasks()
    
    # --- PGN 실행 로직 ---
    def _on_pgn_save(self):
        """현재 대국을 PGN 파일로 저장"""
        filename = filedialog.asksaveasfilename(
            title="기보 저장",
            defaultextension=".pgn",
            filetypes=[("PGN files", "*.pgn"), ("Text files", "*.txt")]
        )
        if not filename:
            return

        try:
            # 2. SidePanel의 텍스트 위젯에서 처음(1.0)부터 끝(END)까지 텍스트 추출
            # 주의: self.side_panel.txt_history 에 접근합니다.
            raw_pgn_text = self.side_panel.txt_history.get("1.0", tk.END).strip()
            
            if not raw_pgn_text:
                messagebox.showwarning("경고", "저장할 기보 내용이 없습니다.")
                return

            # 3. 파일 쓰기
            with open(filename, "w", encoding="utf-8") as f:
                f.write(raw_pgn_text)                
            messagebox.showinfo("성공", f"기보가 성공적으로 저장되었습니다.\n{filename}")
            
        except Exception as e:
            messagebox.showerror("오류", f"파일 저장 중 오류가 발생했습니다:\n{e}")

    def _on_pgn_load(self):
        """PGN 파일을 불러와 대국 재구성"""
        filename = filedialog.askopenfilename(
            title="기보 불러오기",
            filetypes=[("PGN files", "*.pgn"), ("Text files", "*.txt")]
        )
        if filename:
            from app.utils import PGNManager
            fen, history = PGNManager.load_game(filename)
            
            if fen:
                # GameManager에게 데이터 주입 및 보드 재구성 요청
                self.game_manager.load_and_start(fen, history)
                messagebox.showinfo("완료", "기보를 성공적으로 불러왔습니다.")
                # UI 갱신을 messagebox 이후에 호출하여 제대로 표시되도록 함
                self.refresh_ui()
            else:
                messagebox.showerror("오류", "유효한 기보 파일이 아닙니다.")
    
    def _open_new_game_dialog(self):
        from app.ui.dialogs import NewGameDialog
        # GameManager 객체를 전달
        NewGameDialog(self.root, self.game_manager)