Janggi Analyzer-0.8.8
=====
한국 전통 장기를 컴퓨터와 둘 수 있고 기보(.pgn)를 저장하고 분석하는 UI 프로그램입니다.

장기 규칙과 분석은 [ fairy-stockfish ](https://fairy-stockfish.github.io/) 엔진을 이용합니다.

* 0.8.8
    test 코드 및 콘솔용 장기 게임(이미 구현한 클래스 재사용)
* 0.8.6
    FEN 스택 및 기물점수 초기화
* 0.8.5
    졸이나 병이 후진하는 문제 해결

* v0.8.0
    엔진 사용
        - legal move
        - 이동 할 수 없는 곳으로 가려할 때 처리 방법 : 원래 위치로 돌아와야 함
        - 장기 규칙

            반복수 : 착수 금지
            빅장 : 나중에 구현


    기물 점수
        - 매번 장기판 갱신할 때 배열을 읽어 남아있는 기물들의 점수 합산
        
    판정 : 사용자의 입장에서 별도의 윈도우에 승패 보여주기
        - 외통
        - 점수
        - 200 수 제한시 점수로 판정
        - 기권
        - 양쪽에서 동시에 한수쉼 하는 경우 점수로 판정

* v0.4.0
    - 엔진과 통신: 대국 모드 및 자동 대국 기능
    - 처음 부터 진행되 때마다 FEN 문자열을 저장하는 "스택"
        : 엔진과의 기본 소통/ 수순이 꼬이거나 기보창과의 연동에 유리한 방법

* v0.3.2
    - 분석 시작 버튼으로 분석 모드 구현


## TODO
네비게이션 버튼과 기보창의 동기화

대국 시간 : 5분/ 30초 3회 (대국 모드에서만)

기보창 하이라이트

음향 효과

판세 판단 및 그래프로 표현

장기판 편집 기능
    - 박보 장기/ 특정 상황 분석

* UI
윈도우 창크기 고정
기보창/ 분석창: 스크롤 바
기보 파일 열기/ 저장시 기본 폴더를 data/로

엔진 추천수 화살표로 보여주기

기물 선택시 이동 가능한 경로 표시/ 기물을 잡는 경우 빨간색 원으로 표시

장기판/ 장기알 : 그림 파일 사용
마우스 드랙 앤 드롭으로 기물 이동

기물 이동 효과/ 기물 잡는 경우와 외통수 특별 그래픽 효과

* 기보 파일이 유효한지 확인
    - 상/마 표현 (B/ Nd이 표준)
    - 좌표 ( a - i, 0 - 9)

* 특정 시점에 사용 불가능한 메뉴나 버튼 비활성화 시키기(눌러도 작동할 수 없게하고 이름도 흐릿하게 만들기)
    - 각 모드를 선택하면 그 모드는 다시 선택할 수 없음 : 다른 모드를 선택하면 그 모드만 사용불가 나머지 2 모드는 사용 가능
    - 네비게이션 버튼 처음과 끝 : 처음으로 가면 처음/ 되돌리기는 불가

* 엔진 옵션 설정 : 설정 메뉴에 추가
    - Core 


## Bug
* 초가 화면 위(컴퓨터) 한이 화면 아래(사용자)의 경우 오동작을 일으킴
    - 졸/ 병이 후진하는 문제

* 엔진 통신시 순서가 꼬이는 문제
    - 엔진에서 분석 결과가 오기 전에 사용자가 다른 행동을 하는 경우
    - 엔진이 분석 결과를 보내는 시점과 사용자의 행동이 겹치는 경우



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



## Call Back 함수 : 이벤트 기반(Event-Driven) 모델의 핵심
콜백 함수는 다른 함수의 인자로 전달되어, 특정 이벤트가 발생하거나 작업이 완료된 후에 실행되는 함수

---

지금 당장 실행하는 것이 아니라, 특정 조건이나 이벤트가 발생했을 때 나중에 실행해달라고 맡겨두는 함수
언제 버튼을 누를지 모르기 때문데 미리 등록해 둠
    - 사용자가 장기판의 기물을 클릭했을 때
    - 엔진이 수 분석을 끝냈을 때

프로그램의 주도권을 제어하고 비효율적인 대기 시간을 없애기 위해 사용


1. 이벤트 처리 (Event Handling)
GUI(Tkinter)나 웹 브라우저에서 사용자가 언제, 어떤 행동을 할지 예측할 수 없을 때 사용

2. 비동기 작업 및 네트워크 통신 (Asynchronous Operations)
데이터를 요청하고 응답이 올 때까지 시간이 걸리는 경우
    - 서버에서 장기 기보 데이터를 가져올 때
    - 파일 시스템에서 큰 로그 파일을 읽어올 때

3. 시간 지연 및 반복 작업 (Scheduling)
특정 시간이 지난 뒤에 무언가를 실행해야 할 때
정확한 타이밍에 코드를 실행하기 위해 시스템 타이머에게 실행 권한을 넘김

4. 고차 함수를 통한 로직의 추상화 (Strategy Pattern)
함수 내부의 특정 단계만 상황에 따라 다르게 동작시키고 싶을 때 사용
    - 리스트를 정렬할 때 "내림차순으로 정렬할지, 오름차순으로 정렬할지" 결정하는 기준 함수를 넘겨주는 경우

5. 작업 완료 후 처리
장기 프로그램처럼 복잡한 로직에서는 lambda나 functools.partial을 적절히 섞어 써야 기물 좌표값 등을 콜백으로 넘길 수 있음


### 장점
    - 유연성: 함수 실행 후의 동작을 커스터마이징 가능
    - 이벤트 기반 프로그래밍: 특정 조건/시점에만 실행
    - 코드 재사용성: 같은 함수를 다양한 콜백으로 재사용 가능

    - 클래스 간의 느슨한 결합(decoupling)을 만들어 주어, 한 클래스가 다른 클래스의 메서드를 직접 알지 않아도 호출할 수 있게 해줌
    (어떤 클래스에서 다른 클래스에 정의되어 있는 함수를 호출해 사용)

* 예) UI 갱신 콜백
```python
# game_manager.py
class GameManager:
    def __init__(self, ...):
        self.ui_refresh_callback = None                     # ① 콜백 저장 변수 (초기값 None)

    def set_ui_callback(self, callback):
        self.ui_refresh_callback = callback                 # ② 함수를 변수에 저장

    def _refresh_ui(self):
        if self.ui_refresh_callback:
            self.ui_refresh_callback()                      # ③ 저장된 함수 호출

``` 

