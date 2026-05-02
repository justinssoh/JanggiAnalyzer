#!/usr/bin/env python3

import tkinter as tk
import os
import sys

# -------------------------------------------------------------------------
# 프로젝트 루트 디렉토리를 Python Path에 추가
# -------------------------------------------------------------------------
# 이 코드가 있어야 하위 폴더(app/)에 있는 모듈들을 자유롭게 import 할 수 있습니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# -------------------------------------------------------------------------
# 프로젝트 구성 요소 Import
# -------------------------------------------------------------------------
import config                   # 루트의 config.py 불러오기

# 모델, 엔진, 매니저 Import
from app.board import JanggiBoardModel
from app.engine import JanggiEngine
from app.game_manager import GameManager

# UI 메인 윈도우 Import
from app.ui.main_window import JanggiApp

def main():
    """
    프로그램의 진입점(Entry Point)
    """
    
    # [1] Tkinter 루트 객체 생성
    root = tk.Tk()
 
    # [2] 모델(Data) 초기화
    # 장기판의 상태(배열)를 관리하는 순수 데이터 클래스
    model = JanggiBoardModel()
    
    # [3] 엔진(Analysis) 초기화
    # 외부 Fairy-Stockfish 프로세스와 통신을 담당
    engine_path = config.ENGINE_PATH
    engine = None

    # 운영체제에 따라 엔진 파일 이름 설정
    if sys.platform == "win32":
        config.ENGINE_NAME = "fairy-stockfish_x86-64.exe"
    elif sys.platform == "linux":
        config.ENGINE_NAME = "fairy-stockfish_x86-64"
    # Mac OS 등 다른 OS에 대한 처리도 추가 가능

    config.ENGINE_PATH = os.path.join(os.path.dirname(__file__), "engine", config.ENGINE_NAME)
    engine_path = config.ENGINE_PATH        # 업데이트된 경로로 다시 설정

    if not os.path.exists(engine_path):
        print(f"!!! 경고: 엔진 파일을 찾을 수 없습니다 !!!\n경로: {engine_path}")
        # 엔진이 없어도 프로그램은 실행되도록 예외 처리
    else:
        try:
            engine = JanggiEngine()
            print("성공: 장기 분석 엔진이 로드되었습니다.")
        except Exception as e:
            print(f"오류: 엔진 로드 중 문제가 발생했습니다: {e}")

    # [4] 게임 매니저(GameManager) 생성 - 프로그램의 '심장'
    # 모델과 엔진을 소유하며, 게임의 규칙(턴, 이동 등)을 총괄
    # 나중에 UI에서 발생하는 모든 명령은 이 manager를 거치게 됨
    game_manager = GameManager(model, engine, config)

# -------------------------------------------------------------------------
# 메인 UI 앱(JanggiApp) 생성 및 조립
# -------------------------------------------------------------------------
    # root(창), config(설정), manager(로직)를 전달
    # 의존성 주입(Dependency Injection)을 통해 UI가 로직을 알게 함
    try:
        app = JanggiApp(root, config, game_manager)
    except Exception as e:
        print(f"오류: UI 초기화 중 문제가 발생했습니다: {e}")
        sys.exit(1)

    # 프로그램 실행 (이벤트 루프 시작)
    # 사용자가 창을 닫기 전까지 여기서 대기
    print("장기 분석기를 실행합니다...")
    root.mainloop()

# -------------------------------------------------------------------------
# 프로그램 실행 시점 확인
# -------------------------------------------------------------------------
if __name__ == "__main__":
    # 실행 중 발생할 수 있는 예상치 못한 에러를 터미널에 표시하기 위해 예외 처리
    try:
        main()
    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 종료되었습니다.")
        sys.exit(0)