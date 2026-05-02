import config
import datetime
import re

class CoordMapper:
    """
    장기판의 좌표 변환을 전담하는 유틸리티 클래스
    1. 배열 인덱스 (row, col): 0~9, 0~8
    2. 엔진 UCI (f10e9): a~i, 1~10
    3. 화면 픽셀 (x, y): Canvas 상의 위치
    """

    @staticmethod
    def parse_uci(uci_str):
        """
        'a10c9' 또는 'a4b5'에서 (f1, r1, f2, r2)를 안전하게 분리
        결과 예: ('a', 10, 'c', 9)
        """
        # [a-i] 문자 하나와 [0-9]+ 숫자 한뭉치를 번갈아 찾음
        parts = re.findall(r'([a-i])([0-9]+)', uci_str)
        
        # parts 결과 예: [('a', '10'), ('c', '9')]
        if len(parts) == 2:
            f1, r1 = parts[0][0], int(parts[0][1])
            f2, r2 = parts[1][0], int(parts[1][1])
            return f1, r1, f2, r2
        return None

    @staticmethod
    def uci_to_pgn(uci_move):
        """ 엔진(1~10) -> 기보(0~9) 보정 (a10c9 -> a9c8) """
        parsed = CoordMapper.parse_uci(uci_move)
        if not parsed: return uci_move
        
        f1, r1, f2, r2 = parsed
        # 랭크 값에서만 1을 뺌
        return f"{f1}{r1-1}{f2}{r2-1}"

    @staticmethod
    def pgn_to_uci(pgn_move):
        """ 기보(0~9) -> 엔진(1~10) 보정 (a4b5 -> a5b6) """
        parsed = CoordMapper.parse_uci(pgn_move)
        if not parsed: return pgn_move
        
        f1, r1, f2, r2 = parsed
        # 랭크 값에 1을 더함
        return f"{f1}{r1+1}{f2}{r2+1}"

    @staticmethod
    def canvas_to_grid(x, y):
        """
        사용자가 클릭한 캔버스 픽셀 좌표를 배열 인덱스(row, col)로 변환합니다.
        """
        # (클릭좌표 - 여백) / 칸크기 -> 반올림하여 인덱스 산출
        col = round((x - config.OFFSET) / config.CELL_SIZE)
        row = round((y - config.OFFSET) / config.CELL_SIZE)

        # 판 범위를 벗어나는지 체크
        if 0 <= row < config.ROWS and 0 <= col < config.COLS:
            return row, col
        return None

    @staticmethod
    def grid_to_canvas(row, col):
        """
        배열 인덱스(row, col)를 화면에 그릴 픽셀 좌표(x, y)로 변환합니다.
        """
        x = config.OFFSET + (col * config.CELL_SIZE)
        y = config.OFFSET + (row * config.CELL_SIZE)
        return x, y

    @staticmethod
    def grid_to_uci(r1, c1, r2, c2):
        """
        배열 인덱스 이동을 엔진용 UCI 문자열로 변환합니다.
        예: (0, 4, 1, 4) -> "e10e9"
        """
        # 열(col): 0~8 -> a~i
        f1 = chr(ord('a') + c1)
        f2 = chr(ord('a') + c2)
        
        # 행(row): 0~9 -> 10~1 (장기는 아래쪽이 1, 위쪽이 10)
        y1 = 10 - r1
        y2 = 10 - r2
        
        return f"{f1}{y1}{f2}{y2}"

    @staticmethod
    def uci_to_grid(uci_str):
        """
        엔진의 UCI 문자열(e10e9)을 배열 인덱스 (r1, c1, r2, c2)로 변환
        """
        import re
        # 숫자와 문자를 분리 (예: e, 10, e, 9)
        parts = re.findall(r'[a-i]|[0-9]+', uci_str)
        if len(parts) < 4:
            return None

        try:
            c1 = ord(parts[0]) - ord('a')
            r1 = 10 - int(parts[1])
            c2 = ord(parts[2]) - ord('a')
            r2 = 10 - int(parts[3])
            return r1, c1, r2, c2
        except (ValueError, IndexError):
            return None

    @staticmethod
    def get_piece_color(piece_char):
        """
        기물 문자를 보고 초(Blue/Upper)인지 한(Red/Lower)인지 판별
        """
        if piece_char == '.':
            return None
        return "blue" if piece_char.isupper() else "red"


