/*
  BootEsp32.ino - Firmware ESP32 para control de r6g_steppermotor.
  Autor: Alejandro Tevera Ruiz
  Contacto: atevera.rz@gmail.com
  Lanzada para dominio público en 2020. 
*/

#include<r6gController.h>
#include<ArduinoJson.h>

//Declaración de clase Robot.
Robot r6g;

//Declaración de clases DoF.
Joint DoF1;
Joint DoF2;
Joint DoF3;
Joint DoF4;
Joint DoF5;
Joint DoF6;

//Variable temporal para almacenamiento del mensaje serial.
String ROSmessage = "";

DynamicJsonDocument doc(1024);

void setup()
{
  //Inicialización de monitor serial.
  Serial.begin(115200);

  //Configuración de pines: Dir, Step.
  DoF1.SetPines(23,22); //23,22
  DoF2.SetPines(21,19);
  DoF3.SetPines(18,5);
  DoF4.SetPines(17,16);
  DoF5.SetPines(4,15);
  DoF6.SetPines(32,33);

  //Configuración de Relación Mecánica. 
  DoF1.SetRelation(7.1);
  DoF2.SetRelation(5.75);
  DoF3.SetRelation(5);
  DoF4.SetRelation(2.8);
  DoF5.SetRelation(2.1);
  DoF6.SetRelation(1);

  //Configuración de Velocidad Angular Relativa (Método: Delay entre Pasos). 
  DoF1.SetSpeedRotation(10);
  DoF2.SetSpeedRotation(10);
  DoF3.SetSpeedRotation(25);
  DoF4.SetSpeedRotation(10);
  DoF5.SetSpeedRotation(10);
  DoF6.SetSpeedRotation(10);

  //Configuración de Z+ para Modelo DH.
  DoF1.SetPositiveTurn(LOW);
  DoF2.SetPositiveTurn(LOW);
  DoF3.SetPositiveTurn(HIGH);
  DoF4.SetPositiveTurn(LOW);
  DoF5.SetPositiveTurn(LOW);
  DoF6.SetPositiveTurn(HIGH);

  //Configuración de límites por Software. 
  DoF1.SetSoftwareLimits(-90,90);
  DoF2.SetSoftwareLimits(-60,100);
  DoF3.SetSoftwareLimits(-70,60);
  DoF4.SetSoftwareLimits(-70,70);
  DoF5.SetSoftwareLimits(-10,100); 
  DoF6.SetSoftwareLimits(-90,90);

  //Configuración de posiciones de inicio. 
  DoF1.SetInitialAngle(0);
  DoF2.SetInitialAngle(-71);
  DoF3.SetInitialAngle(75);
  DoF4.SetInitialAngle(0);
  DoF5.SetInitialAngle(0);
  DoF6.SetInitialAngle(0);

  //Reinicio de motores: Apagados. 
  ResetMotors();

  //Inicio de efector final [Electroimán]
  r6g.InitEndEffector(2);

}

void loop()
{
  String input = "";
  char var;

  //Lectura de mensaje en ROS.
  while(Serial.available())
  {
    var = Serial.read();
    input = String(var);
    ROSmessage += input;
  }
  if(var == '}') //Verifica estructura JSON con el último caracter.
  {
    digitalWrite(2,LOW);
    //Obtención de valores del mesaje tipo JSON.
    deserializeJson(doc, ROSmessage);
    JsonObject Angles = doc.as<JsonObject>();
    //Inicializa y asigna los valores al array de envío para movimiento. 
    float FlagAngles[6] = {};
    for(int i = 0; i < 6; i++)
    {
      String index = "J" + String(i+1);
      FlagAngles[i] = Angles[index].as<float>();
    }

    //Actualiza el estado del efector final.
    bool State_EF = Angles["EF"].as<int>() == 1;
    
    //Movimiento del robot.
    MoveJ(FlagAngles, State_EF);

    //Limpia variable del mesaje. 
    ROSmessage = ""; 
  }  
  Serial.println("OK"); //Confirmación de disponibilidad. 
}

void MoveJ(float *FlagAngles, bool EndEffector)
{
  ResetMotors();
  //Cálculo de pasos para cada articulación. 
  int Steps[] = {0,0,0,0,0,0};
  Steps[0] = DoF1.DegreesToSteps(FlagAngles[0]);
  Steps[1] = DoF2.DegreesToSteps(FlagAngles[1]);
  Steps[2] = DoF3.DegreesToSteps(FlagAngles[2]);
  Steps[3] = DoF4.DegreesToSteps(FlagAngles[3]);
  Steps[4] = DoF5.DegreesToSteps(FlagAngles[4]);
  Steps[5] = DoF6.DegreesToSteps(FlagAngles[5]);

  //Cálculo del máximo número de pasos.
  int Pmax = r6g.MaxDegrees(Steps);

  //Envío de pulsos a cada Driver.
  for(int i = 0; i <= Pmax+2; i++)
  {
    digitalWrite(r6g.GetEndEffector(), EndEffector);    
    DoF1.AngularMove(FlagAngles[0], Steps[0],i);
    DoF2.AngularMove(FlagAngles[1], Steps[1],i);
    DoF3.AngularMove(FlagAngles[2], Steps[2],i);
    DoF4.AngularMove(FlagAngles[3], Steps[3],i);
    DoF5.AngularMove(FlagAngles[4], Steps[4],i);
    DoF6.AngularMove(FlagAngles[5], Steps[5],i);
  }

  ResetMotors();
  
}

void ResetMotors()
{
  //Reestablecimiento de motores a paso.
  DoF1.Shutdown();
  DoF2.Shutdown();
  DoF3.Shutdown();
  DoF4.Shutdown();
  DoF5.Shutdown();
  DoF6.Shutdown();
}
