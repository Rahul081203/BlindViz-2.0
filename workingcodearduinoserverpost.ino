#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ESPAsyncWebServer.h>
#include "esp_task_wdt.h"

// WiFi Credentials
const char* ssid = "OnePlus Nord CE 2 Lite 5G";
const char* password = "t6judat2";

// Flask server URL (modify this to your backend server's IP)
const char* serverUrl = "http://192.168.248.17:7600/upload";

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// Initialize the HTTP server
AsyncWebServer server(80);

void setup() {
    Serial.begin(115200);
    // // Configure watchdog
    // esp_task_wdt_config_t wdt_config = {
    //     .timeout_ms = 10000,      // 10 seconds
    //     .idle_core_mask = 1 << portNUM_PROCESSORS - 1,  // run on Core 1
    //     .trigger_panic = true     // reboot if not fed
    // };
    // esp_task_wdt_init(&wdt_config);
    // esp_task_wdt_add(NULL);  // add current task to WDT
    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi");

    // Print the IP address
    delay(2000); 
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Configure the camera
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_RGB565; // Keep RGB565 format
    config.frame_size = FRAMESIZE_QVGA;  
    config.jpeg_quality = 10;  
    config.fb_count = 1;

    // Initialize the camera
    if (esp_camera_init(&config) != ESP_OK) {
        Serial.println("Camera initialization failed");
        while (true); // Halt execution if camera initialization fails
    }
    Serial.println("Camera ready!");

    // Handle HTTP request for capturing and sending an image
    server.on("/capture", HTTP_GET, [](AsyncWebServerRequest *request) {
        Serial.println("Received /capture request. Capturing image...");
        String response = sendPhoto();
        if (response.startsWith("Error:")) {
            request->send(500, "text/plain", response);
        } else {
            request->send(200, "text/plain", response);
        }
    });

    // Start the server
    server.begin();
    
    Serial.println("HTTP Server started. Use 'http://ESP32_IP/capture' to trigger image capture.");
}

void loop() {
    // Nothing to do in loop, as server handles everything
    // esp_task_wdt_reset();  // Optional: keeps watchdog happy in case you add work here later
    // delay(1000);
}

String sendPhoto() {
    WiFiClient client;
    HTTPClient http;

    // Capture an image
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Camera capture failed");
        restartCamera(); // Reinitialize the camera if capture fails
        return "Error: Camera capture failed";
    }

    Serial.println("Converting RGB565 to JPEG...");
    size_t jpg_size;
    uint8_t* jpg_buf;

    bool converted = fmt2jpg(fb->buf, fb->len, fb->width, fb->height, PIXFORMAT_RGB565, 80, &jpg_buf, &jpg_size);
    if (!converted) {
        Serial.println("Conversion to JPEG failed");
        esp_camera_fb_return(fb); // Release the frame buffer
        return "Error: Conversion to JPEG failed";
    }

    Serial.println("Connecting to server...");
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "image/jpeg");
    http.setTimeout(5000); // Set timeout to 5 seconds
    esp_task_wdt_reset();
    int httpResponseCode = http.POST(jpg_buf, jpg_size);
    esp_task_wdt_reset();
    String llmResponse = "";
    if (httpResponseCode > 0) {
        Serial.println("Image sent successfully");

        // Parse the response from the server
        String response = http.getString();
        Serial.println("Server response:");
        Serial.println(response);

        // Remove whitespace and line breaks from the response
        response.replace("\n", "");
        response.replace("\r", "");
        // response.replace(" ", "");

        int startIndex = response.indexOf("\"response\":") + 11; // includes colon and space
        while (response[startIndex] == ' ') startIndex++; // skip extra spaces if any

        // Now find the first double quote that starts the actual message
        startIndex = response.indexOf("\"", startIndex) + 1;
        int endIndex = response.indexOf("\"", startIndex);

        if (startIndex > 0 && endIndex > startIndex) {
            llmResponse = response.substring(startIndex, endIndex);
        } else {
            llmResponse = "Error: Failed to parse LLM response";
        }
        Serial.println("LLM response:");
        Serial.println(llmResponse);
    } else {
        Serial.print("Error sending image: ");
        Serial.println(httpResponseCode);
        llmResponse = "Error: Failed to send image";
    }

    // Release resources
    free(jpg_buf);
    esp_camera_fb_return(fb);
    delay(500); // Add a delay between captures
    http.end();

    return llmResponse;
}

void restartCamera() {
    esp_camera_deinit(); // Deinitialize the camera
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_RGB565;
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 10;
    config.fb_count = 1;

    if (esp_camera_init(&config) != ESP_OK) {
        Serial.println("Camera reinitialization failed");
    } else {
        Serial.println("Camera reinitialized successfully");
    }
}
