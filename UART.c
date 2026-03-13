// 在文件开头或新建头文件
#include <STC89C5xRC.H>

// 串口初始化函数（放在main之前）
void UART_Init(void) {
    SCON = 0x50;        // 模式1：8位UART，允许接收
    TMOD &= 0x0F;       // 清除定时器1模式位
    TMOD |= 0x20;       // 定时器1，模式2（8位自动重装）
    TH1 = 0xFD;         // 波特率9600（晶振11.0592MHz）
    TL1 = 0xFD;
    TR1 = 1;            // 启动定时器1
    ES = 1;             // 允许串口中断（如果不使用中断可暂不使能）
    EA = 1;             // 开总中断（如果不使用中断可暂不使能）
}

// 发送单个字符
void UART_SendByte(unsigned char byte) {
    SBUF = byte;
    while (TI == 0);    // 等待发送完成
    TI = 0;             // 清除发送标志
}

// 发送字符串（以'\0'结尾）
void UART_SendString(unsigned char *str) {
    while (*str != '\0') {
        UART_SendByte(*str++);
    }
}