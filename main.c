#include <STC89C5xRC.H>
#include "LCD1602.h"
#include "Delay.h"
#include "XPT2046.h"
#include "UART.h"
#include "OneWire.h"
#include "DS18B20.h"
#include <stdio.h>     // 用于 sprintf

// 全局温度变量
float T;

void main()
{
    unsigned int adj_value, ntc_value, light_value;     // 三路ADC值
    unsigned char xdata send_buf[80] = {0};              // 串口发送缓冲区
    char *status;

    // ===================== 系统初始化 =====================
    DS18B20_ConvertT();     // 上电先转换一次温度，防止第一次读取错误
    Delay(1000);            // 延时1秒

    UART_Init();            // 初始化串口
    LCD_Init();             // 初始化LCD1602

    LCD_ShowString(1, 1, "ADJ NTC RG");   // 第一行显示固定标题

    while (1)
    {
        // ===================== 1. DS18B20温度读取 =====================
        DS18B20_ConvertT();     // 启动温度转换
        T = DS18B20_ReadT();    // 读取温度

        // LCD显示温度（可选）
        /*
        LCD_ShowNum(1, 13, (int)T, 2);           // 整数部分
        LCD_ShowString(1, 15, ".");              // 小数点
        LCD_ShowNum(1, 16, (int)(T * 10) % 10,1);// 小数部分
        */

        // ===================== 2. 三路ADC读取 =====================

        // 可调电阻（电位器）
        adj_value = XPT2046_ReadAD(XPT2046_XP_8);
        LCD_ShowNum(2, 1, adj_value, 4);

        // 热敏电阻
        ntc_value = XPT2046_ReadAD(XPT2046_YP_8);
        LCD_ShowNum(2, 6, ntc_value, 4);

        // 光敏电阻
        light_value = XPT2046_ReadAD(XPT2046_VBAT_8);
        LCD_ShowNum(2, 11, light_value, 4);

        // ===================== 3. 亮暗状态判断 =====================
        if (light_value > 30)
        {
            status = "Light";
        }
        else
        {
            status = "Dark";
        }

        // ===================== 4. 格式化串口发送数据 =====================
        // 格式：
        // ADJ:xxx|NTC:xxx|LIGHT:xxx|STATUS:xxx|TEMP:xx.x
        sprintf(
            send_buf,
            "ADJ:%d|NTC:%d|LIGHT:%d|STATUS:%s|TEMP:%.1f\r\n",
            adj_value,
            ntc_value,
            light_value,
            status,
            T
        );

        // ===================== 5. 串口发送 =====================
        UART_SendString(send_buf);

        // ===================== 6. 延时 =====================
        Delay(100);
    }
}