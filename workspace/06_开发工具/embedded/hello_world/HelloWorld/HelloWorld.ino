// 嵌入式 Hello World：串口打印问候 + 板载灯闪烁
// 目标板：Arduino Uno（AVR 芯片），跟历史 P11/P12/P16 同一套板子

void setup() {
  Serial.begin(9600);          // 打开串口，用来跟电脑说话
  pinMode(LED_BUILTIN, OUTPUT); // 板载灯引脚设成输出
  Serial.println("Hello, Embedded World!");
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH); // 灯亮
  Serial.println("LED ON");
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);  // 灯灭
  Serial.println("LED OFF");
  delay(500);
}
