import subprocess
import threading
import os
import config

class JanggiEngine:
    def __init__(self):
        """
        장기 엔진(Fairy-Stockfish) 제어 객체 초기화.
        """
        self.process = None
        self.is_ready = False
        
        # 엔진 실행 파일 경로 확인
        self.path = config.ENGINE_PATH
        
        # 엔진 연결 시작
        self.connect()

    def connect(self):
        """엔진 프로세스를 실행하고 초기 UCI 설정을 수행합니다."""
        if not os.path.exists(self.path):
            print(f"Engine Error: 파일을 찾을 수 없습니다 -> {self.path}")
            return

        try:
            # 1. 서브프로세스로 엔진 실행
            # universal_newlines=True: 텍스트 모드로 통신
            # bufsize=1: 라인 단위 버퍼링
            self.process = subprocess.Popen(
                self.path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )

            # 2. UCI 초기화 명령어 전송
            self.send_command("uci")
            self.send_command("setoption name UCI_Variant value janggi")
            self.send_command("isready")
            
            # 엔진의 응답을 확인하는 별도 쓰레드 시작 (선택 사항)
            # 여기서는 간단하게 초기 연결 성공만 확인합니다.
            self.is_ready = True
            print(f"Engine: 연결 성공 ({config.ENGINE_NAME})")

        except Exception as e:
            print(f"Engine Connection Failed: {e}")
            self.is_ready = False

    def send_command(self, command):
        """엔진에 명령어를 전송합니다."""
        if self.process and self.process.stdin:
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()

    def reset_engine(self):
        """엔진의 상태를 새 게임 상태로 리셋합니다."""
        if self.is_ready:
            self.send_command("ucinewgame")
            self.send_command("isready")
            print("Engine: 상태 리셋 완료")

    def stop_analysis(self):
        """현재 진행 중인 분석을 중단합니다."""
        if self.is_ready:
            self.send_command("stop")

    def quit_engine(self):
        """엔진 프로세스를 완전히 종료합니다."""
        if self.process:
            self.send_command("quit")
            self.process.terminate()
            self.process = None
            self.is_ready = False

    # ---------------------------------------------------------------------
    # 분석 로직 (비동기 실행 권장)
    # ---------------------------------------------------------------------
    def analyze_position(self, fen, callback):
        """
        주어진 FEN 상태를 분석하여 베스트 무브를 찾습니다.
        :param fen: 현재 장기판의 FEN 문자열
        :param callback: 분석 완료 후 결과를 전달받을 함수
        """
        if not self.is_ready:
            return

        # 분석은 시간이 걸리므로 UI가 멈추지 않게 쓰레드로 실행합니다.
        thread = threading.Thread(
            target=self._run_analysis_thread, 
            args=(fen, callback), 
            daemon=True
        )
        thread.start()

    def _run_analysis_thread(self, fen, callback):
        """별도 쓰레드에서 엔진 분석 결과를 기다리는 로직"""
        # 1. 위치 전송
        self.send_command(f"position fen {fen}")
        # 2. 분석 시작 (config에 설정된 사고 시간 사용)
        self.send_command(f"go movetime {config.MOVETIME}")

        best_move = None
        while True:
            if not self.process:
                break
            line = self.process.stdout.readline().strip()
            if not line:
                continue # 프로세스가 살아있으면 계속 읽기 시도
            
            # 실시간 분석 정보를 보려면 info 라인을 파싱할 수 있음
            # 예: info depth 10 seldepth 12 score cp 15 nodes 12345 nps 1000 pv e10e9 ...
            if callback and line.startswith("info"):
                callback(line, is_info=True)

            # 엔진 응답 예: "bestmove e10e9 ponder d1e1"
            if line.startswith("bestmove"):
                parts = line.split()
                if len(parts) >= 2:
                    best_move = parts[1]
                break
        
        # 3. 분석 결과를 메인 쓰레드(UI)로 돌려보냄
        if callback and best_move:
            callback(best_move, is_info=False)
