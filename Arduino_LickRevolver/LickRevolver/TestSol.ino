

// const int solenoid1Pin = 3; // Pin connected to Solenoid 1
// const int solenoid2Pin = 4; // Pin connected to Solenoid 2

// void setup() {
//   // Set solenoid pins as outputs
//   pinMode(solenoid1Pin, OUTPUT);
//   pinMode(solenoid2Pin, OUTPUT);

//   // Initialize serial communication
//   Serial.begin(9600);
//   Serial.println("Solenoid Control Ready.");
//   Serial.println("Type 'a' to trigger Solenoid 1, 'b' to trigger Solenoid 2.");
// }

// void loop() {
//   // Check if data is available from the serial monitor
//   if (Serial.available() > 0) {
//     char command = Serial.read(); // Read the command
//     Serial.print(command);

//     if (command == 'a') {
//       digitalWrite(solenoid1Pin, HIGH);
//       Serial.println("Solenoid 1 activated.");
//       delay(500); // Delay for 0.5 seconds
//       digitalWrite(solenoid1Pin, LOW);
//       Serial.println("Solenoid 1 deactivated.");
//     } else if (command == 'b') {
//       digitalWrite(solenoid2Pin, HIGH);
//       Serial.println("Solenoid 2 activated.");
//       delay(500); // Delay for 0.5 seconds
//       digitalWrite(solenoid2Pin, LOW);
//       Serial.println("Solenoid 2 deactivated.");
//     } 
//   }
// }