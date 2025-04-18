// #include <Servo.h>

// Servo shutter;
// Servo revolve;

// #define NUM_VIALS 8 // Define the number of vials
// int* sPos;
// int msgInt = 0;
// int ser2read = 0;
// char rxChar = 'x';      // RXcHAR holds the received command
// char rxStr[20];         // Allocate some space for the string
// char inChar = -1;       // Where to store the character read
// static unsigned int mPos = 0; 

// // Constants
// const int lickL = 20;    // TTL lick detect (port to Arduino)
// const int lickR = 17;
// const int lickM = 18;    // TTL lick detect (port to Arduino)
// const int solR = 4;
// const int solL = 5;
// const int buttonStart = 8;
// const int buttonPurgeL = 11;
// const int buttonPurgeR = 12;
// const int ledPin = 15;

// int startState = HIGH;
// int PurgeLState = HIGH;
// int PurgeRState = HIGH;
// int lastPurgeLState = HIGH; 
// int lastPurgeRState = HIGH;
// unsigned long startTime = millis();
// unsigned long lastStartTime = millis();
// int testIteration = 0;
// unsigned long previousTime = 0;
// unsigned long interval = 3600000; // 1 hour in milliseconds
// bool rec = false;
// unsigned long sessionStart = 0;
// int TrialState = 1;
// int currVial = 0;
// int closePos = 0;
// int midPos = 150;
// int openPos = 300;
// int delayMain = 500;
// int delayRew = 200;
// int vialDir = -1;

// enum Mode { MANUAL, RANDOM, AUTOMATED };
// Mode cMode = MANUAL;

// void setup() {
//   sPos = new int[NUM_VIALS];
//   for (int i = 0; i < NUM_VIALS; ++i) {
//     sPos[i] = i * (360 / NUM_VIALS); // Example positioning for servos
//   }
//   pinMode(lickL, INPUT);
//   pinMode(lickR, INPUT);
//   pinMode(lickM, INPUT);
//   pinMode(solL, OUTPUT);
//   pinMode(solR, OUTPUT);
//   digitalWrite(solL, LOW);
//   digitalWrite(solR, LOW);
//   shutter.attach(2); // Attach servo to pin 2
//   revolve.attach(1); // Attach servo to pin 1
//   shutter.writeMicroseconds(closePos);
// }
// void loop(){
//  ser2read = Serial.available();
//   if (ser2read > 0){          // Check receive buffer.
//     // Serial.println(ser2read);
//     delay(50);
//     ser2read = Serial.available();
//     // Serial.println(ser2read);
//     while (ser2read == Serial.available()){
//       rxChar = Serial.read();
//     }
//     // Serial.print("Received via Serial: ");
//     Serial.print(rxChar);
//     // delay(5);
//     if (ser2read > 1){
//       for(int x = 1; x < ser2read; x++) {
//         if(mPos < 19){ // One less than the size of the array
//           // Serial.println((ser2read-x));
//           while ((ser2read-x) == Serial.available()){
//             inChar = Serial.read(); // Read a character
//           }
//           if (inChar == 'x'){
//             break;
//           }
//           rxStr[mPos] = inChar; // Store it
//           mPos++; // Increment where to write next
//         }
//       }
//       rxStr[mPos] = '\0'; // Null terminate the string
//       mPos=0;
//       msgInt = atoi(rxStr);
//     }
//     else{
//       msgInt = -1;
//     }
//   }
//         //  Serial.flush();                    // Clear receive buffer.
//         //  rxChar = 'P';
//   if (rxChar != 'x'){
//     if (msgInt >= 0){
//       Serial.print(msgInt);
//     }
//     Serial.print('!');
//     if (rxChar == 'A'){
//       int vial = msgInt;
//       ChangeVial(vial);
//     }
//     else if (rxChar == 'B') {
//       vialDir = msgInt;
//     } 
//     else if (rxChar =='D') {
//       delayMain = msgInt;
//     } 
//     else if (rxChar == 'E') {
//       delayRew = msgInt;
//     }
//     else if (rxChar == 'X') {
//       cMode = AUTOMATED;
//     } 
//     else if (rxChar == 'Y') {
//       cMode = MANUAL;
//     } 
//     else if (rxChar == 'Z') {
//       cMode = RANDOM;
//     } 
//   Serial.println('%');
//   }
//   rxChar = 'x';

