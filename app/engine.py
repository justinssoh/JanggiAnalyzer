import subprocess
import threading
import os
import config

class JanggiEngine:
    def __init__(self):
        self.process = None
        self.is_ready = False
        self._lock = threading.Lock()  # 동시 분석 방지
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
            self.send_command("uci")
            self.send_command("setoption name UCI_Variant value janggi")
            self.send_command("isready")
            # readyok 응답 대기
            while True:
                line = self.process.stdout.readline().strip()
                if line == "readyok":
                    break
            self.is_ready = True
            print(f"Engine: 연결 성공 ({config.ENGINE_NAME})")
        except Exception as e:
            print(f"Engine Connection Failed: {e}")
            self.is_ready = False

    def send_command(self, command):
        if self.process and self.process.stdin:
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()

    def reset_engine(self):
        if self.is_ready:
            self.send_command("ucinewgame")
            self.send_command("isready")
            # readyok 대기
            while True:
                line = self.process.stdout.readline().strip()
                if line == "readyok":
                    break
            print("Engine: 상태 리셋 완료")

    def stop_analysis(self):
        if self.is_ready:
            self.send_command("stop")

    def quit_engine(self):
        self.is_ready = False
        if self.process:
            try:
                self.send_command("stop")
                self.send_command("quit")
                self.process.stdin.close()
                self.process.wait(timeout=2)
            except Exception:
                pass
            finally:
                self.process.kill()
                self.process = None

    def analyze_position(self, fen, moves, callback):
        """
        :param fen: 초기 FEN 문자열
        :param moves: UCI 수순 리스트
        :param callback: 분석 완료 후 결과를 전달받을 함수
        """
        if not self.is_ready:
            return
        # 이미 분석 중이면 새 스레드 시작 안 함
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
            if moves:
                self.send_command(f"position fen {fen} moves {' '.join(moves)}")
            else:
                self.send_command(f"position fen {fen}")
            self.send_command(f"go movetime {config.MOVETIME}")

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
