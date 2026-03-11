# BiShe-YingJian

本科毕业设计硬件部分代码仓库。

本项目为毕业设计 **《基于 Python 的 LCD1602 显示数据的 WEB 实时同步监控系统》** 的硬件实现部分，主要负责设备数据采集与 LCD1602 显示模块控制。

---

## 项目简介

本仓库主要包含毕业设计系统中的硬件相关程序和接口代码，实现设备数据的采集、处理以及在 LCD1602 显示屏上的实时显示。

系统整体架构如下：

设备数据 → Python程序 → LCD1602显示  
　　　　　　　　　　 ↓  
　　　　　　　 Flask Web API  
　　　　　　　　　　 ↓  
　　　　　　　 Web页面实时监控

---

## 功能说明

当前仓库主要实现以下功能：

- LCD1602 显示模块驱动
- 设备数据采集
- Python 控制硬件接口
- 数据实时显示

---

## 技术栈

- Python
- LCD1602
- GPIO接口
- Flask（Web接口）

---

## 项目结构


BiShe-YingJian
│
├── lcd.py # LCD1602 控制程序
├── data.py # 数据采集模块
├── main.py # 主程序
└── README.md # 项目说明


---

## 运行环境

- Python 3.8+
- Raspberry Pi / Linux
- LCD1602 显示模块

---

## 使用方法

1. 克隆项目


git clone https://github.com/shuangye231/BiShe-YingJian.git


2. 进入项目目录


cd BiShe-YingJian


3. 运行程序


python main.py


---

## 项目说明

本项目仅作为本科毕业设计学习项目使用。
