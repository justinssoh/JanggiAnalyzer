import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from app.board import JanggiBoardModel
from app.utils import FENSetter, CoordMapper, PGNManager
import pprint as pp


def run(name, result, expected=None):
    """테스트 결과 출력 헬퍼"""
    if expected is not None:
        ok = result == expected
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"{status} | {name}")
        if not ok:
            print(f"       기대값: {expected}")
            print(f"       실제값: {result}")
    else:
        print(f"\n[{name}]")
        pp.pprint(result)


# -----------------------------------------------------------------------
# 1. 기본 FEN 파싱
# -----------------------------------------------------------------------
model = JanggiBoardModel()
run("기본 FEN - row0 (한 차/상/마/사)", model.grid[0],
    ['r', 'b', 'n', 'a', '.', 'a', 'b', 'n', 'r'])
run("기본 FEN - row1 한 궁 위치",       model.grid[1][4], 'k')
run("기본 FEN - row8 초 궁 위치",       model.grid[8][4], 'K')
run("기본 FEN - row9 (초 차/상/마/사)", model.grid[9],
    ['R', 'B', 'N', 'A', '.', 'A', 'B', 'N', 'R'])

# -----------------------------------------------------------------------
# 2. 한이 아래쪽 FEN 파싱
# -----------------------------------------------------------------------
model2 = JanggiBoardModel()
han_below = FENSetter.get_initial_fen_cho_player('상마상마', '상마상마')
model2._parse_fen(han_below)
run("한 아래 FEN - row0 초 차/상/마/사", model2.grid[0][0], 'R')
run("한 아래 FEN - row1 초 궁 위치",     model2.grid[1][4], 'K')
run("한 아래 FEN - row8 한 궁 위치",     model2.grid[8][4], 'k')
run("한 아래 FEN - row9 한 차/상/마/사", model2.grid[9][0], 'r')

# -----------------------------------------------------------------------
# 3. FEN 뒤집기
# -----------------------------------------------------------------------
flipped = FENSetter.flip_fen(han_below)
run("flip_fen - 표준 FEN과 일치",
    flipped.split()[0], config.INITIAL_FEN.split()[0])
run("flip_fen - 두 번 뒤집으면 원본 복원",
    FENSetter.flip_fen(flipped).split()[0], han_below.split()[0])

# -----------------------------------------------------------------------
# 4. UCI 수순 뒤집기
# -----------------------------------------------------------------------
for move in ['e10e9', 'e1e2', 'a4b4', 'i7h7', '@@@@']:
    back = FENSetter.flip_uci_move(FENSetter.flip_uci_move(move))
    run(f"flip_uci_move 역변환 - {move}", back, move)

# -----------------------------------------------------------------------
# 5. UCI <-> display 변환
# -----------------------------------------------------------------------
for uci in ['e10e9', 'a4b4', 'i1i2']:
    display = PGNManager.uci_to_display(uci)
    restored = CoordMapper.pgn_to_uci(display)
    run(f"UCI->display->UCI - {uci}", restored, uci)

# -----------------------------------------------------------------------
# 6. 기물 이동
# -----------------------------------------------------------------------
model3 = JanggiBoardModel()
model3.move_piece(8, 4, 7, 4)   # 초 궁 이동
run("move_piece - 출발지 빈칸", model3.grid[8][4], '.')
run("move_piece - 도착지 기물", model3.grid[7][4], 'K')

# -----------------------------------------------------------------------
# 7. 보드 출력 (눈으로 확인)
# -----------------------------------------------------------------------
col_header = "     a    b    c    d    e    f    g    h    i"

print("\n" + "=" * 55)
print("  [표준 배열 - 한 위, 초 아래]")
print("=" * 55)
print(col_header)
for i, row in enumerate(model.grid):
    rank = 10 - i
    print(f"{rank:2}  {'  '.join(f'{p:2}' for p in row)}")

print("\n" + "=" * 55)
print("  [뒤집힌 배열 - 초 위, 한 아래]")
print("=" * 55)
print(col_header)
for i, row in enumerate(model2.grid):
    rank = 10 - i
    print(f"{rank:2}  {'  '.join(f'{p:2}' for p in row)}")