class FENConverter:
    """FEN 문자열과 보드 배열(Grid) 간의 상호 변환을 전담"""

    @staticmethod
    def fen_to_grid(fen_str):
        """
        FEN 문자열을 받아 10x9 2차원 배열로 변환합니다.
        예: "rnbakabnr/9/..." -> [['r','n','b',...], [...]]
        """
        grid = [['.' for _ in range(9)] for _ in range(10)]
        # FEN의 배치 부분만 추출 (첫 번째 공백 이전)
        position_part = fen_str.split(' ')[0]
        rows = position_part.split('/')

        for r, row_str in enumerate(rows):
            c = 0
            for char in row_str:
                if char.isdigit(): # 숫자면 그만큼 빈칸 건너뛰기
                    c += int(char)
                else: # 기물 문자면 배열에 채우기
                    grid[r][c] = char
                    c += 1
        return grid

    @staticmethod
    def grid_to_fen(grid, current_turn='w'):
        """
        10x9 배열을 받아 FEN 문자열로 변환합니다.
        """
        fen_rows = []
        for r in range(10):
            empty_cnt = 0
            row_str = ""
            for c in range(9):
                char = grid[r][c]
                if char == '.':
                    empty_cnt += 1
                else:
                    if empty_cnt > 0:
                        row_str += str(empty_cnt)
                        empty_cnt = 0
                    row_str += char
            if empty_cnt > 0:
                row_str += str(empty_cnt)
            fen_rows.append(row_str)
            
        # 장기 표준 형식: [배치] [차례] [기타] [수수]
        return f"{'/'.join(fen_rows)} {current_turn} - - 0 1"


