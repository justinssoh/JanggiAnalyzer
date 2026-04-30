import subprocess
import threading
import os
import config


class JanggiEngine:
    def __init__(self):
        self.process = None
        self.is_ready = False
        self._lock = threading.Lock()   # 한 번에 하나의 분석만 허용
        self.path = config.ENGINE_PATH
        self.connect()

    def connect(self):
        if not os.path.exists(self.path):
            print(f"Engine Error: 파일을 찾을 수 없습니다 -> {self.path}")
            return
        try:
            self.process = subprocess.Popen(
                self.path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            # uci 초기화 후 readyok까지 모든 출력을 읽어서 버림
            self._send("uci")
            self._send("setoption name UCI_Variant value janggi")
            self._send("isready")
            self._drain_until("readyok")
            self.is_ready = True
            print(f"Engine: 연결 성공 ({config.ENGINE_NAME})")
        except Exception as e:
            print(f"Engine Connection Failed: {e}")
            self.is_ready = False

    def _send(self, command):
        """엔진에 명령어를 전송합니다."""
        if self.process and self.process.stdin:
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()

    def _drain_until(self, keyword, max_lines=200):
        """keyword가 나올 때까지 stdout을 읽어서 버립니다."""
        for _ in range(max_lines):
            if not self.process:
                break
            line = self.process.stdout.readline().strip()
            if keyword in line:
                return True
        return False

    def reset_engine(self):
        """엔진 상태를 새 게임으로 리셋합니다. 블로킹 없이 명령만 전송합니다."""
        if self.is_ready:
            self._send("ucinewgame")
            # isready/readyok는 분석 스레드 내부에서 처리하므로 여기선 보내지 않음
            print("Engine: 리셋 명령 전송")

    def stop_analysis(self):
        if self.is_ready:
            self._send("stop")

    def quit_engine(self):
        self.is_ready = False
        if self.process:
            try:
                self._send("stop")
                self._send("quit")
                self.process.stdin.close()
                self.process.wait(timeout=2)
            except Exception:
                pass
            finally:
                self.process.kill()
                self.process = None

    def analyze_position(self, fen, moves, callback):
        """
        :param fen:      초기 FEN 문자열
        :param moves:    UCI 수순 리스트
        :param callback: 결과를 전달받을 함수 (bestmove, is_info)
        """
        if not self.is_ready:
            return
        # 이미 분석 중이면 새 요청 무시
        if self._lock.locked():
            return
        thread = threading.Thread(
            target=self._run_analysis_thread,
            args=(fen, moves, callback),
            daemon=True
        )
        thread.start()

    def _run_analysis_thread(self, fen, moves, callback):
        with self._lock:
            if not self.process or not self.is_ready:
                return

            # isready/readyok로 엔진 준비 확인 후 분석 시작
            self._send("isready")
            if not self._drain_until("readyok"):
                return

            if moves:
                self._send(f"position fen {fen} moves {' '.join(moves)}")
            else:
                self._send(f"position fen {fen}")
            self._send(f"go movetime {config.MOVETIME}")

            best_move = None
            while True:
                if not self.process or not self.is_ready:
                    break
                line = self.process.stdout.readline().strip()
                if not line:
                    break
                if callback and line.startswith("info"):
                    callback(line, is_info=True)
                if line.startswith("bestmove"):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] != "(none)":
                        best_move = parts[1]
                    break

        if callback and best_move:
            callback(best_move, is_info=False)
