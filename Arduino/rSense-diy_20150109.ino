/**
 * rSense
 * Copyright (c) 2014 Yukihiro Nomura All rights reserved.
 * rsensesystems@gmail.com
 *
 * rSense is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * rSense is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with rSense.  If not, see <http://www.gnu.org/licenses/>.
 *
 * 2015/01/09	
 */

#include <XBee.h>
#include <EEPROM.h>
#include "DHT.h"

#define DHTPIN 3
#define DHTTYPE DHT11
#define actu1 2
#define actu2 4
#define actu3 5
#define actu4 6
#define actu5 7

const byte EEPROM_ID = 0x99;
const int ID_ADDR = 0;

/* This is for smoothing data */
// バッファの長さ
const int BUFFER_LENGTH = 5;
// バッファの中央のインデックス
const int INDEX_OF_MIDDLE = BUFFER_LENGTH / 2;
// バッファ
int buffer[BUFFER_LENGTH];
// バッファにデータを書き込むインデックス
int index = 0;

DHT dht(DHTPIN, DHTTYPE);
const int wsensorPin = A0; //土壌水分センサー用のアナログピン番号
int wsensorValuePre = 0;   //データースムーシングよう
int wsensorValue = 0;
int dhthumed,dhttemp; 

// センサーデーターをコントロラーに送信するための準備
// create the XBee object
XBee xbee = XBee();
uint8_t payload[] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

// SH + SL Address of receiving XBee
XBeeAddress64 addr64 = XBeeAddress64(0x0013a200, 0x40ada218);
ZBTxStatusResponse txStatus = ZBTxStatusResponse();
ZBRxResponse zbRx = ZBRxResponse();

// コントローラーからの依頼でセンサーデーターを送信
void sendsensordata() {
getdht();
getwmoist1();

ZBTxRequest zbTx = ZBTxRequest(addr64, payload, sizeof(payload));
xbee.send(zbTx);
  
// after sending a tx request, we expect a status response
// wait up to half second for the status response
  if (xbee.readPacket(500)) 
  {
    // should be a znet tx status            	
    if (xbee.getResponse().getApiId() == ZB_TX_STATUS_RESPONSE) 
    {
      xbee.getResponse().getZBTxStatusResponse(txStatus);
      // get the delivery status, the fifth byte
      if (txStatus.getDeliveryStatus() == SUCCESS) 
      {
        // success.  time to celebrate
        Serial.print("got it");
        
      } else 
      {
        
        Serial.print("something went wrong..");
      }   
    }
  } else if (xbee.getResponse().isError()) 
  
  {
    
  } else 
  
  {
    
   Serial.print("something went wrong..");
  }
  
}

// コントローラーから送られてくるデーターをローカルに保存する準備
void readcommand() 
{  
  char command[] = {0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0, 
                    0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0
                   }; 
  
  xbee.readPacket();  
  if (xbee.getResponse().isAvailable()) 
  {
      Serial.print("Got it!");
      xbee.getResponse().getZBRxResponse(zbRx);    
      strncpy(command, (char *)zbRx.getData(), sizeof(command));
      String commandstring = command;
      // 一回に２つのセンサー情報を受信する
      String a1 = commandstring.substring(0, 4);   //sensorid1
      String a2 = commandstring.substring(4, 8);   //status1
      String a3 = commandstring.substring(8, 12);  //port1
      String a4 = commandstring.substring(12, 16); //interval
      String a5 = commandstring.substring(16, 20); //mode1  
      
      String a6 = commandstring.substring(20, 24); //sensorid2
      String a7 = commandstring.substring(24, 28); //status2
      String a8 = commandstring.substring(28, 32); //port2
      String a9 = commandstring.substring(32, 36); //interval2
      String a10 = commandstring.substring(36, 40); //mode2
      
      int sensorid1 = a1.toInt();
      int status1 = a2.toInt();
      int port1 = a3.toInt();
      int interval1 = a4.toInt();
      int mode1 = a5.toInt();
      
      int sensorid2 = a6.toInt();
      int status2 = a7.toInt();
      int port2 = a8.toInt();
      int interval2 = a9.toInt();
      int mode2 = a10.toInt();
      
      // デバック用
      /*
      Serial.print(sensorid1); 
      Serial.print(status1); 
      Serial.print(port1); 
      Serial.print(interval1); 
      Serial.print(mode1);
      
      Serial.print(sensorid2); 
      Serial.print(status2); 
      Serial.print(port2); 
      Serial.print(interval2); 
      Serial.print(mode2);
      */
      
      // 取得したデータを所定のピンに保存
      if(sensorid1 == 1111) 
      {
      
        byte hiByte = highByte(status1);
        byte lowByte = lowByte(status1);
        EEPROM.write(2, hiByte);
        EEPROM.write(3, lowByte); 
      
        byte hiByte2 = highByte(port1);
        byte lowByte2 = lowByte(port1);
        EEPROM.write(4, hiByte2);
        EEPROM.write(5, lowByte2);
      
        byte hiByte3 = highByte(interval1);
        byte lowByte3 = lowByte(interval1);
        EEPROM.write(6, hiByte3);
        EEPROM.write(7, lowByte3);
      
        byte hiByte4 = highByte(mode1);
        byte lowByte4 = lowByte(mode1);
        EEPROM.write(8, hiByte4);
        EEPROM.write(9, lowByte4);
      
        byte hiByte5 = highByte(status2);
        byte lowByte5 = lowByte(status2);
        EEPROM.write(10, hiByte5);
        EEPROM.write(11, lowByte5);
      
        byte hiByte6 = highByte(port2);
        byte lowByte6 = lowByte(port2);
        EEPROM.write(12, hiByte6);
        EEPROM.write(13, lowByte6);
      
        byte hiByte7 = highByte(interval2);
        byte lowByte7 = lowByte(interval2);
        EEPROM.write(14, hiByte7);
        EEPROM.write(15, lowByte7);
      
        byte hiByte8 = highByte(mode2);
        byte lowByte8 = lowByte(mode2);
        EEPROM.write(16, hiByte8);
        EEPROM.write(17, lowByte8);
           
      }
       
        // もし、センサー情報送信依頼だったら、送信する
       if(sensorid1 == 1212) 
       {
         sendsensordata();
       }                
   }
 
}

