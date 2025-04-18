
// #include <Servo.h>

// Servo shutter;
// Servo revolve;

// const int TTL_L = 20; // TTL lick detect (port to arduino)
// const int TTL_R = 17; // TTL lick detect (port to arduino)
// const int TTL_M = 18; //FLAG
// const int solL = 4;
// const int solR = 5;
// const int buttonStart = 8;
// const int bpurgeL = 11;
// const int bpurgeR = 12;
// const int ledPin = 15;

// int purgeLS = HIGH;
// int purgeRS = HIGH;
// int startState = HIGH;
// int lastpurgeLS = HIGH; 
// int lastpurgeRS = HIGH;
// unsigned long lastStartTime = millis();
// int testIteration = 0;
// unsigned long previousTime = 0;
// unsigned long interval = 3600000; // 1 hour in milliseconds
// bool rec = false;
// int fExist = 0;

// unsigned long sessionStart = 0;
// String FileName = "";
// #define NUM_VIALS 8
// int vialAssoc[NUM_VIALS] = {0}; 

// void setup() {
//   pinMode(TTL_L, INPUT);
//   pinMode(TTL_R, INPUT);
//   pinMode(solL, OUTPUT);
//   pinMode(solR, OUTPUT);
//   digitalWrite(solL, LOW);
//   digitalWrite(solR, LOW);
//   shutter.attach()
//   revolve.attach()
// }

// void loop() {
 
//   startState = digitalRead(buttonStart);
//   if (!rec){
//     purgeLS = digitalRead(bpurgeL);
//     purgeRS = digitalRead(bpurgeR);
//     if (purgeLS == LOW) {    
//       digitalWrite(solL, HIGH);
//     }
//     else if (purgeLS == HIGH && lastpurgeLS == LOW) { 
//       digitalWrite(solL, LOW);
//     }
//     // Purge solenoid 2
//     if (purgeRS == LOW) {    
//       digitalWrite(solR, HIGH);
//     }
//     else if (purgeRS == HIGH && lastpurgeRS == LOW) { 
//       digitalWrite(solR, LOW);
//     }
//     lastpurgeLS = purgeLS; 
//     lastpurgeRS = purgeRS; 
//   }

//   // Listen for Button Start press -- new file if not recording, else: stop recording
//   if (startState == LOW && millis() - lastStartTime > 500){
//     lastStartTime = millis();
//     if (!rec){
//       createNewFile(FileName, fExist);
//       digitalWrite(ledPin, HIGH);
//       rec = true;
//     }
//     else {
//       Serial.println("Recording Stopped");
//       rec = false;
//       digitalWrite(ledPin, LOW);
//       digitalWrite(solL, LOW);
//       digitalWrite(solR, LOW);
//        // Reset lick counts for next iteration
//       LickCnt1 = 0;
//       LickCnt2 = 0;
//       fExist = 0;
//     }
//   }

//   // Listen for Lick Detection
//   if (rec) {
//    if (TrialState == 1) {
//     handleLickEvent(lickM, -1, delayMain, TrialState, false, currVial); // No solenoid, so set hasSolenoid to false
//   } 

// // Example for TrialState 2
//     if (TrialState == 2) {
//       handleLickEvent(lickL, solL, delayRew, TrialState, true, currVial); // Solenoid is relevant
//       handleLickEvent(lickR, solR, delayRew, TrialState, true, currVial); // Solenoid is relevant
//     }
//   }
// }
// void ChangeVial(int vial) {
//   if (vial < 0 || vial >= NUM_VIALS) {
//     Serial.println("Error: Vial number out of range.");
//     return;
//   }

//   int tarVial;
//   int direction; 
//   switch (cMode) {
//     case MANUAL:
//       tarVial = vial; // use selected position
//       direction = determineDirection(currVial, tarVial);  // 1 for clockwise, -1 for counterclockwise  
//       moveRevolve(tarVial, direction);

//     case RANDOM:
//       tarVial = random(0, NUM_VIALS);  // select random
//       direction = determineDirection(currVial, tarVial);  
//       moveRevolve(tarVial, direction); 

//     case AUTOMATED:
//       tarVial = (currVial + 1) % NUM_VIALS; // increment position
//       direction = determineDirection(currVial, tarVial);  
//       moveRevolve(tarVial, direction);  
//   }
//   currVial = tarVial;  // Update 
//   MoveShutter(TrialState, openPos);
// }

// int getVialDirection(int vial) {
//   if (vial < 1 || vial > NUM_VIALS) {
//     Serial.println("Error: Vial number out of range.");
//     return -1; // Error code
//   }

//   return vialAssoc[vial - 1];
// }
// void setVialAssociation(int vial, char direction) {
//   if (vial < 1 || vial > NUM_VIALS) {
//     Serial.println("Error: Vial number out of range.");
//     return;
//   }

//   if (direction == 'R') {
//     vialAssoc[vial - 1] = 1; // Right direction
//   } else if (direction == 'L') {
//     vialAssoc[vial - 1] = 0; // Left direction
//   } else {
//     Serial.println("Error: Invalid direction. Use 'R' or 'L'.");
//     return;
//   }

//   Serial.print("Vial ");
//   Serial.print(vial);
//   Serial.print(" set to ");
//   Serial.println(direction);
// }

// int getVialDirection(int vial) {
//   if (vial < 1 || vial > NUM_VIALS) {
//     Serial.println("Error: Vial number out of range.");
//     return -1; // Error code
//   }

//   return vialAssoc[vial - 1];
// }
// void changeNumVials() {
//   delete[] vialAssoc;
//   delete[] sPos;
//   delete[] NIM_VIALS;
//   #define NUM_VIALS 8
//   int vialAssoc[NUM_VIALS] = {0};
// }
// void handleLickEvent(int lickPin, int solenoidPin, int delayTime, int TrialState, bool hasSolenoid, int vial) {
//   if (digitalRead(lickPin) == HIGH) {
//     delayMicroseconds(500); // Debounce delay
//     if (digitalRead(lickPin) == HIGH) {
//       int timestamp = millis() - sessionStart;
//       if (TrialState == 1) {
//         startTime = millis();
//         if (lickPin == lickM) {
//           Serial.print(timestamp);
//           Serial.print("M");
//           TrialState = 2;
//           MoveShutter(TrialState, closePos);
//           return;
//         }
//       } else if (TrialState == 2) {
//         int vialDirection = getVialDirection(vial); // Get the direction for the vial

//         if (lickPin == lickL) {
//           Serial.print(timestamp);
//           Serial.print("L");
//           if (hasSolenoid && vialDirection == 0) { // Check if solenoid should be activated for left direction
//             digitalWrite(solenoidPin, HIGH);
//             delay(delayTime);
//             digitalWrite(solenoidPin, LOW);
//           }
//         } else if (lickPin == lickR) {
//           Serial.print(timestamp);
//           Serial.print("R");
//           if (hasSolenoid && vialDirection == 1) { // Check if solenoid should be activated for right direction
//             digitalWrite(solenoidPin, HIGH);
//             delay(delayTime);
//             digitalWrite(solenoidPin, LOW);
//           }
//         }

//         if (cMode == AUTOMATED || cMode == RANDOM) {
//           ChangeVial(0);
//         }
//       }
//     }
//   }
// }



