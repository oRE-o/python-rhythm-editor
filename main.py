import pygame
pygame.init()
pygame.mixer.init() # <-- 2. 이 주석을 꼭 풀어주세요.

import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UILabel, UIHorizontalSlider, UIDropDownMenu, UITextEntryLine, UICheckBox
from pygame_gui.windows import UIFileDialog
from pygame_gui.windows.ui_colour_picker_dialog import UIColourPickerDialog
from pygame_gui.elements.ui_selection_list import UISelectionList
# [추가] 새 이벤트 타입 임포트

import audio_manager
import chart
import editor_canvas


SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rhythm Editor - Step 2: Audio")
clock = pygame.time.Clock()
editor_canvas.init_font() # <-- 이쪽으로 (manager 생성 이후) 옮겨주세요!
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
audio_manager.load_hitsound("hitsound.wav") # (파일 경로 확인!)

# --- 2. UI 레이아웃 정의 (동일) ---
BOTTOM_PANEL_HEIGHT = 60
LEFT_PANEL_WIDTH = 200
RIGHT_PANEL_WIDTH = 250

bottom_panel_rect = pygame.Rect(0, SCREEN_HEIGHT - BOTTOM_PANEL_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL_HEIGHT)
bottom_panel = UIPanel(relative_rect=bottom_panel_rect, starting_height=1, manager=manager)

left_panel_rect = pygame.Rect(0, 0, LEFT_PANEL_WIDTH, SCREEN_HEIGHT - BOTTOM_PANEL_HEIGHT)

right_panel_rect = pygame.Rect(SCREEN_WIDTH - RIGHT_PANEL_WIDTH, 0, RIGHT_PANEL_WIDTH, SCREEN_HEIGHT - BOTTOM_PANEL_HEIGHT)
right_panel = UIPanel(relative_rect=right_panel_rect, starting_height=1, manager=manager)

EDITOR_RECT = pygame.Rect(LEFT_PANEL_WIDTH, 0, SCREEN_WIDTH - LEFT_PANEL_WIDTH - RIGHT_PANEL_WIDTH, SCREEN_HEIGHT - BOTTOM_PANEL_HEIGHT)

# --- 3. UI 요소(위젯) 생성 (수정) ---
current_chart = chart.ChartData()
# 아래쪽 패널
# [수정] Play/Pause 토글 버튼으로 변경
play_pause_button = UIButton(relative_rect=pygame.Rect(100, 10, 80, 40),
                             text='Play',
                             manager=manager,
                             container=bottom_panel)

stop_button = UIButton(relative_rect=pygame.Rect(190, 10, 80, 40),
                       text='Stop',
                       manager=manager,
                       container=bottom_panel)

time_label = UILabel(relative_rect=pygame.Rect(280, 10, 200, 40),
                     text='0.000 / 0.000', # 현재시간 / 총시간
                     manager=manager,
                     container=bottom_panel)


load_song_button = UIButton(relative_rect=pygame.Rect(10, 10, 230, 40), text='Load Song', manager=manager, container=right_panel)
song_name_label = UILabel(relative_rect=pygame.Rect(10, 60, 230, 30), text='No song loaded.', manager=manager, container=right_panel)

save_chart_button = UIButton(relative_rect=pygame.Rect(10, 100, 110, 30), text='Save Chart', manager=manager, container=right_panel)
load_chart_button = UIButton(relative_rect=pygame.Rect(130, 100, 110, 30), text='Load Chart', manager=manager, container=right_panel)

bpm_label = UILabel(relative_rect=pygame.Rect(10, 140, 50, 30), text='BPM:', manager=manager, container=right_panel)
bpm_entry = UITextEntryLine(relative_rect=pygame.Rect(70, 140, 170, 30), manager=manager, container=right_panel)
bpm_entry.set_text(str(current_chart.bpm)) # UI에 현재 BPM 표시


offset_label = UILabel(relative_rect=pygame.Rect(10, 180, 60, 30), text='Offset(ms):', manager=manager, container=right_panel)
offset_entry = UITextEntryLine(relative_rect=pygame.Rect(80, 180, 160, 30), manager=manager, container=right_panel)
offset_entry.set_text(str(current_chart.offset_ms)) # UI에 현재 Offset 표시

