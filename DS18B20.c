//DS18B20.c

#include <STC89C5xRC.H>
#include "OneWire.h"

//DS18B20指令
#define DS18B20_SKIP_ROM 0xCC
#define DS18B20_CONVERT_T 0x44
#define DS18B20_READ_SCRATCHPAD 0xBE

/**
  * @brief  DS18B20开始温度变换
  * @param  无
  * @retval 无
  */
void DS18B20_ConvertT(){
	OneWire_Init();//单总线初始化
	OneWire_SendByte(DS18B20_SKIP_ROM);//单总线发送1个字节（跳过ROM指令）
	OneWire_SendByte(DS18B20_CONVERT_T);//单总线发送1个字节（转换温度指令）
}

/**
  * @brief  DS18B20读取温度
  * @param  无
  * @retval 温度数值
  */
float DS18B20_ReadT(){
	unsigned char TLSB,TMSB;//温度格式
	int Temp;//临时变量
	float T;//浮点数温度
	OneWire_Init();//单总线初始化
	OneWire_SendByte(DS18B20_SKIP_ROM);//单总线发送1个字节（跳过ROM指令）
	OneWire_SendByte(DS18B20_READ_SCRATCHPAD);//单总线发送1个字节（转换温度指令）
	TLSB=OneWire_ReceiveByte();//低8位
	TMSB=OneWire_ReceiveByte();//高8位
	Temp=(TMSB<<8)|TLSB;//合并温度16位
	T=Temp/16.0;//正确转换温度（浮点数）
	return T;//返回温度值
}