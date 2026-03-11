//XPT2046.h

#ifndef __XPT2046_H__
#define __XPT2046_H__

//宏定义可调电阻XP，热敏电阻YP，光敏电阻VBAT//8位输出
#define XPT2046_XP_8 0x9C //0x8C
#define XPT2046_YP_8 0xDC
#define XPT2046_VBAT_8 0xAC
#define XPT2046_AUS_8 0xEC
//宏定义可调电阻XP，热敏电阻YP，光敏电阻VBAT//12位输出
#define XPT2046_XP_12 0x94 //0x84
#define XPT2046_YP_12 0xD4
#define XPT2046_VBAT_12 0xA4
#define XPT2046_AUS_12 0xE4

unsigned int XPT2046_ReadAD(unsigned char Command);

#endif