class PGNManager:
    """기보 파일 관리 전담 (저장 ↔ 읽기)"""

    @staticmethod
    def uci_to_display(uci_str):
        """
        엔진용 UCI(e10e9)를 기보창 표시용(e9e8)으로 변환합니다.
        (엔진의 10~1 좌표를 화면 좌표인 9~0으로 -1씩 보정)
        """
        if uci_str == "@@@@": return "@@@@" # 한수쉼 표시
        
        # 정규식으로 문자와 숫자 분리
        parts = re.findall(r'[a-i]|[0-9]+', uci_str)
        if len(parts) < 4: return uci_str

        try:
            f1, y1, f2, y2 = parts[0], int(parts[1]), parts[2], int(parts[3])
            # 엔진 좌표(10~1)를 화면 좌표(9~0)로 변환
            return f"{f1}{y1-1}{f2}{y2-1}"
        except:
            return uci_str

    @staticmethod
    def get_header(initial_fen):
        """초기 FEN을 포함한 PGN 헤더 생성"""
        now = datetime.datetime.now().strftime("%Y.%m.%d")
        return f'[Event "Janggi Analysis"]\n[Date "{now}"]\n[FEN "{initial_fen}"]\n\n'

    @staticmethod
    def format_moves(initial_fen, move_history):
        """
        기보창에 뿌려줄 전체 텍스트를 생성합니다.
        [FEN ...] 헤더 + 변환된 수순들
        """
        header = PGNManager.get_header(initial_fen)
        res = ""
        
        for i in range(0, len(move_history), 2):
            full_move_num = (i // 2) + 1
            
            # 첫 번째 수 (초)
            m1 = move_history[i]
            
            # 두 번째 수 (한) - 있을 때만 추가
            m2 = ""
            if i + 1 < len(move_history):
                m2 = move_history[i+1]
            
            res += f"{full_move_num}. {m1} {m2} "
            
        return header + res.strip()
    
    @staticmethod
    def save_game(filename, initial_fen, history):
        """현재 대국 상태를 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f'[FEN "{initial_fen}"]\n')
                f.write(f'[Moves]\n')
                # 기보를 한 줄에 2수씩 저장하거나 리스트 형태로 저장
                for i in range(0, len(history), 2):
                    m1 = history[i]
                    m2 = history[i+1] if i+1 < len(history) else ""
                    f.write(f"{m1} {m2} ".strip() + " ")
            return True
        except Exception as e:
            print(f"저장 실패: {e}")
            return False

    @staticmethod
    def load_game(filename):
        """파일에서 FEN과 move_history를 추출"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                # PGNParser를 사용하여 파싱
                fen, history = PGNParser.parse(content)
                return fen, history
        except Exception as e:
            print(f"불러오기 실패: {e}")
            return None, []


class PGNParser:
    @staticmethod
    def parse(content):
        # 1. FEN 헤더 추출: [FEN "rnb..."]
        fen_match = re.search(r'\[FEN "(.*?)"\]', content)
        initial_fen = fen_match.group(1) if fen_match else None
        
        # 2. 모든 헤더([Key "Value"]) 제거 및 주석 제거
        # 헤더 제거
        clean_content = re.sub(r'\[.*?\]', '', content)
        # { ... } 형태의 주석 제거
        clean_content = re.sub(r'\{.*?\}', '', clean_content)
        # 1. 2. 같은 숫자와 마침표 제거
        clean_content = re.sub(r'\d+\.', '', clean_content)
        
        # 3. 순수 이동 경로(@@@@ 또는 e9e8 형태)만 추출
        # 장기 좌표(a-i + 0-9) 4글자 또는 @@@@ 패턴
        move_pattern = r'[a-i]\d[a-i]\d|@@@@'
        moves = re.findall(move_pattern, clean_content)
        
        return initial_fen, moves


class FENSetter:
    """장기 초기 상차림(Formation)을 설정하고 FEN을 조립하는 클래스"""
    
    FORMATIONS = {
        'han': {
            '상마상마': 'rbna1abnr', '마상마상': 'rnba1anbr',
            '상마마상': 'rbna1anbr', '마상상마': 'rnba1abnr'
        },
        'cho': {
            '상마상마': 'RBNA1ABNR', '마상마상': 'RNBA1ANBR',
            '상마마상': 'RBNA1ANBR', '마상상마': 'RNBA1ABNR'
        }
    }

    @staticmethod
    def flip_fen(fen):
        """
        FEN의 보드 방향을 상하 반전합니다.
        한이 아래쪽인 FEN → 엔진 표준 방향(한 위, 초 아래)으로 변환할 때 사용.
        """
        parts = fen.split()
        ranks = parts[0].split('/')
        # rank 순서만 역전 (대소문자 유지)
        flipped = '/'.join(ranks[::-1])
        # 턴은 그대로 유지 (선수는 항상 초)
        return f"{flipped} {parts[1]} {' '.join(parts[2:])}"

    @staticmethod
    def flip_uci_move(uci_move):
        if uci_move in ('@@@@', '0000'):
            return uci_move
        parsed = CoordMapper.parse_uci(uci_move)
        if not parsed:
            return uci_move
        f1, r1, f2, r2 = parsed
        return f"{f1}{11 - r1}{f2}{11 - r2}"

    @staticmethod
    def get_initial_fen(han_key, cho_key, start_player='w'):
        """선택된 차림 키워드를 조합하여 표준 FEN 문자열 생성"""
        han = FENSetter.FORMATIONS['han'].get(han_key, 'rbna1abnr')
        cho = FENSetter.FORMATIONS['cho'].get(cho_key, 'RBNA1ABNR')
        
        # 장기판 중앙 고정 레이아웃 (궁, 포, 졸)
        mid = "4k4/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/4K4"
        
        # FEN은 위(rank 10)부터 아래(rank 1)로 기술되므로 cho(위) / mid / han(아래) 순서
        return f"{cho}/{mid}/{han} {start_player} - - 0 1"

    @staticmethod
    def get_initial_fen_cho_player(han_key, cho_key):
        """초나라 플레이어 관점 - 초가 아래쪽에 보임 (선수는 항상 초)"""
        han = FENSetter.FORMATIONS['han'].get(han_key, 'rbna1abnr')
        cho = FENSetter.FORMATIONS['cho'].get(cho_key, 'RBNA1ABNR')
        
        # 장기판 중앙 고정 레이아웃 (궁, 포, 졸)
        # mid = "4k4/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/4K4"
        mid = "4K4/1C5C1/P1P1P1P1P/9/9/p1p1p1p1p/1c5c1/4k4"
        
        # 초가 아래에 보이는 배치: cho / mid / han
        return f"{cho}/{mid}/{han} w - - 0 1"

    @staticmethod
    def get_initial_fen_han_view(han_key, cho_key):
        """한나라 플레이어 관점 - 한이 아래쪽에 보임 (선수는 항상 초)"""
        han = FENSetter.FORMATIONS['han'].get(han_key, 'rbna1abnr')
        cho = FENSetter.FORMATIONS['cho'].get(cho_key, 'RBNA1ABNR')
        
        # 장기판 중앙 고정 레이아웃 (궁, 포, 졸)
        mid = "4k4/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/4K4"
        # mid = "4K4/1C5C1/P1P1P1P1P/9/9/p1p1p1p1p/1c5c1/4k4"

        # 한이 아래에 보이는 배치: han / mid / cho (뒤집음)
        return f"{han}/{mid}/{cho} w - - 0 1"