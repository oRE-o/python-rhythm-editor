import pygame
import librosa # [복구] librosa 임포트
import numpy as np # [추가] numpy 임포트

# 오디오 시스템 초기화
# pygame.mixer.init()

# --- 상태 변수 ---
current_song_path = ""
is_playing = False
start_time_offset = 0.0 # 재생 시작 오프셋 (pygame.time.get_ticks() 기준)
paused_time = 0.0 # 일시정지 시점
total_song_length_ms = 0.0 # 노래 총 길이 (별도 저장)

current_waveform = None # (샘플 배열)
current_waveform_sr = 0   # (샘플 레이트)
hitsound = None
HITSOUND_CHANNEL = pygame.mixer.Channel(1) # 히트사운드는 1번 채널

try:
    print("가짜 파형 생성 중...")
    _FAKE_SR = 44100
    t = np.linspace(0., 10., int(10 * _FAKE_SR), endpoint=False)
    _FAKE_WAVEFORM = 0.5 * np.sin(2 * np.pi * 220 * t) + 0.3 * np.sin(2 * np.pi * 440 * t)
    print("가짜 파형 생성 완료!")
except Exception as e:
    print(f"가짜 파형 생성 실패: {e}")
    _FAKE_WAVEFORM = None
    _FAKE_SR = 0
# --- [테스트 끝] ---

def load_hitsound(path):
    """타격음 파일을 로드합니다."""
    global hitsound
    try:
        hitsound = pygame.mixer.Sound(path)
        hitsound.set_volume(0.5) # 타격음 볼륨 (0.0 ~ 1.0)
        print(f"히트사운드 로드 성공: {path}")
    except Exception as e:
        print(f"히트사운드 로드 실패: {e}")
        hitsound = None

# [추가] 히트사운드 재생 함수
def play_hitsound():
    """타격음을 재생합니다."""
    if hitsound:
        HITSOUND_CHANNEL.play(hitsound)

def load_song(path):
    """(librosa 버전) 음악 파일을 로드하고 파형을 분석합니다."""
    global current_song_path, is_playing, total_song_length_ms, paused_time
    global current_waveform, current_waveform_sr
    
    try:
        # 1. music 모듈에 로드 (재생용)
        pygame.mixer.music.load(path)
        
        # 2. Sound 객체로 로드 (총 길이 계산용)
        temp_sound = pygame.mixer.Sound(path)
        total_song_length_ms = temp_sound.get_length() * 1000.0
        
        # 3. [librosa]로 파형 분석
        print("파형 분석 시작 (librosa)... (파일 크기에 따라 시간이 걸릴 수 있음)")
        current_waveform, current_waveform_sr = librosa.load(path, sr=None, mono=True)
        print(f"파형 분석 완료 (librosa): {len(current_waveform)} 샘플, {current_waveform_sr} Hz")
        
        current_song_path = path
        is_playing = False
        paused_time = 0.0
        print(f"'{path}' 로드 성공 (길이: {total_song_length_ms / 1000.0:.3f}s)")
        return True
    except Exception as e: 
        print(f"오디오 로드 또는 분석 실패 (librosa): {e}")
        current_song_path = ""
        total_song_length_ms = 0.0
        current_waveform = None
        return False

# [추가] 파형 데이터를 가져오는 함수
def get_waveform_data():
    return current_waveform, current_waveform_sr # <-- 실제 파형 (일단 주석)

def play(start_offset_ms=0.0):
    """음악을 재생합니다 (지정한 시간부터)."""
    global is_playing, start_time_offset, paused_time
    
    if not current_song_path:
        print("재생할 노래가 로드되지 않았습니다.")
        return

    if is_playing:
        return # 이미 재생 중이면 아무것도 안 함

    try:
        # 1. music 모듈에 재생 시작 (start는 초 단위)
        pygame.mixer.music.play(loops=0, start=start_offset_ms / 1000.0)
        
        # 2. 우리 내부 타이머도 동기화
        start_time_offset = pygame.time.get_ticks() - start_offset_ms
        paused_time = 0.0
        is_playing = True
        
    except pygame.error as e:
        print(f"재생 오류: {e}")
        is_playing = False


def stop():
    """음악을 정지하고 처음으로 되돌립니다."""
    global is_playing, paused_time
    if not current_song_path: return
    
    pygame.mixer.music.stop()
    is_playing = False
    paused_time = 0.0 # 정지 시에는 paused_time도 0으로 (재생 위치 리셋)

def pause():
    """음악을 일시정지합니다."""
    global is_playing, paused_time
    if not is_playing: return
    
    pygame.mixer.music.pause()
    is_playing = False
    # get_pos_ms()를 위해 현재 시간 기록
    paused_time = (pygame.time.get_ticks() - start_time_offset)

def unpause():
    """일시정지를 해제합니다."""
    global is_playing, start_time_offset, paused_time
    if not current_song_path or is_playing: return
    
    pygame.mixer.music.unpause()
    is_playing = True
    # 현재 시간 기준으로 start_time_offset을 재설정
    start_time_offset = pygame.time.get_ticks() - paused_time
    paused_time = 0.0

def get_pos_ms():
    """
    현재 재생 시간을 밀리초(ms) 단위로 반환합니다.
    (music.get_pos() 대신 내부 타이머 사용)
    """
    if is_playing:
        # pygame.time.get_ticks()는 Pygame 시작 후 총 시간(ms)
        return (pygame.time.get_ticks() - start_time_offset)
    else:
        # 정지 또는 일시정지 상태
        return paused_time

def get_length_ms():
    """현재 음악의 총 길이를 밀리초(ms) 단위로 반환합니다."""
    return total_song_length_ms