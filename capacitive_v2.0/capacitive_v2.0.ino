const int sensorPin = A0;
int nilaiSensor = 0;
int kelembabanPersen = 0;

// Kalibrasi sensor (ubah sesuai sensor dan kondisi kamu)
const int nilaiKering = 950;  // Nilai saat tanah sangat kering
const int nilaiBasah = 600;   // Nilai saat tanah sangat basah

void setup() {
  Serial.begin(9600);
}

void loop() {
  nilaiSensor = analogRead(sensorPin);

  // Konversi ke persentase kelembaban
  kelembabanPersen = map(nilaiSensor, nilaiKering, nilaiBasah, 0, 100);
  kelembabanPersen = constrain(kelembabanPersen, 0, 100);

  String labelKelembaban = "";

  if (kelembabanPersen < 30) {
    labelKelembaban = "Kering";
  } else if (kelembabanPersen <= 69) {
    labelKelembaban = "Lembab";
  } else {
    labelKelembaban = "Basah";
  }

  Serial.print("Nilai Analog: ");
  Serial.print(nilaiSensor);
  Serial.print(" | Kelembaban: ");
  Serial.print(kelembabanPersen);
  Serial.print("% | Label: ");
  Serial.println(labelKelembaban);

  delay(2000);  // Delay 2 detik
}
