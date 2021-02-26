#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_ADS1015.h>
#include <avr/wdt.h>
#include <TimerOne.h>
#include <EEPROM.h>
 int resultado,resultado2;
 Adafruit_ADS1115 ads;
 SoftwareSerial esp8266(3,2);
 const float multiplier = 0.1875F;
 int16_t adc2, adc3 ;
 String str = "";
 String adc00 = "";
 String adc10 = "";
 String comando = "";
 String multiplicador000 = "";
 float multiplicador0;
 float multiplicador1;
 float adc0;
 float adc1;
 int16_t temp;
 float multiplicador00;
 char c;
 int Actualizar=0;
void setup()
{
 wdt_disable();
 Serial.begin(115200);  // monitor serial del arduino
 esp8266.begin(115200);
 ads.begin();
 pinMode(5,INPUT_PULLUP);
 pinMode(6,INPUT_PULLUP);
 Timer1.initialize(1000000);         // Dispara cada 250 ms
 Timer1.attachInterrupt(ISR_Blink); // Activa la interrupcion y la asocia a ISR_Blink
 Serial.println("ME REINICIE QL");
 wdt_enable(WDTO_2S); // Configurar watchdog a cuatro segundos
                       // Puedes usar el tiempo que te convenga de la lista de arriba
 wdt_reset(); // Actualizar el watchdog para que no produzca un reinicio

  EEPROM.get(0, multiplicador0);
  EEPROM.get(10, multiplicador1);
  //EEPROM.get(0x10, multiplicador1);
  Serial.println(multiplicador0);
  Serial.println(multiplicador1);
 // Serial.println(multiplicador1);
 
}
void loop()

{
  if(digitalRead(6)==0){
    delay(100);
    adc0 = ads.readADC_SingleEnded(0);
    //adc0 = adc0 * multiplier;
    Serial.println(adc0);
    Serial.println("yo fui");
    multiplicador0=(1000/adc0);
    //multiplicador00=(1/multiplicador0);
    Serial.println(multiplicador0);
    
    EEPROM.put(0, multiplicador0);


    adc1 = ads.readADC_SingleEnded(1);
    //adc1 = adc1 * multiplier;
    Serial.println(adc1);
    Serial.println("yo fui 2");
    multiplicador1=(1000/adc1);
    Serial.println(multiplicador1);
    
    EEPROM.put(10, multiplicador1);

    while(digitalRead(6)==0){
      
      }
      
    }
  
  while(digitalRead(5)==0){
    delay(100);
    Serial.println("y ellaaaA?");
    }
    
while(esp8266.available()){
  c = esp8266.read();
 Serial.print(c);
  wdt_reset(); }


   if (Serial.available() > 0)
   {
      str = Serial.readStringUntil('\n');
      int coma = str.indexOf(".");
      comando = str.substring(0, coma); 
      if(comando=="AN"){
          Serial.println("");
  Serial.print("AIN0: "); Serial.println(adc0 * multiplicador0);
  Serial.print("AIN1: "); Serial.println(adc1 * multiplicador1);
  Serial.print("AIN2: "); Serial.println(adc2 * multiplier);
  Serial.print("AIN3: "); Serial.println(adc3 * multiplier);
  Serial.println(" ");
        }
   }


   if(Actualizar==1){
  adc0 = ads.readADC_SingleEnded(0);
  //adc0 = adc0 * multiplier;
  adc1 = ads.readADC_SingleEnded(1);
  //adc1 = adc1 * multiplier;
  adc2 = ads.readADC_SingleEnded(2);   
  adc3 = ads.readADC_SingleEnded(3);
  adc00=String(adc0 * multiplicador0);
  adc10=String(adc1 * multiplicador1);
  //Serial.println(adc00);
  esp8266.println(adc00+","+adc10);
  Actualizar=0;
  }

}


void ISR_Blink()
   {   Actualizar=1;
    wdt_reset();
   }
