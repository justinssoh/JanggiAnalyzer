import tkinter as tk
import config
from app.utils import CoordMapper

class JanggiCanvas(tk.Canvas):
    def __init__(self, master, model, manager):
        """
        장기판을 그리는 캔버스 클래스.
        :param master: 부모 위젯 (Frame)
        :param model: JanggiBoardModel 객체
        :param manager: GameManager 객체
        """
        # 캔버스 크기 계산 (10행 9열 + 여백)
        c_width = (config.COLS - 1) * config.CELL_SIZE + (config.OFFSET * 2)
        c_height = (config.ROWS - 1) * config.CELL_SIZE + (config.OFFSET * 2)
        
        super().__init__(
            master, 
            width=c_width, 
            height=c_height, 
            bg=config.BOARD_COLOR, 
            highlightthickness=0
        )
        
        self.model = model
        self.manager = manager

        # 마우스 클릭 이벤트 바인딩
        self.bind("<Button-1>", self._on_click)
        
        # 최초 1회 그리기
        self.draw_all(full_redraw=True)

    def draw_all(self, full_redraw=False):
        """캔버스를 깨끗이 지우고 모든 요소를 다시 그립니다."""
        # 잔상 방지를 위해 각 태그별로 삭제하고 다시 그리기
        self.delete("grid")
        self.delete("palace") 
        self.delete("markers")
        self.delete("pieces")
        self.delete("selection")
        
        self._draw_grid()           # 1. 격자선
        self._draw_palace()         # 2. 궁성 대각선
        self._draw_markers()        # 3. 포/졸 자리 마커
        self._draw_selection()      # 4. 선택된 칸 강조
        self._draw_pieces()         # 5. 기물 배치

    def _draw_grid(self):
        """가로 10줄, 세로 9줄의 격자를 그립니다."""
        # 가로줄 (Rows)
        for r in range(config.ROWS):
            x1, y1 = CoordMapper.grid_to_canvas(r, 0)
            x2, y2 = CoordMapper.grid_to_canvas(r, config.COLS - 1)
            self.create_line(x1, y1, x2, y2, fill=config.LINE_COLOR, tags="grid")
            
        # 세로줄 (Cols)
        for c in range(config.COLS):
            x1, y1 = CoordMapper.grid_to_canvas(0, c)
            x2, y2 = CoordMapper.grid_to_canvas(config.ROWS - 1, c)
            self.create_line(x1, y1, x2, y2, fill=config.LINE_COLOR, tags="grid")
    def _draw_palace(self):
        """궁성(9개의 칸)에 대각선을 그립니다."""
        palaces = [
            ((0, 3), (2, 5)), ((0, 5), (2, 3)),  # 한나라 궁성
            ((7, 3), (9, 5)), ((7, 5), (9, 3))   # 초나라 궁성
        ]
        for (r1, c1), (r2, c2) in palaces:
            x1, y1 = CoordMapper.grid_to_canvas(r1, c1)
            x2, y2 = CoordMapper.grid_to_canvas(r2, c2)
            self.create_line(x1, y1, x2, y2, fill=config.LINE_COLOR, tags="palace")

    def _draw_markers(self):
        """포(包)와 졸(卒/兵)이 놓이는 위치에 X 마커를 그립니다."""
        marker_pos = [
            (2, 1), (2, 7), (7, 1), (7, 7), # 포 자리
            (3, 0), (3, 2), (3, 4), (3, 6), (3, 8), # 졸/병 자리
            (6, 0), (6, 2), (6, 4), (6, 6), (6, 8)
        ]
        s = 5 # 마커 크기
        for r, c in marker_pos:
            x, y = CoordMapper.grid_to_canvas(r, c)
            self.create_line(x-s, y-s, x+s, y+s, fill=config.LINE_COLOR, tags="markers")
            self.create_line(x+s, y-s, x-s, y+s, fill=config.LINE_COLOR, tags="markers")

    def _draw_pieces(self):
        """모델의 grid 데이터를 읽어 기물을 렌더링합니다."""
        for r in range(config.ROWS):
            for c in range(config.COLS):
                piece_char = self.model.grid[r][c]
                if piece_char == '.':
                    continue
                
                # config에서 기물 정보 가져오기
                p_data = config.PIECE_DATA.get(piece_char, {})
                x, y = CoordMapper.grid_to_canvas(r, c)
                
                # 기물 크기 (왕은 조금 더 크게)
                radius = 26 if piece_char.lower() == 'k' else 22
                if piece_char.lower() in 'pa': radius = 18
                color = config.COLOR_HAN if piece_char.islower() else config.COLOR_CHO
                
                # 기물 배경 원형
                self.create_oval(
                    x-radius, y-radius, x+radius, y+radius, 
                    fill="white", outline=color, width=2,
                    tags="pieces"
                )
                # 기물 이름(한자)
                self.create_text(
                    x, y, 
                    text=p_data.get('name', ''), 
                    fill=color, 
                    font=("Malgun Gothic", 16, "bold"),
                    tags="pieces"
                )
    
    def _draw_selection(self):
        """사용자가 선택한 기물이 있다면 강조 표시를 합니다."""
        if self.manager.selected_pos:
            r, c = self.manager.selected_pos
            x, y = CoordMapper.grid_to_canvas(r, c)
            offset = config.CELL_SIZE // 2
            self.create_rectangle(
                x-offset, y-offset, x+offset, y+offset, 
                outline=config.HIGHLIGHT_COLOR, width=4,
                tags="selection"
            )

    def _on_click(self, event):
        """클릭 좌표를 계산하여 매니저에게 전달합니다."""
        grid_pos = CoordMapper.canvas_to_grid(event.x, event.y)
        if grid_pos:
            r, c = grid_pos
            # 사령부(GameManager)에게 클릭 보고
            self.manager.handle_board_click(r, c)

    def refresh(self):
        """외부에서 호출할 수 있는 화면 갱신 메서드"""
        self.draw_all()