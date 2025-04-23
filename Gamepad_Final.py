import pygame
import sys
import time # Import the time module for tracking cooldown and reaction time

print("""
.-------------------------------------------------------.
| ____   ___   ____ ____ ____    ____   ___ ____  ____  |
||  _ \ / _ \ / ___/ ___/ ___|  |___ \ / _ \___ \| ___| |
|| |_) | | | | |  _\___ \___ \    __) | | | |__) |___ \ |
||  __/| |_| | |_| |___) |__) |  / __/| |_| / __/ ___) ||
||_|    \___/ \____|____/____/  |_____|\___/_____|____/ |
'-------------------------------------------------------'
""")

# Initialize Pygame
pygame.init()
pygame.joystick.init()
pygame.mixer.init() # Initialize the mixer for sound
pygame.font.init() # Initialize the font module for text rendering

# --- Configuration ---
# Screen dimensions
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("POGSS 2025 SCOREBOARD")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Cooldown duration in milliseconds (5 seconds)
COOLDOWN_DURATION = 5000

# --- Font Setup ---
# Use the default system font
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 20)

# --- Sound Setup ---
try:
    buzzer_sound = pygame.mixer.Sound("buzzer.wav")
except pygame.error as e:
    print(f"Warning: Could not load buzzer.wav: {e}")
    buzzer_sound = None # Set to None if loading fails

# --- Joystick Setup ---
joysticks = []
for i in range(pygame.joystick.get_count()):
    joysticks.append(pygame.joystick.Joystick(i))
    joysticks[-1].init()
    print(f"Detected Joystick {i}: {joysticks[-1].get_name()}")

