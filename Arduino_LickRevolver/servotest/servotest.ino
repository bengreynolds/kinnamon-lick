#include <Servo.h>

Servo servo;
int pos = 0;
int msgInt = 0;
int ser2read = 0;
char rxChar = 'x';      // RXcHAR holds the received command
char rxStr[20];         // Allocate some space for the string
char inChar = -1;       // Where to store the character read
static unsigned int mPos = 0; 


void setup() {
  servo.attach(9);
  Serial.begin(9600);
  servo.write(pos);
}
void loop() {
  ser2read = Serial.available();
  if (ser2read > 0){          // Check receive buffer.
    // Serial.println(ser2read);
    delay(50);
    ser2read = Serial.available();
    // Serial.println(ser2read);
    while (ser2read == Serial.available()){
      rxChar = Serial.read();
    }
    // Serial.print("Received via Serial: ");
    Serial.print(rxChar);
    // delay(5);
    if (ser2read > 1){
      for(int x = 1; x < ser2read; x++) {
        if(mPos < 19){ // One less than the size of the array
          // Serial.println((ser2read-x));
          while ((ser2read-x) == Serial.available()){
            inChar = Serial.read(); // Read a character
          }
          if (inChar == 'x'){
            break;
          }
          rxStr[mPos] = inChar; // Store it
          mPos++; // Increment where to write next
        }
      }
      rxStr[mPos] = '\0'; // Null terminate the string
      mPos=0;
      msgInt = atoi(rxStr);
    }
    else{
      msgInt = -1;
    }
  }
        //  Serial.flush();                    // Clear receive buffer.
        //  rxChar = 'P';
  if (rxChar != 'x'){
    if (msgInt >= 0){
      Serial.print(msgInt);
    }
    Serial.print('!');
    if (rxChar == 'A'){
      for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
        servo.write(pos);
        Serial.println(pos);              // tell servo to go to position in variable 'pos'
        delay(75);    
      }
    }
    else if (rxChar == 'B') {
      for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
        servo.write(pos);              // tell servo to go to position in variable 'pos'
        delay(75);  
      } 
    }
    else if (rxChar == 'C') {
      servo.writeMicroseconds(map(0,0,360,500,2500));              // tell servo to go to position in variable 'pos'  
    }
    else if (rxChar == 'D') {
      servo.writeMicroseconds(map(90,0,360,500,2500));              // tell servo to go to position in variable 'pos'  
    }
    else if (rxChar == 'E') {
      servo.writeMicroseconds(map(180,0,360,500,2500));              // tell servo to go to position in variable 'pos'  
    }
    else if (rxChar == 'F') {
      servo.writeMicroseconds(map(270,0,360,500,2500));              // tell servo to go to position in variable 'pos'  
    }
    else if (rxChar == 'G') {
      servo.writeMicroseconds(map(360,0,360,500,2500));              // tell servo to go to position in variable 'pos'  
    }
  }
}
  

