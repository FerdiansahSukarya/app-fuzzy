const int sensorPin = A0;  // Pin analog untuk sensor kelembaban tanah
int nilaiSensor = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  // Baca nilai ADC dari sensor
  nilaiSensor = analogRead(sensorPin);

  // Kirim nilai ke Python (hanya angka)
  Serial.println(nilaiSensor);

  delay(1000); // delay 1 detik
}
