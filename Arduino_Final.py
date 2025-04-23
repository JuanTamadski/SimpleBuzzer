import serial
import time
import sys
import pygame

# --- Configuration ---
# List of potential serial ports to check
SERIAL_PORTS_TO_CHECK = ['COM7', 'COM8', 'COM3', '/dev/ttyACM0', '/dev/ttyUSB0'] # Add ports relevant to your OS
BAUD_RATE = 9600 # Must match the baud rate set in the Arduino code (Serial.begin(9600))

# Screen dimensions
screen_width = 600
screen_height = 400

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Cooldown duration in milliseconds (5 seconds) - Applied after a round ends (ESC pressed)
COOLDOWN_DURATION = 5000

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init() # Initialize the mixer for sound
pygame.font.init() # Initialize the font module for text rendering
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Arduino Button Buzzer with Scoring")

# --- Font Setup ---
# Use the default system font
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 20)

# --- Sound Setup ---
buzzer_sound = None # Initialize to None
try:
    buzzer_sound = pygame.mixer.Sound("buzzer.wav")
    print("Buzzer sound loaded successfully.")
except pygame.error as e:
    print(f"Warning: Could not load buzzer.wav: {e}")
    print("Buzzer sound will not play.")


# --- Serial Connection ---
ser = None # Initialize serial object to None
connected_port = None
print("Attempting to connect to serial port...")

for port in SERIAL_PORTS_TO_CHECK:
    try:
        # Attempt to open the serial port
        ser = serial.Serial(port, BAUD_RATE, timeout=0.01) # Use a small timeout for non-blocking read
        time.sleep(2) # Give the Arduino time to reset after opening the port
        if ser.isOpen():
            connected_port = port
            print(f"Successfully connected to serial port {connected_port}")
            break # Exit the loop once connected
    except serial.SerialException:
        # print(f"Could not connect to {port}") # Uncomment for debugging connection attempts
        if ser and ser.isOpen():
            ser.close() # Close the port if it was partially opened


