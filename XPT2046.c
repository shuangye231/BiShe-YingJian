#include <STC89C5xRC.H>
#include "Delay.h"

//定义引脚
sbit XPT2046_CS=P3^5;
sbit XPT2046_DIN=P3^4;
sbit XPT2046_DCLK=P3^6;
sbit XPT2046_DOUT=P3^7;

//读取模拟信号转换为数字信号
unsigned int XPT2046_ReadAD(unsigned char Command){//Command模拟信号指令
	unsigned int ADVAlue=0;//数字信号
	unsigned char i;//定义循环，右移单位
	XPT2046_DCLK=0;//低电平
	XPT2046_CS=0;//低电平
	for(i=0;i<8;i++){//8位模拟信号的接收
		XPT2046_DIN=Command&(0x80>>i);//右移，获取当前位/&有0即0
		XPT2046_DCLK=1;//高电平
		XPT2046_DCLK=0;//低电平	
	}
	for(i=0;i<16;i++){//转换为数字信号
		XPT2046_DCLK=1;//高电平
		XPT2046_DCLK=0;//低电平
		Delay(1);//忙线1ms
		if(XPT2046_DOUT){ADVAlue|=0x8000>>i;}//右移，赋值当前位/|有1即1
	}
	XPT2046_CS=1;//高电平
	if(Command&0x08){//选择8为输出还是12位输出
		return ADVAlue>>8;
	}else{
		return ADVAlue>>4;
	}
	
}