// union to convery float to byte string
union u_tag {
    uint8_t b[4];
    float fval;
} u;

//DHTからデータを取得する
void getdht() 
{ 
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  float t = dht.readTemperature(); 
  // check if returns are valid, if they are NaN (not a number) then something went wrong!
  if (isnan(t) || isnan(h)) 
  {
    Serial.println("Failed to read from DHT");
  } else 
  
    {
      // デバッグ用
      /*
      Serial.print("Humidity: "); 
      Serial.print(h);
      Serial.print(" %\t");
      Serial.print("Temperature: "); 
      Serial.print(t);
      Serial.println(" *C");
      */
    
      u.fval = h;
      for (int i=0;i<4;i++)
      {
        //Payloadに設定
        payload[i]=u.b[i];
      }  
     
       u.fval = t;
       for (int i=0;i<4;i++)
       {
         //Payloadに設定
       payload[i+4]=u.b[i];
       }
  
    }  
  
}

// 水分センサー1
void getwmoist1() 
{
  wsensorValue = analogRead(wsensorPin);  
  
  // データスムージング
  buffer[index] = wsensorValue;
  index = (index + 1) % BUFFER_LENGTH;
  // Medianフィルタでスムージング
  int smoothedByMedianFilter = smoothByMedianFilter();  
  u.fval = smoothedByMedianFilter;
  
  for (int i=0;i<4;i++)
  {
    //Payloadに設定
  payload[i+8]=u.b[i];
  }
  
}

