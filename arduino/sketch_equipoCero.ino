/*
  LIBRERÍAS NECESARIAS
*/
#include <EEPROM.h>
#include "GravityTDS.h"
/*
  DEFINICIÓN DE PINES DIGITALES
*/
// Sensor Selenoide
int selenoide_signal = 8; // Digital 2
// SOPLADOR DE ASPIRADO
int sentidoA = 4;
int sentidoB = 5;
int aire_poder = 9;
volatile int NumPulsos; //variable para la cantidad de pulsos recibidos
int aire_caudal = 2;    //Sensor conectado en el pin 8
float factor_conversion=7245.0; //para convertir de frecuencia a caudal

/*
  DEFINICIÓN DE PINES ANALÓGICOS
*/
// int pm_sensor = A0;
#define TdsSensorPin A1
GravityTDS gravityTds;
// TDS Variables
float temperature = 25,tdsValue = 0;

void ContarPulsos ()
{ 
  NumPulsos++;  //incrementamos la variable de pulsos
} 


void setup() {
  // CONFIGURACIÓN CONSOLA SERIAL
  Serial.begin(9600);


  //CONFIGURACIÓN PINES DIGITALES
  pinMode(selenoide_signal, OUTPUT);
  pinMode(sentidoA, OUTPUT);
  pinMode(sentidoB, OUTPUT);

  // CONFIGURACIÓN PINES ANALÓGICOS
  pinMode(aire_caudal, INPUT);
  attachInterrupt(0,ContarPulsos,RISING); // <---------------
  pinMode(aire_poder, OUTPUT); 

  // TDS CONFIG
  gravityTds.setPin(TdsSensorPin);
  gravityTds.setAref(5.0);  //reference voltage on ADC, default 5.0V on Arduino UNO
  gravityTds.setAdcRange(1024);  //1024 for 10bit ADC;4096 for 12bit ADC
  gravityTds.begin();  //initialization

}

/*
  MÓDULOS DE CONTROL PARA LOS SENSORES
*/

void changeSelenoide(bool action){
  /*
    Utilicela para cambiar la señal dirigida al MOSFET, el cual controla
    la válvula selenoide.
  */
  if(action){
    digitalWrite(selenoide_signal, HIGH);
  } else {
    digitalWrite(selenoide_signal, LOW);
  }
}

void airController(char sentido, int power){
  /*
    Utilícese para encender el motor de aspirado en un sentido señalado.
    Para indiciar el sentido de giro utilice 'L' para izquierda y 'R' derecha.
    Cualquier otro caracter desactivará ambos sentidos.
    La potencia 'power' debe establecerse en valores entre 0 y 255
  */
  if(power > 255){
    power = 255;
  } else if(power < 0){
    power = 0;
  }


  if(sentido == 'L'){
    // Se asegura de girar hacia el sentido A, desactivando B
    analogWrite(aire_poder, power);
    digitalWrite(sentidoA, HIGH);
    digitalWrite(sentidoB, LOW);
  } else if(sentido == 'R'){
    // Se asegura de girar hacia el sentido B, desactivando A
    analogWrite(aire_poder, power);
    digitalWrite(sentidoA, LOW);
    digitalWrite(sentidoB, HIGH);
  } else {
    // Si el caracter no coincide con los anteriores, desactiva ambos sentidos
    analogWrite(aire_poder, 0);
    digitalWrite(sentidoA, LOW);
    digitalWrite(sentidoB, LOW);
  }
}

float getAirMeasure(){
  
  // Leyendo datos provenientes del Water Flow Sensor
  // WFS entrega una frecuencia de giro
  float hz = analogRead(aire_caudal);
  float result = hz / 7.5;
  Serial.println(result);
  return result;
  delay(2000);

}

int ObtenerFrecuencia() 
{
  int frecuencia;
  NumPulsos = 0;   //Ponemos a 0 el número de pulsos
  interrupts();    //Habilitamos las interrupciones
  delay(1000);   //muestra de 1 segundo
  noInterrupts(); //Desabilitamos las interrupciones
  frecuencia=NumPulsos; //Hz(pulsos por segundo)
  return frecuencia;
}

/* FIN DE LA SECCIÓN DE MÓDULOS */

void loop() {
  changeSelenoide(true);
  analogWrite(aire_poder, 192);
  digitalWrite(sentidoA, LOW);
  digitalWrite(sentidoB, HIGH);


  float frecuencia=ObtenerFrecuencia(); //obtenemos la Frecuencia de los pulsos en Hz
  float caudal_L_m=(frecuencia/factor_conversion) * 60; //calculamos el caudal en L/m

  Serial.print ("FrecuenciaPulsos: "); 
  Serial.print (frecuencia,0); 
  Serial.print ("Hz\tCaudal: "); 
  Serial.print (caudal_L_m,3); 
  Serial.print (" L/m\t"); 

    //temperature = readTemperature();  //add your temperature sensor and read it
  gravityTds.setTemperature(temperature);  // set the temperature and execute temperature compensation
  gravityTds.update();  //sample and calculate
  tdsValue = gravityTds.getTdsValue();  // then get the value
  Serial.print(tdsValue,0);
  Serial.println("ppm");
  delay(1000);

}






















