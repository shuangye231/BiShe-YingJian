#ifndef __LCD1602_H__
#define __LCD1602_H__

//用户调用函数：
void LCD_Init();//初始化
void LCD_ShowChar(unsigned char Line,unsigned char Column,char Char);//显示单个字符
void LCD_ShowString(unsigned char Line,unsigned char Column,char *String);//显示字符串
void LCD_ShowNum(unsigned char Line,unsigned char Column,unsigned int Number,unsigned char Length);//显示数字
void LCD_ShowSignedNum(unsigned char Line,unsigned char Column,int Number,unsigned char Length);//显示带符号数字
void LCD_ShowHexNum(unsigned char Line,unsigned char Column,unsigned int Number,unsigned char Length);//显示十进制数字
void LCD_ShowBinNum(unsigned char Line,unsigned char Column,unsigned int Number,unsigned char Length);//显示二进制数字

#endif