```python
# main_window.py
class JanggiApp:
    def __init__(self, ...):
        self.game_manager.set_ui_callback(self.refresh_ui)  # ④ 등록

    def referesh_ui(self):                                  # 실제 실행될 함수  

```
**중요** 인자명으로 변수처럼 넘기지만 실제 함수이므로 '함수이름()'으로 함수로 실행할 수 있음


* 예) 엔진 분석 결과 콜백
비동기 작업 완료 후 처리/ 엔진이 별도 스레드에서 돌기 때문에 반드시 콜백 사용해야
```python
# engine.py
def analyze_position(self, fen, moves, callback):           # callback을 인자로 받음
    thread = threading.Thread(
        target=self._run_analysis_thread,
        args=(fen, moves, callback),                        # 스레드에 콜백 전달
        daemon=True
    )
    thread.start()

def _run_analysis_thread(self, fen, moves, callback):
    # ... 분석 중 ...
    self._result_queue.put((callback, line, True))          # 큐에 콜백 저장
    
```

```python
# engine.py
def poll_results(self):
    callback, data, is_info = self._result_queue.get_nowait()
    if callback:
        callback(data, is_info=is_info)                     # 큐에서 꺼내 실행

```
engine.py는 분석 작업만 처리/ 실제 실행되는 함수는 game_manager에 만듬
콜백을 저장(등록)하지 않고, 매번 analyze_position() 호출 시 인자로 받아서 그때그때 전달

```python
# game_manager.py
def _run_analysis_cycle(self):
    self.engine.analyze_position(fen, moves, self._on_analysis_result)  # 여기서 연결
    #                                        ^^^^^^^^^^^^^^^^^^^^^^^^
    #                                        이 순간 콜백이 engine에 전달됨

def _engine_move(self):
    self.engine.analyze_position(fen, moves, self._on_engine_move_result)  # 여기서 연결

def _auto_game_step(self):
    self.engine.analyze_position(fen, moves, self._on_auto_game_result)  # 여기서 연결

```

| | game_manager | engine |
| :--- | :----: | :----:|
| 방식 | 등록(저장) 후 나중에 호출| 호출할 때마다 인자로 전달 |
| 콜백 고정 여부 | 항상 같은 함수(refresh_ui)| 상황마다 다른 함수 전달 가능 |
| 사용 이유 | UI는 항상 같은 함수로 갱신 | 분석/대국/자동대국 모드마다 다른 콜백 필요 |

engine은 모드에 따라 _on_analysis_result, _on_engine_move_result, _on_auto_game_result 중 하나를 받아야 하므로 "전달" 방식이 더 적합


* Tkinter 이벤트 콜백
이벤트 처리의 예 : Tkinter가 클릭 이벤트 발생 시 자동으로 호출
```python
# canvas.py
class JanggiCanvas:
    def __init__(self, ...):
        self.bind("<Button-1>", self._on_click)             # 클릭 이벤트에 콜백 등록

    def _on_click(self, event):                             # Tkinter가 자동으로 호출
        grid_pos = CoordMapper.canvas_to_grid(event.x, event.y)
        if grid_pos:
            self.manager.handle_board_click(r, c)

```

* lambda 콜백 
간단한 1회성 콜백에 lambda를 사용
```python
# main_window.py
settings_menu.add_command(
    label="엔진 설정",
    command=lambda: print("Engine Settings")                # 익명 함수로 콜백 등록
)

```

* Test
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




## Tips
* 테스트 용 코드 만들기
예: FEN 무자열을 생성하는 코드를 확인하는 방법
프로젝트 루트 디렉토리에서 실행
```bash
python3 -c "
from app.utils import FENSetter
fen = FENSetter.get_initial_fen_cho_player('상마상마', '상마상마')
print(fen)
"
```

프로젝트 루트 디렉토리에서 python 대화형 셸에서 실행해도 됩니다. tests 디렉토리에 테스트 파일로 만들어도 가능합니다.