if not joysticks:
    print("No joysticks detected. Please connect a gamepad and restart the script.")
    # Display error message on screen before quitting
    error_text = font.render("No joysticks detected. Connect gamepad and restart.", True, RED)
    screen.fill(BLACK)
    screen.blit(error_text, (50, screen_height // 2 - 20))
    pygame.display.flip()
    pygame.time.wait(3000) # Wait 3 seconds before quitting
    pygame.quit()
    sys.exit()


joystick = joysticks[0]

# --- Game State ---
game_state = "mapping_p1" # States: mapping_p1, mapping_p2, waiting, buzzed
player_buttons = {1: None, 2: None}
player_scores = {1: 0, 2: 0} # Initialize scores
buzzed_player = None
last_buzz_time = 0 # Variable to store the time of the last valid buzz for cooldown
waiting_start_time = 0 # Variable to store the time when the game enters the 'waiting' state

# Variable to hold the winning buzz event for the current frame
# Format: (player_number, buzz_time) or None
winning_buzz_this_frame = None

# --- Text Rendering Helper ---
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

print("\n--- Game Setup ---")
print("Press the button for Player 1.")

# --- Main Game Loop ---
running = True
while running:
    # Get current time in milliseconds
    current_time = pygame.time.get_ticks()

    # Reset winning buzz for this frame at the start of each loop iteration
    winning_buzz_this_frame = None

    # --- Event Handling ---
    # Process all events in the queue for this frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle joystick button presses
        if event.type == pygame.JOYBUTTONDOWN:
            button = event.button
            # print(f"Button {button} pressed on Joystick {event.joy}") # Uncomment for debugging button presses

            if game_state == "mapping_p1":
                # Assign this button to Player 1
                player_buttons[1] = button
                print(f"Button {button} assigned to Player 1.")
                game_state = "mapping_p2"
                print("Press the button for Player 2.")

            elif game_state == "mapping_p2":
                # Assign this button to Player 2
                if button == player_buttons[1]:
                    print("This button is already assigned to Player 1. Please choose a different button for Player 2.")
                else:
                    player_buttons[2] = button
                    print(f"Button {button} assigned to Player 2.")
                    game_state = "waiting"
                    waiting_start_time = current_time # Record the time when waiting starts
                    print("\n--- Game Started ---")
                    print("Waiting for a buzz...")
                    print("Press the ESC key to reset.")

            elif game_state == "waiting":
                # Check if the cooldown has passed before processing a buzz
                if current_time - last_buzz_time > COOLDOWN_DURATION:
                    # Check if the pressed button is one of the player buttons
                    if button == player_buttons[1] or button == player_buttons[2]:
                        # If this is the first valid buzz detected in this frame's event queue
                        if winning_buzz_this_frame is None:
                            buzzer_player = 1 if button == player_buttons[1] else 2
                            # Use the current_time from the main loop as the buzz time
                            # Pygame event queue order determines which event is processed first
                            buzz_time = current_time
                            winning_buzz_this_frame = (buzzer_player, buzz_time)

                # else:
                    # print("Cooldown active. Please wait.") # Uncomment for debugging cooldown

        # Handle keyboard input for scoring, resetting, and exiting
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "buzzed":
                    print("\n--- Game Reset ---")
                    game_state = "waiting"
                    buzzed_player = None
                    last_buzz_time = 0 # Reset cooldown timer on game reset
                    waiting_start_time = pygame.time.get_ticks() # Reset waiting start time
                    print("Waiting for a buzz...")
            # Scoring keys - only active when a player has buzzed
            elif game_state == "buzzed" and buzzed_player is not None:
                if event.key == pygame.K_f:
                    player_scores[buzzed_player] += 10
                    print(f"Player {buzzed_player} score +10. New score: {player_scores[buzzed_player]}")
                elif event.key == pygame.K_g:
                    player_scores[buzzed_player] += 5
                    print(f"Player {buzzed_player} score +5. New score: {player_scores[buzzed_player]}")
                elif event.key == pygame.K_h:
                    player_scores[buzzed_player] -= 10
                    print(f"Player {buzzed_player} score -10. New score: {player_scores[buzzed_player]}")
            # Exit key
            elif event.key == pygame.K_p:
                running = False # Set running to False to exit the main loop


    # --- Process the winning buzz for this frame (after all events are handled) ---
    # Check if a winning buzz was recorded during the event processing for this frame
    if game_state == "waiting" and winning_buzz_this_frame is not None:
        buzzed_player, buzz_time = winning_buzz_this_frame
        game_state = "buzzed"
        last_buzz_time = buzz_time # Record the time of this buzz
        reaction_time = buzz_time - waiting_start_time # Calculate reaction time
        if buzzer_sound:
            buzzer_sound.play() # Play the buzzer sound
        print(f"\n!!! PLAYER {buzzed_player} BUZZED FIRST !!! Reaction Time: {reaction_time} ms")
        print("Press the ESC key to reset.")


    # --- Drawing ---
    screen.fill(BLACK) # Clear the screen

    # Display scores
    draw_text(f"Player 1 Score: {player_scores[1]}", font, WHITE, screen, 50, 50)
    draw_text(f"Player 2 Score: {player_scores[2]}", font, WHITE, screen, screen_width - 250, 50) # Adjust position for Player 2

    # Display game state/instructions
    if game_state == "mapping_p1":
        draw_text("Press the button for Player 1", font, WHITE, screen, 50, screen_height // 2 - 20)
    elif game_state == "mapping_p2":
        draw_text("Press the button for Player 2", font, WHITE, screen, 50, screen_height // 2 - 20)
    elif game_state == "waiting":
        draw_text("Waiting for a buzz...", font, GREEN, screen, 50, screen_height // 2 - 20)
        draw_text("Press ESC to reset.", small_font, WHITE, screen, 50, screen_height // 2 + 20)
        draw_text("Press P to exit.", small_font, WHITE, screen, 50, screen_height // 2 + 40) # Add exit instruction
    elif game_state == "buzzed":
        reaction_time = last_buzz_time - waiting_start_time # Recalculate for display
        draw_text(f"PLAYER {buzzed_player} BUZZED FIRST!", font, BLUE, screen, 50, screen_height // 2 - 40)
        draw_text(f"Reaction Time: {reaction_time} ms", font, BLUE, screen, 50, screen_height // 2)
        draw_text("Press F (+10), G (+5), H (-10) to score.", small_font, WHITE, screen, 50, screen_height // 2 + 40)
        draw_text("Press ESC to reset for next round.", small_font, WHITE, screen, 50, screen_height // 2 + 60)
        draw_text("Press P to exit.", small_font, WHITE, screen, 50, screen_height // 2 + 80) # Add exit instruction
	

    pygame.display.flip() # Update the display

# --- Cleanup ---
pygame.quit()
sys.exit()
