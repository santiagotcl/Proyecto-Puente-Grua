#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_ADS1015.h>
 // arduino Rx (pin 2) ---- ESP8266 Tx
 // arduino Tx (pin 3) ---- ESP8266 Rx
SoftwareSerial esp8266(3,2); 
 int resultado,resultado2;
 Adafruit_ADS1115 ads;
 const float multiplier = 0.1875F;
 int16_t adc0, adc1, adc2, adc3;
void setup()
{
 Serial.begin(9600);  // monitor serial del arduino
 esp8266.begin(115200); // baud rate del ESP8255
 ads.begin();
 pinMode(13,OUTPUT);
 digitalWrite(13,LOW);
 
 sendData("AT+RST\r\n",2000);      // resetear módulo
 sendData("AT+CWMODE=1\r\n",1000); // configurar como cliente
 sendData("AT+CWJAP=\"TP-LINK_E950\",\"22822611\"\r\n",8000); //SSID y contraseña para unirse a red 
 sendData("AT+CIFSR\r\n",1000);    // obtener dirección IP
 sendData("AT+CIPSTA=\"192.168.0.3\"\r\n",1000);    // obtener dirección IP
 sendData("AT+CIPMUX=1\r\n",1000); // configurar para multiples conexiones
 sendData("AT+CIPSERVER=1,80\r\n",1000);         // servidor en el puerto 80
}
void loop()

{
 if(esp8266.available())   // revisar si hay mensaje del ESP8266
 {
 if(esp8266.find("+IPD,")) // revisar si el servidor recibio datos
 {
 delay(150); // esperar que lleguen los datos hacia el buffer, se achico este timpo para mejorar respuesta de 1500
 int conexionID = esp8266.read()-48; // obtener el ID de la conexión para poder responder
 //esp8266.find("led="); // bucar el texto "led="
 //int state = (esp8266.read()-48); // Obtener el estado del pin a mostrar
 //digitalWrite(13, state); // Cambiar estado del pin
while(esp8266.available()){
 char c = esp8266.read();
 Serial.print(c);
 }
 
 //responder y cerrar la conexión para que el navegador no se quede cargando 
 // página web a enviar
  adc0 = ads.readADC_SingleEnded(0);
  adc1 = ads.readADC_SingleEnded(1);
  adc2 = ads.readADC_SingleEnded(2);
  adc3 = ads.readADC_SingleEnded(3);
  resultado=adc0 * multiplier;
  resultado2=adc1 * multiplier;
  Serial.print("AIN0: "); Serial.println(adc0 * multiplier);
  Serial.print("AIN1: "); Serial.println(adc1 * multiplier);
  Serial.print("AIN2: "); Serial.println(adc2 * multiplier);
  Serial.print("AIN3: "); Serial.println(adc3 * multiplier);
  Serial.println(" ");
 String webpage = "<!DOCTYPE HTML> \n <html> <HEAD> \n <TITLE>WI-FI Monitor</TITLE> \n </HEAD> \n <BODY> \n <H1>Balanza de Big-Bags, Molino Cotella</H1> \n <p> \n peso1:" +  String(resultado) + "</p> \n <p> \n peso2:" +  String(resultado2) + "</p> \n <br /> \n Santiago Cuozzo \n </html>" ;

 
 // comando para enviar página web
 String comandoWebpage = "AT+CIPSEND=";
 comandoWebpage+=conexionID;
 comandoWebpage+=",";
 comandoWebpage+=webpage.length();
 comandoWebpage+="\r\n";
 sendData(comandoWebpage,100);
 sendData(webpage,100);
 
 // comando para terminar conexión
 String comandoCerrar = "AT+CIPCLOSE=";
 comandoCerrar+=conexionID;
 comandoCerrar+="\r\n";
 sendData(comandoCerrar,300);
 }
 }
}
/*
Enviar comando al esp8266 y verificar la respuesta del módulo, todo esto dentro del tiempo timeout
*/
void sendData(String comando, const int timeout)
{
 long int time = millis(); // medir el tiempo actual para verificar timeout
 
 esp8266.print(comando); // enviar el comando al ESP8266
 
 while( (time+timeout) > millis()) //mientras no haya timeout
 {
 while(esp8266.available()) //mientras haya datos por leer
 { 
 // Leer los datos disponibles
 char c = esp8266.read(); // leer el siguiente caracter
 Serial.print(c);
 }
 } 
 return;
}
