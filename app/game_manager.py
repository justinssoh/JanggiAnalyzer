import re
import tkinter as tk
from app.utils import PGNManager, CoordMapper


class GameManager:
    def __init__(self, model, engine, cfg):
        self.model = model
        self.engine = engine
        self.cfg = cfg
        self.ui_refresh_callback = None
        self.initialize_game()

    def initialize_game(self):
        self.model.reset()
        if self.engine:
            self.engine.reset_engine()

        self.move_history = []      # 기보 기록 (표시용)
        self.current_step = 0       # 현재 수순
        self.current_turn = 'w'
        self.is_game_over = False
        self.selected_pos = None
        self.fen_stack = [self.cfg.DEFAULT_FEN]  # FEN 스택: 수순별 FEN 저장

        self.current_mode = 'idle'
        self.engine_process = None
        self.engine_analysis_thread = None
        self.engine_game_thread = None
        self.legal_moves = set()  # 선택된 기물의 합법적 이동 목록

        print('GameManager: 게임이 초기화되었습니다.')

    # ------------------------------------------------------------------
    # 프로퍼티: 현재 FEN
    # ------------------------------------------------------------------
    @property
    def current_fen(self):
        """현재 수순의 FEN을 반환합니다."""
        if self.current_step < len(self.fen_stack):
            return self.fen_stack[self.current_step]
        return self.fen_stack[-1]

    # ------------------------------------------------------------------
    # UI 콜백
    # ------------------------------------------------------------------
    def set_ui_callback(self, callback):
        self.ui_refresh_callback = callback

    def _refresh_ui(self):
        if self.ui_refresh_callback:
            self.ui_refresh_callback()

    # ------------------------------------------------------------------
    # 모드 제어
    # ------------------------------------------------------------------
    def start_analysis_mode(self):
        self.stop_current_mode()
        self.current_mode = 'analysis'
        print('GameManager: 분석 모드 시작')
        self._refresh_ui()
        self._run_analysis_cycle()

    def start_game_mode(self):
        self.stop_current_mode()
        self.current_mode = 'game'
        self.player_side = self._detect_player_side()
        print(f"GameManager: 대국 모드 시작 (플레이어: {'초' if self.player_side == 'w' else '한'})")
        self._refresh_ui()
        if self.current_turn != self.player_side:
            self._engine_move()

    def start_auto_game_mode(self):
        self.stop_current_mode()
        self.current_mode = 'auto_game'
        print('GameManager: 자동 대국 모드 시작')
        self._refresh_ui()
        self._auto_game_step()

    def stop_current_mode(self):
        if self.current_mode != 'idle':
            print(f'GameManager: {self.current_mode} 모드 중단')
            if self.engine:
                self.engine.stop_analysis()
            self.current_mode = 'idle'
            self._refresh_ui()

    def request_reset(self):
        self.stop_current_mode()
        self.initialize_game()
        self._refresh_ui()

    # ------------------------------------------------------------------
    # 플레이어 사이드 판별
    # ------------------------------------------------------------------
    def _detect_player_side(self):
        K_row = k_row = -1
        for r in range(self.cfg.ROWS):
            for c in range(self.cfg.COLS):
                if self.model.grid[r][c] == 'K': K_row = r
                if self.model.grid[r][c] == 'k': k_row = r
        if K_row > k_row: return 'w'
        if k_row > K_row: return 'b'
        return 'w'

    # ------------------------------------------------------------------
    # 엔진 분석
    # ------------------------------------------------------------------
    def _run_analysis_cycle(self):
        if self.current_mode != 'analysis' or not self.engine:
            return
        self.engine.analyze_position(self.current_fen, [], self._on_analysis_result)

    def _on_analysis_result(self, data, is_info=False):
        if self.current_mode != 'analysis':
            return
        if is_info:
            if ' pv ' not in data:
                return
            info_part, pv_part = data.split(' pv ', 1)
            pv = pv_part.split()[0]
            score = ''
            m = re.search(r'score (cp|mate) (-?\d+)', info_part)
            if m:
                score = f'[{m.group(1)} {m.group(2)}]'
            try:
                pv = CoordMapper.uci_to_pgn(pv)
            except:
                pass
            depth_m = re.search(r'depth (\d+)', info_part)
            depth = depth_m.group(1) if depth_m else '?'
            if depth in ('10', '15') and hasattr(self, 'side_panel'):
                self.side_panel.log_analysis(f'depth {depth} {score} pv {pv}')
            return

        best_move = data
        try:
            display = CoordMapper.uci_to_pgn(best_move)
        except:
            display = best_move
        if hasattr(self, 'side_panel'):
            self.side_panel.log_analysis(f'★ Final Best Move: {display} ({best_move})')
            self.side_panel.log_analysis('-' * 30)

    def _engine_move(self):
        if not self.engine or not self.engine.is_ready:
            return
        self.engine.analyze_position(self.current_fen, [], self._on_engine_move_result)

    def _on_engine_move_result(self, data, is_info=False):
        if self.current_mode != 'game' or is_info:
            return
        self._apply_engine_move(data)

    def _auto_game_step(self):
        if self.current_mode != 'auto_game' or not self.engine or not self.engine.is_ready:
            return
        self.engine.analyze_position(self.current_fen, [], self._on_auto_game_result)

    def _on_auto_game_result(self, data, is_info=False):
        if self.current_mode != 'auto_game' or is_info:
            return
        self._apply_engine_move(data)
        self._refresh_ui()
        if hasattr(self, '_root'):
            self._root.after(self.cfg.AUTO_GAME_DELAY, self._auto_game_step)

    def _apply_engine_move(self, best_move):
        """엔진 bestmove를 보드에 적용합니다."""
        parsed = CoordMapper.parse_uci(best_move)
        if not parsed:
            return
        f1, r1, f2, r2 = parsed
        c1, c2 = ord(f1) - ord('a'), ord(f2) - ord('a')
        row1, row2 = 10 - r1, 10 - r2
        self._log_engine_move(best_move)
        self.execute_move(best_move, row1, c1, row2, c2)
        self._refresh_ui()

    def _log_engine_move(self, uci_move):
        if not hasattr(self, 'side_panel'):
            return
        try:
            display = CoordMapper.uci_to_pgn(uci_move)
        except:
            display = uci_move
        turn_label = '초' if self.current_turn == 'w' else '한'
        self.side_panel.log_analysis(f'[{turn_label}] ★ {display}')

    # ------------------------------------------------------------------
    # 수(Move) 처리
    # ------------------------------------------------------------------
    def handle_board_click(self, row, col):
        if self.is_game_over:
            return
        if self.current_mode == 'game' and self.current_turn != self.player_side:
            return

        piece = self.model.grid[row][col]

        if self.selected_pos is None:
            # 기물 선택
            if piece != '.' and self._is_my_turn(piece):
                self.selected_pos = (row, col)
                # 엔진에서 legal moves 가져오기
                if self.engine and self.engine.is_ready:
                    self.legal_moves = self.engine.get_legal_moves(self.current_fen)
                else:
                    self.legal_moves = set()
                self._refresh_ui()
        else:
            prev_row, prev_col = self.selected_pos

            if (prev_row, prev_col) == (row, col):
                # 같은 자리 클릭 → 선택 취소
                self.selected_pos = None
                self.legal_moves = set()
            else:
                move_uci = self._coords_to_uci(prev_row, prev_col, row, col)

                if not self.legal_moves or move_uci in self.legal_moves:
                    # 합법적인 수 → 이동 실행
                    self.execute_move(move_uci, prev_row, prev_col, row, col)
                    if self.current_mode == 'analysis':
                        self._run_analysis_cycle()
                else:
                    # 불법 이동 → 선택 취소
                    print(f'Invalid move: {move_uci}')

                self.selected_pos = None
                self.legal_moves = set()
            self._refresh_ui()

    def execute_move(self, move_uci, r1, c1, r2, c2):
        """기물을 이동하고 FEN 스택과 기보를 업데이트합니다."""
        # 1. 보드 이동
        self.model.move_piece(r1, c1, r2, c2)

        # 2. 복기 중 이동 시 이후 기록 잘라내기
        if self.current_step < len(self.move_history):
            self.move_history = self.move_history[:self.current_step]
            self.fen_stack = self.fen_stack[:self.current_step + 1]

        # 3. 기보 기록
        self.move_history.append(PGNManager.uci_to_display(move_uci))

        # 4. 턴 교체
        next_turn = 'b' if self.current_turn == 'w' else 'w'
        self.current_turn = next_turn

        # 5. FEN 스택에 새 상태 추가
        self.fen_stack.append(self.model.generate_fen(self.current_turn))
        self.current_step = len(self.move_history)

        print(f'GameManager: Move Executed - {move_uci} (Step: {self.current_step})')

        # 6. 대국 모드: 엔진 차례면 자동 실행
        if self.current_mode == 'game' and self.current_turn != self.player_side:
            self._engine_move()

    def pass_turn(self):
        """한수쉼: 턴만 넘깁니다."""
        if self.engine:
            self.engine.stop_analysis()
            try:
                while True:
                    self.engine._result_queue.get_nowait()
            except Exception:
                pass

        self.move_history.append('@@@@')
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'

        # FEN 스택: 보드는 그대로, 턴만 바뀐 FEN 추가
        self.fen_stack.append(self.model.generate_fen(self.current_turn))
        self.current_step = len(self.move_history)

        print(f'Pass Turn: @@@@ | Next Turn: {self.current_turn}')
        self._refresh_ui()

        if self.current_mode == 'analysis':
            if hasattr(self, '_root'):
                self._root.after(200, self._run_analysis_cycle)
        elif self.current_mode == 'game' and self.current_turn != self.player_side:
            if hasattr(self, '_root'):
                self._root.after(200, self._engine_move)

    # ------------------------------------------------------------------
    # 수순 네비게이션
    # ------------------------------------------------------------------
    def go_to_step(self, step):
        if step < 0: step = 0
        if step > len(self.move_history): step = len(self.move_history)

        # FEN 스택에서 해당 수순의 보드 복원
        fen = self.fen_stack[step]
        self.model._parse_fen(fen)
        self.current_turn = fen.split()[1]
        self.current_step = step
        self._refresh_ui()

    def go_to_first(self): self.go_to_step(0)
    def go_to_last(self):  self.go_to_step(len(self.move_history))
    def go_to_next(self):  self.go_to_step(self.current_step + 1)
    def go_to_prev(self):  self.go_to_step(self.current_step - 1)

    def handle_undo(self):
        if self.current_step > 0:
            if self.current_step == len(self.move_history):
                if tk.messagebox.askyesno('무르기', '마지막 수를 무르시겠습니까?'):
                    self.move_history.pop()
                    self.fen_stack.pop()
                    self.current_step -= 1
            else:
                self.current_step -= 1
            self.go_to_step(self.current_step)

    # ------------------------------------------------------------------
    # 새 대국 / PGN 로드
    # ------------------------------------------------------------------
    def request_new_game(self, fen):
        self.initialize_game()
        self.model._parse_fen(fen)
        fen_parts = fen.split()
        self.current_turn = fen_parts[1] if len(fen_parts) > 1 else 'w'
        self.fen_stack = [fen]
        if self.engine:
            self.engine.reset_engine()
        self._refresh_ui()
        print(f'GameManager: 새로운 게임 시작 - FEN: {fen}')

    def load_and_start(self, fen, history):
        if self.engine:
            self.engine.reset_engine()

        self.model.reset()
        self.model._parse_fen(fen)
        self.is_game_over = False
        self.selected_pos = None

        fen_parts = fen.split()
        self.current_turn = fen_parts[1] if len(fen_parts) > 1 else 'w'

        self.move_history = history
        self.fen_stack = [fen]

        # 수순별 FEN 재구성
        for move in history:
            if move != '@@@@':
                uci = CoordMapper.pgn_to_uci(move)
                self.model.move_piece_uci(uci)
            self.current_turn = 'b' if self.current_turn == 'w' else 'w'
            self.fen_stack.append(self.model.generate_fen(self.current_turn))

        self.current_step = len(self.move_history)

        if self.engine:
            self.engine.reset_engine()
        self._refresh_ui()
        print(f'GameManager: PGN 로드 완료 - {len(history)}수')

    # ------------------------------------------------------------------
    # 유틸리티
    # ------------------------------------------------------------------
    def _is_my_turn(self, piece):
        if self.current_turn == 'w' and piece.isupper(): return True
        if self.current_turn == 'b' and piece.islower(): return True
        return False

    def _coords_to_uci(self, r1, c1, r2, c2):
        return f"{chr(ord('a')+c1)}{10-r1}{chr(ord('a')+c2)}{10-r2}"