zoom_label = UILabel(relative_rect=pygame.Rect(10, 220, 230, 30), text='Zoom (Scroll Speed)', manager=manager, container=right_panel)
scale_slider = UIHorizontalSlider(relative_rect=pygame.Rect(10, 250, 230, 30), start_value=0.5, value_range=(0.05, 2.0), manager=manager, container=right_panel)

# (Y좌표 120 -> 210 으로 변경)
snap_label = UILabel(relative_rect=pygame.Rect(10, 290, 230, 30), text='Snap Division', manager=manager, container=right_panel)
snap_options = ["4", "8", "12", "16", "24"]
snap_dropdown = UIDropDownMenu(options_list=snap_options, starting_option="16", relative_rect=pygame.Rect(10, 320, 230, 40), manager=manager, container=right_panel)

lane_label = UILabel(relative_rect=pygame.Rect(10, 330, 230, 30), text='Number of Lanes (3-7)', manager=manager, container=right_panel)
lane_options = ["3", "4", "5", "6", "7"]
lane_dropdown = UIDropDownMenu(options_list=lane_options,
                               starting_option=str(current_chart.num_lanes), # 기본값 4
                               relative_rect=pygame.Rect(10, 360, 230, 40),
                               manager=manager,
                               container=right_panel)

# (Y좌표 수정: 370~: 노트 타입)
note_type_label = UILabel(relative_rect=pygame.Rect(10, 410, 230, 30), text='Note Type', manager=manager, container=right_panel)
note_type_names = list(current_chart.note_types.keys())
note_type_list = UISelectionList(relative_rect=pygame.Rect(10, 440, 230, 100), item_list=note_type_names, manager=manager, container=right_panel)

new_note_type_button = UIButton(relative_rect=pygame.Rect(10, 530, 110, 40), 
                                text='[+] New',
                                manager=manager,
                                container=right_panel)

edit_note_type_button = UIButton(relative_rect=pygame.Rect(130, 530, 110, 40), 
                                 text='[Edit Selected]',
                                 manager=manager,
                                 container=right_panel)
edit_note_type_button.disable() # (아무것도 선택 안 됐으니 일단 비활성화)
editor_title = UILabel(relative_rect=pygame.Rect(10, 10, 230, 30), text='New Note Type', manager=manager, container=right_panel)
editor_name_label = UILabel(relative_rect=pygame.Rect(10, 60, 100, 30), text='Name:', manager=manager, container=right_panel) 
editor_name_entry = UITextEntryLine(relative_rect=pygame.Rect(120, 60, 110, 30), manager=manager, container=right_panel)
editor_color_label = UILabel(relative_rect=pygame.Rect(10, 110, 100, 30), text='Color:', manager=manager, container=right_panel) 
editor_color_button = UIButton(relative_rect=pygame.Rect(120, 110, 110, 30), text='Pick Color', manager=manager, container=right_panel)

PRESET_COLORS = [
    (255, 80, 80), (80, 255, 80), (80, 80, 255), (255, 255, 80), # R, G, B, Yellow
    (80, 255, 255), (255, 80, 255), (200, 200, 200), (255, 150, 80) # Cyan, Magenta, Whiteish, Orange
]
editor_preset_buttons = []
btn_size, btn_margin = 50, 7 # (버튼 4개 너비: 50*4 + 7*3 = 221px. OK)

y_pos = 150
for i in range(4):
    x_pos = 10 + i * (btn_size + btn_margin)
    btn = UIButton(relative_rect=pygame.Rect(x_pos, y_pos, btn_size, 30), text='', manager=manager, container=right_panel)
    # 버튼 배경색을 프리셋 색깔로
    btn.colours['normal_bg'] = pygame.Color(PRESET_COLORS[i])
    btn.rebuild()
    editor_preset_buttons.append(btn)

# Row 2 (Y = 150 + 30 + 5 = 185)
y_pos = 185
for i in range(4):
    x_pos = 10 + i * (btn_size + btn_margin)
    btn = UIButton(relative_rect=pygame.Rect(x_pos, y_pos, btn_size, 30), text='', manager=manager, container=right_panel)
    # 버튼 배경색을 프리셋 색깔로
    btn.colours['normal_bg'] = pygame.Color(PRESET_COLORS[i+4])
    btn.rebuild()
    editor_preset_buttons.append(btn)


