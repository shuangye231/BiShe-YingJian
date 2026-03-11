#include <STC89C5xRC.H>
#include "LCD1602.h"
#include "Delay.h"
#include "XPT2046.h"
#include "UART.h"
#include <stdio.h>      // 用于 sprintf

unsigned int ADValue;   // ADC转换数字信号

// 删掉重复的声明（已在UART.h中声明）
// void UART_Init(void);   
// void UART_SendString(unsigned char *str);  

void main(){
    unsigned int adj_value, ntc_value, light_value; // 分别存储三路值
    unsigned char send_buf[64] = {0};               // 增大缓冲区，初始化
    char *status;
    
    UART_Init();        // 初始化串口
    LCD_Init();         // 初始化LCD1602
    LCD_ShowString(1, 1, "ADJ  NTC  RG"); // 显示固定字符串
    
    while(1){
        // 1. 读取可调电阻（电位器）
        adj_value = XPT2046_ReadAD(XPT2046_XP_8);
        LCD_ShowNum(2, 1, adj_value, 4);
        
        // 2. 读取热敏电阻
        ntc_value = XPT2046_ReadAD(XPT2046_YP_8);
        LCD_ShowNum(2, 6, ntc_value, 4);
        
        // 3. 读取光敏电阻
        light_value = XPT2046_ReadAD(XPT2046_VBAT_8);
        LCD_ShowNum(2, 11, light_value, 4);
        
        // 4. 根据光照值判断状态
        if (light_value > 800) 
            status = "Bright";
        else if (light_value > 300) 
            status = "Normal";
        else 
            status = "Dark";
        
        // 5. 格式化发送字符串（新增ADJ/NTC）
        sprintf(send_buf, "ADJ:%d|NTC:%d|LIGHT:%d|STATUS:%s\r\n", 
                adj_value, ntc_value, light_value, status);
        
        // 6. 通过串口发送
        UART_SendString(send_buf);
        
        // 7. 延时
        Delay(100);      
    }
}