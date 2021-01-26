#include <ESP8266WiFi.h>

//Información de nuestro WIFI
const char *ssid = "TP-LINK_E950";
const char *password = "22822611";

//Datos para una IP estática
IPAddress ip(192,168,0,3);     
IPAddress gateway(192,168,0,1);   
IPAddress subnet(255,255,255,0); 

//Definimos el pin donde está conectado el led
int ledPin = 2; 
String str = "";
String peso1 = "";
String peso2 = "";
//Puerto 80 TCP, este puerto se usa para la navegación web http
WiFiServer server(80);
 
void setup() {
  ESP.wdtDisable();
  Serial.begin(115200); //Iniciamos comunicación serial
  delay(10);
  pinMode(ledPin, INPUT_PULLUP);  //Pin del Led como salida
  //digitalWrite(ledPin, LOW);  //Ponemos la salida de led en bajo
   
  // Conectandose al Wifi
  Serial.println();
  Serial.println();
  Serial.println("Me Reinicie");
  Serial.print("Conectandose a ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA); //Wifi en modo estación
  WiFi.config(ip, gateway, subnet);//Configuramos la ip estática
  WiFi.begin(ssid, password); //Iniciamos conexión con el nombre y la contraseña del wifi que indicamos

  //Mientras se conecta se imprimiran puntos
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  //Cuando se conecte lo imprimimos
  Serial.println("");
  Serial.println("WiFi Conectado");
   
  // Iniciamos el esp como servidor web
  server.begin();
  Serial.println("Servidor iniciado");
 
  // Imprimimos la dirección IP
  Serial.println("Usa esta URL para comunicar al ESP: ");
  Serial.println("http://");
  Serial.println(WiFi.localIP());
  Serial.println("/");
  ESP.wdtEnable(1000);
    
}
 
void loop() {
  ESP.wdtFeed();
while (digitalRead(ledPin) == 0){
  Serial.println("yella");
  }
  
   if (Serial.available() > 0)
   {
      str = Serial.readStringUntil('\n');
      int coma = str.indexOf(",");
      peso1 = str.substring(0, coma);
      peso2 = str.substring((coma + 1));
   }
  
  // El servidor siempre estará esperando a que se conecte un cliente
  WiFiClient client = server.available();
  if (!client) {
    return;
  }
   
  
  Serial.println("Nuevo cliente"); //Cuando un cliente se conecte vamos a imprimir que se conectó
  while(!client.available()){  //Esperamos a que el ciente mande una solicitud
    delay(1);
  }
   
  // Leemos la primer línea de la solicitud y la guardamos en la variable string request
  String request = client.readStringUntil('\r');
  Serial.println(request); //Imprimimos la solicitud
  client.flush(); //Descartamos los datos que se han escrito en el cliente y no se han leído
   ESP.wdtFeed();


ESP.wdtFeed();
  // Respuesta del servidor web
  
  client.println("HTTP/1.1 200 OK"); // La respuesta empieza con una linea de estado  
  client.println("Content-Type: text/html"); //Empieza el cuerpo de la respuesta indicando que el contenido será un documento html
  client.println(""); // Ponemos un espacio
  client.println("<!DOCTYPE HTML>"); //Indicamos el inicio del Documento HTML
  client.println("<html lang=\"en\">");
  client.println("<head>");
  client.println("<meta charset=\"UTF-8\">");
  client.println("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"); //Para que se adapte en móviles
  client.println("<TITLE>WI-FI Monitor</TITLE>");
  client.println("</head>");
  client.println("<body>");
  client.println("<br><br>");
  
  client.println("<H1>Balanza de Big-Bags, Molino Cotella</H1>");
  
  client.println("<p> peso1:" +  peso1 + "</p>");
  client.println("<p> peso2:" +  peso2 + "</p>");
  client.println("<p>Santiago Cuozzo</p>");

  client.println("</body>");
  
  client.println("</html>"); //Terminamos el HTML
 
  delay(1);
  Serial.println("Cliente desconectado"); //Imprimimos que terminó el proceso con el cliente desconectado
  Serial.println("");
 
}

 