btn_size, btn_margin = 50, 7 # (버튼 4개 너비: 50*4 + 7*3 = 221px. OK)
editor_is_long_check = UICheckBox(relative_rect=pygame.Rect(10, 235, 100, 30), text='Is Long Note?', initial_state=False, manager=manager, container=right_panel)
editor_hitsound_check = UICheckBox(relative_rect=pygame.Rect(10, 275, 100, 30), text='Play Hitsound?', initial_state=True, manager=manager, container=right_panel)
editor_cancel_button = UIButton(relative_rect=pygame.Rect(10, 325, 110, 40), text='Cancel', manager=manager, container=right_panel)
editor_ok_button = UIButton(relative_rect=pygame.Rect(130, 325, 100, 40), text='OK', manager=manager, container=right_panel)
# [추가] UI 그룹화
default_ui_elements = [
    load_song_button, song_name_label, 
    save_chart_button, load_chart_button, bpm_label, bpm_entry, 
    offset_label, offset_entry,
    zoom_label, scale_slider, 
    snap_label, snap_dropdown, 
    lane_label, lane_dropdown, 
    note_type_label, note_type_list, 
    new_note_type_button,
    edit_note_type_button # <-- 이 줄을 추가!
]
editor_ui_elements = [
    editor_title, editor_name_label, editor_name_entry, 
    editor_color_label, editor_color_button, 
    editor_is_long_check, editor_hitsound_check, 
    editor_cancel_button, editor_ok_button,
    editor_name_label, editor_color_label
]
# [수정!] 1. 프리셋 버튼 8개를 리스트에 '먼저' 추가하고
editor_ui_elements.extend(editor_preset_buttons)

# [수정!] 2. '그 다음에' 리스트 전체를 숨겨주세요!
for element in editor_ui_elements:
    element.hide()
    


pending_long_note_start = None
last_played_time_ms = 0.0

# [추가] 노트 에디터용 변수
color_picker = None
editor_selected_color = (255, 255, 255) # 기본 흰색
editor_mode = "new" # <-- [신규!] 'new' 또는 'edit' 모드
editing_note_name = None # <-- [신규!] 지금 편집 중인 노트 이름

# --- [추가] 4. 에디터 상태 변수 ---
current_time_ms = 0.0
total_time_ms = 0.0
file_dialog = None # 파일 대화상자 객체

scale_pixels_per_ms = 0.5
judgement_line_y = EDITOR_RECT.height * 0.8

# [추가] 현재 스냅 설정
current_snap_division = 16
# [추가] 현재 선택된 노트 타입 (임시)

current_note_type_name = note_type_names[0] if note_type_names else None
DELETE_TIME_TOLERANCE_MS = 50

# [추가] 롱노트 배치를 위한 에디터 상태
STATE_IDLE = 0            # 기본 상태
STATE_PLACING_LONG = 1    # 롱노트의 끝점을 기다리는 상태
editor_state = STATE_IDLE

# [추가] 롱노트 시작점 정보 임시 저장
pending_long_note_start = None # e.g., {"time_ms": 1000, "lane": 0, "type_name": "Long"}
last_played_time_ms = 0.0