//   // Purge Rewards
//   startState = digitalRead(buttonStart);
//   if (!rec) {
//     PurgeLState = digitalRead(buttonPurgeL);
//     PurgeRState = digitalRead(buttonPurgeR);
//     if (PurgeLState == LOW) {    
//       digitalWrite(solL, HIGH);
//     } else if (PurgeLState == HIGH && lastPurgeLState == LOW) { 
//       digitalWrite(solL, LOW);
//     }
//     if (PurgeRState == LOW) {    
//       digitalWrite(solR, HIGH);
//     } else if (PurgeRState == HIGH && lastPurgeRState == LOW) { 
//       digitalWrite(solR, LOW);
//     }
//     lastPurgeLState = PurgeLState; 
//     lastPurgeRState = PurgeRState; 
//   }

//   // Listen for Lick Detection
//   if (rec) {
//     if (TrialState == 1) {
//       handleLickEvent(lickM, -1, delayMain, TrialState, vialDir); // Pass -1 if no solenoid
//     }
//     if (TrialState == 2) {
//       handleLickEvent(lickL, solL, delayRew, TrialState, vialDir);
//       handleLickEvent(lickR, solR, delayRew, TrialState, vialDir);
//     }
//   }
// }

// void ChangeVial(int vial) {
//   if (vial < 0 || vial >= NUM_VIALS) {
//     Serial.println("Error: Vial number out of range.");
//     return;
//   }
//   int tarVial;
//   switch (cMode) {
//     case MANUAL:
//       tarVial = vial; // use selected position
//       break;

//     case RANDOM:
//       tarVial = random(0, NUM_VIALS);  // select random
//       break;

//     case AUTOMATED:
//       tarVial = (currVial + 1) % NUM_VIALS; // increment position

//       break;
//   }
//   int direction = detServoDirect(currVial, tarVial);  
//   moveRevolve(tarVial, direction);  
//   currVial = tarVial;  // Update 
//   MoveShutter(openPos);
// }

// int detServoDirect(int currVial, int tarVial) {
//   int diff = (tarVial - currVial + NUM_VIALS) % NUM_VIALS;
//   if (diff <= NUM_VIALS / 2) {
//     return 1;  // Clockwise
//   } else {
//     return -1;  // Counterclockwise
//   }
// }

// void moveRevolve(int tarVial, int direction) {
//   int currPos = sPos[currVial-1];
//   int tarPos = sPos[tarVial-1];
//   int servoStep = 1;
//   int servoRange = 360;  

//   if (direction == 1) { // Clockwise
//     while (currPos != tarPos) {
//         currPos = (currPos + servoStep) % servoRange;  
//         revolve.writeMicroseconds(map(currPos, 0, 360, 1000, 2000)); // Adjust pulse width based on angle
//         delay(1); // Adjust delay for smoother motion if needed
//     }
//   } 
//   else { // Counterclockwise
//     while (currPos != tarPos) {
//         currPos = (currPos - servoStep + servoRange) % servoRange;
//         revolve.writeMicroseconds(map(currPos, 0, 360, 1000, 2000)); // Adjust pulse width based on angle
//         delay(1); // Adjust delay for smoother motion if needed
//     }
//   }
// }

// void MoveShutter(int position) {
//   unsigned long TS = millis()-sTime;
//   shutter.writeMicroseconds(position);  // Move shutter to position
//   if (position == openPos){
//     Serial.write("O"+String(TS)+ "+");
//   }
//   if (position == closePos){
//     Serial.write("C"+String(TS)+ "+");
//   }
//   if (position == midPos){
//     Serial.write("M"+String(TS)+ "+");
//   }
// }

// void handleLickEvent(int lickPin, int solenoidPin, int delayTime, int TrialState, int vialDirection) {
//   if (digitalRead(lickPin) == HIGH) {
//     delayMicroseconds(500); 
//     if (digitalRead(lickPin) == HIGH) {
//       unsigned long TS = millis() - sTime;
//       if (TrialState == 1) {
//         startTime = millis();
//         if (lickPin == lickM) {
//           Serial.write("S"+String(TS)+"+");
//           TrialState = 2;
//           MoveShutter(midPos);
//           return;
//         }
//       } 
//       else if (TrialState == 2) {
//         if (lickPin == lickL) {
//           Serial.write("L"+String(TS)+"+");
//           if (vialDirection == 0) { // Check if solenoid should be activated for left direction
//             digitalWrite(solenoidPin, HIGH);
//             delay(delayTime);
//             digitalWrite(solenoidPin, LOW);
//           }
//         }
//         else if (lickPin == lickR) {
//           Serial.write("R"+String(TS)+"+");
//           if (vialDirection == 1) { // Check if solenoid should be activated for right direction
//             digitalWrite(solenoidPin, HIGH);
//             delay(delayTime);
//             digitalWrite(solenoidPin, LOW);
//           }
//         }
//         if (cMode == AUTOMATED || cMode == RANDOM) {
//           MoveShutter(closePos);
//           ChangeVial(0);
//         }
//       }
//     }
//   }
// }
