import os

# =========================================================================
# [1] 경로 설정 (Path Settings)
# =========================================================================
# 프로젝트의 루트 디렉토리를 기준으로 각 폴더의 절대 경로를 계산합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 엔진 파일이 위치한 폴더
ENGINE_DIR = os.path.join(BASE_DIR, "engine")

# 이미지, 사운드 등 리소스 폴더
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGE_DIR = os.path.join(ASSETS_DIR, "images")
SOUND_DIR = os.path.join(ASSETS_DIR, "sounds")

# 기보 저장 폴더
DATA_DIR = os.path.join(BASE_DIR, "data")

# =========================================================================
# [2] 장기 규칙 및 판 설정 (Game Rules & Board)
# =========================================================================
# 한나라(후수)에게 주어지는 덤 점수
DOM_SCORE = 1.5      

# 장기판 규격 (10행 9열)
ROWS, COLS = 10, 9

# UI 표현을 위한 크기 설정 (픽셀 단위)
CELL_SIZE = 60       # 한 칸의 크기
OFFSET = 30          # 판 가장자리의 여백

# 초기 장기판 배열 (FEN 포맷)
# 'w'는 초(Blue)가 선수임을 의미합니다.
INITIAL_FEN = 'rbna1abnr/4k4/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/4K4/RBNA1ABNR w 0 1'


# =========================================================================
# [3] 통합 기물 데이터 매핑 (PIECE_DATA)
# =========================================================================
# UCI 기호를 키(Key)로 사용합니다. (대문자: 초나라, 소문자: 한나라)
# 이 데이터는 로직(점수)과 UI(이름, 이미지 경로)에서 공통으로 참조합니다.
PIECE_DATA = {
    # --- 초나라 (Cho / Blue) ---
    'K': {'score': 0,  'name': '楚', 'full_name': '궁', 'color': 'blue'},
    'R': {'score': 13, 'name': '車', 'full_name': '차', 'color': 'blue'},
    'C': {'score': 7,  'name': '包', 'full_name': '포', 'color': 'blue'},
    'N': {'score': 5,  'name': '馬', 'full_name': '마', 'color': 'blue'},
    'B': {'score': 3,  'name': '象', 'full_name': '상', 'color': 'blue'},
    'A': {'score': 3,  'name': '士', 'full_name': '사', 'color': 'blue'},
    'P': {'score': 2,  'name': '卒', 'full_name': '졸', 'color': 'blue'},

    # --- 한나라 (Han / Red) ---
    'k': {'score': 0,  'name': '漢', 'full_name': '궁', 'color': 'red'},
    'r': {'score': 13, 'name': '車', 'full_name': '차', 'color': 'red'},
    'c': {'score': 7,  'name': '包', 'full_name': '포', 'color': 'red'},
    'n': {'score': 5,  'name': '馬', 'full_name': '마', 'color': 'red'},
    'b': {'score': 3,  'name': '象', 'full_name': '상', 'color': 'red'},
    'a': {'score': 3,  'name': '士', 'full_name': '사', 'color': 'red'},
    'p': {'score': 2,  'name': '兵', 'full_name': '병', 'color': 'red'}
}


# =========================================================================
# [4] 화면 UI 디자인 설정 (UI Aesthetics)
# =========================================================================
WINDOW_TITLE = "Python Janggi Analyzer v1.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

BOARD_COLOR = "#f2d5a3"       # 장기판 배경 (밝은 나무색)
LINE_COLOR = "#333333"        # 격자선 색상
HIGHLIGHT_COLOR = "#ffeb3b"   # 선택된 칸 강조색 (노란색)

# 기물 텍스트 색상
COLOR_CHO = "#0040ff"         # 진한 파랑
COLOR_HAN = "#cc0000"         # 진한 빨강


# =========================================================================
# [5] 엔진 설정 (Engine Settings)
# =========================================================================
# 운영체제에 따라 확장자를 자동으로 붙여줍니다. (.exe 등)
ENGINE_NAME = "fairy-stockfish-largeboard_x86-64"
if os.name == 'nt': # Windows인 경우
    ENGINE_NAME += ".exe"

ENGINE_PATH = os.path.join(ENGINE_DIR, ENGINE_NAME)

# 엔진 분석 옵션
MOVETIME = 1000      # 수당 엔진 사고 시간 (밀리초)
THREADS = 2          # 엔진 사용 스레드 수
HASH_SIZE = 128      # 엔진 해시 메모리 (MB)
