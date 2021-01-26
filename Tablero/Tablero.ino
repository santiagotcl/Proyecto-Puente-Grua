#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_ADS1015.h>
#include <avr/wdt.h>
#include <TimerOne.h>
 int resultado,resultado2;
 Adafruit_ADS1115 ads;
 SoftwareSerial esp8266(3,2);
 const float multiplier = 0.1875F;
 int16_t adc0, adc1, adc2, adc3;
 String str = "";
 String adc00 = "";
 String adc10 = "";
 String comando = "";
 char c;
 int Actualizar=0;
void setup()
{
  wdt_disable();
 Serial.begin(115200);  // monitor serial del arduino
 esp8266.begin(115200);
 ads.begin();
 pinMode(5,INPUT_PULLUP);
 Timer1.initialize(1000000);         // Dispara cada 250 ms
 Timer1.attachInterrupt(ISR_Blink); // Activa la interrupcion y la asocia a ISR_Blink
 Serial.println("ME REINICIE QL");
 wdt_enable(WDTO_2S); // Configurar watchdog a cuatro segundos
                       // Puedes usar el tiempo que te convenga de la lista de arriba
  wdt_reset(); // Actualizar el watchdog para que no produzca un reinicio
}
void loop()

{
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
  Serial.print("AIN0: "); Serial.println(adc0 * multiplier);
  Serial.print("AIN1: "); Serial.println(adc1 * multiplier);
  Serial.print("AIN2: "); Serial.println(adc2 * multiplier);
  Serial.print("AIN3: "); Serial.println(adc3 * multiplier);
  Serial.println(" ");
        }
   }


   if(Actualizar==1){
  adc0 = ads.readADC_SingleEnded(0);
  adc1 = ads.readADC_SingleEnded(1);   
  adc2 = ads.readADC_SingleEnded(2);   
  adc3 = ads.readADC_SingleEnded(3);
  adc00=String(adc0 * multiplier);
  adc10=String(adc1 * multiplier);
  //Serial.println(adc00);
  esp8266.println(adc00+","+adc10);
  Actualizar=0;
  }

}


void ISR_Blink()
   {   Actualizar=1;
    wdt_reset();
   }
