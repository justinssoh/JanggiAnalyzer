"""
엔진 연결 및 명령어 실험 유틸리티
====================================
엔진에 직접 명령을 보내고 결과를 확인합니다.

실행 방법:
    python3 tests/test_engine_manual.py
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from app.engine import JanggiEngine


def run(label, fen, moves=[], movetime=500):
    """FEN과 수순을 받아 엔진 분석 결과를 출력합니다."""
    print(f'\n[{label}]')
    print(f'  FEN:   {fen}')
    if moves:
        print(f'  moves: {" ".join(moves)}')

    results = []
    def cb(data, is_info=False):
        if is_info:
            if ' pv ' in data:
                import re
                score_m = re.search(r'score (cp|mate) (-?\d+)', data)
                depth_m = re.search(r'depth (\d+)', data)
                pv = data.split(' pv ')[1].split()[0]
                score = f'{score_m.group(1)} {score_m.group(2)}' if score_m else '?'
                depth = depth_m.group(1) if depth_m else '?'
                print(f'  depth {depth:>2} | score {score:>8} | pv {pv}')
        else:
            results.append(data)
            print(f'  >>> bestmove: {data}')

    engine.analyze_position(fen, moves, cb)

    # 결과 대기
    deadline = time.time() + movetime / 1000 + 1.0
    while time.time() < deadline:
        time.sleep(0.1)
        engine.poll_results()
        if results:
            break


def legal_moves(label, fen):
    """현재 FEN의 합법적인 수 목록을 출력합니다."""
    print(f'\n[{label}]')
    print(f'  FEN: {fen}')
    engine._send(f'position fen {fen}')
    engine._send('go perft 1')
    import re
    moves = []
    while True:
        line = engine.process.stdout.readline().strip()
        if not line:
            continue
        if line.startswith('Nodes searched'):
            break
        m = re.match(r'^([a-i]\d+[a-i]\d+):\s*\d+$', line)
        if m:
            moves.append(m.group(1))
    print(f'  합법적인 수 ({len(moves)}개): {sorted(moves)}')


# -----------------------------------------------------------------------
# 엔진 시작
# -----------------------------------------------------------------------
print(f'엔진 경로: {config.ENGINE_PATH}')
print(f'UCI_VARIANT: {config.UCI_VARIANT}')
engine = JanggiEngine()

if not engine.is_ready:
    print('엔진 연결 실패')
    sys.exit(1)

# -----------------------------------------------------------------------
# 실험 1: 초기 포지션 분석
# -----------------------------------------------------------------------
run('초기 포지션 - 초 선수', config.DEFAULT_FEN, movetime=config.MOVETIME)

# -----------------------------------------------------------------------
# 실험 2: 수순 이후 분석
# -----------------------------------------------------------------------
run('2수 후 포지션', config.DEFAULT_FEN,
    moves=['e10e9', 'e1e2'],
    movetime=config.MOVETIME)

# -----------------------------------------------------------------------
# 실험 3: 한수쉼(0000) 포함 수순
# -----------------------------------------------------------------------
run('한수쉼 포함', config.DEFAULT_FEN,
    moves=['a4b4', '0000'],
    movetime=config.MOVETIME)

# -----------------------------------------------------------------------
# 실험 4: legal moves
# -----------------------------------------------------------------------
legal_moves('초기 포지션 합법적인 수', config.DEFAULT_FEN)

# -----------------------------------------------------------------------
# 실험 5: 뒤집힌 포진 (초가 위쪽)
# -----------------------------------------------------------------------
from app.utils import FENSetter
flipped_fen = FENSetter.get_initial_fen_cho_player('상마상마', '상마상마')
run('초가 위쪽 포진', flipped_fen, movetime=config.MOVETIME)

# -----------------------------------------------------------------------
# 종료
# -----------------------------------------------------------------------
engine.quit_engine()
print('\n완료')
