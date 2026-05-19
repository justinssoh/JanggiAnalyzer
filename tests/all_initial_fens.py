"""
32가지 장기 초기 배열 FEN 생성 유틸리티
=========================================
초나라 상차림 4가지 × 한나라 상차림 4가지 × 방향 2가지 = 32가지

실행 방법:
    python3 tests/all_initial_fens.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import FENSetter

FORMATIONS = ['상마상마', '마상마상', '상마마상', '마상상마']


def generate_all_fens():
    """32가지 초기 FEN을 딕셔너리로 반환합니다."""
    fens = {}
    for cho in FORMATIONS:
        for han in FORMATIONS:
            # 초가 아래쪽 (사용자=초)
            key = f'초↓ | 초:{cho} 한:{han}'
            fens[key] = FENSetter.get_initial_fen_cho_player(han, cho)
            # 한이 아래쪽 (사용자=한)
            key = f'한↓ | 초:{cho} 한:{han}'
            fens[key] = FENSetter.get_initial_fen_han_player(han, cho)
    return fens


if __name__ == '__main__':
    fens = generate_all_fens()

    print(f'총 {len(fens)}가지 초기 배열\n')
    print(f'{"번호":>3}  {"구분":<20}  {"FEN"}')
    print('-' * 80)
    for i, (key, fen) in enumerate(fens.items(), 1):
        print(f'{i:>3}. {key:<20}  {fen}')