# --- 5. 메인 루프 ---
running = True
while running:
    time_delta = clock.tick(60) / 1000.0

    # (1) 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)
        # [수정] pygame-gui 이벤트 처리
        if event.type == pygame.MOUSEWHEEL:
            # [수정] GUI가 마우스를 쓰고 있지 '않을' 때만 캔버스 스크롤
            if EDITOR_RECT.collidepoint(pygame.mouse.get_pos()):
                if not audio_manager.is_playing:
                    
                    # 1. Alt 키가 눌렸는지 확인
                    keys = pygame.key.get_pressed()
                    is_alt_pressed = keys[pygame.K_LALT] or keys[pygame.K_RALT]

                    # 2. 기본 스크롤 속도
                    base_scroll_speed = (1000.0 / scale_pixels_per_ms) * 0.1
                    
                    # 3. [수정] event.y를 그대로 사용해서 방향 반전 (1: 미래, -1: 과거)
                    scroll_amount_ms = event.y * base_scroll_speed 

                    # 4. Alt 키 눌렀으면 1/10로 느리게
                    if is_alt_pressed:
                        scroll_amount_ms *= 0.1 # 10배 느리게

                    # 5. [수정] -= 를 += 로 변경
                    current_time_ms += scroll_amount_ms 
                    current_time_ms = max(0, current_time_ms)
        
        # [수정] 마우스 클릭 (노트 배치 & 삭제)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if manager.get_hovering_any_element():
                continue                
                # 1. 공통 계산: 클릭한 레인과 시간
            if EDITOR_RECT.collidepoint(event.pos):
                num_lanes = current_chart.num_lanes
                lane_width = EDITOR_RECT.width / num_lanes
                mouse_x_in_canvas = event.pos[0] - EDITOR_RECT.left
                lane = int(mouse_x_in_canvas // lane_width)
                
                raw_time_ms = editor_canvas.screen_y_to_time(
                    event.pos[1], 
                    current_time_ms, 
                    scale_pixels_per_ms, 
                    judgement_line_y
                )

                # 스냅 적용 (공통)
                beat_ms = 60000.0 / current_chart.bpm
                if current_snap_division == 0: current_snap_division = 1
                snap_ms = beat_ms / (current_snap_division / 4.0)
                snapped_time_ms = round(raw_time_ms / snap_ms) * snap_ms

                # --- (1) 좌클릭: 노트 배치 (상태별 분기) ---
                if event.button == 1: 
                    
                    # === 상태 1: 기본 (STATE_IDLE) ===
                    if editor_state == STATE_IDLE:
                        if current_note_type_name:
                            note_type = current_chart.note_types.get(current_note_type_name)
                            if not note_type: continue # <-- 'break'를 'continue'로 수정!
                            if note_type.is_long_note:
                                # 롱노트 -> 시작점 기록 및 상태 변경
                                pending_long_note_start = {
                                    "time_ms": snapped_time_ms,
                                    "lane": lane,
                                    "type_name": current_note_type_name
                                }
                                editor_state = STATE_PLACING_LONG
                                print(f"롱노트 시작점: {snapped_time_ms}ms, Lane {lane}")
                            else:
                                # 단노트 -> 즉시 배치
                                new_note = chart.Note(snapped_time_ms, current_note_type_name, lane)
                                current_chart.notes.append(new_note)

                    # === 상태 2: 롱노트 끝점 대기 (STATE_PLACING_LONG) ===
                    elif editor_state == STATE_PLACING_LONG:
                        # 클릭한 레인이 시작점과 같은지 확인
                        if lane == pending_long_note_start["lane"]:
                            start_time = pending_long_note_start["time_ms"]
                            end_time = snapped_time_ms
                            
                            # 시작 시간과 끝 시간 보정 (항상 end > start)
                            if end_time < start_time:
                                start_time, end_time = end_time, start_time # 시간 스왑

                            if end_time == start_time:
                                # 요청사항: "클릭하고 다시 클릭하면 단노트"
                                # 단, 롱노트 타입이므로 'Tap' 타입으로 강제 변경
                                new_note = chart.Note(start_time, "Tap", lane)
                                print("롱노트 -> 단노트로 변경 배치")
                            else:
                                # 롱노트 완성
                                new_note = chart.Note(
                                    start_time,
                                    pending_long_note_start["type_name"],
                                    lane,
                                    end_time_ms=end_time
                                )
                                print(f"롱노트 완성: {start_time} ~ {end_time}ms")
                            
                            current_chart.notes.append(new_note)

                        else:
                            # 다른 레인을 클릭함 (무시 또는 취소)
                            print("롱노트 취소: 다른 레인 클릭")

                        # 상태 초기화
                        editor_state = STATE_IDLE
                        pending_long_note_start = None

                # --- (2) 우클릭: 노트 삭제 / 롱노트 취소 ---
                if event.button == 3: 
                    
                    # [추가] 롱노트 배치 중이었다면 취소
                    if editor_state == STATE_PLACING_LONG:
                        editor_state = STATE_IDLE
                        pending_long_note_start = None
                        print("롱노트 배치 취소 (우클릭)")
                    else:
                        # 기존 노트 삭제 로직 (동일)
                        note_to_delete = None
                        for note in reversed(current_chart.notes):
                            if note.lane == lane:
                                if abs(note.time_ms - raw_time_ms) < DELETE_TIME_TOLERANCE_MS:
                                    note_to_delete = note
                                    break
                        if note_to_delete:
                            current_chart.notes.remove(note_to_delete)
                            print(f"노트 삭제됨: {note_to_delete.time_ms}ms, Lane {note_to_delete.lane}")

        if event.type == pygame_gui.UI_BUTTON_PRESSED: # <--- 이렇게 수정
            if event.ui_element == play_pause_button:
                if audio_manager.is_playing:
                    # 재생 중 -> 일시정지
                    audio_manager.pause()
                    play_pause_button.set_text('Play')
                else:
                    # 멈춤 상태 -> 재생

                    # 1. 일시정지 상태(paused_time > 0)였는지 확인
                    if audio_manager.get_pos_ms() > 0:
                        audio_manager.unpause()
                    else:
                        # 2. 완전히 정지(stop)된 상태였으면 current_time_ms에서 재생
                        audio_manager.play(current_time_ms)

                    play_pause_button.set_text('Pause')

            if event.ui_element == stop_button:
                audio_manager.stop()
                current_time_ms = 0.0 # 정지 시 에디터 시간도 0으로
                # audio_manager.paused_time = 0.0 # audio_manager.stop()이 이걸 해줌
                play_pause_button.set_text('Play')
                
            if event.ui_element == load_song_button:
                # 파일 대화상자 생성
               
                file_dialog = UIFileDialog(pygame.Rect(100, 100, 400, 300),
                                            manager,
                                            window_title='Open Song File...',
                                            allow_existing_files_only=True,
                                            object_id='#load_song_dialog') # <-- [수정] object_id 추가!
            
            if event.ui_element == save_chart_button:
                file_dialog = UIFileDialog(pygame.Rect(100, 100, 400, 300),
                                        manager,
                                        window_title='Save Chart As...',
                                        allow_existing_files_only=False,
                                        object_id='#save_chart_dialog')

            # [추가] Load Chart 버튼
            if event.ui_element == load_chart_button:
                file_dialog = UIFileDialog(pygame.Rect(100, 100, 400, 300),
                                        manager,
                                        window_title='Open Chart File...',
                                        allow_existing_files_only=True,
                                        object_id='#load_chart_dialog')
                
            # 1. [+] 버튼 (기본 -> "새 노트" 에디터)
            if event.ui_element == new_note_type_button:
                editor_mode = "new" # [수정] '새로 만들기' 모드

                for element in default_ui_elements:
                    element.hide()
                for element in editor_ui_elements:
                    element.show()

                # [수정] 에디터 필드 초기화
                editor_title.set_text("New Note Type")
                editor_name_entry.set_text("")
                editor_name_entry.enable() # [수정] 이름 칸 활성화!

                editor_selected_color = (255, 255, 255)
                editor_color_button.colours['normal_bg'] = pygame.Color(editor_selected_color) 
                editor_color_button.rebuild()
                editor_is_long_check.set_state(False)
                editor_hitsound_check.set_state(True)

            # [신규!] 2. [Edit] 버튼 (기본 -> "노트 편집" 에디터)
            if event.ui_element == edit_note_type_button:
                if editing_note_name is None: # (선택된 노트가 없으면 무시)
                    break

                editor_mode = "edit" # [수정] '편집' 모드

                for element in default_ui_elements:
                    element.hide()
                for element in editor_ui_elements:
                    element.show()

                # [수정] '편집할 노트' 정보로 UI 채우기
                note_to_edit = current_chart.note_types[editing_note_name]

                editor_title.set_text(f"Edit: {note_to_edit.name}")
                editor_name_entry.set_text(note_to_edit.name)
                editor_name_entry.disable() # [수정] 이름(Key)은 변경 못하게 막기!

                editor_selected_color = note_to_edit.color
                editor_color_button.colours['normal_bg'] = pygame.Color(note_to_edit.color)
                editor_color_button.rebuild()

                editor_is_long_check.set_state(note_to_edit.is_long_note)
                editor_hitsound_check.set_state(note_to_edit.play_hitsound)

            # 3. [Cancel] 버튼 (에디터 -> 기본)
            if event.ui_element == editor_cancel_button:
                for element in editor_ui_elements:
                    element.hide()
                for element in default_ui_elements:
                    element.show()

            # 4. [OK] 버튼 (에디터 -> 기본 + 노트 생성/수정)
            if event.ui_element == editor_ok_button:

                if editor_mode == "new":
                    # --- '새로 만들기' 모드 로직 (기존과 동일) ---
                    new_name = editor_name_entry.get_text()
                    if not new_name:
                        print("에러: 노트 이름이 비어있음")
                    elif new_name in current_chart.note_types:
                        print(f"에러: '{new_name}' 이름이 이미 존재함")
                    else:
                        new_type = chart.NoteType(
                            name=new_name,
                            color=editor_selected_color,
                            is_long_note=editor_is_long_check.is_selected,
                            play_hitsound=editor_hitsound_check.is_selected
                        )
                        current_chart.note_types[new_name] = new_type

                        new_item_list = list(current_chart.note_types.keys())
                        note_type_list.set_item_list(new_item_list)

                        for element in editor_ui_elements:
                            element.hide()
                        for element in default_ui_elements:
                            element.show()

                elif editor_mode == "edit":
                    # --- [신규!] '편집' 모드 로직 ---

                    # (이름은 비활성화되어 있으니, editing_note_name을 사용)
                    note_to_edit = current_chart.note_types[editing_note_name]

                    # 1. 값 덮어쓰기
                    note_to_edit.color = editor_selected_color
                    note_to_edit.is_long_note = editor_is_long_check.is_selected
                    note_to_edit.play_hitsound = editor_hitsound_check.is_selected

                    print(f"'{note_to_edit.name}' 노트 타입 수정 완료!")

                    # 2. 기본 뷰로 복귀
                    for element in editor_ui_elements:
                        element.hide()
                    for element in default_ui_elements:
                        element.show()
        
            # 2. [Cancel] 버튼 (에디터 -> 기본)
            if event.ui_element == editor_cancel_button:
                for element in editor_ui_elements:
                    element.hide()
                for element in default_ui_elements:
                    element.show()

            # 3. [OK] 버튼 (에디터 -> 기본 + 노트 생성)
            if event.ui_element == editor_ok_button:
                new_name = editor_name_entry.get_text()
                
                if not new_name:
                    print("에러: 노트 이름이 비어있음")
                elif new_name in current_chart.note_types:
                    print(f"에러: '{new_name}' 이름이 이미 존재함")
                else:
                    new_type = chart.NoteType(
                        name=new_name,
                        color=editor_selected_color, # (차트 데이터에는 튜플로 저장해도 OK)
                        is_long_note=editor_is_long_check.is_checked,
                        play_hitsound=editor_hitsound_check.is_checked
                    )
                    current_chart.note_types[new_name] = new_type
                    
                    new_item_list = list(current_chart.note_types.keys())
                    note_type_list.set_item_list(new_item_list)
                    
                    for element in editor_ui_elements:
                        element.hide()
                    for element in default_ui_elements:
                        element.show()

            # 4. [Pick Color] 버튼
            if event.ui_element == editor_color_button:
                if color_picker:
                    color_picker.kill()
                color_picker = UIColourPickerDialog(pygame.Rect(100, 100, 300, 300),
                                                   manager,
                                                   window_title="Pick a color...")
                editor_color_button.disable()

            for i, preset_btn in enumerate(editor_preset_buttons):
                if event.ui_element == preset_btn:
                    # 1. 선택된 색깔을 바로 저장
                    editor_selected_color = PRESET_COLORS[i] 

                    # 2. [Pick Color] 버튼 색깔도 업데이트 (시각적 피드백)
                    color_obj = pygame.Color(editor_selected_color)
                    editor_color_button.colours['normal_bg'] = color_obj
                    editor_color_button.rebuild()
                    print(f"프리셋 색상 {i}번 선택: {editor_selected_color}")
                    break # 버튼 찾았으니 루프 종료
            
        # [추가] 스케일 슬라이더 이벤트
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == scale_slider:
                scale_pixels_per_ms = event.value

        # [추가] 스냅 드롭다운 이벤트
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == snap_dropdown:
                current_snap_division = int(event.text)

        # [추가] 노트 타입 리스트 선택 이벤트
        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION: 
            if event.ui_element == note_type_list:
                current_note_type_name = event.text
                editing_note_name = event.text # (편집할 노트 이름 기억)
                edit_note_type_button.enable() # (버튼 활성화!)
                print(f"노트 타입 변경: {current_note_type_name}")
        
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == bpm_entry:
                try:
                    new_bpm = float(event.text)
                    if new_bpm > 0:
                        current_chart.bpm = new_bpm
                        print(f"BPM 변경됨: {new_bpm}")
                    else:
                        bpm_entry.set_text(str(current_chart.bpm)) # 0 이하면 원래대로
                except ValueError:
                    # 숫자가 아니면 원래 BPM으로 되돌리기
                    bpm_entry.set_text(str(current_chart.bpm))
            if event.ui_element == offset_entry:
                try:
                    new_offset = int(event.text)
                    current_chart.offset_ms = new_offset
                    print(f"Offset 변경됨: {new_offset}ms")
                except ValueError:
                    # 숫자가 아니면 원래 Offset으로 되돌리기
                    offset_entry.set_text(str(current_chart.offset_ms))        
        # [추가] 파일 대화상자 이벤트 처리
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            # 1. 노래 로드
            if event.ui_object_id == '#load_song_dialog':
                song_path = event.text
                if audio_manager.load_song(song_path):
                    total_time_ms = audio_manager.get_length_ms()
                    current_time_ms = 0.0
                    last_played_time_ms = 0.0 # <-- [추가!] 마지막 시간도 0으로!
                    song_name_label.set_text(song_path.split('/')[-1].split('\\')[-1])
                    current_chart.song_path = song_path
                else:
                    song_name_label.set_text('Load Failed!')

            # 2. 차트 저장
            elif event.ui_object_id == '#save_chart_dialog':
                current_chart.save_to_json(event.text)

            # 3. 차트 불러오기
            elif event.ui_object_id == '#load_chart_dialog':
                if current_chart.load_from_json(event.text):
                    # [핵심] 불러오기 성공 후 UI 새로고침
                    bpm_entry.set_text(str(current_chart.bpm))
                    new_item_list = list(current_chart.note_types.keys())
                    note_type_list.set_item_list(new_item_list)
                    # (노래 이름도 업데이트)
                    if current_chart.song_path:
                        song_name_label.set_text(current_chart.song_path.split('/')[-1].split('\\')[-1])
                    else:
                        song_name_label.set_text("No song loaded.")
                else:
                    print("차트 불러오기 실패 (파일 오류)")
            elif event.ui_object_id == '#load_chart_dialog':
                if current_chart.load_from_json(event.text):
                    # [핵심] 불러오기 성공 후 UI 새로고침
                    bpm_entry.set_text(str(current_chart.bpm))
                    offset_entry.set_text(str(current_chart.offset_ms))
                    lane_dropdown.set_text(str(current_chart.num_lanes)) # <-- 이 줄을 추가!
                    new_item_list = list(current_chart.note_types.keys())
                    note_type_list.set_item_list(new_item_list)

        # [추가] 색상 선택기 팝업 이벤트
        if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            if event.ui_element == color_picker:
                # [수정!] Color 객체 -> (R, G, B) 튜플로 변환해서 저장!
                editor_selected_color = (event.colour.r, event.colour.g, event.colour.b) 

                # [수정!] 버튼 색깔 지정은 Color 객체로!
                editor_color_button.colours['normal_bg'] = event.colour
                editor_color_button.rebuild()
                editor_color_button.enable()
                color_picker = None
        
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == color_picker:
                editor_color_button.enable()
                color_picker = None

        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            # 1. 스냅 변경
            if event.ui_element == snap_dropdown:
                current_snap_division = int(event.text)
            
            # 2. [신규] 라인 수 변경
            elif event.ui_element == lane_dropdown:
                current_chart.num_lanes = int(event.text)
                print(f"라인 수 변경: {current_chart.num_lanes}")


    manager.update(time_delta)

    if audio_manager.is_playing:
        # 1. 현재 시간 가져오기
        current_time_ms = audio_manager.get_pos_ms()

        # (버그 1: 중복된 '노래 끝' 체크 삭제!)
        # (버그 2: 'last_played_time_ms' 업데이트를 맨 뒤로 이동!)

        # 2. [추가] 히트사운드 재생 체크
        # (last_played_time_ms는 '이전 프레임'의 시간을 잘 갖고 있음!)
        for note in current_chart.notes:
            note_type = current_chart.note_types.get(note.note_type_name)
            if not (note_type and note_type.play_hitsound):
                continue # 히트사운드 재생 안 하는 노트면 스킵
                
            # 단노트 타이밍 체크
            if note.time_ms > last_played_time_ms and note.time_ms <= current_time_ms:
                audio_manager.play_hitsound()
            
            # 롱노트 끝나는 타이밍 체크
            if note.end_time_ms:
                 if note.end_time_ms > last_played_time_ms and note.end_time_ms <= current_time_ms:
                    audio_manager.play_hitsound()

        # 3. 노래 끝났는지 체크 (기존 코드)
        if current_time_ms > total_time_ms and total_time_ms > 0:
            audio_manager.stop()
            current_time_ms = total_time_ms # 시간을 노래 끝에 고정
            play_pause_button.set_text('Play')
        
        # 4. [수정!] '다음 프레임'을 위해, '현재 시간'을 '마지막 시간'으로 덮어쓰기
        last_played_time_ms = current_time_ms
        
    else:
        # [추가] 재생 중이 아닐 때는 last_played_time_ms를 현재 스크롤 위치로 리셋
        last_played_time_ms = current_time_ms
    # [수정] 시간 레이블 업데이트 (기존 코드)
    current_sec = current_time_ms / 1000.0
    total_sec = total_time_ms / 1000.0
    time_label.set_text(f'{current_sec:.3f} / {total_sec:.3f}')


    # (3) 렌더링 (그리기)
    screen.fill((30, 30, 30))
    # pygame.draw.rect(screen, (50, 50, 50), EDITOR_RECT)
    editor_canvas.draw_canvas(screen, 
                              EDITOR_RECT, 
                              current_chart, 
                              current_time_ms, 
                              scale_pixels_per_ms, 
                              judgement_line_y,
                              current_snap_division,
                              editor_state,             # <-- 추가
                              pending_long_note_start)  # <-- 추가
    
    # [추가] 2. 파형 그리기
    waveform, sr = audio_manager.get_waveform_data()

    time_at_top = editor_canvas.screen_y_to_time(
        EDITOR_RECT.top, current_time_ms, scale_pixels_per_ms, judgement_line_y
    )
    time_at_bottom = editor_canvas.screen_y_to_time(
        EDITOR_RECT.bottom, current_time_ms, scale_pixels_per_ms, judgement_line_y
    )

    # [수정] 'left_panel.image' 대신 'screen'에 'left_panel_rect'를 넘겨줍니다.
    
    # print(waveform)
    editor_canvas.draw_waveform(screen, 
                                left_panel_rect, # <-- 여기!
                                waveform, 
                                sr, 
                                time_at_top, 
                                time_at_bottom)

    # [수정] 3. 파형 패널에도 판정선 그리기 ('screen'에)
    judgement_line_y_ratio = judgement_line_y / EDITOR_RECT.height
    judgement_line_y_in_wave_panel = judgement_line_y_ratio * left_panel_rect.height

    # [수정] 'wave_panel_surface' 대신 'screen'에 'left_panel_rect' 기준으로 그립니다.
    pygame.draw.line(screen, (255, 255, 0), 
                    (left_panel_rect.left, judgement_line_y_in_wave_panel), 
                    (left_panel_rect.right, judgement_line_y_in_wave_panel), 1)
    manager.draw_ui(screen)
    pygame.display.update()

pygame.quit()