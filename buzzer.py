import pygame
import time
import serial
import threading
from collections import deque

# --- CONFIG ---
BUZZ_WINDOW = 0.5  # seconds
PORT = 'COM8'
BAUDRATE = 9600

# --- INIT ---
pygame.init()
pygame.mixer.init()

# Sounds
buzzer_sound = pygame.mixer.Sound("buzzer.wav")
sounds = {
    "P1": pygame.mixer.Sound("player1.wav"),
    "P2": pygame.mixer.Sound("player2.wav"),
    "P3": pygame.mixer.Sound("player3.wav"),
}

# GUI setup
WIDTH, HEIGHT = 500, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer Buzzer & Scoreboard")
font = pygame.font.SysFont(None, 48)

# Serial setup
arduino = serial.Serial(PORT, BAUDRATE, timeout=1)
time.sleep(2)  # wait for Arduino reset

# State
scores = {"P1": 0, "P2": 0, "P3": 0}
last_player = None
cooldown_active = False
last_play_time = 0
conflict_message = None
trigger_lock = threading.Lock()
buzz_queue = deque()

# Draw scoreboard
def draw_scores(message=None):
    screen.fill((30, 30, 30))
    y = 80
    for player, score in scores.items():
        color = (255, 255, 255) if player != last_player else (255, 215, 0)
        label = font.render(f"{player}: {score}", True, color)
        screen.blit(label, (50, y))
        y += 60

    if message:
        msg = font.render(message, True, (255, 100, 100))
        screen.blit(msg, (50, HEIGHT - 60))

    pygame.display.flip()

# Trigger player
def trigger_player(player_key):
    global cooldown_active, last_play_time, last_player
    if not cooldown_active:
        with trigger_lock:
            print(f"{player_key} triggered!")
            buzzer_sound.play()
            time.sleep(0.5)
            sounds[player_key].play()
            last_player = player_key
            cooldown_active = True
            last_play_time = time.time()

# Resolution logic
def trigger_resolution_loop():
    global cooldown_active, last_play_time, last_player, conflict_message
    while True:
        if len(buzz_queue) > 0:
            now = time.time()
            recent_buzzes = [(p, t) for p, t in buzz_queue if now - t <= BUZZ_WINDOW]
            buzz_queue.clear()

            if len(recent_buzzes) >= 2:
                conflicted_players = [p for p, _ in recent_buzzes]
                conflict_message = f"\u26a0\ufe0f Conflict: {' & '.join(conflicted_players)}"
                print(conflict_message)
                with trigger_lock:
                    cooldown_active = True
                    last_player = None
                    last_play_time = time.time()
                time.sleep(1)
                conflict_message = None

            elif len(recent_buzzes) == 1:
                player_key, _ = recent_buzzes[0]
                trigger_player(player_key)

        time.sleep(0.05)

# Poller class
class ButtonPoller(threading.Thread):
    def __init__(self, player_key, match_string):
        super().__init__(daemon=True)
        self.player_key = player_key
        self.match_string = match_string

    def run(self):
        while True:
            if arduino.in_waiting > 0 and not cooldown_active:
                line = arduino.readline().decode('utf-8').strip()
                if line == self.match_string:
                    buzz_queue.append((self.player_key, time.time()))

# Start pollers and resolver
pollers = [
    ButtonPoller("P1", "PLAYER_1"),
    ButtonPoller("P2", "PLAYER_2"),
    ButtonPoller("P3", "PLAYER_3"),
]
for p in pollers:
    p.start()

threading.Thread(target=trigger_resolution_loop, daemon=True).start()

# Main loop
running = True
while running:
    draw_scores(conflict_message)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_ESCAPE:
                running = False

            elif key == pygame.K_i:
                buzz_queue.append(("P1", time.time()))
            elif key == pygame.K_o:
                buzz_queue.append(("P2", time.time()))
            elif key == pygame.K_u:
                buzz_queue.append(("P3", time.time()))

            elif last_player:
                if key == pygame.K_1:
                    scores[last_player] += 10
                elif key == pygame.K_2:
                    scores[last_player] += 5
                elif key == pygame.K_3:
                    scores[last_player] -= 10

    if cooldown_active and time.time() - last_play_time >= 5:
        cooldown_active = False
        last_player = None

pygame.quit()
