import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from app.board import JanggiBoardModel
from app.utils import FENSetter, CoordMapper, PGNManager


def test_parse_initial_fen():
    """기본 FEN 파싱 후 기물 배치 확인"""
    model = JanggiBoardModel()
    # 한나라 (소문자) - 위쪽
    assert model.grid[0] == ['r', 'b', 'n', 'a', '.', 'a', 'b', 'n', 'r']
    assert model.grid[1][4] == 'k'   # 한 궁
    assert model.grid[2] == ['.', 'c', '.', '.', '.', '.', '.', 'c', '.']
    # 초나라 (대문자) - 아래쪽
    assert model.grid[9] == ['R', 'B', 'N', 'A', '.', 'A', 'B', 'N', 'R']
    assert model.grid[8][4] == 'K'   # 초 궁
    assert model.grid[7] == ['.', 'C', '.', '.', '.', '.', '.', 'C', '.']


def test_parse_flipped_fen():
    """한이 아래쪽인 FEN 파싱 확인"""
    model = JanggiBoardModel()
    fen = FENSetter.get_initial_fen_cho_player('상마상마', '상마상마')
    model._parse_fen(fen)
    # 초나라 (대문자) - 위쪽
    assert model.grid[0][0] == 'R'
    assert model.grid[1][4] == 'K'   # 초 궁
    # 한나라 (소문자) - 아래쪽
    assert model.grid[9][0] == 'r'
    assert model.grid[8][4] == 'k'   # 한 궁


def test_flip_fen():
    """한이 아래쪽 FEN을 뒤집으면 표준 FEN과 일치해야 함"""
    han_below = FENSetter.get_initial_fen_cho_player('상마상마', '상마상마')
    flipped = FENSetter.flip_fen(han_below)
    assert flipped.split()[0] == config.INITIAL_FEN.split()[0]


def test_flip_fen_double():
    """두 번 뒤집으면 원본과 일치해야 함"""
    fen = FENSetter.get_initial_fen_cho_player('상마상마', '상마상마')
    assert FENSetter.flip_fen(FENSetter.flip_fen(fen)).split()[0] == fen.split()[0]


def test_flip_uci_move():
    """UCI 수순 뒤집기 후 역변환하면 원본과 일치해야 함"""
    for move in ['e10e9', 'e1e2', 'a4b4', 'i7h7']:
        flipped = FENSetter.flip_uci_move(move)
        assert FENSetter.flip_uci_move(flipped) == move


def test_uci_display_roundtrip():
    """UCI -> display -> UCI 변환이 일치해야 함"""
    for uci in ['e10e9', 'a4b4', 'i1i2']:
        display = PGNManager.uci_to_display(uci)
        restored = CoordMapper.pgn_to_uci(display)
        assert restored == uci, f"{uci} -> {display} -> {restored}"


def test_generate_fen():
    """보드 상태를 FEN으로 변환 후 다시 파싱하면 동일해야 함"""
    model = JanggiBoardModel()
    fen = model.generate_fen('w')
    model2 = JanggiBoardModel()
    model2._parse_fen(fen)
    assert model.grid == model2.grid


def test_move_piece():
    """기물 이동 후 출발지는 빈칸, 도착지에 기물이 있어야 함"""
    model = JanggiBoardModel()
    piece = model.grid[8][4]  # 초 궁 K
    model.move_piece(8, 4, 7, 4)
    assert model.grid[8][4] == '.'
    assert model.grid[7][4] == piece
