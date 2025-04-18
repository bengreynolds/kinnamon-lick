
// const int buttonStart = 8;
const int buttonPurge1 = 8;
const int buttonPurge2 = 11;
int Purge1State = HIGH;
int Purge2State = HIGH;
int startState = HIGH;
int lastPurge1State = HIGH; 
int lastPurge2State = HIGH;
int lastStartState = HIGH;
const int solenoid1 = 4;
const int solenoid2 = 5;

void setup() {
  pinMode(solenoid1, OUTPUT);
  pinMode(solenoid2, OUTPUT);
  pinMode(1, OUTPUT);
  digitalWrite(1, LOW);
  pinMode(12, OUTPUT);
  digitalWrite(12, LOW);
  pinMode(9, OUTPUT);
  digitalWrite(12, LOW);
  pinMode(6, OUTPUT);
  digitalWrite(12, LOW);
  pinMode(buttonPurge1, INPUT_PULLUP);
  pinMode(buttonPurge1, INPUT_PULLUP);
  // pinMode(buttonStart, INPUT_PULLUP);
  Serial.begin(115200);
}

void loop() {
   if (Serial.available() > 0) {
    char receivedChar = Serial.read();
    if (receivedChar == 'A') {
      Serial.println("Received");
      digitalWrite(4, HIGH);
      digitalWrite(5, HIGH);
      delay(500);
      digitalWrite(4, LOW);
      digitalWrite(5, LOW);
    }
  }
  Purge1State = digitalRead(buttonPurge1);
  Purge2State = digitalRead(buttonPurge2);
  // startState = digitalRead(buttonStart);
  // if (startState == LOW && lastStartState == HIGH){
  //   Serial.println("Start");
  //   delay(200);
  // }
  // Purge solenoid 1
  if (Purge1State == LOW) {    
    digitalWrite(solenoid1, HIGH);
    Serial.println("1");
    delay(200);
  }
  if (Purge1State == HIGH && lastPurge1State == LOW) { 
    digitalWrite(solenoid1, LOW);
  }
   // Purge solenoid 2
  if (Purge2State == LOW) {    
    digitalWrite(solenoid2, HIGH);
    Serial.println("2");
    delay(50);
  }
  if (Purge2State == HIGH && lastPurge2State == LOW) { 
    digitalWrite(solenoid2, LOW);
  }
  lastPurge1State = Purge1State; 
  lastPurge2State = Purge2State; 
}
