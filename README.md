# RFID-Based Smart Shopping System

## Overview
This project combines three major components to create an RFID-based shopping experience:

1. **ESP8266 Microcontroller Code** (C++/Arduino)
2. **Flask Backend** (Python)
3. **Streamlit Frontend** (Python)

The main idea is to scan RFID tags on products using the ESP8266 device, communicate the product ID to a Flask server, and display/track products and totals in a web-based Streamlit application. This README will walk you through setup, configuration, and usage.

---

## 1. Hardware & Setup for the ESP8266

### Hardware Requirements
- ESP8266 module (e.g., NodeMCU or Wemos D1 Mini)
- RFID reader module
- LCD (LiquidCrystal_I2C)
- Jumpers/Wires
- USB cable for programming the ESP8266
- A computer with Arduino IDE (or PlatformIO) installed
- Access to a WiFi network

### Wiring
1. **RFID Reader**: Connected via SoftwareSerial pins `13` (RX) and `12` (TX) on ESP8266 (as configured in the code).
2. **LCD**: I2C pins typically connected to **SDA** and **SCL** (check your board’s pinout). The code uses address `0x27`, but confirm your LCD’s I2C address.
3. **Power**: Ensure the modules are powered at proper voltages (3.3V for ESP8266, check your RFID module’s voltage requirements).

### Libraries Needed (Arduino/ESP8266)
- **ESP8266WiFi.h**
- **ESP8266HTTPClient.h**
- **Wire.h**
- **LiquidCrystal_I2C.h** (often from a custom library fork for ESP8266)
- **SoftwareSerial.h**

### Installation
1. Open the code in the Arduino IDE or your preferred environment.
2. Install the ESP8266 board package from the Arduino Boards Manager (if using Arduino IDE).
3. Verify you have installed all required libraries.
4. Update the following lines in the code with your **WiFi SSID**, **Password**, and **Server IP**:
   ```cpp
   const char* ssid = "pratham";       // Replace with your WiFi name
   const char* password = "12345678";  // Replace with your WiFi password
   const char* serverIP = "192.168.136.219";  // Replace with your Flask server IP
   ```
5. Connect your ESP8266 board.
6. Compile and upload the code.
7. Open the Serial Monitor (baud rate: 9600) to observe debug messages.

### How It Works
1. After successful WiFi connection, the LCD will display your IP address and eventually show **"Ready to Scan"**.
2. When an RFID tag is scanned:
   - The tag’s unique ID is read by the RFID module.
   - The ESP8266 sends an HTTP POST request to the Flask endpoint `/scan`, passing the RFID as `rfid=TAG_VALUE`.
   - The Flask server responds with the product name & price or **"Unknown Tag"** if not found.
   - The ESP8266 displays the product details on the LCD briefly, then reverts to showing total items and amount.
3. The ESP8266 also periodically checks `/display` to update total items and total bill on the LCD.

---

## 2. Flask Backend Setup

### Requirements
- Python 3.x
- `Flask`
- Possibly `requests` for internal usage if needed

Install the dependencies:
```
pip install flask requests
```

### Project Structure
The key file is `app.py` (or whatever Python file the code is in), containing:
- Predefined product list with RFID mappings.
- `/scan` endpoint to handle RFID scans.
- `/display` endpoint to return total items and amount.
- Additional endpoints:
  - `/products` - returns all available products
  - `/bill` - returns items in the cart
  - `/reduce_quantity` - reduce an item quantity
  - `/add_product` - add a product by ID
  - `/drop_product` - drop an item entirely from the cart

### Running the Flask App
1. Make sure you’re in the directory containing the Flask code.
2. Run:
   ```bash
   python app.py
   ```
3. By default, the app will run on port `5000` at `http://0.0.0.0:5000`. If you’re using localhost on your development machine, the address is `http://127.0.0.1:5000`.
4. Update the ESP code with the correct IP address (if it’s on the same network, you may need your local network IP rather than `127.0.0.1`).

### Testing with cURL or Browser
- **Check product list**: `GET /products` => `http://<serverip>:5000/products`
- **View cart**: `GET /bill` => returns a JSON object of scanned items
- **Simulate an RFID scan**: `POST /scan` with form data `rfid=<TAG>`

---

## 3. Streamlit Frontend

### Requirements
- Python 3.x
- `streamlit`
- `requests`

Install the dependencies:
```
pip install streamlit requests
```

### Code Overview
The main code does the following:
- **Products Page**: Lists all available products from the `/products` endpoint, letting you add an item to the cart.
- **Cart Page**: Shows the current cart from the `/bill` endpoint, allowing you to increment, decrement, or drop items.
- **Store Layout**: An additional page showing a store layout image.

### Running the Streamlit App
1. Place the Streamlit code in a file, e.g., `app_frontend.py`.
2. In your terminal, run:
   ```bash
   streamlit run app_frontend.py
   ```
3. By default, Streamlit will open a local web server on port `8501`. You’ll see a URL like `http://localhost:8501`.
4. Make sure the `BASE_URL` in the code is updated to point to your Flask server, for example:
   ```python
   BASE_URL = "http://192.168.136.219:5000"  # or wherever Flask is accessible
   ```

### Directory Structure Example
```
project/
 ├── esp_code/
 │    └── main.ino
 ├── backend/
 │    └── app.py
 ├── frontend/
 │    └── app_frontend.py
 ├── images/
 │    ├── biscuit.jpg
 │    ├── bread.jpg
 │    ├── store_layout.jpg
 │    └── ...
 └── README.md
```

---

## 4. End-to-End Usage
1. **Start the Flask server**:
   - `cd backend`
   - `python app.py`
   - Note the IP address or domain (e.g., `192.168.0.100:5000`).
2. **Configure & run the ESP8266**:
   - Update `serverIP` and credentials in the ESP code.
   - Upload to your board.
   - Open Serial Monitor to see logs.
3. **Run the Streamlit Frontend**:
   - `cd frontend`
   - `streamlit run app_frontend.py`
   - Access `localhost:8501` in your browser.
4. **Scan an RFID tag**:
   - The ESP8266 reads the tag, sends it to the Flask server.
   - If recognized, the product is added to the cart. The total updates.
   - The LCD on the ESP8266 shows you the new total.
   - The Streamlit app’s cart will also reflect the updated items.

---

## 5. Common Troubleshooting
- **WiFi not connecting**: Double-check SSID and password in the ESP code.
- **LCD not displaying properly**: Check I2C address or wiring.
- **Flask server unreachable**: Ensure your server and ESP8266 are on the same network. Use your PC’s local IP (not `127.0.0.1`) if the ESP8266 is connecting over WiFi.
- **RFID reads no data**: Check baud rates, wiring (RX-TX cross), and library initialization.
- **Images not showing in Streamlit**: Verify the `images/` folder path is correct.

---

## 6. Acknowledgments
- **Arduino & Libraries**: For enabling the ESP8266 to handle WiFi and HTTP.
- **Flask**: For an easy Python web server.
- **Streamlit**: For building interactive Python dashboards and apps.

---

## 7. License
Include a license if needed (e.g., MIT, Apache 2.0, etc.).

---

**Enjoy your RFID-based smart shopping demo!**

