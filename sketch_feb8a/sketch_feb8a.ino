#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

// WiFi Settings
const char* ssid = "pratham";       // Replace with your WiFi name
const char* password = "12345678";   // Replace with your WiFi password

// RFID Serial setup
SoftwareSerial rfidSerial(13, 12);   // RX, TX

// Initialize LCD
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Python server IP
const char* serverIP = "192.168.136.219";  // Replace with your Python server IP
const int serverPort = 5000;               // Port where Flask is running

// Global variable for periodic fetching
unsigned long lastTotalFetchTime = 0;

void setup() {
  Serial.begin(9600);
  rfidSerial.begin(9600);
  lcd.init();
  lcd.backlight();

  // Connect to WiFi
  WiFi.begin(ssid, password);
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    lcd.setCursor(0, 1);
    lcd.print("Waiting...");
    Serial.println("Connecting to WiFi...");
  }
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("IP Address:");
  lcd.setCursor(0, 1);
  lcd.print(WiFi.localIP());
  Serial.println(WiFi.localIP());
  delay(3000);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Ready to Scan");
}

void loop() {
  // Check for RFID data
  if (rfidSerial.available() >= 12) {
    delay(100);
    char rfidData[13] = {0};
    int index = 0;
    while (rfidSerial.available() && index < 12) {
      rfidData[index++] = rfidSerial.read();
    }
    rfidData[12] = '\0';
    Serial.print("RFID Data: ");
    Serial.println(rfidData);
    sendRFIDData(rfidData);
  }
  
  // Periodically fetch data from /display every 2 seconds
  unsigned long currentMillis = millis();
  if (currentMillis - lastTotalFetchTime >= 2000) {
    fetchAndDisplayTotal();
    lastTotalFetchTime = currentMillis;
  }
}

void sendRFIDData(char* rfidData) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    String url = String("http://") + serverIP + ":" + String(serverPort) + "/scan";
    String postData = "rfid=" + String(rfidData);

    Serial.println("Connecting to: " + url);
    Serial.println("Sending Data: " + postData);

    http.begin(client, url);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    int httpResponseCode = http.POST(postData);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("HTTP Response Code: " + String(httpResponseCode));
      Serial.println("Response: " + response);
      processResponse(response);
    } else {
      Serial.println("HTTP POST Failed");
      Serial.println("Error Code: " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("WiFi is disconnected.");
  }
}

void processResponse(String response) {
  int separatorIndex = response.indexOf('\n');
  if (separatorIndex != -1) {
    String productName = response.substring(0, separatorIndex);
    String productPrice = response.substring(separatorIndex + 1);

    // Display product name and price for 2 seconds
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(productName.substring(0, 16));  // Trim to LCD width
    lcd.setCursor(0, 1);
    lcd.print("Rs." + productPrice);
    delay(2000);

    // Display total items and total amount
    fetchAndDisplayTotal();
  } else {
    // Handle unknown tag
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Unknown Tag");
    lcd.setCursor(0, 1);
    lcd.print(response);
    delay(2000);

    // Display ready message
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Ready to Scan");
  }
}

void fetchAndDisplayTotal() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    String url = String("http://") + serverIP + ":" + String(serverPort) + "/display";

    Serial.println("Fetching totals from: " + url);

    http.begin(client, url);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    int httpResponseCode = http.POST("");

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Total Response: " + response);

      // Parse the response
      int separatorIndex = response.indexOf('\n');
      if (separatorIndex != -1) {
        String totalItems = response.substring(0, separatorIndex);
        String totalAmount = response.substring(separatorIndex + 1);

        // Display total items and amount
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Items: " + totalItems);
        lcd.setCursor(0, 1);
        lcd.print("Total: Rs." + totalAmount);
      }
    } else {
      Serial.println("HTTP POST Failed");
      Serial.println("Error Code: " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("WiFi is disconnected.");
  }
}
