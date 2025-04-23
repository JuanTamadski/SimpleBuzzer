// Simple Arduino Button Detection (2 Players)
// Detects presses on digital pins 2 and 4 and reports via Serial.

const int button1 = 4;  // Player 1 button connected to digital pin 2
const int button2 = 6;  // Player 2 button connected to digital pin 4

void setup() {
  // Configure button pins with internal pull-up resistors
  pinMode(button1, INPUT_PULLUP);
  pinMode(button2, INPUT_PULLUP);

  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("Arduino Button Detector Ready");
  Serial.println("Press Player 1 (Pin 2) or Player 2 (Pin 4) button.");
}

void loop() {
  // Read the current state of the buttons
  int reading1 = digitalRead(button1);
  int reading2 = digitalRead(button2);

  // Check if Button 1 is pressed (LOW because of INPUT_PULLUP)
  if (reading1 == LOW) {
    Serial.println("Player 1 pressed");
    // Add a small delay to prevent multiple prints while button is held
    delay(100);
  }

  // Check if Button 2 is pressed (LOW because of INPUT_PULLUP)
  if (reading2 == LOW) {
    Serial.println("Player 2 pressed");
    // Add a small delay to prevent multiple prints while button is held
    delay(100);
  }

  // A small delay in the loop helps keep things stable, especially without debounce
  // For more robust detection, consider adding debounce logic
  // delay(1); // Optional small delay if needed
}
