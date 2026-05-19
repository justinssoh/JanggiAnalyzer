"""
콘솔 장기 게임
==============
터미널에서 장기를 둘 수 있는 프로그램입니다.
엔진과 대국하거나 자동 대국을 관전할 수 있습니다.

실행 방법:
    python3 tests/console_game.py
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from app.board import JanggiBoardModel
from app.engine import JanggiEngine
from app.game_manager import GameManager
from app.utils import CoordMapper, PGNManager


# ------------------------------------------------------------------
# 보드 출력
# ------------------------------------------------------------------
def print_board(model, current_turn, move_history, selected=None, legal=set()):
    """현재 보드 상태를 콘솔에 출력합니다."""
    PIECE_NAMES = {
        'K': '楚', 'R': '車', 'C': '包', 'N': '馬', 'B': '象', 'A': '士', 'P': '卒',
        'k': '漢', 'r': '車', 'c': '包', 'n': '馬', 'b': '象', 'a': '士', 'p': '兵',
    }

    print()
    print('     a    b    c    d    e    f    g    h    i')
    print('  ' + '─' * 46)
    for r in range(config.ROWS):
        rank = 10 - r
        row_str = f'{rank:2}│'
        for c in range(config.COLS):
            piece = model.grid[r][c]
            uci_pos = f'{chr(ord("a")+c)}{rank}'
            # 선택된 기물 강조
            if selected and selected == (r, c):
                cell = f'[{PIECE_NAMES.get(piece, ".")}]'
            # 이동 가능한 위치 표시
            elif any(m.startswith(uci_pos) or m[3:] == uci_pos for m in legal
                     if selected and m.startswith(f'{chr(ord("a")+selected[1])}{10-selected[0]}')):
                cell = f'({PIECE_NAMES.get(piece, ".")})' if piece != '.' else '( )'
            elif piece == '.':
                cell = '  . '
            elif piece.isupper():
                cell = f' \033[34m{PIECE_NAMES[piece]}\033[0m '  # 초 파랑
            else:
                cell = f' \033[31m{PIECE_NAMES[piece]}\033[0m '  # 한 빨강
            row_str += cell + '│'
        print(row_str)
        if r < config.ROWS - 1:
            print('  ' + '┼'.join(['─────'] * config.COLS))
    print('  ' + '─' * 46)

    turn_str = '\033[34m초(Blue)\033[0m' if current_turn == 'w' else '\033[31m한(Red)\033[0m'
    print(f'  현재 턴: {turn_str}  |  {len(move_history)}수')


# ------------------------------------------------------------------
# 메인
# ------------------------------------------------------------------
def main():
    print('=' * 50)
    print('       콘솔 장기 게임')
    print('=' * 50)
    print('1. 사용자(초) vs 엔진(한)')
    print('2. 사용자(한) vs 엔진(초)')
    print('3. 자동 대국 (엔진 vs 엔진)')
    print('4. 두 사람이 대국')
    mode = input('선택 (1-4): ').strip()

    model = JanggiBoardModel()
    engine = JanggiEngine() if mode in ('1', '2', '3') else None
    gm = GameManager(model, engine, config)

    # 포진 선택
    print('\n상차림: 1.상마상마  2.마상마상  3.상마마상  4.마상상마')
    formations = ['상마상마', '마상마상', '상마마상', '마상상마']
    cho_idx = int(input('초 상차림 (1-4): ').strip()) - 1
    han_idx = int(input('한 상차림 (1-4): ').strip()) - 1
    cho_f = formations[cho_idx]
    han_f = formations[han_idx]

    from app.utils import FENSetter
    if mode == '2':
        fen = FENSetter.get_initial_fen_cho_player(han_f, cho_f)  # 한이 아래
    else:
        fen = FENSetter.get_initial_fen_han_player(han_f, cho_f)  # 초가 아래

    gm.request_new_game(fen)

    print('\n입력 형식: e2f3 (이동) | pass (한수쉼) | quit (종료)')
    print('─' * 50)

    while not gm.is_game_over:
        print_board(model, gm.current_turn, gm.move_history)

        is_player_turn = (
            mode == '4' or
            (mode == '1' and gm.current_turn == 'w') or
            (mode == '2' and gm.current_turn == 'b')
        )

        if mode == '3' or not is_player_turn:
            # 엔진 차례
            side = '초' if gm.current_turn == 'w' else '한'
            print(f'  [{side}] 엔진 생각 중...')

            result = []
            def cb(data, is_info=False):
                if not is_info:
                    result.append(data)

            engine.analyze_position(gm.current_fen, [], cb)
            deadline = time.time() + config.MOVETIME / 1000 + 1.5
            while time.time() < deadline:
                time.sleep(0.1)
                engine.poll_results()
                if result:
                    break

            if not result:
                print('  엔진 응답 없음')
                break

            best_move = result[0]
            if best_move == '(none)':
                print(f'  [{side}] 더 이상 둘 수 없습니다 - 외통!')
                break

            parsed = CoordMapper.parse_uci(best_move)
            f1, r1, f2, r2 = parsed
            c1, c2 = ord(f1) - ord('a'), ord(f2) - ord('a')
            row1, row2 = 10 - r1, 10 - r2
            display = PGNManager.uci_to_display(best_move)
            print(f'  [{side}] 최선의 수: {display}')
            gm.execute_move(best_move, row1, c1, row2, c2)

            if mode == '3':
                time.sleep(config.AUTO_GAME_DELAY / 1000)

        else:
            # 사용자 차례
            side = '초' if gm.current_turn == 'w' else '한'
            user_input = input(f'  [{side}] 입력: ').strip().lower()

            if user_input == 'quit':
                print('종료합니다.')
                break
            elif user_input == 'pass':
                gm.pass_turn()
                continue

            # 입력 형식 검증 (e2f3 형태)
            parsed = CoordMapper.parse_uci(user_input)
            if not parsed:
                print('  올바른 형식이 아닙니다. 예: e2f3')
                continue

            # legal move 확인
            if engine:
                legal = engine.get_legal_moves(gm.current_fen)
                if user_input not in legal:
                    print(f'  합법적이지 않은 수입니다. ({user_input})')
                    continue

            f1, r1, f2, r2 = parsed
            c1, c2 = ord(f1) - ord('a'), ord(f2) - ord('a')
            row1, row2 = 10 - r1, 10 - r2
            gm.execute_move(user_input, row1, c1, row2, c2)

        # 승패 확인
        result = gm._check_game_over()
        if result:
            print_board(model, gm.current_turn, gm.move_history)
            print(f'\n  ★ {result[0]} ({result[1]}) ★')
            break

    if engine:
        engine.quit_engine()
    print('\n기보:', ' '.join(gm.move_history))


if __name__ == '__main__':
    main()
