// openweatherapi shreevathsa

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "Test";
const char* password = "testpass";

// OpenWeatherMap API details
const char* apiKey = "911c17d59859e1246025e5439ed83f2d";
const char* city = "Bangalore";

// API URLs
String currentURL = "http://api.openweathermap.org/data/2.5/weather?q=" + String(city) + "&units=metric&appid=" + String(apiKey);
String forecastURL = "http://api.openweathermap.org/data/2.5/forecast?q=" + String(city) + "&units=metric&cnt=16&appid=" + String(apiKey);

// GPIO pin connected to STM32 PC1
const int requestPin = 16;

bool alreadySent = false;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, 16, 17);  // RX=16, TX=17 

  pinMode(requestPin, INPUT); // input from STM32 (PC1)

  pinMode(0, OUTPUT); // red
  pinMode(4, OUTPUT); // green 
  pinMode(2, OUTPUT); // blue 
  digitalWrite(0, HIGH);
  digitalWrite(2, HIGH);
  digitalWrite(4, HIGH);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    //Red LED to show Wifi disconnected
    digitalWrite(0, LOW);
    digitalWrite(2, HIGH);
    digitalWrite(4, HIGH);
  }
  Serial.println("\nWiFi connected");
  //Green LED to show Wifi connected
  digitalWrite(4, LOW);  
  digitalWrite(0, HIGH); 
  digitalWrite(2, HIGH); 
}

void loop() {
  //send weather data when PC1 pin is high & prevent sending more than once
  if (digitalRead(requestPin) == HIGH && !alreadySent) {
    delay(10);
    fetchAndSendWeather();
    alreadySent = true; 
  } 
  // Reset flag when STM32 brings PC1 low
  else if (digitalRead(requestPin) == LOW) {
    alreadySent = false;
  }
  delay(50);
}

void fetchAndSendWeather() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected");
    //Red LED to show Wifi disconnected
    digitalWrite(0, LOW);
    digitalWrite(2, HIGH);
    digitalWrite(4, HIGH);
    return;
  }

  float nowTemp = 0;
  int nowHumidity = 0;
  String nowCondition = "Unknown";

  // --- CURRENT WEATHER ---
  HTTPClient http;
  http.begin(currentURL);
  int httpCode = http.GET();

  if (httpCode == 200) {
    String payload = http.getString();
    StaticJsonDocument<2048> doc;
    DeserializationError error = deserializeJson(doc, payload);
    if (!error) {
      nowTemp = doc["main"]["temp"];
      nowHumidity = doc["main"]["humidity"];
      nowCondition = doc["weather"][0]["main"].as<String>();
    } 
    else Serial.println("JSON parse error (current)");
    
  } 
  else {
    Serial.print("HTTP error (current): ");
    Serial.println(httpCode);
    //Blue LED to show HTTP Error
    digitalWrite(2, LOW);
    digitalWrite(0, HIGH);
    digitalWrite(4, HIGH);
    return;
  }
  http.end();

  // --- TOMORROW FORECAST ---
  float sumTemp = 0;
  int sumHumidity = 0;
  int count = 0;
  String tomorrowCondition = "Unknown";

  http.begin(forecastURL);
  httpCode = http.GET();

  if (httpCode == 200) {
    String payload = http.getString();
    StaticJsonDocument<8192> doc;
    DeserializationError error = deserializeJson(doc, payload);
    if (!error) {
      for (int i = 0; i < 16; i++) {
        const char* timeStr = doc["list"][i]["dt_txt"];
        String time = String(timeStr);
        if (time.indexOf("12:00:00") != -1 || time.indexOf("15:00:00") != -1) {
          sumTemp += doc["list"][i]["main"]["temp"].as<float>();
          sumHumidity += doc["list"][i]["main"]["humidity"].as<int>();
          tomorrowCondition = doc["list"][i]["weather"][0]["main"].as<String>();
          count++;
        }
      }
    } 
    else Serial.println("JSON parse error (forecast)");
    
  } 
  else {
    Serial.print("HTTP error (forecast): ");
    Serial.println(httpCode);
    //Blue LED to show HTTP Error
    digitalWrite(2, LOW); 
    digitalWrite(0, HIGH);
    digitalWrite(4, HIGH);
    return;
  }
  http.end();

  float avgTemp = (count > 0) ? sumTemp / count : 0;
  int avgHumidity = (count > 0) ? sumHumidity / count : 0;

  String rainNow = (nowCondition.indexOf("Rain") != -1) ? "Rain" : "No_rain";
  String rainTomorrow = (tomorrowCondition.indexOf("Rain") != -1) ? "Rain" : "No_rain";

  // Final compact key-value message
  String msg = "Now=" + rainNow + ",Temp=" + String(nowTemp, 1) +
               ",Humidity=" + String(nowHumidity) +
               ",Tom=" + rainTomorrow + ",Temp=" + String(avgTemp, 1) +
               ",Humidity=" + String(avgHumidity);

  Serial.println(msg);       // Debug
  Serial2.println(msg);      // Send to STM32

  //Orange LED to show success
  digitalWrite(4, LOW);   
  digitalWrite(0, LOW);   
  digitalWrite(2, HIGH);  
}
