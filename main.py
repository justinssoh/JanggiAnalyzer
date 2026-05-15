#!/usr/bin/env python3

import tkinter as tk
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import config
from app.board import JanggiBoardModel
from app.engine import JanggiEngine
from app.game_manager import GameManager
from app.ui.main_window import JanggiApp


def main():
    root = tk.Tk()
    model = JanggiBoardModel()

    engine = None
    if not os.path.exists(config.ENGINE_PATH):
        print(f"!!! 경고: 엔진 파일을 찾을 수 없습니다 !!!\n경로: {config.ENGINE_PATH}")
    else:
        try:
            engine = JanggiEngine()
        except Exception as e:
            print(f"오류: 엔진 로드 중 문제가 발생했습니다: {e}")

    game_manager = GameManager(model, engine, config)

    try:
        app = JanggiApp(root, config, game_manager)
    except Exception as e:
        print(f"오류: UI 초기화 중 문제가 발생했습니다: {e}")
        sys.exit(1)

    print("장기 분석기를 실행합니다...")
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 종료되었습니다.")
        sys.exit(0)
