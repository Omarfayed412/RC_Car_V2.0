#include <Servo.h>
Servo myservo;

#define IN1 5  // Motor 1 forward
#define IN2 6  // Motor 1 backward
#define IN3 7  // Motor 2 forward
#define IN4 8  // Motor 2 backward
#define En1 5
#define En2 10

#define LED 4
#define trig A3
#define echo A2

#define sensorL 13 // Left sensor
#define sensorR 12 // Right sensor
#define sensorM 2 // Middle sensor
#define INITIAL_STATE 0

#define Nozzle 3

int speed = 150; // Global speed variable (adjustable)
int speedDiff = 0;

int sl = 0; // Left sensor state
int sr = 0; // Right sensor state
int sm = 0; // Middle sensor state

String Reading;   //Buffer
long duration, distance;    
int angle = INITIAL_STATE; 

int nozzleState = 0;

char operation;

void setup() {
  Serial.begin(9600);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  pinMode(En1, OUTPUT);
  pinMode(En2, OUTPUT);

  pinMode(sensorL, INPUT);
  pinMode(sensorR, INPUT);
  pinMode(sensorM, INPUT);

  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);

  pinMode(LED, OUTPUT);
  pinMode(Nozzle, OUTPUT);
  myservo.attach(11);
  
}

void Ultrasonic() {
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);
  duration = pulseIn(echo, HIGH);
  distance = (duration / 2) * 0.0343; // Convert to cm
}

void forword() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(En1, speed);
  analogWrite(En2, speed);
  Serial.println("forward");
}
void backword() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(En1, speed);
  analogWrite(En2, speed);
  Serial.println("back");
}

void left() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(En1, speed);
  analogWrite(En2, speed);  
  Serial.println("left");
}
void right() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(En1, speed);
  analogWrite(En2, speed);  
  Serial.println("right");
}

void stopp() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  Serial.println("stopp");
}

void manual()
{
  Serial.println("In Manual Mode");
  while(1) { 
    if (Serial.available() > 0) {
      int commaIndex; 
      String firstPart;
      Reading = Serial.readStringUntil('\n');
      commaIndex = Reading.indexOf(",");
      if (commaIndex != -1) {
        firstPart = Reading.substring(0, commaIndex);
        speed = Reading.substring(commaIndex + 1).toInt();
  
        Serial.println("First part: " + firstPart);
        Serial.println("Speed: " + String(speed));
      }
      if (firstPart == "f") {
        forword();
      } else if (firstPart == "b") {
        backword();
      } else if (firstPart == "r") {
        right();
      } else if (firstPart == "l") {
        left();
      } else if (firstPart == "s") {
        stopp();
      } else if (firstPart == "z") {
        break;
      } else if (firstPart == "S") {
          ServoUp();
      } else if (firstPart == "s") {
          ServoDown();
      } else if (firstPart == "N") {
          changeNozzleState();
      }
      
    }
  }
}

void ServoUp() {
  angle+= 15;
  servo.write(angle);
}

void Servodown() {
  angle-= 15;
  servo.write(angle);
}

void changeNozzleState() {
  state = !(state);
  digitalWrite(Nozzle, HIGH);
}

void AvoidingObstacle()
{
  int threshold = 4;
  Serial.println("Start Obstacle avoidance");
  Ultrasonic();
  if (distance <= threshold) {
    stopp();
    int prevTime = millis();
    int currentTime = prevTime;
    while (currentTime - prevTime <= 2000 && distance <= threshold) {
        right();
        currentTime = millis(); 
    }
    if (distance > threshold)
      avoidingAvoidingObstacle();
    stopp();
    Serial.println("No Path Found");
  } 
  else {
    forword();
  }
}

void LineFollower()
{
  Serial.println("in Line Follower");
  
  sl = digitalRead(sensorL);
  sr = digitalRead(sensorR);
  sm = digitalRead(sensorM);

  //Line in the middle 
  if (sm == 1 && sl == 0 && sr == 0) {
    forword(); 
    Serial.println("Line in the middle ");
  } 
  
  //Line on the right
  else if (sm == 0 && sl == 0 && sr == 1) {
    while(!(sm == 1 && sl == 0 && sr == 0))
      right();
    Serial.println("Line on the right");
  } 
  
  //Line on the left
  else if (sm == 0 && sl == 1 && sr == 0) {
    while(!(sm == 1 && sl == 0 && sr == 0))
      left();
    Serial.println("Line on the left");
  } 
  
  //End case all black
  else if (sm == 1 && sl == 1 && sr == 1) {
    stopp();  //basecase
    Serial.println("End of Line");
  } 
  
  //Line on the left and middle
  else if (sm == 1 && sl == 1 && sr == 0) {
    while(!(sm == 1 && sl == 0 && sr == 0))
      left();
    Serial.println("Line on the left and middle");
  } 
  
  //Line on the right and middle
  else if (sm == 1 && sl == 0 && sr == 1) {
    while(!(sm == 1 && sl == 0 && sr == 0))
      right();
    Serial.println("Line on the right and middle");
  }
  
  //No line found
  else if (sm == 0 && sl == 0 && sr == 0) {
    Serial.println("No line found");
    int prevTime = millis();
    int currentTime = prevTime;
    while (currentTime - prevTime <= 2000 & !(sm == 1 && sl == 0 && sr == 0)) {
      if (sm == 0 && sl == 0 && sr == 1) 
        right();
      else if (sm == 0 && sl == 1 && sr == 0) {
        left();
      }
      currentTime = millis();   //update current time
    }
    if (sm == 1 && sl == 0 && sr == 0) 
      LineFollower();
    }
  
  //Line on the left and right with no middle found
  else if (sm == 0 && sl == 1 && sr == 1) {
    while(!(sm == 1 && sl == 0 && sr == 0))
        left();
      }
    Serial.println("Line on the left and right with no middle found");
}

/* L M R 
 * 0 0 0 ok
 * 0 0 1 ok
 * 0 1 0 ok 
 * 0 1 1 ok
 * 1 0 0 ok
 * 1 0 1 Don't care
 * 1 1 0 ok 
 * 1 1 1 ok
 */
void loop() {
  if (Serial.available()) {
      char c = Serial.read();
     if(c == 'B')
     {
           manual();
     }
     else if(c == 'A')
     {
        AvoidingObstacle();  
     }
     else if(c == 'L')
     {
      LineFollower();
     }
  }
}