// 保存したデータを読み込む
void actkick() {
  
  byte hiByte =  EEPROM.read(2);
  byte lowByte =  EEPROM.read(3);

  byte hiByte2 =  EEPROM.read(4);
  byte lowByte2 =  EEPROM.read(5);
  
  byte hiByte3 =  EEPROM.read(6);
  byte lowByte3 =  EEPROM.read(7);
  
  byte hiByte4 =  EEPROM.read(8);
  byte lowByte4 =  EEPROM.read(9);
  
  byte hiByte5 =  EEPROM.read(10);
  byte lowByte5 =  EEPROM.read(11);
  
  byte hiByte6 =  EEPROM.read(12);
  byte lowByte6 =  EEPROM.read(13);
  
  byte hiByte7 =  EEPROM.read(14);
  byte lowByte7 =  EEPROM.read(15);
  
  byte hiByte8 =  EEPROM.read(16);
  byte lowByte8 =  EEPROM.read(17);
  
  int status1 =  word(hiByte, lowByte);
  int port1 = word(hiByte2, lowByte2);
  int interval1 = word(hiByte3,lowByte3);
  int mode1 = word(hiByte4, lowByte4);
  
  int status2 =  word(hiByte5, lowByte5);
  int port2 = word(hiByte6, lowByte6);
  int interval2 =  word(hiByte7, lowByte7);
  int mode2 = word(hiByte8, lowByte8);
   
  // 現在のデーターに基づいてアクチュエーターの起動を行う 
  wsensorValuePre = analogRead(wsensorPin);
  
  /* For smoothing data */
  buffer[index] = wsensorValuePre;
  index = (index + 1) % BUFFER_LENGTH;
  //Medianフィルタでスムージング
  wsensorValue = smoothByMedianFilter();  
  
  // DHT から温湿度を取得
  dhthumed = dht.readHumidity();
  dhttemp = dht.readTemperature(); 

// デバッグ用
/*
  Serial.print("status1 is ");  
  Serial.print(status1);
  Serial.print("port1 is ");  
  Serial.print(port1);
  Serial.print("INTERVAL ");
  Serial.print(interval1)  ;
  Serial.print("mode1 ");
  Serial.print(mode1)  ;
  
  Serial.print("status2 is ");  
  Serial.print(status2);
  Serial.print("port2 is ");  
  Serial.print(port2);
  Serial.print("INTERVAL ");
  Serial.print(interval2)  ;
  Serial.print("mode2 ");
  Serial.print(mode2)  ;
  
  Serial.print("status3 is ");  
  Serial.print(status3);
  Serial.print("port3 is ");  
  Serial.print(port3);
  Serial.print("INTERVAL ");
  Serial.print(interval3)  ;
  Serial.print("mode3 ");
  Serial.print(mode3)  ;
  
  Serial.print("status4 is ");  
  Serial.print(status4);
  Serial.print("port4 is ");  
  Serial.print(port4);
  Serial.print("INTERVAL ");
  Serial.print(interval4)  ;
  Serial.print("mode4 ");
  Serial.print(mode4)  ;
  
  Serial.print("status5 is ");  
  Serial.print(status5);
  Serial.print("port5 is ");  
  Serial.print(port5);
  Serial.print("INTERVAL ");
  Serial.print(interval5)  ;
  Serial.print("mode5 ");
  Serial.print(mode5)  ;
 */
  
  // 水分センサーに基ずく電源ON OFF制御
   if(wsensorValue != 0.0) 
   { 
  
      if(status1 == 9999) 
      {
     
         digitalWrite(port1, HIGH);
     
      } else if(status1 == 8888) 
        
        {
       
           digitalWrite(port1, LOW);
           
        } else if(status1 == 7777) 
            
            {
           
             if(mode1 == 1111 && wsensorValue > interval1) 
               
               {

               digitalWrite(port1, HIGH);
               
               } else if(mode1 == 2222 && wsensorValue < interval1) 
               
                 {

                 digitalWrite(port1, HIGH);          
       
                 } else 
                 
                 {
      
                   digitalWrite(port1, LOW);
                 }
     
             } else 
             
             {
              digitalWrite(port1, LOW); 
    
             }
 
 }
 
 
    // DH温度湿度センサーに基づくアクション 巻き上下機
    if(dhttemp != 0) 
    { 
  
      if(status2 == 9999) 
      {
         digitalWrite(actu1, HIGH);
         digitalWrite(port2, HIGH);       
     
      } else if(status2 == 8888) 
         
         {
           
         digitalWrite(actu1, LOW);
         digitalWrite(port2, LOW);
           
         } else if(status2 == 7777) 
         
           {
           
             if(dhttemp > interval2) 
             {

                digitalWrite(port2, HIGH);
                digitalWrite(actu1, HIGH);
               
              } else if(dhttemp < interval2) 
              
                {
                  digitalWrite(port2, LOW);
                  digitalWrite(actu1, LOW);      
       
                } else 
              
                  {
      
                   //Do nothing here
                  }
     
             } else 
             
               {
           
                //Do nothing here
    
               }
 
   }
 
   
}
  

void setup() {
 
  pinMode(actu1, OUTPUT); // D2
  pinMode(actu2, OUTPUT); // D4
  pinMode(actu3, OUTPUT); // D5
  
  //シリアル開始
  Serial.begin(9600);
  //Xbee シリアルで初期化
  xbee.setSerial(Serial);
  //DHTデーター取得開始
  dht.begin();
  
}

// Medianフィルタによるスムージング
int smoothByMedianFilter() 
{
  // ソートに使用するバッファ
  static int sortBuffer[BUFFER_LENGTH];
  // ソートに使用するバッファにデータをコピー
  for (int i = 0; i < BUFFER_LENGTH; i++) 
  {
    sortBuffer[i] = buffer[i];
  }

  // クイックソートで並び替える
  // 引数はバッファ、要素の数、要素のサイズ、比較用の関数
  qsort(sortBuffer, BUFFER_LENGTH, sizeof(int),
  comparisonFunction);

  // ソート結果の中央の値を出力結果として返す
  return sortBuffer[INDEX_OF_MIDDLE];
}

// クイックソートで使用する比較用の関数
int comparisonFunction(const void *a, const void *b) 
{
  // void型をint型にキャスト
  int _a = *(int *)a;
  int _b = *(int *)b;
  if (_a < _b) 
  {
    // a < bであれば-1を返す
    return -1;
  } 
  else if (_a > _b) 
    {
      // a > bであれば1を返す
      return 1;
    } 
  else 
    {
      // いずれでもない（つまりa == b）であれば0を返す
      return 0;
    }
}


void loop() {  
      
readcommand();  
actkick();

delay(1000);
}


