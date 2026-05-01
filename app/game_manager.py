import re
import tkinter as tk
from app.utils import PGNManager

class GameManager:
    def __init__(self, model, engine, cfg):
        """
        심판(Manager) 객체 생성
        :param model: JanggiBoardModel 인스턴스
        :param engine: JanggiEngine 인스턴스
        """
        self.model = model
        self.engine = engine
        self.cfg = cfg
        
        # UI 갱신을 위한 콜백 함수 저장용 (JanggiApp에서 등록 예정)
        self.ui_refresh_callback = None
        
        # 게임 상태 변수들 (인스턴스 변수로 선언)
        self.move_history = []                      # 기보 기록 리스트
        self.current_step = 0                       # 현재 화면에 표시되는 수순 번호
        self.current_turn = "w"                     # 'w'는 초(Blue), 'b'는 한(Red)
        self.current_fen = self.cfg.INITIAL_FEN     # 현재 FEN 문자열
        self.is_game_over = False
        self.selected_pos = None                    # UI에서 선택된 칸 (row, col)
        self.board_states = []                      # 각 수순의 보드 상태 저장
        
        # 게임 상태 초기화
        self.initialize_game()

    def initialize_game(self):
        """
        게임의 모든 상태를 태초의 상태로 초기화합니다.
        (프로그램 시작 시 및 리셋 버튼 클릭 시 호출)
        """
        # 1. 모델 데이터 리셋 (기물 배치 초기화)
        self.model.reset()
        
        # 2. 엔진 상태 리셋 (새 게임 신호 전송)
        if self.engine:
            self.engine.reset_engine()
        
        # 3. 게임 관리 변수 초기화
        self.move_history = []                      # 기보 기록 리스트
        self.current_step = 0                       # 현재 화면에 표시되는 수순 번호
        self.current_turn = "w"                     # 'w'는 초(Blue), 'b'는 한(Red)
        self.current_fen = self.cfg.INITIAL_FEN     # 현재 FEN 문자열
        self.game_initial_fen = self.cfg.INITIAL_FEN  # 이 대국의 시작 FEN
        self.is_game_over = False
        self.selected_pos = None                    # UI에서 선택된 칸 (row, col)
        self.board_states = [self._copy_board()]    # 각 수순의 보드 상태 저장 (초기 상태)
        
        self.current_mode = "idle"
        self.engine_process = None
        self.engine_analysis_thread = None
        self.engine_game_thread = None
        self.is_flipped = False  # 한이 아래쪽이면 True

        print("GameManager: 게임이 초기화되었습니다.")

    def set_ui_callback(self, callback):
        """MainWindow의 화면 갱신 함수를 연결합니다."""
        self.ui_refresh_callback = callback

    # --- UI 버튼과 연결될 메서드들 ---
    def start_analysis_mode(self):
        self.stop_current_mode()
        self.current_mode = "analysis"
        print("GameManager: 분석 모드 시작")
        self._refresh_ui()
        self._run_analysis_cycle()

    def _get_engine_fen_and_moves(self):
        from app.utils import FENSetter
        fen = self.game_initial_fen
        moves = self._get_uci_moves()
        if self.is_flipped:
            fen = FENSetter.flip_fen(fen)
            moves = [FENSetter.flip_uci_move(m) for m in moves]
        return fen, moves

    def _flip_bestmove(self, best_move):
        """is_flipped일 때 엔진의 bestmove를 실제 보드 좌표로 역변환합니다."""
        if not self.is_flipped:
            return best_move
        from app.utils import FENSetter
        return FENSetter.flip_uci_move(best_move)

    def _get_uci_moves(self):
        """move_history(표시용)를 UCI 수순 리스트로 변환합니다."""
        from app.utils import CoordMapper
        result = []
        for m in self.move_history[:self.current_step]:
            if m == '@@@@':
                result.append('@@@@')
            else:
                result.append(CoordMapper.pgn_to_uci(m))
        return result

    def _run_analysis_cycle(self):
        if self.current_mode != "analysis" or not self.engine:
            return
        fen, moves = self._get_engine_fen_and_moves()
        self.engine.analyze_position(fen, moves, self._on_analysis_result)

    def _on_analysis_result(self, data, is_info=False):
        """엔진 분석 결과가 도착했을 때 호출되는 콜백"""
        if self.current_mode != "analysis":
            return

        if is_info:
            # 실시간 분석 정보 (depth, score 등)
            if " pv " in data:
                # PV(Principal Variation)가 포함된 경우만 표시
                parts = data.split(" pv ")
                info_part = parts[0]
                pv_part = parts[1].split()[0] # 첫 번째 수만 추출
                
                # 점수 추출 시도
                score = ""
                score_match = re.search(r"score (cp|mate) (-?\d+)", info_part)
                if score_match:
                    score = f"[{score_match.group(1)} {score_match.group(2)}]"
                
                from app.utils import CoordMapper
                try:
                    display_pv = CoordMapper.uci_to_pgn(pv_part)
                except:
                    display_pv = pv_part
                
                msg = f"Analyzing... {score} Best: {display_pv}"
                if hasattr(self, "side_panel"):
                    # 기존 텍스트를 덮어씌우거나 마지막 줄을 수정하는 기능이 없으므로 일단 로그로 남김
                    # 실시간으로 너무 많이 찍히면 복잡하므로 특정 주기나 depth마다 찍는 것이 좋음
                    if "depth 10" in info_part or "depth 15" in info_part:
                        self.side_panel.log_analysis(msg)
            return

        # 최종 베스트 무브
        best_move = data
        from app.utils import CoordMapper
        try:
            display_move = CoordMapper.uci_to_pgn(best_move)
        except:
            display_move = best_move

        msg = f"★ Final Best Move: {display_move} ({best_move})"
        
        if hasattr(self, "side_panel"):
            self.side_panel.log_analysis(msg)
            self.side_panel.log_analysis("-" * 30)
        
        # 반복 분석을 위해 다시 실행
        # self._run_analysis_cycle()

    def _detect_player_side(self):
        """
        보드에서 궁(초=K, 한=k)의 행 위치를 비교하여 플레이어 사이드를 판별합니다.
        아래쪽(높은 row 번호)에 있는 궁의 진영이 사용자 진영입니다.
        """
        K_row = k_row = -1
        for r in range(self.cfg.ROWS):
            for c in range(self.cfg.COLS):
                if self.model.grid[r][c] == 'K': K_row = r
                if self.model.grid[r][c] == 'k': k_row = r
        # 더 아래쪽(큰 row)에 있는 궁이 사용자
        if K_row > k_row: return 'w'
        if k_row > K_row: return 'b'
        return 'w'

    def _update_is_flipped(self):
        """보드에서 K/k 위치를 보고 is_flipped를 갱신합니다."""
        K_row = k_row = -1
        for r in range(self.cfg.ROWS):
            for c in range(self.cfg.COLS):
                if self.model.grid[r][c] == 'K': K_row = r
                if self.model.grid[r][c] == 'k': k_row = r
        self.is_flipped = (k_row > K_row)

    def start_game_mode(self):
        self.stop_current_mode()
        self.current_mode = "game"
        self.player_side = self._detect_player_side()
        self._update_is_flipped()
        print(f"GameManager: 대국 모드 시작 (플레이어: {'초' if self.player_side == 'w' else '한'}, flipped: {self.is_flipped})")
        self._refresh_ui()
        if self.current_turn != self.player_side:
            self._engine_move()

    def start_auto_game_mode(self):
        self.stop_current_mode()
        self.current_mode = "auto_game"
        self._update_is_flipped()
        print(f"GameManager: 자동 대국 모드 시작 (flipped: {self.is_flipped})")
        self._refresh_ui()
        self._auto_game_step()

    def _log_engine_move(self, uci_move):
        """분석창에 엔진이 선택한 수를 출력합니다."""
        if not hasattr(self, 'side_panel'):
            return
        from app.utils import CoordMapper
        try:
            display = CoordMapper.uci_to_pgn(uci_move)
        except:
            display = uci_move
        turn_label = '초' if self.current_turn == 'w' else '한'
        self.side_panel.log_analysis(f"[{turn_label}] ★ {display}")

    def _auto_game_step(self):
        if self.current_mode != "auto_game" or not self.engine or not self.engine.is_ready:
            return
        fen, moves = self._get_engine_fen_and_moves()
        self.engine.analyze_position(fen, moves, self._on_auto_game_result)

    def _on_auto_game_result(self, data, is_info=False):
        if self.current_mode != "auto_game" or is_info:
            return
        best_move = self._flip_bestmove(data)  # 뒤집힌 경우 역변환
        from app.utils import CoordMapper
        parsed = CoordMapper.parse_uci(best_move)
        if not parsed:
            return
        f1, r1, f2, r2 = parsed
        c1, c2 = ord(f1) - ord('a'), ord(f2) - ord('a')
        row1, row2 = 10 - r1, 10 - r2
        if self.current_mode != "auto_game":
            return
        self._log_engine_move(best_move)
        self.execute_move(best_move, row1, c1, row2, c2)
        self._refresh_ui()
        if hasattr(self, '_root'):
            self._root.after(self.cfg.AUTO_GAME_DELAY, self._auto_game_step)

    def stop_current_mode(self):
        if self.current_mode != "idle":
            print(f"GameManager: {self.current_mode} 모드 중단")
            if self.engine:
                self.engine.stop_analysis()
            self.current_mode = "idle"
            self._refresh_ui()

    def request_reset(self):
        """사용자가 UI에서 리셋을 요청했을 때 호출됩니다."""
        self.stop_current_mode() # 기존 모드 중단
        self.initialize_game()
        self._refresh_ui()

    # ---------------------------------------------------------------------
    # 수(Move) 처리 로직
    # ---------------------------------------------------------------------
    def handle_board_click(self, row, col):
        """
        Canvas에서 마우스 클릭 시 호출되는 핵심 로직.
        """
        if self.is_game_over:
            return
        
        # 대국 모드: 플레이어 턴이 아니면 클릭 무시
        if self.current_mode == "game" and self.current_turn != self.player_side:
            return

        piece = self.model.grid[row][col]

        # 1. 기물 선택 단계
        if self.selected_pos is None:
            if piece != '.' and self._is_my_turn(piece):
                self.selected_pos = (row, col)
                self._refresh_ui()
        
        # 2. 이동 실행 단계
        else:
            prev_row, prev_col = self.selected_pos
            
            # 같은 자리를 클릭하면 선택 취소
            if (prev_row, prev_col) == (row, col):
                self.selected_pos = None
            else:
                # 여기에 장기 규칙 검증(Rule Check) 로직이 들어갈 자리입니다.
                # 예: if self.is_valid_move(prev_row, prev_col, row, col):
                
                # UCI 형식으로 변환 (엔진 통신 및 기보 저장용)
                move_uci = self._coords_to_uci(prev_row, prev_col, row, col)
                
                # 기물 이동 적용
                self.execute_move(move_uci, prev_row, prev_col, row, col)
                
                # 이동 후 분석 모드라면 분석 갱신
                if self.current_mode == "analysis":
                    self._run_analysis_cycle()
            
            self.selected_pos = None
            self._refresh_ui()

    def _copy_board(self):
        """현재 보드 상태를 복사하여 반환"""
        return [row[:] for row in self.model.grid]

    def execute_move(self, move_uci, r1, c1, r2, c2):
        """실제로 기물을 옮기고 다음 상태로 전환합니다."""
        # 1. 모델 데이터 업데이트 (실제 이동 처리)
        self.model.move_piece(r1, c1, r2, c2)
        
        # 2. 기보(Move History) 기록
        # uci_to_display는 e10e9 -> 5958 또는 PGN 형식 등 UI용 문자열로 변환
        from app.utils import PGNManager
        display_move = PGNManager.uci_to_display(move_uci)
        
        # 현재 수순 이후의 기록이 있다면 (복기 중 이동 시) 잘라내기 (새로운 분기)
        if self.current_step < len(self.move_history):
            self.move_history = self.move_history[:self.current_step]
            self.board_states = self.board_states[:self.current_step + 1]

        self.move_history.append(display_move)
        
        # 3. 현재 수순 및 보드 상태 저장
        self.current_step = len(self.move_history)
        self.board_states.append(self._copy_board())
        
        # 4. 현재 FEN 업데이트 (엔진용)
        self.current_fen = self.model.generate_fen()
        
        # 5. 턴 교체
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'
        
        print(f"GameManager: Move Executed - {move_uci} (Step: {self.current_step})")
        
        # 6. 대국 모드: 엔진 차례면 자동으로 엔진 수 실행
        if self.current_mode == "game" and self.current_turn != self.player_side:
            self._engine_move()

    def _engine_move(self):
        if not self.engine or not self.engine.is_ready:
            return
        fen, moves = self._get_engine_fen_and_moves()
        self.engine.analyze_position(fen, moves, self._on_engine_move_result)

    def _on_engine_move_result(self, data, is_info=False):
        if self.current_mode != "game" or is_info:
            return
        best_move = self._flip_bestmove(data)  # 뒤집힌 경우 역변환
        from app.utils import CoordMapper
        parsed = CoordMapper.parse_uci(best_move)
        if not parsed:
            return
        f1, r1, f2, r2 = parsed
        c1, c2 = ord(f1) - ord('a'), ord(f2) - ord('a')
        row1, row2 = 10 - r1, 10 - r2
        self._log_engine_move(best_move)
        self.execute_move(best_move, row1, c1, row2, c2)
        self._refresh_ui()

    def pass_turn(self):
        """한수쉼을 실행합니다."""
        # 기보에 한수쉼 추가
        self.move_history.append("@@@@")
        
        # 현재 수순 업데이트
        self.current_step = len(self.move_history)
        
        # 보드 상태 저장 (한수쉼이므로 현재 상태 유지)
        self.board_states.append(self._copy_board())
        
        # 턴 교체
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'
        
        print(f"Pass Turn: @@@@ | Next Turn: {self.current_turn}")
        
        if self.current_mode == "analysis":
            self._run_analysis_cycle()
        elif self.current_mode == "game" and self.current_turn != self.player_side:
            self._engine_move()
            
        self._refresh_ui()

    # ---------------------------------------------------------------------
    # 유틸리티 및 엔진 연동
    # ---------------------------------------------------------------------
    def _is_my_turn(self, piece):
        """클릭한 기물이 현재 턴의 것인지 확인 (대문자 초, 소문자 한)"""
        if self.current_turn == 'w' and piece.isupper(): return True
        if self.current_turn == 'b' and piece.islower(): return True
        return False

    def _coords_to_uci(self, r1, c1, r2, c2):
        """좌표(0,0)를 엔진용 UCI(e10e9) 포맷으로 변환"""
        f1 = chr(ord('a') + c1)
        y1 = 10 - r1
        f2 = chr(ord('a') + c2)
        y2 = 10 - r2
        return f"{f1}{y1}{f2}{y2}"

    def _refresh_ui(self):
        """등록된 UI 콜백을 호출하여 화면을 다시 그리게 합니다."""
        if self.ui_refresh_callback:
            self.ui_refresh_callback()
            
    def handle_undo(self):
        """이전 수로 가기 (< 버튼)"""
        if self.current_step > 0:
            # 1. 만약 실제 대국 중이라면 (마지막 수에서 뒤로 가기)
            if self.current_step == len(self.move_history):
                if tk.messagebox.askyesno("무르기", "마지막 수를 무르시겠습니까?"):
                    self.move_history.pop() # 데이터 삭제
                    self.current_step -= 1
            else:
                # 2. 단순히 복기 중이라면 화면만 뒤로 이동
                self.current_step -= 1
            
            self.sync_board_with_step()

    def sync_board_with_step(self):
        """current_step에 맞춰 판의 형세를 재구성"""
        # 1. 판을 초기 상태로 리셋
        # Note: self.model.load_fen이 없을 경우 reset() 호출
        if hasattr(self.model, 'load_fen'):
            self.model.load_fen(self.cfg.INITIAL_FEN)
        else:
            self.model.reset()
        
        # 2. 0번째 수부터 current_step까지만 순차적으로 실행
        from app.utils import CoordMapper
        for i in range(self.current_step):
            move = self.move_history[i]
            # 표시용 좌표를 엔진용 UCI로 변환하여 적용
            uci_move = CoordMapper.pgn_to_uci(move) if move != "@@@@" else "@@@@"
            self.model.move_piece_uci(uci_move)
        
        # 3. UI 갱신
        self._refresh_ui()

    def request_new_game(self, fen):
        """
        새로운 FEN으로 게임을 시작합니다.
        :param fen: 새로운 게임의 초기 FEN
        """
        # request_reset()과 동일한 완전한 초기화 수행
        self.initialize_game()
        
        # FEN으로 보드 재설정
        self.model._parse_fen(fen)
        self.current_fen = fen
        self.game_initial_fen = fen  # 엔진용 시작 FEN 저장
        
        # 턴 정보 재설정 (FEN에서 추출)
        fen_parts = fen.split()
        self.current_turn = fen_parts[1] if len(fen_parts) > 1 else 'w'
        
        # 보드 상태 재설정
        self.board_states = [self._copy_board()]
        
        # 엔진 리셋
        if self.engine:
            self.engine.reset_engine()
        
        # UI 갱신 
        self._refresh_ui()
        
        print(f"GameManager: 새로운 게임 시작 - FEN: {fen}")

    def load_and_start(self, fen, history):
        """
        PGN 파일에서 로드된 FEN과 이동 기록으로 게임을 시작합니다.
        :param fen: 초기 FEN 문자열
        :param history: 이동 기록 리스트 (표시용 형식)
        """
        # 0. 엔진 리셋 (새 게임을 위해 가장 먼저 수행)
        if self.engine:
            self.engine.reset_engine()

        # 1. FEN으로 보드 초기화 (모델을 먼저 리셋한 후 FEN 적용)
        self.model.reset()
        self.model._parse_fen(fen)
        
        # 2. 현재 FEN 저장 및 게임 상태 초기화
        self.current_fen = fen
        self.game_initial_fen = fen  # 엔진용 시작 FEN 저장
        self.is_game_over = False
        self.selected_pos = None
        
        # 3. 턴 정보 추출 (FEN의 두 번째 부분)
        fen_parts = fen.split()
        if len(fen_parts) > 1:
            self.current_turn = fen_parts[1]
        else:
            self.current_turn = "w"  # 기본값
        
        # 4. 이동 기록 설정
        self.move_history = history
        self.current_step = 0  # PGN 로드 시 첫 수순부터 시작
        
        # 5. 보드 상태들 재구성
        self.board_states = [self._copy_board()]  # 초기 상태
        
        from app.utils import CoordMapper
        for move in history:
            # 각 이동을 적용하여 모든 수순의 보드 상태를 미리 계산하여 저장
            uci_move = CoordMapper.pgn_to_uci(move) if move != "@@@@" else "@@@@"
            self.model.move_piece_uci(uci_move)
            self.board_states.append(self._copy_board())
        
        # 6. 현재 표시할 상태 설정 (PGN 로드 시 보통 마지막 수순을 보여줌)
        self.current_step = len(self.move_history)
        self.model.grid = [row[:] for row in self.board_states[-1]]
        
        # 차례(턴) 정보 업데이트 (마지막 수순 기준)
        if self.current_step % 2 == 0:
            self.current_turn = fen_parts[1] if len(fen_parts) > 1 else "w"
        else:
            original_start_turn = fen_parts[1] if len(fen_parts) > 1 else "w"
            self.current_turn = "b" if original_start_turn == "w" else "w"
        
        # 6. 엔진 리셋 (새로운 포지션으로)
        if self.engine:
            self.engine.reset_engine()
        
        # 7. UI 갱신
        self._refresh_ui()
        
        print(f"GameManager: PGN에서 게임을 로드했습니다. FEN: {fen}, 수순: {len(history)}수")

    def go_to_step(self, step):
        """
        특정 수순으로 이동합니다.
        :param step: 이동할 수순 (0부터 시작)
        """
        if step < 0:
            step = 0
        if step > len(self.move_history):
            step = len(self.move_history)
            
        # 보드 상태 복원
        if step < len(self.board_states):
            self.model.grid = [row[:] for row in self.board_states[step]]
        
        self.current_step = step
        
        # 턴 정보 업데이트
        if step % 2 == 0:
            self.current_turn = "w"  # 초 차례
        else:
            self.current_turn = "b"  # 한 차례
            
        # UI 갱신
        self._refresh_ui()

    def go_to_first(self):
        """첫 수순으로 이동"""
        self.go_to_step(0)

    def go_to_last(self):
        """마지막 수순으로 이동"""
        self.go_to_step(len(self.move_history))

    def go_to_next(self):
        """다음 수순으로 이동"""
        self.go_to_step(self.current_step + 1)

    def go_to_prev(self):
        """이전 수순으로 이동"""
        self.go_to_step(self.current_step - 1)