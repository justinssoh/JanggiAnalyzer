import subprocess
import threading
import queue
import os
import config


class JanggiEngine:
    def __init__(self):
        self.process = None
        self.is_ready = False
        self._lock = threading.Lock()       # 한 번에 하나의 분석만 허용
        self._result_queue = queue.Queue()  # 분석 결과를 메인 스레드로 전달
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
        if self.is_ready:
            self._send("ucinewgame")
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
        분석 요청. 결과는 큐를 통해 메인 스레드로 전달됩니다.
        :param fen:      초기 FEN (항상 표준 방향: 한 위, 초 아래)
        :param moves:    UCI 수순 리스트
        :param callback: (data, is_info) 형태로 호출될 함수
        """
        if not self.is_ready:
            return
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
                if line.startswith("info"):
                    self._result_queue.put((callback, line, True))
                if line.startswith("bestmove"):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] != "(none)":
                        best_move = parts[1]
                    break

        if best_move:
            self._result_queue.put((callback, best_move, False))

    def poll_results(self):
        """
        메인 스레드에서 주기적으로 호출하여 큐에 쌓인 결과를 처리합니다.
        Tkinter의 after()와 함께 사용합니다.
        """
        try:
            while True:
                callback, data, is_info = self._result_queue.get_nowait()
                if callback:
                    callback(data, is_info=is_info)
        except queue.Empty:
            pass
