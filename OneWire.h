//OneWire.h

#ifndef __OneWire_H__
#define __OneWire_H__

unsigned char OneWire_Init();
unsigned char OneWire_ReceiveByte();
void OneWire_SendByte(unsigned char Byte);
unsigned char OneWire_ReceiveBit();
void OneWire_SendBit(unsigned char Bit);

#endif