if not connected_port:
    error_message = "Error: Could not connect to any of the specified serial ports."
    print(error_message)
    print("Please check the port name(s) and ensure the Arduino is connected and the Arduino IDE Serial Monitor is closed.")
    # Display error message on screen before quitting
    screen.fill(BLACK)
    error_text = font.render(error_message, True, RED)
    error_text2 = font.render("Check ports and connection.", True, RED)
    screen.blit(error_text, (50, screen_height // 2 - 30))
    screen.blit(error_text2, (50, screen_height // 2 + 10))
    pygame.display.flip()
    pygame.time.wait(5000) # Wait 5 seconds before quitting Pygame
    pygame.quit()
    sys.exit(1) # Exit the script if connection fails


# --- Game State ---
# States: waiting, buzzed
game_state = "waiting"
player_scores = {1: 0, 2: 0} # Initialize scores
buzzed_player = None
waiting_start_time = pygame.time.get_ticks() # Record time when waiting starts
cooldown_end_time = 0 # Time when the current cooldown period ends (applies to waiting state)
reaction_time = 0 # Store reaction time when buzzed

# Variable to hold the first valid buzz message received in the current frame
# Format: (player_number, buzz_time_in_pygame_ticks) or None
first_buzz_this_frame = None

# --- Text Rendering Helper ---
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# --- Main Game Loop ---
running = True
while running:
    current_time = pygame.time.get_ticks()

    # Reset the first_buzz_this_frame at the start of each loop iteration
    first_buzz_this_frame = None

    # --- Event Handling (Pygame Window) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle keyboard input for scoring, resetting, and exiting
        if event.type == pygame.KEYDOWN:
            # Exit key - always active
            if event.key == pygame.K_p:
                running = False # Set running to False to exit the main loop

            # Handle actions based on current game state
            if game_state == "buzzed" and buzzed_player is not None:
                # Scoring keys - active when a player has buzzed
                if event.key == pygame.K_f:
                    player_scores[buzzed_player] += 10
                    print(f"Player {buzzed_player} score +10. New score: {player_scores[buzzed_player]}")
                    # State remains 'buzzed' after scoring
                elif event.key == pygame.K_g:
                    player_scores[buzzed_player] += 5
                    print(f"Player {buzzed_player} score +5. New score: {player_scores[buzzed_player]}")
                     # State remains 'buzzed' after scoring
                elif event.key == pygame.K_h:
                    player_scores[buzzed_player] -= 10
                    print(f"Player {buzzed_player} score -10. New score: {player_scores[buzzed_player]}")
                     # State remains 'buzzed' after scoring
                # Reset key in buzzed state (to go to next round)
                elif event.key == pygame.K_ESCAPE:
                    print("\n--- Next Round ---")
                    game_state = "waiting"
                    buzzed_player = None
                    


    # --- Read from Serial Port ---
    # Read all available lines from the serial buffer in this frame
    while ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line: # Check if the line is not empty
                # print(f"Received from Arduino: {line}") # Uncomment for debugging serial input

                # Process the received message only if in the waiting state
                if game_state == "waiting":
                     # Check if cooldown has passed before processing a new buzz
                    if current_time >= cooldown_end_time:
                        if line == "Player 1 pressed":
                            # If this is the first buzz detected in this frame's serial buffer
                            if first_buzz_this_frame is None:
                                first_buzz_this_frame = (1, current_time) # Store player and time
                                # print("P1 buzz recorded for this frame") # Debugging
                        elif line == "Player 2 pressed":
                             # If this is the first buzz detected in this frame's serial buffer
                            if first_buzz_this_frame is None:
                                first_buzz_this_frame = (2, current_time) # Store player and time
                                # print("P2 buzz recorded for this frame") # Debugging

        except serial.SerialException as e:
            print(f"Serial read error: {e}")
            running = False # Exit loop on serial error
            break # Exit the while ser.in_waiting loop

    # --- Process the winning buzz for this frame (after all serial data is read) ---
    # Check if a winning buzz was recorded during the serial reading for this frame
    if game_state == "waiting" and first_buzz_this_frame is not None:
        buzzed_player, buzz_time = first_buzz_this_frame
        reaction_time = buzz_time - waiting_start_time # Calculate reaction time
        game_state = "buzzed" # Change state after processing the buzz
        if buzzer_sound:
            buzzer_sound.play()
        print(f"\n!!! PLAYER {buzzed_player} BUZZED FIRST !!! Reaction Time: {reaction_time} ms")
        # Stay in 'buzzed' state to allow scoring via keyboard


    # --- Drawing ---
    screen.fill(BLACK) # Clear the screen

    # Display scores
    draw_text(f"Player 1 Score: {player_scores[1]}", font, WHITE, screen, 50, 50)
    draw_text(f"Player 2 Score: {player_scores[2]}", font, WHITE, screen, screen_width - 250, 50) # Adjust position for Player 2

    # Display game state/instructions
    if game_state == "waiting":
        draw_text("Waiting for a buzz...", font, GREEN, screen, 50, screen_height // 2 - 20)
        # Optionally show cooldown timer if currently in the cooldown period within waiting state
        if current_time < cooldown_end_time:
             remaining_cooldown = max(0, cooldown_end_time - current_time)
             draw_text(f"Next buzz in: {remaining_cooldown/1000:.1f} s", small_font, RED, screen, 50, screen_height // 2 + 20)
             draw_text("Press P to exit.", small_font, WHITE, screen, 50, screen_height // 2 + 40)
        else:
            draw_text("Press P to exit.", small_font, WHITE, screen, 50, screen_height // 2 + 20)


    elif game_state == "buzzed":
        # Display the reaction time calculated when buzzing occurred
        draw_text(f"PLAYER {buzzed_player} BUZZED FIRST!", font, BLUE, screen, 50, screen_height // 2 - 40)
        draw_text(f"Reaction Time: {reaction_time} ms", font, BLUE, screen, 50, screen_height // 2)
        draw_text("Press F (+10), G (+5), H (-10) to score.", small_font, WHITE, screen, 50, screen_height // 2 + 40)
        draw_text("Press ESC for next round.", small_font, WHITE, screen, 50, screen_height // 2 + 60) # Changed instruction
        draw_text("Press P to exit.", small_font, WHITE, screen, 50, screen_height // 2 + 80)


    pygame.display.flip() # Update the display

# --- Cleanup ---
if ser and ser.isOpen():
    ser.close()
    print("Serial port closed.")
pygame.quit()
sys.exit()
