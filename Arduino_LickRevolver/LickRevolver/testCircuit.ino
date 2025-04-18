// #include <Servo.h>

// Servo shutter1;
// Servo shutter2;
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
// const int lick1 = 4;
// const int lick2 = 5;    // TTL lick detect (port to Arduino)
// const int lickM = 6;    // TTL lick detect (port to Arduino)
// const int sol1 = 12;
// const int sol2 = 13;
// const int buttonStart = 8;
// const int buttonPurge1 = 2;
// const int buttonPurge2 = 3;
// const int ledPin = 15;

// int startState = HIGH;
// int Purge2State = HIGH;
// int Purge1State = HIGH;
// int lastPurge2State = HIGH; 
// int lastPurge1State = HIGH;
// unsigned long sTime = millis();
// unsigned long lastStartTime = millis();
// bool rec = false;
// unsigned long sessionStart = 0;
// int TrialState = 1;
// int prevTrialState = 0;
// int currVial = 0;
// int closePos = 1000;
// int midPos = 1250;
// int openPos = 1500;
// int delayMain = 500;
// int delayRew = 1000;
// int vialDir = -1;
// int acidAssoc = -1;

// int maxIdleTime = 0;
// int maxIdleTimeMain = 30000;
// int maxIdleTimeRew = 30000;
// unsigned long listenTime = 0;

// void setup() {
//   sPos = new int[NUM_VIALS];
//   for (int i = 0; i < NUM_VIALS; ++i) {
//     sPos[i] = i * (360 / NUM_VIALS); // Example positioning for servos
//   }
//   pinMode(lick2, INPUT);
//   pinMode(lick1, INPUT);
//   pinMode(lickM, INPUT);
//   pinMode(sol2, OUTPUT);
//   pinMode(sol1, OUTPUT);
//   pinMode(buttonPurge1, INPUT_PULLUP);
//   pinMode(buttonPurge2, INPUT_PULLUP);
//   digitalWrite(sol2, LOW);
//   digitalWrite(sol1, LOW);
//   shutter1.attach(9); // Attach servo to pin 2
//   shutter2.attach(10); // Attach servo to pin 2
//   revolve.attach(11); // Attach servo to pin 1
//   revolve.writeMicroseconds(map(0, 0, 360, 500, 2500));
//   shutter1.writeMicroseconds(closePos);
//   shutter2.writeMicroseconds(closePos);
//   Serial.begin(9600);
//   MoveShutter(closePos);
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
//       TrialState = 1;
//       prevTrialState = 2;
//       ChangeVial(vial);
//     }
//     else if (rxChar == 'B') {
//       vialDir = msgInt;
//     } 
//     else if (rxChar == 'C') {
//       Serial.println(TrialState);
//     } 
//     else if (rxChar =='D') {
//       delayMain = msgInt;
//     } 
//     else if (rxChar == 'E') {
//       delayRew = msgInt;
//     }
//     else if (rxChar =='F') {
//       maxIdleTimeMain = msgInt;
//     } 
//     else if (rxChar == 'G') {
//       maxIdleTimeRew = msgInt;
//     }
//     else if (rxChar == 'H') {
//       Serial.println(TrialState);
//     } 
//     else if (rxChar == 'I') {
//       rec = !rec;
//       Serial.println(rec);
//     }     
//     else if (rxChar == 'S'){
//       rec = !rec;
//       sTime = millis();
//     }
//     else if (rxChar == 'O'){
//       acidAssoc = msgInt;
//     }
//     else if (rxChar == 'X'){
//       MoveShutter(openPos);
//     }
//     else if (rxChar == 'Y'){
//       MoveShutter(closePos);
//     }
//     else if (rxChar == 'Z'){
//       TrialState = msgInt;
//       Serial.println("TrialState:  ");
//       Serial.print(TrialState);
//     }
//   Serial.println('%');
//   }
//   rxChar = 'x';

//   // Purge Rewards
//   if (!rec) {
//     Purge2State = digitalRead(buttonPurge2);
//     Purge1State = digitalRead(buttonPurge1);
//     if (Purge1State == LOW && lastPurge1State == HIGH) {    
//       Serial.println("Button1Pressed");
//       digitalWrite(sol1, HIGH);
//     } else if (Purge1State == HIGH && lastPurge1State == LOW) { 
//       digitalWrite(sol1, LOW);
//       Serial.println("Button1Released");
//     }
//     if (Purge2State == LOW && lastPurge2State == HIGH) {    
//       Serial.println("Button2Pressed");
//       digitalWrite(sol2, HIGH);
//     } else if (Purge2State == HIGH && lastPurge2State == LOW) { 
//       digitalWrite(sol2, LOW);
//       Serial.println("Button2Released");
//     }
//     lastPurge2State = Purge2State; 
//     lastPurge1State = Purge1State; 
//   }

