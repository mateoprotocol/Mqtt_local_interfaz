#include <PubSubClient.h>
#include <WiFi.h>
//-----------Credentials------------------------------------------------------------
const char* ssid = "Redmi Note 11";
const char* pass = "sinatra00";
const char* broker = "192.168.188.179";
const char* topic = "categoria/rally";
//----------------------Sensor------------------------------------------------------
const int inputPin = 34;
int lastPinState = LOW;
int currentPinState = LOW;

// Variables para el temporizador
unsigned long startTime = 0;
unsigned long elapsedTime = 0;
bool isTiming = false;

//-------------Crea el objeto-------------------------------------------------------
WiFiClient espClient;
PubSubClient client(espClient); 

//-----------Callback---------------------------------------------------------------
void Callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Mensaje recibido en el tópico: ");
  Serial.println(topic);  // Aquí imprimes el tópico que ha recibido el mensaje
  
  Serial.print("Mensaje: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);  // Imprime el mensaje recibido
  }
  Serial.println();
}

//-------Network Conection----------------------------------------------------------
void setup_wifi(){
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid,pass);
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.print("Accedido a la red: ");
  Serial.println(WiFi.localIP()); 
}

//--------------Setup----------------------------------
void setup(){
  Serial.begin(115200);
  pinMode(inputPin, INPUT);
  setup_wifi(); 
  client.setServer(broker,1883);
  client.setCallback(Callback);
}
//-----------Reconnect---------------------------------------
void reconnect(){
  while(!client.connected()){
    Serial.print("Intentando reconectar a: ");
    Serial.println(broker);

    String clientID = "ESP32METAROBOTS";
    if(client.connect(clientID.c_str())){
      Serial.println("Conectado al servidor");
      //client.subscribe("mateop");
    }
    else{
      Serial.print("No se pudo reconectar al servidor: ");
      Serial.println(broker); 
      delay(5000);
    }
    
  }
}
//---------------Loop------------------------------------
void loop(){

  if(!client.connected()){
    reconnect();
  }
  client.loop();

 //------------------------LOOP SENSOR--------------------
  currentPinState = digitalRead(inputPin);
  
  // Detectar si hay un cambio de estado de LOW a HIGH
  if (currentPinState == HIGH && lastPinState == LOW) {
    if (!isTiming) {
      // Iniciar la temporización
      startTime = millis();
      isTiming = true;
      client.publish(topic,"-->Temporizacion iniciada");
    } else {
      // Detener la temporización
      elapsedTime = millis() - startTime;
      String elapsedTimeS = String(elapsedTime/1000.0);
      
      isTiming = false;
     String mensaje = ("Tiempo de vuelta: "+ elapsedTimeS);
      client.publish(topic,mensaje.c_str());
     
    }
  }
  
  // Actualizar el estado anterior del pin
  lastPinState = currentPinState;

}
