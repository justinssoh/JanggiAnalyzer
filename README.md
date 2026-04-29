Janggi Analyzer-0.3.2
=====
한국 전통 장기를 컴퓨터와 둘 수 있고 기보(.pgn)를 저장하고 분석하는 UI 프로그램입니다.

장기 규칙과 분석은 [ fairy-stockfish ](https://fairy-stockfish.github.io/) 엔진을 이용합니다.


v0.3.2
    분석 시작 버튼으로 분석 모드 구현
    
## TODO
네비게이션 버튼과 기보창의 동기화

앤진 사용

    - 이동 규칙 변환이 맞는지 확인
    - 이동 할 수 없는 곳으로 가려할 때 처리 방법
    - 장기 규칙

    bestmove
    기물 선택시 이동 가능한 경로 표시/ 기물을 잡는 경우 빨간색 원
    승/ 패

    **분석 모드** 추천수 3 가지와 각각에 대한 예상 수순


기물 점수
대국 시간 : 5분/ 30초 3회 (대국 모드에서만)

기보창 하이라이트

사이드 패녈 버튼
    - 분석 시작/ 자동 대국/ 대국 시작

음향 효과

판세 판단 및 그래프로 표현

장기판 편집 기능
    - 박보 장기/ 특정 상황 분석


* UI
윈도우 창크기 고정
버튼 크기/ 레이아웃 확인

엔진 추천수 화살표로 보여주기

장기판/ 장기알 : 그림 파일 사용
마우스 드랙 앤 드롭으로 기물 이동

기물 이동 효과/ 기물 잡는 경우와 외통수 특별 그래픽 효과

승패 판정 윈도우 및 기보창 

* 기보 파일이 유효한지 확인
    - 상/마 표현 (B/ Nd이 표준)
    - 좌표 ( a - i, 0 - 9)

특정 시점에 사용 불가능한 메뉴나 버튼 비활성화 시키기(눌러도 작동할 수 없게하고 이름도 흐릿하게 만들기)



## Linux 환경 실행 가이드

1.  **Fairy-Stockfish 엔진 다운로드:**
    -   [Fairy-Stockfish 릴리스 페이지](https://github.com/fairy-stockfish/Fairy-Stockfish/releases)에서 본인 시스템에 맞는 Linux용 실행 파일을 다운로드합니다.
    -   예: `fairy-stockfish_x86-64`

2.  **엔진 파일 배치:**
    -   다운로드한 엔진 파일을 프로젝트의 `engine/` 디렉토리 아래에 둡니다. (`JanggiAnalyzer/engine/`)
    -   파일 이름이 `fairy-stockfish_x86-64`와 같이 실행 가능한 형태인지 확인합니다.

3.  **실행 권한 부여:**
    -   터미널에서 다음 명령어를 실행하여 엔진 파일에 실행 권한을 부여합니다.
        ```bash
        chmod +x engine/fairy-stockfish-largeboard_x86-64
        ```
        (다운로드한 파일 이름이 다르면 해당 이름으로 변경)

4.  **`config.py` 설정 확인:**
    -   `config.py` 파일에서 `ENGINE_PATH`가 올바른 엔진 파일 경로를 가리키는지 확인합니다.
        ```python
        # config.py
        ENGINE_NAME = "fairy-stockfish_x86-64"
        ENGINE_PATH = os.path.join(os.path.dirname(__file__), "engine", ENGINE_NAME)
        ```

5.  **의존성 설치:**
    -   Python 3가 설치되어 있어야 합니다.
    -   프로젝트 루트에서 다음 명령어를 실행하여 필요한 라이브러리를 설치합니다.
        ```bash
        pip install -r requirements.txt
        ```

6.  **프로그램 실행:**
    -   프로젝트 루트 디렉토리에서 다음 명령어로 프로그램을 실행합니다.
        ```bash
        python3 main.py
        ```



## 프로젝트 폴더 구조
```Plain Text
janggi_project/
├── main.py
├── config.py
├── engine/
│   └── fairy-stockfish_x86-64  (또는 .exe 파일)
├── assets/
│   └── images/
│   └── sounds/
└── app/
    ├── __init__.py
    ├── board.py
    ├── engine.py
    ├── game_manager.py
    ├── utils.py
    └── ui/
        ├── __init__.py
        ├── main_window.py
        ├── canvas.py
        ├── side_panel.py
        └── dialogs.py
```

* main.py

* 변하지 않는 것과 변하는 것 구분
    - 초기화 : 다기 그리기

    -  Manager : 변수(차례, 배열, 움직임 ...)
        배열 움직임이 핵심

            배열을 순환 하면서 초/한 점수 계산
            배열과 움직임 차례 : FEN 생성 가능
    
    - 움직임 : 배열과 PGN Engine 과의 규격 변환 - 기준:   **TODO**... 로 하고/ 변환 로직



    - 윈도우
        Canvas(장기판) : 장기판/ 배열 인덱스는 변하지 않는데도 다시 그려야 하나? 장기 알만 다시 그리면 되지 않을까?
        나중에 장기판을 배경 그림 파일로 바꿨을 때



## GUI 설계의 핵심
* MVC 패턴 : 데이터와 화면의 "완전 분리"
데이터(move_history, current_step)가 주인이고, 화면은 그저 데이터를 **"그려주는 거울"**일 뿐
    - 데이터가 변하면? → refresh_all_ui()를 호출해 화면 전체를 새로고침

* "진실의 근원(Single Source of Truth)" 설정
GameManager에 있는 move_history와 current_step만이 현재 게임의 상태를 결정
    - "현재 판의 배치"를 여기저기서 관리하면 내비게이션(수순 이동) 기능을 만들 때 코드가 꼬이게 됨
    - 내비게이션 버튼을 누르든, 기물을 직접 옮기든, 파일을 불러오든 상관없이 모든 로직은 결국 이 두 값을 수정하는 것으로 수렴해야/ 그 후 화면을 다시 그리면 로직이 매우 단순해짐

* "무상태(Stateless)" 방식의 화면 갱신
정교한 로직의 비결: 그냥 "전체 삭제 후 처음부터 다시 그리기" 전략
    - 컴퓨터는 100~200수의 장기 기보를 처음부터 끝까지 다시 계산해서 그리는 데 1ms도 걸리지 않음
    - Undo, Redo, Jump to Move가 모두 동일한 함수 하나로 해결
기물이 이동하게 보이는 것도 보드 배열을 바꾸고 장기판을 통째로 다시 그리는 방식
    - 특정 기물만 따로 선택해서 이동하는 것이 아님
    - 잔상 처리 효과를 넣을 수도 있음 



## 의존성 주입
```plain text
            config.py

                    impirt config
                                                canvas.py                                                                           
                                                    class JanggiCanvas(tk.Canvas):
                                                        def __init__(self, master, model, manager):
            main.py (조립)                      **UI** main_window.py  
                                                        JanggiApp(root, config, game_manager)
                                                            self.canvas = JanggiCanvas(...)
                                                            self.side_panel = SidePanel(...)

                                                side_panel.py
                                                    class SidePanel(tk.Frame):
                                                        def __init__(self, parent, manager):
                
            def main()
              root = tk.Tk()
                                                                **BOARD**
                                                                    class JanggiBoardModel:

              app = JanggiApp(root, config, game_manager)
              root.mainloop()
                                                                **LOGIC** game_manager.py
                                                                    class GameManager:
                                                                        def __init__(self, model, engine, cfg):


                             **ENGINE**
                                class JanggiEngine:
                                    def __init__(self):
```

* config.py의 설정값
    - self.cfg.HEIGHT 처럼 사용



## Call Back 함수
콜백 함수는 다른 함수의 인자로 전달되어, 특정 이벤트가 발생하거나 작업이 완료된 후에 실행되는 함수
    1. 이벤트 처리 (UI)
    2. 비동기 작업
    3. 리스트/배열 처리
    4. 지연 실행/타이머
    5. 작업 완료 후 처리

장점
유연성: 함수 실행 후의 동작을 커스터마이징 가능
이벤트 기반 프로그래밍: 특정 조건/시점에만 실행
코드 재사용성: 같은 함수를 다양한 콜백으로 재사용 가능

클래스 간의 느슨한 결합(decoupling)을 만들어 주어, 한 클래스가 다른 클래스의 메서드를 직접 알지 않아도 호출할 수 있게 해줌(어떤 클래스에서 다른 클래스에 정의되어 있는 함수를 호출해 사용)


사용자 클릭 → Canvas._on_click() 
    ↓
GameManager.handle_board_click() 
    ↓
Game 상태 변경 후 ui_refresh_callback() 호출
    ↓
MainWindow.refresh_ui() 실행
    ↓
Canvas.draw_all() + SidePanel 업데이트

* 콜백 함수 사용 위치
    - 1. Engine의 비동기 분석 콜백 (engine.py)
    - 2. GameManager의 UI 갱신 콜백 (game_manager.py)
    - 3. MainWindow에서 콜백 등록 (main_window.py)
    - 4. Canvas의 Tkinter 이벤트 콜백 (canvas.py)

**중요** 인자명으로 변수처럼 넘기지만 실제 함수이므로 '같은 이름()'으로 함수로 실행할 수 있음

```python
class GameManager:
    def __init__(self):
        self.ui_callback = None  # 콜백 저장 변수 (초기값 None)
    
    def set_callback(self, func):
        self.ui_callback = func  # 함수를 변수에 저장
    
    def do_something(self):
        print("게임 로직 실행...")
        if self.ui_callback:    # 콜백이 있으면
            self.ui_callback()  # 저장된 함수 호출

# UI 함수 (콜백으로 사용할 함수)
def refresh_screen():
    print("화면을 갱신합니다!")

# 사용
manager = GameManager()
manager.set_callback(refresh_screen)  # 콜백 등록
manager.do_something()  # 실행 → "게임 로직 실행..." → "화면을 갱신합니다!"
```

## 참고
```python

class (tk.Canvas):                                          # 상속
    def __init__(self, master, model, manager):             # 의존성 주입 : master는 메인 윈도우의 canvas_frame
    
    super().__init__(                                       # 부모 클래스(tk.Canvas)의 변수 사용 
            master, 


class SidePanel(tk.Frame):
    def __init__(self, parent, manager):

   super().__init__(parent, width=300, relief="flat", bg="#f0f0f0") 

```

* callback 함수
```python

class GameManager:
    def __init__(self, model, engine, cfg):
        self.ui_refresh_callback = None

    def set_ui_callback(self, callback):
        """MainWindow의 화면 갱신 함수를 연결합니다."""
        self.ui_refresh_callback = callback
    
    def request_reset(self):
        """사용자가 UI에서 리셋을 요청했을 때 호출됩니다."""
        self.initialize_game()
        if self.ui_refresh_callback:
            self.ui_refresh_callback()


class JanggiApp:
    def __init__(self, root, config, game_manager):
        # 게임 매니저에 UI 갱신 콜백 등록
        # 매니저가 데이터 처리를 끝내면 이 클래스의 refresh_ui를 호출하게 됩니다.
        self.game_manager.set_ui_callback(self.refresh_ui)

```
