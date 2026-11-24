#include <WiFi.h>
#include <HTTPClient.h>

// WiFi Details
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// Server / Firebase API Endpoint
const char* serverUrl = "https://your-project-id.firebaseio.com/machines/CNC-01.json";

// Input Pins from Machine Panel (via Optocoupler)
const int PIN_RUNNING = 32; // Green Tower Light / Cycle Start
const int PIN_ALARM   = 33; // Red Tower Light / Alarm Signal
const int PIN_PART    = 25; // M30 / Part Count Pulse Signal

int partCount = 0;
bool lastPartState = LOW;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_RUNNING, INPUT_PULLDOWN);
  pinMode(PIN_ALARM, INPUT_PULLDOWN);
  pinMode(PIN_PART, INPUT_PULLDOWN);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
}

void loop() {
  bool isRunning = digitalRead(PIN_RUNNING);
  bool isAlarm   = digitalRead(PIN_ALARM);
  bool partPulse = digitalRead(PIN_PART);

  // Detect Part Count (Rising Edge)
  if (partPulse == HIGH && lastPartState == LOW) {
    partCount++;
  }
  lastPartState = partPulse;

  // Determine Machine Status
  String status = "IDLE";
  if (isAlarm) {
    status = "ALARM";
  } else if (isRunning) {
    status = "RUNNING";
  }

  // Send Data to Cloud every 3 seconds
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"id\":\"CNC-01\",\"status\":\"" + status + "\",\"partCount\":" + String(partCount) + "}";
    int httpResponseCode = http.PUT(jsonPayload);
    
    Serial.println("Sent: " + jsonPayload + " | Code: " + String(httpResponseCode));
    http.end();
  }

  delay(3000);
}