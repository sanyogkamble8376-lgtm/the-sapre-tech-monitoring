
#include <WiFi.h>
#include <HTTPClient.h>

// ===== WIFI SETTINGS =====
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// ===== FIREBASE SETTINGS =====
// प्रत्येक ESP32 साठी Machine ID बदला
const char* machineId = "CNC-01";

// Firebase Realtime Database URL
const char* serverUrl =
"https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/machines/CNC-01.json";

// ===== INPUT PINS =====
const int PIN_RUNNING = 32;
const int PIN_ALARM   = 33;
const int PIN_PART    = 25;

// ===== MACHINE DATA =====
unsigned long partCount = 0;

bool lastPartState = LOW;
unsigned long lastPulseTime = 0;
unsigned long lastSendTime = 0;

const unsigned long SEND_INTERVAL = 3000;
const unsigned long DEBOUNCE_MS = 100;

void setup() {
  Serial.begin(115200);

  pinMode(PIN_RUNNING, INPUT_PULLDOWN);
  pinMode(PIN_ALARM, INPUT_PULLDOWN);
  pinMode(PIN_PART, INPUT_PULLDOWN);

  Serial.println("Connecting WiFi...");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected!");
  Serial.println(WiFi.localIP());
}

void loop() {

  bool isRunning = digitalRead(PIN_RUNNING);
  bool isAlarm = digitalRead(PIN_ALARM);
  bool partPulse = digitalRead(PIN_PART);

  // ===== PART COUNT =====
  unsigned long now = millis();

  if (partPulse == HIGH &&
      lastPartState == LOW &&
      now - lastPulseTime >= DEBOUNCE_MS) {

    partCount++;
    lastPulseTime = now;

    Serial.print("Part Count: ");
    Serial.println(partCount);
  }

  lastPartState = partPulse;

  // ===== MACHINE STATUS =====
  String status = "IDLE";

  if (isAlarm) {
    status = "ALARM";
  }
  else if (isRunning) {
    status = "RUNNING";
  }

  // ===== SEND DATA =====
  if (now - lastSendTime >= SEND_INTERVAL) {

    lastSendTime = now;

    if (WiFi.status() == WL_CONNECTED) {

      HTTPClient http;

      http.setTimeout(3000);
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");

      String payload = "{";
      payload += "\"id\":\"" + String(machineId) + "\",";
      payload += "\"status\":\"" + status + "\",";
      payload += "\"partCount\":" + String(partCount) + ",";
      payload += "\"runningSignal\":" + String(isRunning ? "true" : "false") + ",";
      payload += "\"alarmSignal\":" + String(isAlarm ? "true" : "false") + ",";
      payload += "\"updatedAt\":" + String(now);
      payload += "}";

      int responseCode = http.PUT(payload);

      Serial.println(payload);
      Serial.print("Firebase Response: ");
      Serial.println(responseCode);

      http.end();
    }
    else {
      Serial.println("WiFi Disconnected!");
      WiFi.reconnect();
    }
  }
}
