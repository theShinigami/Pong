#include <Arduino.h>
#include "Wire.h"
#include "MMC5883.h"
#include <I2Cdev.h>
#include "L3G4200D.h"
#include "ADXL345.h"
#include <Adafruit_Sensor.h>


// RGB PINS
#define BLUE 14
#define GREEN 12
#define RED 13


L3G4200D gyro;
ADXL345 accel;
MMC5883MA MMC5883(Wire);

int16_t ax, ay, az;
int16_t avx, avy, avz;

void all_rgb_pins_to_low(void);
void reset_pin_state(void);


void setup() {

  Serial.begin(9600);
  Wire.begin();

  Serial.println("Initializing I2C devices...");
  gyro.initialize();
  accel.initialize();

  // verify connection
  Serial.println("Testing device connections...");
  Serial.println(gyro.testConnection() ? "L3G4200D connection successful" : "L3G4200D connection failed");
  Serial.println("Testing device connections...");
  Serial.println(accel.testConnection() ? "ADXL345 connection successful" : "ADXL345 connection failed");

  // data seems to be best when full scale is 2000
  gyro.setFullScale(2000);

  // set rgb output pins
  pinMode(RED, OUTPUT);
  pinMode(BLUE, OUTPUT);
  pinMode(GREEN, OUTPUT);

}

// pin state for rgb
int pin_state[3] = {0, 0, 0};

void loop() {
  
  // read raw accel measurements from device
  accel.getAcceleration(&ax, &ay, &az);

  if (ax < 0) {
    Serial.println("-1");
    
    if (pin_state[0] == 0) {
      reset_pin_state();
      pin_state[0] = 1;
      all_rgb_pins_to_low();
      digitalWrite(RED, HIGH);
    }


  } else if ((ax > 0) && (ax <= 60)) {
    Serial.println("0");

    if (pin_state[1] == 0) {
      reset_pin_state();
      pin_state[1] = 1;
      all_rgb_pins_to_low();
      digitalWrite(BLUE, HIGH);
    }

  } else if ((ax > 80)) {
    Serial.println("1");

    if (pin_state[2] == 0) {
      reset_pin_state();
      pin_state[2] = 1;
      all_rgb_pins_to_low();
      digitalWrite(GREEN, HIGH);
    }

  }
  

  delay(100);
}


void all_rgb_pins_to_low(void) {
  digitalWrite(RED, LOW);
  digitalWrite(GREEN, LOW);
  digitalWrite(BLUE, LOW);
}

void reset_pin_state(void) {
  for (int i=0; i < 4; i++) {
    pin_state[i] = 0;
  }
}


