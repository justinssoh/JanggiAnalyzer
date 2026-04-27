import config

class JanggiBoardModel:
    def __init__(self):
        """
        장기판 데이터 모델 초기화.
        내부에 10행 9열의 2차원 리스트를 가집니다.
        """
        # grid[row][col] 형태로 기물 문자를 저장합니다.
        # '.' 은 빈 칸을 의미합니다.
        self.grid = [['.' for _ in range(config.COLS)] for _ in range(config.ROWS)]
        
        # 기물 점수 합계나 잡힌 기물 목록 등을 추가로 관리할 수 있습니다.
        self.captured_pieces = {"w": [], "b": []}
        
        # 최초 생성 시 초기 배치(Reset)를 실행합니다.
        self.reset()

    def reset(self):
        """
        장기판의 모든 데이터를 초기 상태(config.INITIAL_FEN)로 되돌립니다.
        GameManager에서 리셋 명령을 내릴 때 호출됩니다.
        """
        # 1. 모든 칸을 빈 칸으로 초기화
        for r in range(config.ROWS):
            for c in range(config.COLS):
                self.grid[r][c] = '.'
        
        # 2. 잡힌 기물 목록 초기화
        self.captured_pieces = {"w": [], "b": []}
        
        # 3. FEN 문자열을 해석하여 기물 배치
        self._parse_fen(config.INITIAL_FEN)
        
        print(f"BoardModel: 데이터가 '{config.INITIAL_FEN}' 기준으로 리셋되었습니다.")

    def _parse_fen(self, fen):
        """
        FEN(Forsyth-Edwards Notation) 문자열을 읽어 grid 배열에 채웁니다.
        예: 'rbna1abnr/4k4/...' -> [['r','b','n',...], ...]
        """
        try:
            # FEN의 첫 번째 부분(기물 배치 정보)만 추출
            ranks = fen.split(' ')[0].split('/')
            
            for r, rank_str in enumerate(ranks):
                c = 0
                i = 0
                while i < len(rank_str):
                    char = rank_str[i]
                    if char.isdigit():
                        # 연속된 숫자를 하나의 숫자로 처리
                        num_str = ''
                        while i < len(rank_str) and rank_str[i].isdigit():
                            num_str += rank_str[i]
                            i += 1
                        num = int(num_str)
                        c += num
                        continue
                    else:
                        # 문자라면 해당 위치에 기물을 배치합니다.
                        if c < config.COLS:
                            self.grid[r][c] = char
                        c += 1
                        i += 1
        except Exception as e:
            print(f"BoardModel Error (FEN Parsing): {e}")

    def get_piece(self, row, col):
        """특정 위치의 기물을 반환합니다."""
        if 0 <= row < config.ROWS and 0 <= col < config.COLS:
            return self.grid[row][col]
        return None

    def set_piece(self, row, col, piece_char):
        """특정 위치에 기물을 놓습니다."""
        if 0 <= row < config.ROWS and 0 <= col < config.COLS:
            self.grid[row][col] = piece_char

    def move_piece(self, r1, c1, r2, c2):
        """
        기물을 (r1, c1)에서 (r2, c2)로 이동시킵니다.
        이동 경로에 기물이 있었다면 잡힌 기물로 처리할 수 있습니다.
        """
        moving_piece = self.grid[r1][c1]
        target_piece = self.grid[r2][c2]
        
        # 잡힌 기물 처리 (빈 칸이 아닐 경우)
        if target_piece != '.':
            side = "b" if target_piece.islower() else "w"
            self.captured_pieces[side].append(target_piece)
            
        # 이동 실행
        self.grid[r2][c2] = moving_piece
        self.grid[r1][c1] = '.'

    def undo_move_piece(self, r1, c1, r2, c2, captured_piece=None):
        """
        이동을 취소합니다.
        :param r1, c1: 원래 위치
        :param r2, c2: 이동한 위치
        :param captured_piece: 잡힌 기물 (있으면 복원)
        """
        moving_piece = self.grid[r2][c2]
        
        # 기물을 원래 위치로 돌림
        self.grid[r1][c1] = moving_piece
        self.grid[r2][c2] = captured_piece if captured_piece else '.'
        
        # 잡힌 기물 복원
        if captured_piece and captured_piece != '.':
            side = "b" if captured_piece.islower() else "w"
            self.captured_pieces[side].append(captured_piece)

    def move_piece_uci(self, uci_move):
        """
        UCI 형식의 이동(e10e9)을 받아 기물을 이동시킵니다.
        :param uci_move: UCI 형식의 이동 문자열 (예: 'e10e9')
        """
        from app.utils import CoordMapper
        
        # UCI를 좌표로 변환
        parsed = CoordMapper.parse_uci(uci_move)
        if not parsed:
            print(f"Invalid UCI move: {uci_move}")
            return False
            
        f1, r1, f2, r2 = parsed
        # 파일(a-i)을 열(0-8)로 변환
        c1 = ord(f1) - ord('a')
        c2 = ord(f2) - ord('a')
        # 랭크(1-10)를 행(9-0)으로 변환 (장기판은 위에서 아래로 9~0)
        row1 = 10 - r1
        row2 = 10 - r2
        
        # 이동 실행
        self.move_piece(row1, c1, row2, c2)
        return True

    def generate_fen(self):
        """
        현재 grid 상태를 다시 FEN 문자열로 변환합니다.
        (엔진에게 현재 상황을 전달할 때 사용됩니다.)
        """
        fen_rows = []
        for r in range(config.ROWS):
            empty_count = 0
            row_str = ""
            for c in range(config.COLS):
                char = self.grid[r][c]
                if char == '.':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += char
            if empty_count > 0:
                row_str += str(empty_count)
            fen_rows.append(row_str)
        
        return "/".join(fen_rows)