//   // Listen for Lick Detection
//   if (rec) {
//     // if (TrialState != prevTrialState){
//     //   if (TrialState == 1){
//     //     listenTime = millis();
//     //     maxIdleTime = maxIdleTimeMain;
//     //   }
//     //   else if (TrialState == 2){
//     //     listenTime = millis();
//     //     maxIdleTime = maxIdleTimeRew;
//     //   }
//     //   Serial.println("MaxIdle:");
//     //   Serial.println(maxIdleTime);
//     // }
//     if (TrialState == 1) {
//       handleLickEvent(lickM, -1, delayMain, TrialState, vialDir, maxIdleTime, listenTime); // Pass -1 if no solenoid
//     }
//     // if (TrialState != 1) break;
//     // if (Serial.available() > 0) {
//     //   char userInput = Serial.read();
//     //   if (userInput == 'Q') {  // Replace 'Q' with any character of your choice
//     //     Serial.println("Exiting TrialState 1 based on user input.");
//     //     TrialState = 1;
//     //     rec = false;  // Stop the recording if required
//     //     break;
//     //   }
//     // }
//     // }
//     if (TrialState == 2) {
//         handleLickEvent(lick2, sol2, delayRew, TrialState, vialDir, maxIdleTime, listenTime);
//         handleLickEvent(lick1, sol1, delayRew, TrialState, vialDir, maxIdleTime, listenTime);
//     }
//     // Serial.print(TrialState);
//     // if (TrialState != 2) break;
//     // if (Serial.available() > 0) {
//     //   char userInput = Serial.read();
//     //   if (userInput == 'Q') {  // Replace 'Q' with any character of your choice
//     //     Serial.println("Exiting TrialState 2 based on user input.");
//     //     TrialState = 1;
//     //     rec = false;  // Stop the recording if required
//     //     break;
//     //     }
//     // }      
//     // }
//   }
// }

// void ChangeVial(int tarVial) {
//   if (tarVial <= 0 || tarVial > NUM_VIALS) {
//     Serial.println("Error: Vial number out of range.");
//     return;
//   }
//   moveRevolve(tarVial);  
//   currVial = tarVial;  // Update 
//   MoveShutter(closePos);
//   TrialState = 1;
//   prevTrialState = 2;
// }
// void moveRevolve(int tarVial) {
//   int currPos = sPos[currVial-1];
//   int tarPos = sPos[tarVial-1];
//   revolve.writeMicroseconds(map(tarPos, 0, 360, 500, 2500)); // Adjust pulse width based on angle
// }

// void tickRevolve(){
//   int currPos = sPos[currVial-1];
//   int tarPos = currPos+150;
//   revolve.writeMicroseconds(map(tarPos, 0, 360, 500, 2500)); // Adjust pulse width based on angle
// }


// void MoveShutter(int position) {
//   unsigned long TS = millis()-sTime;
//   shutter1.writeMicroseconds(position);  // Move shutter to position
//   shutter2.writeMicroseconds(position);  // Move shutter to position
//   if (position == openPos){
//     Serial.print("O"+String(TS)+ "+");
//   }
//   else if (position == closePos){
//     Serial.print("C"+String(TS)+ "+");
//   }
// }

// void activateSolenoid(int delayTime, int solenoidPin) {
//   digitalWrite(solenoidPin, HIGH);
//   delay(delayTime);
//   digitalWrite(solenoidPin, LOW);
// }

// void handleLickEvent(int lickPin, int solenoidPin, int delayTime, int &TrialState, int vialDirection, unsigned long maxIdleTime, unsigned long listenTime) {
//   // if (millis()-listenTime > maxIdleTime){
//   //   if (TrialState == 1){
//   //     Serial.print("#");
//   //   }
//   //   else if (TrialState == 2){
//   //     Serial.print("%");
//   //   }
//   //   Serial.print("N");
//   //   ChangeVial(1); // ************* REMOVE WHEN USING GUI!!
//   //   return;
//   // }
//   if (digitalRead(lickPin) == HIGH) {
//     delayMicroseconds(500); 
//     if (digitalRead(lickPin) == HIGH) {
//       unsigned long TS = millis() - sTime;
//       if (TrialState == 1) {
//         if (lickPin == lickM) {
//           Serial.print("M"+String(TS)+"+");
//           TrialState = 2;
//           // prevTrialState = 1;
//           tickRevolve();
//           MoveShutter(openPos);
//           return;
//         }
//       } 
//       else if (TrialState == 2) {
//         if (lickPin == lick2) {
//           Serial.print("L"+String(TS)+"+");
//           // if ((vialDirection == 0 && acidAssoc == 2) || (vialDirection == 1 && acidAssoc == 1)) {
//           Serial.print("S" + String(TS) + "+");
//           activateSolenoid(delayTime, solenoidPin);
//           MoveShutter(closePos);
//           // }
//           // else Serial.print("F"+String(TS)+"+");
//           // Serial.print("N");
//         }
//         else if (lickPin == lick1) {
//           Serial.print("R"+String(TS)+"+");
//           // if ((vialDirection == 0 && acidAssoc == 1) || (vialDirection == 1 && acidAssoc == 2)) {
//           Serial.print("S" + String(TS) + "+");
//           activateSolenoid(delayTime, solenoidPin);
//           MoveShutter(closePos);
//           // }
//           // else Serial.print("F"+String(TS)+"+");
//           // Serial.print("N");
//         }
//         TrialState = 1;
//         return;
//       }
//     }
//   }
// }
