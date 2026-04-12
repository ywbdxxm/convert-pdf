## ESP32-S3 Series

## Datasheet Version 2.2

Xtensa ® 32-bit LX7 dual-core microprocessor 2.4 GHz Wi-Fi (IEEE 802.11b/g/n) and Bluetooth ® 5 (LE) Optional 1.8 V or 3.3 V flash and PSRAM in the chip's package 45 GPIOs QFN56 (7×7 mm) Package

## Including:

ESP32-S3

ESP32-S3FN8

ESP32-S3RH2

ESP32-S3R8

ESP32-S3R16V

ESP32-S3FH4R2

ESP32-S3R8V - End of life (EOL)

ESP32-S3R2 - End of life (EOL), upgraded to ESP32-S3RH2

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000000_ae4894605ee0b6eb4af8aa7897781e701626a0d502aa77bf15d047caaf1ddf53.png)

<!-- page_break -->

## Product Overview

ESP32-S3 is a low-power MCU-based system on a chip (SoC) with integrated 2.4 GHz Wi-Fi and Bluetooth ® Low Energy (Bluetooth LE). It consists of high-performance dual-core microprocessor (Xtensa ® 32-bit LX7), a ULP coprocessor, a Wi-Fi baseband, a Bluetooth LE baseband, RF module, and numerous peripherals.

The functional block diagram of the SoC is shown below.

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000001_d9397166f69b26d859c19084ea624335518f3b16ac2a8603a78eaa398d7d6991.png)

## Power consumption

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000002_23f0ffa8da83b73f93b12971666ce7ce15f55095fe1a6fe937f6d1945c4abbe0.png)

Normal

Low power consumption components capable of working in Deep-sleep mode

## ESP32-S3 Functional Block Diagram

For more information on power consumption, see Section 4.1.3.5 Power Management Unit (PMU) .

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000003_e5296b71f7dc392ebaa6cb23eda2769663f959fda10ad746f340d7ae8ddea7c3.png)

<!-- page_break -->

## Features

## Wi-Fi

- Complies with IEEE 802.11b/g/n
- Supports 20 MHz and 40 MHz bandwidth in 2.4 GHz band
- 1T1R mode with data rate up to 150 Mbps
- Wi-Fi Multimedia (WMM)
- TX/RX A-MPDU, TX/RX A-MSDU
- Immediate Block ACK
- Fragmentation and defragmentation
- Automatic Beacon monitoring (hardware TSF)
- Four virtual Wi-Fi interfaces
- Simultaneous support for Infrastructure BSS in Station, SoftAP, or Station + SoftAP modes Note that when ESP32-S3 scans in Station mode, the SoftAP channel will change along with the Station channel
- Antenna diversity
- 802.11mc FTM

## Bluetooth ®

- Bluetooth LE: Bluetooth 5, Bluetooth Mesh
- High-power mode with up to 20 dBm transmission power
- Speed: 125 Kbps, 500 Kbps, 1 Mbps, 2 Mbps
- LE Advertising Extensions
- Multiple Advertising Sets
- LE Channel Selection Algorithm #2
- Internal co-existence mechanism between Wi-Fi and Bluetooth to share the same antenna

## CPU and Memory

- Xtensa ® dual-core 32-bit LX7 microprocessor
- Clock speed: up to 240 MHz
- CoreMark ® score:
- -Two cores at 240 MHz: 1329.92 CoreMark; 5.54 CoreMark/MHz
- Five-stage pipeline
- 128-bit data bus and dedicated SIMD instructions
- Single precision floating point unit (FPU)

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000004_d710551aadcaecb7826aec84d639c16cc7b9d06a8c71cbdcbfc58f7ee63a299a.png)

<!-- page_break -->

- Ultra-Low-Power (ULP) coprocessors:
- -ULP-RISC-V coprocessor
- -ULP-FSM coprocessor
- General DMA controller, with 5 transmit channels and 5 receive channels
- L1 cache
- ROM: 384 KB
- SRAM: 512 KB
- SRAM in RTC: 16 KB
- 4096-bit eFuse memory, up to 1792 bits for users
- Supported SPI protocols: SPI, Dual SPI, Quad SPI, Octal SPI, QPI and OPI interfaces that allow connection to flash, external RAM, and other SPI devices
- Flash controller with cache is supported
- Flash in-Circuit Programming (ICP) is supported

## Peripherals

- 45 programmable GPIOs
- -4 strapping GPIOs
- -GPIOs allocated for in-package memory:
* 6 GPIOs for either in-package flash or PSRAM
* 7 GPIOs when both in-package flash and PSRAM are integrated
- Connectivity interfaces:
- -Three UART interfaces
- -Two I2C interfaces
- -Two I2S interfaces
- -LCD interface
- -8-bit ~ 16-bit DVP camera interface
- -Two SPI ports for communication with flash and RAM
- -Two general-purpose SPI ports
- -TWAI ® controller, compatible with ISO 11898-1 (CAN Specification 2.0)
- -Full-speed USB OTG
- -USB Serial/JTAG controller
- -SD/MMC host controller with 2 slots
- -LED PWM controller, up to 8 channels
- -Two Motor Control PWM (MCPWM)

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000005_b2b78cf900e1c122f0e4f707c550aa00e432fd05aa7192e9585efcce3706d2b6.png)

<!-- page_break -->

- -RMT (TX/RX)
- -Pulse count controller
- Analog signal processing:
- -Two 12-bit SAR ADCs, up to 20 channels
- -Temperature sensor
- -14 capacitive touch sensing IOs
- Timers:
- -Four 54-bit general-purpose timers
- -52-bit system timer
- -Three watchdog timers

## Power Management

- Fine-resolution power control, including clock frequency, duty cycle, Wi-Fi operating modes, and individual internal component control
- Four power modes designed for typical scenarios: Active, Modem-sleep, Light-sleep, Deep-sleep
- Power consumption in Deep-sleep mode is 7 µ A
- RTC memory remains powered on in Deep-sleep mode

## Security

- Secure boot - permission control on accessing internal and external memory
- Flash encryption - memory encryption and decryption
- Cryptographic hardware acceleration:
- -SHA Accelerator (FIPS PUB 180-4)
- -AES Accelerator (FIPS PUB 197)
- -RSA Accelerator
- -HMAC Accelerator
- -RSA Digital Signature Peripheral (RSA\_DS)
- -Random Number Generator (RNG)

## RF Module

- Antenna switches, RF balun, power amplifier, low-noise receive amplifier
- Up to +21 dBm of power for an 802.11b transmission
- Up to +19.5 dBm of power for an 802.11n transmission
- Up to -104.5 dBm of sensitivity for Bluetooth LE receiver (125 Kbps)

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000006_e631131e595d0a497086e6164677930681fc2da2b682ef9462f09be647326bfc.png)

<!-- page_break -->

## Applications

With low power consumption, ESP32-S3 is an ideal choice for IoT devices in the following areas:

- Smart Home
- Industrial Automation
- Health Care
- Consumer Electronics
- Smart Agriculture
- POS Machines
- Service Robot
- Audio Devices
- Generic Low-power IoT Sensor Hubs
- Generic Low-power IoT Data Loggers
- Cameras for Video Streaming
- USB Devices
- Speech Recognition
- Image Recognition
- Wi-Fi + Bluetooth Networking Card
- Touch and Proximity Sensing

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000007_0d747648374711b5880890710096db781785b8be201a318df55f4274cf01c0a8.png)

<!-- page_break -->

## Note:

Check the link or the QR code to make sure that you use the latest version of this document:

[https://www.espressif.com/documentation/esp32-s3\_datasheet\_en.pdf](https://www.espressif.com/documentation/esp32-s3_datasheet_en.pdf)

## Contents

| Product Overview   | Product Overview                         | Product Overview                         |   2 |
|--------------------|------------------------------------------|------------------------------------------|-----|
| Features           | Features                                 | Features                                 |   3 |
| Applications       | Applications                             | Applications                             |   6 |
| 1                  | ESP32-S3 Series Comparison               | ESP32-S3 Series Comparison               |  13 |
| 1.1                | Nomenclature                             | Nomenclature                             |  13 |
| 1.2                | Comparison                               | Comparison                               |  13 |
| 1.3                | Chip Revision                            | Chip Revision                            |  14 |
| 2                  | Pins                                     | Pins                                     |  15 |
| 2.1                | Pin Layout                               | Pin Layout                               |  15 |
| 2.2                | Pin Overview                             | Pin Overview                             |  16 |
| 2.3                | IO Pins                                  | IO Pins                                  |  20 |
|                    | 2.3.1 IO MUX Functions                   | 2.3.1 IO MUX Functions                   |  20 |
|                    | 2.3.2                                    | RTC Functions                            |  23 |
|                    | 2.3.3                                    | Analog Functions                         |  24 |
|                    | 2.3.4                                    | Restrictions for GPIOs and RTC_GPIOs     |  25 |
|                    | 2.3.5                                    | Peripheral Pin Assignment                |  26 |
| 2.4                | Analog                                   | Pins                                     |  28 |
| 2.5                | Power Supply                             | Power Supply                             |  29 |
|                    | 2.5.1 Power Pins                         | 2.5.1 Power Pins                         |  29 |
|                    | 2.5.2                                    | Power Scheme                             |  29 |
|                    | 2.5.3                                    | Chip Power-up and Reset                  |  30 |
| 2.6                | Pin Mapping Between Chip and Flash/PSRAM | Pin Mapping Between Chip and Flash/PSRAM |  31 |
| 3                  | Boot Configurations                      | Boot Configurations                      |  32 |
| 3.1                | Chip Boot Mode Control                   | Chip Boot Mode Control                   |  33 |
| 3.2                | VDD_SPI Voltage Control                  | VDD_SPI Voltage Control                  |  34 |
| 3.3                | ROM Messages Printing Control            | ROM Messages Printing Control            |  34 |
| 3.4                | JTAG Signal Source Control               | JTAG Signal Source Control               |  34 |
| 4                  | Functional Description                   | Functional Description                   |  36 |
| 4.1                | System                                   | System                                   |  36 |
|                    | 4.1.1 Microprocessor and Master          | 4.1.1 Microprocessor and Master          |  36 |
|                    | 4.1.1.1 CPU                              | 4.1.1.1 CPU                              |  36 |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000008_8649f8f33a256fa42b63212e4e111bdb54b97a0f67e01aab351dc824c17d6c0b.png)

<!-- page_break -->

4.2

|       | 4.1.1.3                             | Ultra-Low-Power Coprocessor (ULP)         | 37    |
|-------|-------------------------------------|-------------------------------------------|-------|
|       | 4.1.1.4                             | GDMA Controller (GDMA)                    | 37    |
| 4.1.2 | Memory Organization                 | Memory Organization                       | 38    |
|       | 4.1.2.1                             | Internal Memory                           | 38    |
|       | 4.1.2.2                             | External Flash and RAM                    | 39    |
|       | 4.1.2.3                             | Cache                                     | 39    |
|       | 4.1.2.4                             | eFuse Controller                          | 40    |
| 4.1.3 | System Components                   | System Components                         | 40    |
|       | 4.1.3.1                             | IO MUX and GPIO Matrix                    | 40    |
|       | 4.1.3.2                             | Reset                                     | 41    |
|       | 4.1.3.3                             | Clock                                     | 41    |
|       | 4.1.3.4                             | Interrupt Matrix                          | 42    |
|       | 4.1.3.5                             | Power Management Unit (PMU)               | 42    |
|       | 4.1.3.6                             | System Timer                              | 44    |
|       | 4.1.3.7                             | General Purpose Timers                    | 44    |
|       | 4.1.3.8                             | Watchdog Timers                           | 45    |
|       | 4.1.3.9                             | XTAL32K Watchdog Timers                   | 45    |
|       | 4.1.3.10                            | Permission Control                        | 45    |
|       | 4.1.3.11                            | World Controller                          | 46    |
|       | 4.1.3.12                            | System Registers                          | 47    |
| 4.1.4 | Cryptography and Security Component | Cryptography and Security Component       | 47    |
|       | 4.1.4.1                             | SHA Accelerator                           | 47    |
|       | 4.1.4.2                             | AES Accelerator                           | 48    |
|       | 4.1.4.3                             | RSA Accelerator                           | 48    |
|       | 4.1.4.4                             | Secure Boot                               | 48    |
|       | 4.1.4.5                             | HMAC Accelerator                          | 49    |
|       | 4.1.4.6                             | RSA Digital Signature Peripheral (RSA_DS) | 49    |
|       | 4.1.4.7                             | External Memory Encryption and Decryption | 49    |
|       | 4.1.4.8                             | Clock Glitch Detection                    | 50    |
|       | 4.1.4.9                             | Random Number Generator                   | 50    |
|       | Peripherals                         | Peripherals                               | 51    |
| 4.2.1 | Connectivity Interface              | Connectivity Interface                    | 51    |
|       | 4.2.1.1                             | UART Controller                           | 51    |
|       | 4.2.1.2                             | I2C Interface                             | 51    |
|       | 4.2.1.3                             | I2S Interface                             | 52    |
|       | 4.2.1.4                             | LCD and Camera Controller                 | 52    |
|       | 4.2.1.5                             | Serial Peripheral Interface (SPI)         | 53    |
|       | 4.2.1.6                             | Two-Wire Automotive Interface (TWAI ® )   | 54    |
|       | 4.2.1.7                             | USB 2.0 OTG Full-Speed Interface          | 55    |
|       | 4.2.1.8                             | USB Serial/JTAG Controller                | 56    |
|       | 4.2.1.9                             | SD/MMC Host Controller                    | 56    |
|       | 4.2.1.10                            | Motor Control PWM (MCPWM)                 | 57    |
|       | 4.2.1.11                            | Remote Control Peripheral (RMT)           | 58    |
|       | 4.2.1.12                            | Pulse Count Controller (PCNT)             | 58    |
| 4.2.2 | Analog Signal Processing 4.2.2.1    | SAR ADC                                   | 59 59 |

<!-- page_break -->

|                                     |                                                                 | 4.2.2.2                                                         | Temperature Sensor                                              | 59    |
|-------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------|-------|
|                                     | 4.2.2.3 Touch Sensor                                            | 4.2.2.3 Touch Sensor                                            | 4.2.2.3 Touch Sensor                                            | 59    |
| 4.3                                 | Wireless Communication                                          | Wireless Communication                                          | Wireless Communication                                          | 61    |
|                                     | 4.3.1                                                           | Radio                                                           | Radio                                                           | 61    |
|                                     |                                                                 | 4.3.1.1                                                         | 2.4 GHz Receiver                                                | 61    |
|                                     |                                                                 | 4.3.1.2                                                         | 2.4 GHz Transmitter                                             | 61    |
|                                     |                                                                 | 4.3.1.3                                                         | Clock Generator                                                 | 61    |
|                                     | 4.3.2                                                           | Wi-Fi                                                           | Wi-Fi                                                           | 61    |
|                                     |                                                                 | 4.3.2.1                                                         | Wi-Fi Radio and Baseband                                        | 62    |
|                                     |                                                                 | 4.3.2.2                                                         | Wi-Fi MAC                                                       | 62    |
|                                     |                                                                 | 4.3.2.3                                                         | Networking Features                                             | 62    |
|                                     | 4.3.3                                                           | Bluetooth LE                                                    | Bluetooth LE                                                    | 62    |
|                                     |                                                                 | 4.3.3.1                                                         | Bluetooth LE PHY                                                | 63    |
|                                     |                                                                 | 4.3.3.2                                                         | Bluetooth LE Link Controller                                    | 63    |
| 5                                   | Electrical Characteristics                                      | Electrical Characteristics                                      | Electrical Characteristics                                      | 64    |
| 5.1                                 | Absolute Maximum Ratings                                        | Absolute Maximum Ratings                                        | Absolute Maximum Ratings                                        | 64    |
| 5.2                                 | Recommended Operating Conditions                                | Recommended Operating Conditions                                | Recommended Operating Conditions                                | 64    |
| 5.3                                 | VDD_SPI Output Characteristics                                  | VDD_SPI Output Characteristics                                  | VDD_SPI Output Characteristics                                  | 65    |
| 5.4                                 | DC Characteristics (3.3 V, 25 °C)                               | DC Characteristics (3.3 V, 25 °C)                               | DC Characteristics (3.3 V, 25 °C)                               | 65    |
| 5.5                                 | ADC Characteristics                                             | ADC Characteristics                                             | ADC Characteristics                                             | 66    |
| 5.6                                 | Current Consumption                                             | Current Consumption                                             | Current Consumption                                             | 66    |
|                                     | 5.6.1                                                           | Current Consumption in Active Mode                              | Current Consumption in Active Mode                              | 66    |
|                                     | 5.6.2 Current Consumption in Other Modes                        | 5.6.2 Current Consumption in Other Modes                        | 5.6.2 Current Consumption in Other Modes                        | 67    |
| 5.7                                 | Memory Specifications                                           | Memory Specifications                                           | Memory Specifications                                           | 68    |
| 5.8                                 | Reliability                                                     | Reliability                                                     | Reliability                                                     | 69    |
| 6                                   | RF Characteristics                                              | RF Characteristics                                              | RF Characteristics                                              | 70    |
| 6.1                                 | Wi-Fi Radio                                                     | Wi-Fi Radio                                                     | Wi-Fi Radio                                                     | 70    |
|                                     | 6.1.1                                                           | Wi-Fi RF Transmitter (TX) Characteristics                       | Wi-Fi RF Transmitter (TX) Characteristics                       | 70    |
| 6.2                                 | 6.1.2 Wi-Fi RF Receiver (RX) Characteristics Bluetooth LE Radio | 6.1.2 Wi-Fi RF Receiver (RX) Characteristics Bluetooth LE Radio | 6.1.2 Wi-Fi RF Receiver (RX) Characteristics Bluetooth LE Radio | 71 72 |
|                                     |                                                                 | Bluetooth LE RF Transmitter (TX) Characteristics                | Bluetooth LE RF Transmitter (TX) Characteristics                |       |
|                                     | 6.2.1                                                           |                                                                 |                                                                 | 73    |
|                                     | 6.2.2                                                           | Bluetooth LE RF Receiver (RX) Characteristics                   | Bluetooth LE RF Receiver (RX) Characteristics                   | 74    |
| 7                                   | Packaging                                                       | Packaging                                                       | Packaging                                                       | 77    |
| ESP32-S3 Consolidated Pin Overview  | ESP32-S3 Consolidated Pin Overview                              | ESP32-S3 Consolidated Pin Overview                              | ESP32-S3 Consolidated Pin Overview                              | 79    |
| Datasheet Versioning                | Datasheet Versioning                                            | Datasheet Versioning                                            | Datasheet Versioning                                            | 80    |
| Glossary                            | Glossary                                                        | Glossary                                                        | Glossary                                                        | 81    |
| Related Documentation and Resources | Related Documentation and Resources                             | Related Documentation and Resources                             | Related Documentation and Resources                             | 82    |

<!-- page_break -->

## List of T ables

| 1-1   | ESP32-S3 Series Comparison                                   |   13 |
|-------|--------------------------------------------------------------|------|
| 2-1   | Pin Overview                                                 |   16 |
| 2-2   | Power-Up Glitches on Pins                                    |   18 |
| 2-3   | Peripheral Signals Routed via IO MUX                         |   20 |
| 2-4   | IO MUX Functions                                             |   21 |
| 2-5   | RTC Peripheral Signals Routed via RTC IO MUX                 |   23 |
| 2-6   | RTC Functions                                                |   23 |
| 2-7   | Analog Signals Routed to Analog Functions                    |   24 |
| 2-8   | Analog Functions                                             |   24 |
| 2-9   | Peripheral Pin Assignment                                    |   27 |
| 2-10  | Analog Pins                                                  |   28 |
| 2-11  | Power Pins                                                   |   29 |
| 2-12  | Voltage Regulators                                           |   29 |
| 2-13  | Description of Timing Parameters for Power-up and Reset      |   30 |
| 2-14  | Pin Mapping Between Chip and Flash or PSRAM                  |   31 |
| 3-1   | Default Configuration of Strapping Pins                      |   32 |
| 3-2   | Description of Timing Parameters for the Strapping Pins      |   33 |
| 3-3   | Chip Boot Mode Control                                       |   33 |
| 3-4   | VDD_SPI Voltage Control                                      |   34 |
| 3-5   | JTAG Signal Source Control                                   |   35 |
| 4-1   | Components and Power Domains                                 |   44 |
| 5-1   | Absolute Maximum Ratings                                     |   64 |
| 5-2   | Recommended Operating Conditions                             |   64 |
| 5-3   | VDD_SPI Internal and Output Characteristics                  |   65 |
| 5-4   | DC Characteristics (3.3 V, 25 °C)                            |   65 |
| 5-5   | ADC Characteristics                                          |   66 |
| 5-6   | ADC Calibration Results                                      |   66 |
| 5-7   | Current Consumption for Wi-Fi (2.4 GHz) in Active Mode       |   66 |
| 5-8   | Current Consumption for Bluetooth LE in Active Mode          |   67 |
| 5-9   | Current Consumption in Modem-sleep Mode                      |   67 |
| 5-10  | Current Consumption in Low-Power Modes                       |   68 |
| 5-11  | Flash Specifications                                         |   68 |
| 5-12  | PSRAM Specifications                                         |   69 |
| 5-13  | Reliability Qualifications                                   |   69 |
| 6-1   | Wi-Fi RF Characteristics                                     |   70 |
| 6-2   | TX Power with Spectral Mask and EVM Meeting 802.11 Standards |   70 |
| 6-3   | TX EVM Test 1                                                |   70 |
| 6-4   | RX Sensitivity                                               |   71 |
| 6-5   | Maximum RX Level                                             |   72 |
| 6-6   | RX Adjacent Channel Rejection                                |   72 |
| 6-7   | Bluetooth LE Frequency                                       |   72 |
| 6-8   | Transmitter Characteristics - Bluetooth LE 1 Mbps            |   73 |
| 6-9   | Transmitter Characteristics - Bluetooth LE 2 Mbps            |   73 |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000009_f565b24c6bda9a03ae3c597d32574ac4c7f6f61d5ba9267edfe222cd83698770.png)

<!-- page_break -->

| 6-10   | Transmitter Characteristics - Bluetooth LE 125 Kbps   |   73 |
|--------|-------------------------------------------------------|------|
| 6-11   | Transmitter Characteristics - Bluetooth LE 500 Kbps   |   74 |
| 6-12   | Receiver Characteristics - Bluetooth LE 1 Mbps        |   74 |
| 6-13   | Receiver Characteristics - Bluetooth LE 2 Mbps        |   75 |
| 6-14   | Receiver Characteristics - Bluetooth LE 125 Kbps      |   75 |
| 6-15   | Receiver Characteristics - Bluetooth LE 500 Kbps      |   76 |
| 7-1    | Consolidated Pin Overview                             |   79 |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000010_3475873afd35da4954944b0abc098e40186081c3fb88bc44ed03049d4f7d48e8.png)

<!-- page_break -->

## List of Figures

| 1-1   | ESP32-S3 Series Nomenclature                              |   13 |
|-------|-----------------------------------------------------------|------|
| 2-1   | ESP32-S3 Pin Layout (Top View)                            |   15 |
| 2-2   | ESP32-S3 Power Scheme                                     |   30 |
| 2-3   | Visualization of Timing Parameters for Power-up and Reset |   30 |
| 3-1   | Visualization of Timing Parameters for the Strapping Pins |   33 |
| 4-1   | Address Mapping Structure                                 |   38 |
| 4-2   | Components and Power Domains                              |   43 |
| 7-1   | QFN56 (7×7 mm) Package                                    |   77 |
| 7-2   | QFN56 (7×7 mm) Package (Only for ESP32-S3FH4R2)           |   78 |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000011_936fbe4e0ff26e8191eb82dd0da1e758473414a417547d1efa66725cf3d07c76.png)

<!-- page_break -->

## 1 ESP32-S3 Series Comparison

## 1.1 Nomenclature

Figure 1-1. ESP32-S3 Series Nomenclature

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000012_d7320839e00497c843f3f19cf70e47c8b40b20ee5556713d1dcc85473ea9c899.png)

Table 1-1. ESP32-S3 Series Comparison

| Part Number 1      | In-Package Flash 2   | In-Package PSRAM   | Ambient Temp. 3   | VDD_SPI Voltage 4   | Chip Revision   |
|--------------------|----------------------|--------------------|-------------------|---------------------|-----------------|
| ESP32-S3           | -                    | -                  | - 40 ∼ 105 °C     | 3.3 V/1.8 V         | v0.1/v0.2       |
| ESP32-S3FN8        | 8 MB (Quad SPI) 5    | -                  | - 40 ∼ 85 °C      | 3.3 V               | v0.1/v0.2       |
| ESP32-S3RH2        | -                    | 2 MB (Quad SPI)    | - 40 ∼ 105 °C     | 3.3 V               | v0.2            |
| ESP32-S3R8         | -                    | 8 MB (Octal SPI)   | - 40 ∼ 65 °C      | 3.3 V               | v0.1/v0.2       |
| ESP32-S3R16V       | -                    | 16 MB (Octal SPI)  | - 40 ∼ 65 °C      | 1.8 V               | v0.2            |
| ESP32-S3FH4R2      | 4 MB (Quad SPI)      | 2 MB (Quad SPI)    | - 40 ∼ 85 °C      | 3.3 V               | v0.1/v0.2       |
| ESP32-S3R8V (EOL)  | -                    | 8 MB (Octal SPI)   | - 40 ∼ 65 °C      | 1.8 V               | v0.1/v0.2       |
| ESP32-S3R2 (EOL) 6 | -                    | 2 MB (Quad SPI)    | - 40 ∼ 85 °C      | 3.3 V               | v0.1/v0.2       |

## 1.2 Comparison

<!-- page_break -->

## 1.3 Chip Revision

As shown in T able 1-1 ESP32-S3 Series Comparison , ESP32-S3 now has multiple chip revisions available on the market using the same part number.

For chip revision identification, ESP-IDF release that supports a specific chip revision, and errors fixed in each chip revision, please refer to ESP32-S3 Series SoC Errata .

<!-- page_break -->

## 2 Pins

## 2.1 Pin Layout

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000013_0547ec23b04cbdf01d287bcc19d867651a8d8fb77bc27a424a2036b3536d11f8.png)

Figure 2-1. ESP32-S3 Pin Layout (Top View)

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000014_240f92e65687ec46e1f76f9071d18a7cc90ff71e577977944f089e7449b81acb.png)

<!-- page_break -->

## 2.2 Pin Overview

The ESP32-S3 chip integrates multiple peripherals that require communication with the outside world. To keep the chip package size reasonably small, the number of available pins has to be limited. So the only way to route all the incoming and outgoing signals is through pin multiplexing. Pin muxing is controlled via software programmable registers (see ESP32-S3 Technical Reference Manual &gt; Chapter IO MUX and GPIO Matrix ).

All in all, the ESP32-S3 chip has the following types of pins:

- IO pins with the following predefined sets of functions to choose from:
- Each IO pin has predefined IO MUX functions - see T able 2-4 IO MUX Functions
- Some IO pins have predefined RTC functions - see T able 2-6 RTC Functions
- Some IO pins have predefined analog functions - see T able 2-8 Analog Functions

Predefined functions means that each IO pin has a set of direct connections to certain on-chip peripherals. During run-time, the user can configure which peripheral from a predefined set to connect to a certain pin at a certain time via memory mapped registers (see ESP32-S3 Technical Reference Manual &gt; Chapter IO MUX and GPIO pins ).

- Analog pins that have exclusively-dedicated analog functions - see T able 2-10 Analog Pins
- Power pins that supply power to the chip components and non-power pins - see T able 2-11 Power Pins

Table 2-1 Pin Overview gives an overview of all the pins. For more information, see the respective sections for each pin type below, or ESP32-S3 Consolidated Pin Overview .

Table 2-1. Pin Overview

|         |          |          | 2-5                 | Pin Settings 6   | Pin Settings 6   | Pin Function Sets 1   | Pin Function Sets 1   | Pin Function Sets 1   |
|---------|----------|----------|---------------------|------------------|------------------|-----------------------|-----------------------|-----------------------|
| Pin No. | Pin Name | Pin Type | Pin Providing Power | At Reset         | After Reset      | IO MUX                | RTC IO MUX            | Analog                |
| 1       | LNA_IN   | Analog   |                     |                  |                  |                       |                       |                       |
| 2       | VDD3P3   | Power    |                     |                  |                  |                       |                       |                       |
| 3       | VDD3P3   | Power    |                     |                  |                  |                       |                       |                       |
| 4       | CHIP_PU  | Analog   | VDD3P3_RTC          |                  |                  |                       |                       |                       |
| 5       | GPIO0    | IO       | VDD3P3_RTC          | WPU, IE          | WPU, IE          | IO MUX                | RTC IO MUX            |                       |
| 6       | GPIO1    | IO       | VDD3P3_RTC          | IE               | IE               | IO MUX                | RTC IO MUX            | Analog                |
| 7       | GPIO2    | IO       | VDD3P3_RTC          | IE               | IE               | IO MUX                | RTC IO MUX            | Analog                |
| 8       | GPIO3    | IO       | VDD3P3_RTC          | IE               | IE               | IO MUX                | RTC IO MUX            | Analog                |
| 9       | GPIO4    | IO       | VDD3P3_RTC          |                  |                  | IO MUX                | RTC IO MUX            | Analog                |
| 10      | GPIO5    | IO       | VDD3P3_RTC          |                  |                  | IO MUX                | RTC IO MUX            | Analog                |
| 11      | GPIO6    | IO       | VDD3P3_RTC          |                  |                  | IO MUX                | RTC IO MUX            | Analog                |
| 12      | GPIO7    | IO       | VDD3P3_RTC          |                  |                  | IO MUX                | RTC IO MUX            | Analog                |
| 13      | GPIO8    | IO       | VDD3P3_RTC          |                  |                  | IO MUX                | RTC IO MUX            | Analog                |
| 14      | GPIO9    | IO       | VDD3P3_RTC          |                  | IE               | IO MUX                | RTC IO MUX            | Analog                |
| 15      | GPIO10   | IO       | VDD3P3_RTC          |                  | IE               | IO MUX                | RTC IO MUX            | Analog                |
| 16      | GPIO11   | IO       | VDD3P3_RTC          |                  | IE               | IO MUX                | RTC IO MUX            | Analog                |
| 17      | GPIO12   | IO       | VDD3P3_RTC          |                  | IE               | IO MUX                | RTC IO MUX            | Analog                |
| 18      | GPIO13   | IO       | VDD3P3_RTC          |                  | IE               | IO MUX                | RTC IO MUX            | Analog                |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000015_7161135bfd243b11df360e6cc2f1276a7ea418cf384f6a48505403d71469c746.png)

<!-- page_break -->

## Cont'd from previous page

|         |            |          |                         | Pin Settings 6   | Pin Settings 6   | Pin Function Sets 1   | Pin Function Sets 1   | Pin Function Sets 1   |
|---------|------------|----------|-------------------------|------------------|------------------|-----------------------|-----------------------|-----------------------|
| Pin No. | Pin Name   | Pin Type | Pin Providing Power 2-5 | At Reset         | After Reset      | IO MUX                | RTC IO MUX            | Analog                |
| 19      | GPIO14     | IO       | VDD3P3_RTC              |                  | IE               | IO MUX                | RTC IO MUX            | Analog                |
| 20      | VDD3P3_RTC | Power    |                         |                  |                  |                       |                       |                       |
| 21      | XTAL_32K_P | IO       | VDD3P3_RTC              |                  |                  | IO MUX                | RTC IO MUX            | Analog                |
| 22      | XTAL_32K_N | IO       | VDD3P3_RTC              |                  |                  | IO MUX                | RTC IO MUX            | Analog                |
| 23      | GPIO17     | IO       | VDD3P3_RTC              |                  | IE               | IO MUX                | RTC IO MUX            | Analog                |
| 24      | GPIO18     | IO       | VDD3P3_RTC              |                  | IE               | IO MUX                | RTC IO MUX            | Analog                |
| 25      | GPIO19     | IO       | VDD3P3_RTC              |                  |                  | IO MUX                | RTC IO MUX            | Analog                |
| 26      | GPIO20     | IO       | VDD3P3_RTC              | USB_PU           | USB_PU           | IO MUX                | RTC IO MUX            | Analog                |
| 27      | GPIO21     | IO       | VDD3P3_RTC              |                  |                  | IO MUX                | RTC IO MUX            |                       |
| 28      | SPICS1     | IO       | VDD_SPI                 | WPU, IE          | WPU, IE          | IO MUX                |                       |                       |
| 29      | VDD_SPI    | Power    |                         |                  |                  |                       |                       |                       |
| 30      | SPIHD      | IO       | VDD_SPI                 | WPU, IE          | WPU, IE          | IO MUX                |                       |                       |
| 31      | SPIWP      | IO       | VDD_SPI                 | WPU, IE          | WPU, IE          | IO MUX                |                       |                       |
| 32      | SPICS0     | IO       | VDD_SPI                 | WPU, IE          | WPU, IE          | IO MUX                |                       |                       |
| 33      | SPICLK     | IO       | VDD_SPI                 | WPU, IE          | WPU, IE          | IO MUX                |                       |                       |
| 34      | SPIQ       | IO       | VDD_SPI                 | WPU, IE          | WPU, IE          | IO MUX                |                       |                       |
| 35      | SPID       | IO       | VDD_SPI                 | WPU, IE          | WPU, IE          | IO MUX                |                       |                       |
| 36      | SPICLK_N   | IO       | VDD_SPI/VDD3P3_CPU      | IE               | IE               | IO MUX                |                       |                       |
| 37      | SPICLK_P   | IO       | VDD_SPI/VDD3P3_CPU      | IE               | IE               | IO MUX                |                       |                       |
| 38      | GPIO33     | IO       | VDD_SPI/VDD3P3_CPU      |                  | IE               | IO MUX                |                       |                       |
| 39      | GPIO34     | IO       | VDD_SPI/VDD3P3_CPU      |                  | IE               | IO MUX                |                       |                       |
| 40      | GPIO35     | IO       | VDD_SPI/VDD3P3_CPU      |                  | IE               | IO MUX                |                       |                       |
| 41      | GPIO36     | IO       | VDD_SPI/VDD3P3_CPU      |                  | IE               | IO MUX                |                       |                       |
| 42      | GPIO37     | IO       | VDD_SPI/VDD3P3_CPU      |                  | IE               | IO MUX                |                       |                       |
| 43      | GPIO38     | IO       | VDD3P3_CPU              |                  | IE               | IO MUX                |                       |                       |
| 44      | MTCK       | IO       | VDD3P3_CPU              |                  | IE 7             | IO MUX                |                       |                       |
| 45      | MTDO       | IO       | VDD3P3_CPU              |                  | IE               | IO MUX                |                       |                       |
| 46      | VDD3P3_CPU | Power    |                         |                  |                  |                       |                       |                       |
| 47      | MTDI       | IO       | VDD3P3_CPU              |                  | IE               | IO MUX                |                       |                       |
| 48      | MTMS       | IO       | VDD3P3_CPU              |                  | IE               | IO MUX                |                       |                       |
| 49      | U0TXD      | IO       | VDD3P3_CPU              | WPU, IE          | WPU, IE          | IO MUX                |                       |                       |
| 50      | U0RXD      | IO       | VDD3P3_CPU              | WPU, IE          | WPU, IE          | IO MUX                |                       |                       |
| 51      | GPIO45     | IO       | VDD3P3_CPU              | WPD, IE          | WPD, IE          | IO MUX                |                       |                       |
| 52      | GPIO46     | IO       | VDD3P3_CPU              | WPD, IE          | WPD, IE          | IO MUX                |                       |                       |
| 53      | XTAL_N     | Analog   |                         |                  |                  |                       |                       |                       |
| 54      | XTAL_P     | Analog   |                         |                  |                  |                       |                       |                       |
| 55      | VDDA       | Power    |                         |                  |                  |                       |                       |                       |
| 56      | VDDA       | Power    |                         |                  |                  |                       |                       |                       |
| 57      | GND        | Power    |                         |                  |                  |                       |                       |                       |

1. Bold marks the pin function set in which a pin has its default function in the default boot mode. For more information about the boot mode ， see Section 3.1 Chip Boot Mode Control .
2. In column Pin Providing Power , regarding pins powered by VDD\_SPI:
- Power actually comes from the internal power rail supplying power to VDD\_SPI. For details, see Section 2.5.2 Power Scheme .
3. In column Pin Providing Power , regarding pins powered by VDD3P3\_CPU / VDD\_SPI:

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000016_e767b2ef1a3868f08a8f05f4a7fb2b2e54e91b5952ec7be3661e5fd07c792a1e.png)

<!-- page_break -->

- Pin Providing Power (either VDD3P3\_CPU or VDD\_SPI) is decided by eFuse bit EFUSE\_PIN\_POWER\_SELECTION (see ESP32-S3 Technical Reference Manual &gt; Chapter eFuse Controller ) and can be configured via the IO\_MUX\_PAD\_POWER\_CTRL bit (see ESP32-S3 Technical Reference Manual &gt; Chapter IO MUX and GPIO pins ).
4. For ESP32-S3R8V and ESP32-S3R16V chip, as the VDD\_SPI voltage has been set to 1.8 V, the working voltage for pins SPICLK\_N and SPICLK\_P (GPIO47 and GPIO48) would also be 1.8 V, which is different from other GPIOs.
5. The default drive strengths for each pin are as follows:
- GPIO17 and GPIO18: 10 mA
- GPIO19 and GPIO20: 40 mA
- All other pins: 20 mA
6. Column Pin Settings shows predefined settings at reset and after reset with the following abbreviations:
- IE - input enabled
- WPU - internal weak pull-up resistor enabled
- WPD - internal weak pull-down resistor enabled
- USB\_PU - USB pull-up resistor enabled
- -By default, the USB function is enabled for USB pins (i.e., GPIO19 and GPIO20), and the pin pull-up is decided by the USB pull-up. The USB pull-up is controlled by USB\_SERIAL\_JTAG\_DP/DM\_PULLUP and the pull-up resistor value is controlled by USB\_SERIAL\_JTAG\_PULLUP\_VALUE. For details, see ESP32-S3 Technical Reference Manual &gt; Chapter USB Serial/JTAG Controller ).
- -When the USB function is disabled, USB pins are used as regular GPIOs and the pin's internal weak pull-up and pull-down resistors are disabled by default (configurable by IO\_MUX\_FUN\_ WPU/WPD). For details, see ESP32-S3 Technical Reference Manual &gt; Chapter IO MUX and GPIO Matrix .
- 7 . Depends on the value of EFUSE\_DIS\_PAD\_JTAG
- 0 - WPU is enabled
- 1 - pin floating

Some pins have glitches during power-up. See details in T able 2-2.

Table 2-2. Power-Up Glitches on Pins

| Pin        | Glitch 1         |   Typical Time Period ( µ s) |
|------------|------------------|------------------------------|
| GPIO1      | Low-level glitch |                           60 |
| GPIO2      | Low-level glitch |                           60 |
| GPIO3      | Low-level glitch |                           60 |
| GPIO4      | Low-level glitch |                           60 |
| GPIO5      | Low-level glitch |                           60 |
| GPIO6      | Low-level glitch |                           60 |
| GPIO7      | Low-level glitch |                           60 |
| GPIO8      | Low-level glitch |                           60 |
| GPIO9      | Low-level glitch |                           60 |
| GPIO10     | Low-level glitch |                           60 |
| GPIO11     | Low-level glitch |                           60 |
| GPIO12     | Low-level glitch |                           60 |
| GPIO13     | Low-level glitch |                           60 |
| GPIO14     | Low-level glitch |                           60 |
| XTAL_32K_P | Low-level glitch |                           60 |
| XTAL_32K_N | Low-level glitch |                           60 |
| GPIO17     | Low-level glitch |                           60 |

Cont'd on next page

<!-- page_break -->

Table 2-2 - cont'd from previous page

| Pin    | Glitch 1            |   Typical Time Period ( µ s) |
|--------|---------------------|------------------------------|
| GPIO18 | Low-level glitch    |                           60 |
| GPIO18 | High-level glitch   |                           60 |
| GPIO19 | Low-level glitch    |                           60 |
| GPIO19 | High-level glitch 2 |                           60 |
| GPIO20 | Pull-down glitch    |                           60 |
| GPIO20 | High-level glitch 2 |                           60 |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000017_0f08b1250bb4c89856b7d173082b4d04fcb445ce149bef381fb90f8390291388.png)

<!-- page_break -->

## 2.3 IO Pins

## 2.3.1 IO MUX Functions

The IO MUX allows multiple input/output signals to be connected to a single input/output pin. Each IO pin of ESP32-S3 can be connected to one of the five signals (IO MUX functions, i.e., F0-F4), as listed in T able 2-4 IO MUX Functions .

Among the five sets of signals:

- Some are routed via the GPIO Matrix ( GPIO0, GPIO1, etc. ), which incorporates internal signal routing circuitry for mapping signals programmatically. It gives the pin access to almost any peripheral signals. However, the flexibility of programmatic mapping comes at a cost as it might affect the latency of routed signals. For details about connecting to peripheral signals via GPIO Matrix, see ESP32-S3 Technical Reference Manual &gt; Chapter IO MUX and GPIO Matrix .
- Some are directly routed from certain peripherals ( U0TXD, MTCK, etc. ), including UART0/1, JTAG, SPI0/1, and SPI2 - see T able 2-3 Peripheral Signals Routed via IO MUX .

Table 2-3. Peripheral Signals Routed via IO MUX

| Pin Function                                          | Signal                                                                         | Description                                                                                                                                                                                                        |
|-------------------------------------------------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| U…TXD U…RXD U…RTS U…CTS                               | Transmit data Receive data Request to send Clear to send                       | UART0/1 interface                                                                                                                                                                                                  |
| MTCK MTDO MTDI MTMS                                   | Test clock Test Data Out Test Data In Test Mode Select                         | JTAG interface for debugging                                                                                                                                                                                       |
| SPIQ SPID SPIHD SPIWP SPICLK SPICS…                   | Master in, slave out Master out, slave in Hold Write protect Clock Chip select | SPI0/1 interface (powered by VDD_SPI) for connection to in-package or off-package flash/PSRAM via the SPI bus. It supports 1-, 2-, 4-line SPI modes. See also Section 2.6 Pin Mapping Between Chip and Flash/PSRAM |
| SPIIO… SPIDQS                                         | Data Data strobe/data mask                                                     | SPI0/1 interface (powered by VDD_SPI or VDD3P3_CPU) for the higher 4 bits data line interface and DQS interface in 8-line SPI mode                                                                                 |
| SPICLK_N_DIFF SPICLK_P_DIFF                           | Negative clock signal Positive clock signal                                    | Differential clock negative/positive for the SPI bus                                                                                                                                                               |
| SUBSPIQ SUBSPID SUBSPIHD SUBSPIWP SUBSPICLK SUBSPICS… | Master in, slave out Master out, slave in Hold Write protect Clock Chip select | SPI0/1 interface (powered by VDD3P3_RTC or VDD3V3_CPU) for connection to in-package or off-package flash/PSRAM via the SUBSPI bus. It supports 1-, 2-, 4-line SPI modes                                            |
| SUBSPICLK_N_DIFF SUBSPICLK_P_DIFF                     | Negative clock signal Positive clock signal                                    | Differential clock negative/positive for the SUBSPI bus                                                                                                                                                            |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000018_26aed88bf717ffb02dd8fc6e6d84df2ded51468b86e2a1220ba6e28cbba73fb9.png)

<!-- page_break -->

Table 2-3 - cont'd from previous page

| Pin Function                              | Signal                                                                         | Description                                                                                   |
|-------------------------------------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| FSPIQ FSPID FSPIHD FSPIWP FSPICLK FSPICS0 | Master in, slave out Master out, slave in Hold Write protect Clock Chip select | SPI2 interface for fast SPI connection. It supports 1-, 2-, 4-line SPI modes                  |
| FSPIIO…                                   | Data Data strobe/data mask                                                     | The higher 4 bits data line interface and DQS interface for SPI2 interface in 8-line SPI mode |
| FSPIDQS                                   |                                                                                | Output clock signals generated by the chip's internal components                              |
| CLK_OUT…                                  | Clock output                                                                   |                                                                                               |

Table 2-4 IO MUX Functions shows the IO MUX functions of IO pins.

Table 2-4. IO MUX Functions

|     |        | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   |
|-----|--------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|
| Pin | GPIO 2 | F0                        | Type 3                    | F1                        | Type                      | F2                        | Type                      | F3                        | Type                      | F4                        | Type                      |
| 5   | GPIO0  | GPIO0                     | I/O/T                     | GPIO0                     | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 6   | GPIO1  | GPIO1                     | I/O/T                     | GPIO1                     | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 7   | GPIO2  | GPIO2                     | I/O/T                     | GPIO2                     | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 8   | GPIO3  | GPIO3                     | I/O/T                     | GPIO3                     | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 9   | GPIO4  | GPIO4                     | I/O/T                     | GPIO4                     | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 10  | GPIO5  | GPIO5                     | I/O/T                     | GPIO5                     | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 11  | GPIO6  | GPIO6                     | I/O/T                     | GPIO6                     | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 12  | GPIO7  | GPIO7                     | I/O/T                     | GPIO7                     | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 13  | GPIO8  | GPIO8                     | I/O/T                     | GPIO8                     | I/O/T                     |                           |                           | SUBSPICS1                 | O/T                       |                           |                           |
| 14  | GPIO9  | GPIO9                     | I/O/T                     | GPIO9                     | I/O/T                     |                           |                           | SUBSPIHD                  | I1/O/T                    | FSPIHD                    | I1/O/T                    |
| 15  | GPIO10 | GPIO10                    | I/O/T                     | GPIO10                    | I/O/T                     | FSPIIO4                   | I1/O/T                    | SUBSPICS0                 | O/T                       | FSPICS0                   | I1/O/T                    |
| 16  | GPIO11 | GPIO11                    | I/O/T                     | GPIO11                    | I/O/T                     | FSPIIO5                   | I1/O/T                    | SUBSPID                   | I1/O/T                    | FSPID                     | I1/O/T                    |
| 17  | GPIO12 | GPIO12                    | I/O/T                     | GPIO12                    | I/O/T                     | FSPIIO6                   | I1/O/T                    | SUBSPICLK                 | O/T                       | FSPICLK                   | I1/O/T                    |
| 18  | GPIO13 | GPIO13                    | I/O/T                     | GPIO13                    | I/O/T                     | FSPIIO7                   | I1/O/T                    | SUBSPIQ                   | I1/O/T                    | FSPIQ                     | I1/O/T                    |
| 19  | GPIO14 | GPIO14                    | I/O/T                     | GPIO14                    | I/O/T                     | FSPIDQS                   | O/T                       | SUBSPIWP                  | I1/O/T                    | FSPIWP                    | I1/O/T                    |
| 21  | GPIO15 | GPIO15                    | I/O/T                     | GPIO15                    | I/O/T                     | U0RTS                     | O                         |                           |                           |                           |                           |
| 22  | GPIO16 | GPIO16                    | I/O/T                     | GPIO16                    | I/O/T                     | U0CTS                     | I1                        |                           |                           |                           |                           |
| 23  | GPIO17 | GPIO17                    | I/O/T                     | GPIO17                    | I/O/T                     | U1TXD                     | O                         |                           |                           |                           |                           |
| 24  | GPIO18 | GPIO18                    | I/O/T                     | GPIO18                    | I/O/T                     | U1RXD                     | I1                        | CLK_OUT3                  | O                         |                           |                           |
| 25  | GPIO19 | GPIO19                    | I/O/T                     | GPIO19                    | I/O/T                     | U1RTS                     | O                         | CLK_OUT2                  | O                         |                           |                           |
| 26  | GPIO20 | GPIO20                    | I/O/T                     | GPIO20                    | I/O/T                     | U1CTS                     | I1                        | CLK_OUT1                  | O                         |                           |                           |
| 27  | GPIO21 | GPIO21                    | I/O/T                     | GPIO21                    | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 28  | GPIO26 | SPICS1                    | O/T                       | GPIO26                    | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 30  | GPIO27 | SPIHD                     | I1/O/T                    | GPIO27                    | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 31  | GPIO28 |                           | I1/O/T                    | GPIO28                    | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 32  | GPIO29 | SPIWP SPICS0              | O/T                       | GPIO29                    | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 33  | GPIO30 | SPICLK                    | O/T                       | GPIO30                    | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 34  | GPIO31 | SPIQ                      | I1/O/T                    | GPIO31                    | I/O/T                     |                           |                           |                           |                           |                           |                           |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000019_105c7435f1e5efa61bf51aa20e10856ae69ba2a7d5ce7f4d70443595af5ffeb8.png)

<!-- page_break -->

## Cont'd from previous page

|         |        | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   | IO MUX Function 1, 2, 3   |
|---------|--------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|
| Pin No. | GPIO 2 | F0                        | Type 3                    | F1                        | Type                      | F2                        | Type                      | F3                        | Type                      | F4                        | Type                      |
| 35      | GPIO32 | SPID                      | I1/O/T                    | GPIO32                    | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 36      | GPIO48 | SPICLK_N_DIFF             | O/T                       | GPIO48                    | I/O/T                     | SUBSPICLK_N_DIFF          | O/T                       |                           |                           |                           |                           |
| 37      | GPIO47 | SPICLK_P_DIFF             | O/T                       | GPIO47                    | I/O/T                     | SUBSPICLK_P_DIFF          | O/T                       |                           |                           |                           |                           |
| 38      | GPIO33 | GPIO33                    | I/O/T                     | GPIO33                    | I/O/T                     | FSPIHD                    | I1/O/T                    | SUBSPIHD                  | I1/O/T                    | SPIIO4                    | I1/O/T                    |
| 39      | GPIO34 | GPIO34                    | I/O/T                     | GPIO34                    | I/O/T                     | FSPICS0                   | I1/O/T                    | SUBSPICS0                 | O/T                       | SPIIO5                    | I1/O/T                    |
| 40      | GPIO35 | GPIO35                    | I/O/T                     | GPIO35                    | I/O/T                     | FSPID                     | I1/O/T                    | SUBSPID                   | I1/O/T                    | SPIIO6                    | I1/O/T                    |
| 41      | GPIO36 | GPIO36                    | I/O/T                     | GPIO36                    | I/O/T                     | FSPICLK                   | I1/O/T                    | SUBSPICLK                 | O/T                       | SPIIO7                    | I1/O/T                    |
| 42      | GPIO37 | GPIO37                    | I/O/T                     | GPIO37                    | I/O/T                     | FSPIQ                     | I1/O/T                    | SUBSPIQ                   | I1/O/T                    | SPIDQS                    | I0/O/T                    |
| 43      | GPIO38 | GPIO38                    | I/O/T                     | GPIO38                    | I/O/T                     | FSPIWP                    | I1/O/T                    | SUBSPIWP                  | I1/O/T                    |                           |                           |
| 44      | GPIO39 | MTCK                      | I1                        | GPIO39                    | I/O/T                     | CLK_OUT3                  | O                         | SUBSPICS1                 | O/T                       |                           |                           |
| 45      | GPIO40 | MTDO                      | O/T                       | GPIO40                    | I/O/T                     | CLK_OUT2                  | O                         |                           |                           |                           |                           |
| 47      | GPIO41 | MTDI                      | I1                        | GPIO41                    | I/O/T                     | CLK_OUT1                  | O                         |                           |                           |                           |                           |
| 48      | GPIO42 | MTMS                      | I1                        | GPIO42                    | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 49      | GPIO43 | U0TXD                     | O                         | GPIO43                    | I/O/T                     | CLK_OUT1                  | O                         |                           |                           |                           |                           |
| 50      | GPIO44 | U0RXD                     | I1                        | GPIO44                    | I/O/T                     | CLK_OUT2                  | O                         |                           |                           |                           |                           |
| 51      | GPIO45 | GPIO45                    | I/O/T                     | GPIO45                    | I/O/T                     |                           |                           |                           |                           |                           |                           |
| 52      | GPIO46 | GPIO46                    | I/O/T                     | GPIO46                    | I/O/T                     |                           |                           |                           |                           |                           |                           |

- I - input. O - output. T - high impedance.
- I0 - input; if the pin is assigned a function other than F n , the input signal of F n is always 0 .
- I1 - input; if the pin is assigned a function other than F n , the input signal of F n is always 1 .

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000020_9315f1f97a5cb7b94a6d48393fc8dfd5307b99865ddc4a6c203512b30651a6fb.png)

<!-- page_break -->

## 2.3.2 RTC Functions

When the chip is in Deep-sleep mode, the IO MUX described in Section 2.3.1 IO MUX Functions will not work. That is where the RTC IO MUX comes in. It allows multiple input/output signals to be a single input/output pin in Deep-sleep mode, as the pin is connected to the RTC system and powered by VDD3P3\_RTC.

RTC IO pins can be assigned to RTC functions . They can

- Either work as RTC GPIOs ( RTC\_GPIO0, RTC\_GPIO1, etc. ), connected to the ULP coprocessor
- Or connect to RTC peripheral signals ( sar\_i2c\_scl\_0, sar\_i2c\_sda\_0, etc. ) - see T able 2-5 RTC Peripheral Signals Routed via RTC IO MUX

Table 2-5. RTC Peripheral Signals Routed via RTC IO MUX

| Pin Function              | Signal                   | Description          |
|---------------------------|--------------------------|----------------------|
| sar_i2c_scl… sar_i2c_sda… | Serial clock Serial data | RTC I2C0/1 interface |

Table 2-6 RTC Functions shows the RTC functions of RTC IO pins.

Table 2-6. RTC Functions

| Pin No.   | RTC IO Name 1   | RTC Function 2   | RTC Function 2   | RTC Function 2   | RTC Function 2   |
|-----------|-----------------|------------------|------------------|------------------|------------------|
| Pin No.   | RTC IO Name 1   | F0               | F1               | F2               | F3               |
| 5         | RTC_GPIO0       | RTC_GPIO0        |                  |                  | sar_i2c_scl_0    |
| 6         | RTC_GPIO1       | RTC_GPIO1        |                  |                  | sar_i2c_sda_0    |
| 7         | RTC_GPIO2       | RTC_GPIO2        |                  |                  | sar_i2c_scl_1    |
| 8         | RTC_GPIO3       | RTC_GPIO3        |                  |                  | sar_i2c_sda_1    |
| 9         | RTC_GPIO4       | RTC_GPIO4        |                  |                  |                  |
| 10        | RTC_GPIO5       | RTC_GPIO5        |                  |                  |                  |
| 11        | RTC_GPIO6       | RTC_GPIO6        |                  |                  |                  |
| 12        | RTC_GPIO7       | RTC_GPIO7        |                  |                  |                  |
| 13        | RTC_GPIO8       | RTC_GPIO8        |                  |                  |                  |
| 14        | RTC_GPIO9       | RTC_GPIO9        |                  |                  |                  |
| 15        | RTC_GPIO10      | RTC_GPIO10       |                  |                  |                  |
| 16        | RTC_GPIO11      | RTC_GPIO11       |                  |                  |                  |
| 17        | RTC_GPIO12      | RTC_GPIO12       |                  |                  |                  |
| 18        | RTC_GPIO13      | RTC_GPIO13       |                  |                  |                  |
| 19        | RTC_GPIO14      | RTC_GPIO14       |                  |                  |                  |
| 21        | RTC_GPIO15      | RTC_GPIO15       |                  |                  |                  |
| 22        | RTC_GPIO16      | RTC_GPIO16       |                  |                  |                  |
| 23        | RTC_GPIO17      | RTC_GPIO17       |                  |                  |                  |
| 24        | RTC_GPIO18      | RTC_GPIO18       |                  |                  |                  |
| 25        | RTC_GPIO19      | RTC_GPIO19       |                  |                  |                  |
| 26        | RTC_GPIO20      | RTC_GPIO20       |                  |                  |                  |
| 27        | RTC_GPIO21      | RTC_GPIO21       |                  |                  |                  |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000021_8a305661742a4104fe05ef18ad723f17dc0e1d1305921521ae56cc9808d8553b.png)

<!-- page_break -->

## 2.3.3 Analog Functions

Some IO pins also have analog functions , for analog peripherals (such as ADC) in any power mode. Internal analog signals are routed to these analog functions, see T able 2-7 Analog Signals Routed to Analog Functions .

Table 2-7. Analog Signals Routed to Analog Functions

| Pin Function   | Signal                        | Description                          |
|----------------|-------------------------------|--------------------------------------|
| TOUCH…         | Touch sensor channel … signal | Touch sensor interface               |
| ADC…_CH…       | ADC1/2 channel … signal       | ADC1/2 interface                     |
| XTAL_32K_N     | Negative clock signal         | 32 kHz external clock input/output   |
| XTAL_32K_P     | Positive clock signal         | connected to ESP32-S3's oscillator   |
| USB_D-         | Data -                        | USB OTG and USB Serial/JTAG function |
| USB_D+         | Data +                        | USB OTG and USB Serial/JTAG function |

Table 2-8 Analog Functions shows the analog functions of IO pins.

Table 2-8. Analog Functions

|         |            | Analog Function 1, 2   | Analog Function 1, 2   |
|---------|------------|------------------------|------------------------|
| Pin No. | GPIO 3     | F0                     | F1                     |
| 6       | RTC_GPIO1  | TOUCH1                 | ADC1_CH0               |
| 7       | RTC_GPIO2  | TOUCH2                 | ADC1_CH1               |
| 8       | RTC_GPIO3  | TOUCH3                 | ADC1_CH2               |
| 9       | RTC_GPIO4  | TOUCH4                 | ADC1_CH3               |
| 10      | RTC_GPIO5  | TOUCH5                 | ADC1_CH4               |
| 11      | RTC_GPIO6  | TOUCH6                 | ADC1_CH5               |
| 12      | RTC_GPIO7  | TOUCH7                 | ADC1_CH6               |
| 13      | RTC_GPIO8  | TOUCH8                 | ADC1_CH7               |
| 14      | RTC_GPIO9  | TOUCH9                 | ADC1_CH8               |
| 15      | RTC_GPIO10 | TOUCH10                | ADC1_CH9               |
| 16      | RTC_GPIO11 | TOUCH11                | ADC2_CH0               |
| 17      | RTC_GPIO12 | TOUCH12                | ADC2_CH1               |
| 18      | RTC_GPIO13 | TOUCH13                | ADC2_CH2               |
| 19      | RTC_GPIO14 | TOUCH14                | ADC2_CH3               |
| 21      | RTC_GPIO15 | XTAL_32K_P             | ADC2_CH4               |
| 22      | RTC_GPIO16 | XTAL_32K_N             | ADC2_CH5               |
| 23      | RTC_GPIO17 |                        | ADC2_CH6               |
| 24      | RTC_GPIO18 |                        | ADC2_CH7               |
| 25      | RTC_GPIO19 | USB_D-                 | ADC2_CH8               |
| 26      | RTC_GPIO20 | USB_D+                 | ADC2_CH9               |

<!-- page_break -->

## 2.3.4 Restrictions for GPIOs and RTC\_GPIOs

All IO pins of ESP32-S3 have GPIO and some have RTC\_GPIO pin functions. However, the IO pins are multiplexed and can be configured for different purposes based on the requirements. Some IOs have restrictions for usage. It is essential to consider the multiplexed nature and the limitations when using these IO pins.

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000022_93cce6daca2dcba4bb255db9179d665ee9ce341f0c8f8c46d6d7cbcb90f82e1d.png)

In tables of this chapter, some pin functions are in red or yellow . These functions indicate pins that require extra caution when used as GPIO / GPIO :

- IO Pins - allocated for communication with in-package flash/PSRAM and NOT recommended for other uses. For details, see Section 2.6 Pin Mapping Between Chip and Flash/PSRAM .
- IO Pins - have one of the following important functions:
- Strapping pins - need to be at certain logic levels at startup. See Section 3 Boot Configurations . Note:

Strapping pins are highlighted by Pin Name or configurations At Reset , instead of the pin functions.

- USB\_D+/-- by default, connected to the USB Serial/JTAG Controller. To function as GPIOs, these pins need to be reconfigured via the IO\_MUX\_MCU\_SEL bit (see ESP32-S3 Technical Reference Manual &gt; Chapter IO MUX and GPIO Matrix for details).
- JTAG interface - often used for debugging. See T able 2-4 IO MUX Functions . To free these pins up, the pin functions USB\_D+/- of the USB Serial/JTAG Controller can be used instead. See also Section 3.4 JTAG Signal Source Control .
- UART0 interface - often used for debugging. See T able 2-4 IO MUX Functions .
- 8-line SPI interface - no restrictions, unless the chip is connected to flash/PSRAM using 8-line SPI mode.

For more information about assigning pins, please see Section 2.3.5 Peripheral Pin Assignment and ESP32-S3 Consolidated Pin Overview.

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000023_2c209c28f40b20180378ad54f48b07edf7b0ff61016f74818292ef58b14cb46e.png)

<!-- page_break -->

## 2.3.5 Peripheral Pin Assignment

Table 2-9 Peripheral Pin Assignment highlights which pins can be assigned to each peripheral interface according to the following priorities:

- Priority 1 (P1) : Fixed pins connected directly to peripheral signals via IO MUX or RTC IO MUX. If a peripheral interface does not have priority 1 pins, such as UART2, it can be assigned to any GPIO pins from priority 2 to priority 4.
- Any GPIO pins mapping to peripheral signals via GPIO Matrix, can be priority 2, 3, or 4.
- -Priority 2 (P2) : GPIO pins can be freely used without restrictions.
- -Priority 3 (P3) : GPIO pins should be used with caution, as they may conflict with the following important functions described in Section 2.3.4 Restrictions for GPIOs and RTC\_GPIOs :
* GPIO0, GPIO3, GPIO45, GPIO46 : Strapping pins.
* GPIO19, GPIO20 : USB Serial/JTAG interface.
* GPIO39, GPIO40, GPIO41, GPIO42 : JTAG interface.
* GPIO43, GPIO44 : UART0 interface.
* GPIO33, GPIO34, GPIO35, GPIO36, GPIO37 : The higher 4 bits data line interface and DQS interface for the SPI0/1 interface in 8-line SPI mode, and can be GPIO pins if the chip is not connected to flash or PSRAM in 8-line SPI mode.
- -Priority 4 (P4) : GPIO pins already allocated or not recommended for use, as described in Section 2.3.4 Restrictions for GPIOs and RTC\_GPIOs :
* GPIO26, GPIO27 , GPIO28, GPIO29, GPIO30, GPIO31, GPIO32 : SPI0/1 interface connected to the in-package flash and PSRAM, or recommended for the off-package flash and PSRAM.

If a peripheral interface does not have priority 2 to 4 pins, such as USB Serial/JTAG, it means it can be assigned only to priority 1 pins.

## Note:

- For details about which peripheral signals are connected to IO MUX or RTC IO MUX pins, please refer to Section 2.3.1 IO MUX Functions or Section 2.3.2 RTC Functions .
- For details about which peripheral signals can be assigned to GPIO pins, please refer to ESP32-S3 Technical Reference Manual &gt; Chapter IO MUX and GPIO Matrix &gt; Section Peripheral Signal List.

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000024_5c7ca706499c6fb50a41d4bf08619a539102b1734c0ce4aaa5765405221c2a96.png)

<!-- page_break -->

27

## Table 2-9. Peripheral Pin Assignment

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000025_303a637708064640a93675b346ce7102db513258c67207e179b475b7486cfcbd.png)

2 Signals of UART0, UART1, SPI0/1, and SPI2 interfaces can be mapped to any GPIO pins through the GPIO Matrix, regardless of whether they are directly routed to fixed pins

via IO MUX.

<!-- page_break -->

## 2.4 Analog Pins

Table 2-10. Analog Pins

|   Pin No. | Pin Name   | Pin Type   | Pin Function                                                                                                                      |
|-----------|------------|------------|-----------------------------------------------------------------------------------------------------------------------------------|
|         1 | LNA_IN     | I/O        | Low Noise Amplifier (RF LNA) input/output signals                                                                                 |
|         4 | CHIP_PU    | I          | High: on, enables the chip (powered up). Low: off, disables the chip (powered down). Note: Do not leave the CHIP_PU pin floating. |
|        53 | XTAL_N     | -          | External clock input/output connected to chip's crystal or oscillator. P/N means differential clock positive/negative.            |
|        54 | XTAL_P     | -          |                                                                                                                                   |

<!-- page_break -->

## 2.5 Power Supply

## 2.5.1 Power Pins

The chip is powered via the power pins described in T able 2-11 Power Pins .

Table 2-11. Power Pins

|         |             | Power Supply   | Power Supply                           | Power Supply   |
|---------|-------------|----------------|----------------------------------------|----------------|
| Pin No. | Pin Name    | Direction      | Power Domain/Other                     | IO Pins 5      |
| 2       | VDD3P3      | Input          | Analog power domain                    |                |
| 3       | VDD3P3      | Input          | Analog power domain                    |                |
| 20      | VDD3P3_RTC  | Input          | RTC and part of Digital power domains  | RTC IO         |
| 29      | VDD_SPI 3,4 | Input          | In-package memory (backup power line)  |                |
| 29      | VDD_SPI 3,4 | Output         | In-package and off-package flash/PSRAM | SPI IO         |
| 46      | VDD3P3_CPU  | Input          | Digital power domain                   | Digital IO     |
| 55      | VDDA        | Input          | Analog power domain                    |                |
| 56      | VDDA        | Input          | Analog power domain                    |                |
| 57      | GND         | -              | External ground connection             |                |

## 2.5.2 Power Scheme

The power scheme is shown in Figure 2-2 ESP32-S3 Power Scheme .

The components on the chip are powered via voltage regulators.

Table 2-12. Voltage Regulators

| Voltage Regulator   | Output   | Power Supply                                                            |
|---------------------|----------|-------------------------------------------------------------------------|
| Digital             | 1.1 V    | Digital power domain                                                    |
| Low-power           | 1.1 V    | RTC power domain                                                        |
| Flash               | 1.8 V    | Can be configured to power in-package flash/PSRAM or off-package memory |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000026_4b9c375defe3a943bdecff0b4e46d5330f8aa1cc81294e0682078adbde8ae560.png)

<!-- page_break -->

Figure 2-2. ESP32-S3 Power Scheme

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000027_aef63a98dbb4c80247a61c2c22740b45ef0de1996da7e20628fc5a053cac3964.png)

## 2.5.3 Chip Power-up and Reset

Once the power is supplied to the chip, its power rails need a short time to stabilize. After that, CHIP\_PU - the pin used for power-up and reset - is pulled high to activate the chip. For information on CHIP\_PU as well as power-up and reset timing, see Figure 2-3 and T able 2-13.

Figure 2-3. Visualization of Timing Parameters for Power-up and Reset

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000028_51a0625e68f37e89b6b9ccec69b5fefeba7afd414f8503b543e4f3e7d2d675dd.png)

Table 2-13. Description of Timing Parameters for Power-up and Reset

| Parameter   | Description                                                                                                                                           |   Min ( µ s) |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|
| t STBL      | Time reserved for the power rails of VDDA, VDD3P3, VDD3P3_RTC, and VDD3P3_CPU to stabilize before the CHIP_PU pin is pulled high to activate the chip |           50 |
| t RST       | Time reserved for CHIP_PU to stay below V IL _ nRST to reset the chip (see Table 5-4)                                                                 |           50 |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000029_da0c4522a9db0c19a38e02a8db553367c78615a902197db93ed80e6e58e79475.png)

<!-- page_break -->

## 2.6 Pin Mapping Between Chip and Flash/PSRAM

Table 2-14 lists the pin mapping between the chip and flash/PSRAM for all SPI modes.

For chip variants with in-package flash/PSRAM (see T able 1-1 ESP32-S3 Series Comparison ), the pins allocated for communication with in-package flash/PSRAM can be identified depending on the SPI mode used.

For off-package flash/PSRAM, these are the recommended pin mappings.

For more information on SPI controllers, see also Section 4.2.1.5 Serial Peripheral Interface (SPI) .

Notice: Do not use the pins connected to in-package flash/PSRAM for any other purposes.

Table 2-14. Pin Mapping Between Chip and Flash or PSRAM

|     |          | Single SPI   | Single SPI   | Dual SPI   | Dual SPI   | Quad SPI/QPI   | Quad SPI/QPI   | Octal SPI/OPI   | Octal SPI/OPI   |
|-----|----------|--------------|--------------|------------|------------|----------------|----------------|-----------------|-----------------|
| Pin | Pin Name | Flash        | PSRAM        | Flash      | PSRAM      | Flash          | PSRAM          | Flash           | PSRAM           |
| 28  | SPICS1 2 |              | CE#          |            | CE#        |                | CE#            |                 | CE#             |
| 30  | SPIHD    | HOLD#        | SIO3         | HOLD#      | SIO3       | HOLD#          | SIO3           | DQ3             | DQ3             |
| 31  | SPIWP    | WP#          | SIO2         | WP#        | SIO2       | WP#            | SIO2           | DQ2             | DQ2             |
| 32  | SPICS0 1 | CS#          |              | CS#        |            | CS#            |                | CS#             |                 |
| 33  | SPICLK   | CLK          | CLK          | CLK        | CLK        | CLK            | CLK            | CLK             | CLK             |
| 34  | SPIQ     | DO           | SO/SIO1      | DO         | SO/SIO1    | DO             | SO/SIO1        | DQ1             | DQ1             |
| 35  | SPID     | DI           | SI/SIO0      | DI         | SI/SIO0    | DI             | SI/SIO0        | DQ0             | DQ0             |
| 38  | GPIO33   |              |              |            |            |                |                | DQ4             | DQ4             |
| 39  | GPIO34   |              |              |            |            |                |                | DQ5             | DQ5             |
| 40  | GPIO35   |              |              |            |            |                |                | DQ6             | DQ6             |
| 41  | GPIO36   |              |              |            |            |                |                | DQ7             | DQ7             |
| 42  | GPIO37   |              |              |            |            |                |                | DQS/DM          | DQS/DM          |

<!-- page_break -->

## 3 Boot Configurations

The chip allows for configuring the following boot parameters through strapping pins and eFuse parameters at power-up or a hardware reset, without microcontroller interaction.

- Chip boot mode
- -Strapping pin: GPIO0 and GPIO46
- VDD\_SPI voltage
- -Strapping pin: GPIO45
- -eFuse parameter: EFUSE\_VDD\_SPI\_FORCE and EFUSE\_VDD\_SPI\_TIEH
- ROM message printing
- -Strapping pin: GPIO46
- -eFuse parameter: EFUSE\_UART\_PRINT\_CONTROL and EFUSE\_DIS\_USB\_SERIAL\_JTAG\_ROM\_PRINT
- JTAG signal source
- -Strapping pin: GPIO3
- -eFuse parameter: EFUSE\_DIS\_PAD\_JTAG, EFUSE\_DIS\_USB\_JTAG, and EFUSE\_STRAP\_JTAG\_SEL

The default values of all the above eFuse parameters are 0, which means that they are not burnt. Given that eFuse is one-time programmable, once programmed to 1, it can never be reverted to 0. For how to program eFuse parameters, please refer to ESP32-S3 Technical Reference Manual &gt; Chapter eFuse Controller .

The default values of the strapping pins, namely the logic levels, are determined by pins' internal weak pull-up/pull-down resistors at reset if the pins are not connected to any circuit, or connected to an external high-impedance circuit.

Table 3-1. Default Configuration of Strapping Pins

| Strapping Pin   | Default Configuration   | Bit Value   |
|-----------------|-------------------------|-------------|
| GPIO0           | Weak pull-up            | 1           |
| GPIO3           | Floating                | -           |
| GPIO45          | Weak pull-down          | 0           |
| GPIO46          | Weak pull-down          | 0           |

To change the bit values, the strapping pins should be connected to external pull-down/pull-up resistances. If the ESP32-S3 is used as a device by a host MCU, the strapping pin voltage levels can also be controlled by the host MCU.

All strapping pins have latches. At Chip Reset, the latches sample the bit values of their respective strapping pins and store them until the chip is powered down or shut down. The states of latches cannot be changed in any other way. It makes the strapping pin values available during the entire chip operation, and the pins are freed up to be used as regular IO pins after reset. For details on Chip Reset, see ESP32-S3 Technical Reference Manual &gt; Chapter Reset and Clock .

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000030_1b49dc24bfd32956d62e183d10931967ad19b2b1cc990bcc0e50f5332e4e29f2.png)

<!-- page_break -->

The timing of signals connected to the strapping pins should adhere to the setup time and hold time specifications in T able 3-2 and Figure 3-1.

Table 3-2. Description of Timing Parameters for the Strapping Pins

| Parameter   | Description                                                                                                                                                          |   Min (ms) |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|
| t SU        | Setup time is the time reserved for the power rails to stabilize be- fore the CHIP_PU pin is pulled high to activate the chip.                                       |          0 |
| t H         | Hold time is the time reserved for the chip to read the strapping pin values after CHIP_PU is already high and before these pins start operating as regular IO pins. |          3 |

Figure 3-1. Visualization of Timing Parameters for the Strapping Pins

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000031_c3598a6579a7564c1c53ddcbefa92006a0993853136df92563917b2aa38f32bd.png)

## 3.1 Chip Boot Mode Control

GPIO0 and GPIO46 control the boot mode after the reset is released. See T able 3-3 Chip Boot Mode Control .

Table 3-3. Chip Boot Mode Control

| Boot Mode                  |   GPIO0 | GPIO46    |
|----------------------------|---------|-----------|
| SPI boot mode              |       1 | Any value |
| Joint download boot mode 2 |       0 | 0         |

- 2 Joint Download Boot mode supports the following download methods:
- USB Download Boot:
- -USB-Serial-JTAG Download Boot
- -USB-OTG Download Boot
- UART Download Boot

In addition to SPI Boot and Joint Download Boot modes, ESP32-S3 also supports SPI Download Boot mode.

<!-- page_break -->

For details, please see ESP32-S3 Technical Reference Manual &gt; Chapter Chip Boot Control .

## 3.2 VDD\_SPI Voltage Control

The required VDD\_SPI voltage for the chips of the ESP32-S3 Series can be found in T able 1-1 ESP32-S3 Series Comparison .

The VDD\_SPI voltage can be:

- (Default) 3.3 V supplied by VDD3P3\_RTC via R SPI
- 1.8V supplied by the Flash Voltage Regulator

The voltage is determined by EFUSE\_VDD\_SPI\_FORCE, GPIO45, and EFUSE\_VDD\_SPI\_TIEH.

Table 3-4. VDD\_SPI Voltage Control

| VDD_SPI power source 2   | Voltage   |   EFUSE_VDD_SPI_FORCE | GPIO45   | EFUSE_VDD_SPI_TIEH   |
|--------------------------|-----------|-----------------------|----------|----------------------|
| VDD3P3_RTC via R SPI     | 3.3 V     |                     0 | 0        | Ignored              |
| VDD3P3_RTC via R SPI     | 3.3 V     |                     1 | Ignored  | 1                    |
| Flash Voltage Regulator  | 1.8 V     |                     0 | 1        | Ignored              |
| Flash Voltage Regulator  | 1.8 V     |                     1 | Ignored  | 0                    |

## 3.3 ROM Messages Printing Control

During the boot process, the messages by the ROM code can be printed to:

- (Default) UART0 and USB Serial/JTAG controller
- USB Serial/JTAG controller
- UART0

The ROM messages printing to UART or USB Serial/JTAG controller can be respectively disabled by configuring registers and eFuse. For detailed information, please refer to ESP32-S3 Technical Reference Manual &gt; Chapter Chip Boot Control .

## 3.4 JTAG Signal Source Control

The strapping pin GPIO3 can be used to control the source of JTAG signals during the early boot process. This pin does not have any internal pull resistors and the strapping value must be controlled by the external circuit that cannot be in a high impedance state.

As T able 3-5 JTAG Signal Source Control shows, GPIO3 is used in combination with EFUSE\_DIS\_PAD\_JTAG, EFUSE\_DIS\_USB\_JTAG, and EFUSE\_STRAP\_JTAG\_SEL.

<!-- page_break -->

Table 3-5. JTAG Signal Source Control

| JTAG Signal Source          |   EFUSE_DIS_PAD_JTAG |   EFUSE_DIS_USB_JTAG | EFUSE_STRAP_JTAG_SEL   | GPIO3   |
|-----------------------------|----------------------|----------------------|------------------------|---------|
| USB Serieal/JTAG Controller |                    0 |                    0 | 0                      | Ignored |
| USB Serieal/JTAG Controller |                    0 |                    0 | 1                      | 1       |
| USB Serieal/JTAG Controller |                    1 |                    0 | Ignored                | Ignored |
| JTAG pins 2                 |                    0 |                    0 | 1                      | 0       |
| JTAG pins 2                 |                    0 |                    1 | Ignored                | Ignored |
| JTAG is disabled            |                    1 |                    1 | Ignored                | Ignored |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000032_51406aea810bacc49a7a8a5a2fca16ab3307b1adf8125b6624c305606054cafd.png)

<!-- page_break -->

## 4 Functional Description

## 4.1 System

This section describes the core of the chip's operation, covering its microprocessor, memory organization, system components, and security features.

## 4.1.1 Microprocessor and Master

This subsection describes the core processing units within the chip and their capabilities.

## 4.1.1.1 CPU

ESP32-S3 has a low-power Xtensa ® dual-core 32-bit LX7 microprocessor.

## Feature List

- Five-stage pipeline that supports the clock frequency of up to 240 MHz
- 16-bit/24-bit instruction set providing high code density
- 32-bit customized instruction set and 128-bit data bus that provide high computing performance
- Support for single-precision floating-point unit (FPU)
- 32-bit multiplier and 32-bit divider
- Unbuffered GPIO instructions
- 32 interrupts at six levels
- Windowed ABI with 64 physical general registers
- Trace function with TRAX compressor, up to 16 KB trace memory
- JTAG for debugging

For information about the Xtensa ® Instruction Set Architecture, please refer to Xtensa ® Instruction Set Architecture (ISA) Summary .

## 4.1.1.2 Processor Instruction Extensions (PIE)

ESP32-S3 contains a series of new extended instruction set in order to improve the operation efficiency of specific AI and DSP (Digital Signal Processing) algorithms.

## Feature List

- 128-bit new general-purpose registers
- 128-bit vector operations, e.g., complex multiplication, addition, subtraction, multiplication, shifting, comparison, etc
- Data handling instructions and load/store operation instructions combined
- Non-aligned 128-bit vector data

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000033_8f1c07f9317a3b29b586dc6dcadbc2b4d6ce2141f81872fbef94756a4c9e5537.png)

<!-- page_break -->

- Saturation operation

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Processor Instruction Extensions .

## 4.1.1.3 Ultra-Low-Power Coprocessor (ULP)

The ULP coprocessor is designed as a simplified, low-power replacement of CPU in sleep modes. It can be also used to supplement the functions of the CPU in normal working mode. The ULP coprocessor and RTC memory remain powered up during the Deep-sleep mode. Hence, the developer can store a program for the ULP coprocessor in the RTC slow memory to access RTC GPIO, RTC peripheral devices, RTC timers and internal sensors in Deep-sleep mode.

ESP32-S3 has two ULP coprocessors, one based on RISC-V instruction set architecture (ULP-RISC-V) and the other on finite state machine (ULP-FSM). The clock of the coprocessors is the internal fast RC oscillator.

## Feature List

- ULP-RISC-V:
- -Support for RV32IMC instruction set
- -Thirty-two 32-bit general-purpose registers
- -32-bit multiplier and divider
- -Support for interrupts
- -Booted by the CPU, its dedicated timer, or RTC GPIO
- ULP-FSM:
- -Support for common instructions including arithmetic, jump, and program control instructions
- -Support for on-board sensor measurement instructions
- -Booted by the CPU, its dedicated timer, or RTC GPIO

## Note:

Note that these two coprocessors cannot work simultaneously.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter ULP Coprocessor .

## 4.1.1.4 GDMA Controller (GDMA)

ESP32-S3 has a general-purpose DMA controller (GDMA) with five independent channels for transmitting and another five independent channels for receiving. These ten channels are shared by peripherals that have DMA feature, and support dynamic priority.

The GDMA controller controls data transfer using linked lists. It allows peripheral-to-memory and memory-to-memory data transfer at a high speed. All channels can access internal and external RAM.

The ten peripherals on ESP32-S3 with DMA feature are SPI2, SPI3, UHCI0, I2S0, I2S1, LCD/CAM, AES, SHA, ADC, and RMT.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter GDMA Controller .

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000034_7b812ccf75dd2e1bce7dc5aea3e40a0aff31e249e41ded83847c52f494e64a7e.png)

<!-- page_break -->

## 4.1.2 Memory Organization

This subsection describes the memory arrangement to explain how data is stored, accessed, and managed for efficient operation.

Figure 4-1 illustrates the address mapping structure of ESP32-S3.

CPU

Figure 4-1. Address Mapping Structure

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000035_3e1fb5e3ede84b41efe5af13e44f35ad57e0687696df5ece92cc8c7870dc4750.png)

## 4.1.2.1 Internal Memory

The internal memory of ESP32-S3 refers to the memory integrated on the chip die or in the chip package, including ROM, SRAM, eFuse, and flash.

## Feature List

- 384 KB ROM : for booting and core functions
- 512 KB on-chip SRAM : for data and instructions, running at a configurable frequency of up to 240 MHz
- RTC FAST memory : 8 KB SRAM that supports read/write/instruction fetch by the main CPU (LX7 dual-core processor). It can retain data in Deep-sleep mode

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000036_a6946ca320967325bd391fcb451221de0669e1d5c2b12cb1542b5b333c5d5f33.png)

<!-- page_break -->

- RTC SLOW Memory : 8 KB SRAM that supports read/write/instruction fetch by the main CPU (LX7 dual-core processor) or coprocessors. It can retain data in Deep-sleep mode
- 4096-bit eFuse memory: 1792 bits are available for users, such as encryption key and device ID. See also Section 4.1.2.4 eFuse Controller
- In-package flash and PSRAM :
- -See flash and PSRAM size in Chapter 1 ESP32-S3 Series Comparison
- -For specifications, refer to Section 5.7 Memory Specifications .

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter System and Memory .

## 4.1.2.2 External Flash and RAM

ESP32-S3 supports SPI, Dual SPI, Quad SPI, Octal SPI, QPI, and OPI interfaces that allow connection to multiple external flash and RAM.

The external flash and RAM can be mapped into the CPU instruction memory space and read-only data memory space. The external RAM can also be mapped into the CPU data memory space. ESP32-S3 supports up to 1 GB of external flash and RAM, and hardware encryption/decryption based on XTS-AES to protect users' programs and data in flash and external RAM.

Through high-speed caches, ESP32-S3 can support at a time up to:

- External flash or RAM mapped into 32 MB instruction space as individual blocks of 64 KB
- External RAM mapped into 32 MB data space as individual blocks of 64 KB. 8-bit, 16-bit, 32-bit, and 128-bit reads and writes are supported. External flash can also be mapped into 32 MB data space as individual blocks of 64 KB, but only supporting 8-bit, 16-bit, 32-bit and 128-bit reads.

## Note:

After ESP32-S3 is initialized, firmware can customize the mapping of external RAM or flash into the CPU address space.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter System and Memory .

## 4.1.2.3 Cache

ESP32-S3 has an instruction cache and a data cache shared by the two CPU cores. Each cache can be partitioned into multiple banks.

## Feature List

- Instruction cache: 16 KB (one bank) or 32 KB (two banks) Data cache: 32 KB (one bank) or 64 KB (two banks)
- Instruction cache: four-way or eight-way set associative Data cache: four-way set associative
- Block size of 16 bytes or 32 bytes for both instruction cache and data cache
- Pre-load function
- Lock function

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000037_4f5e338ecd28a758066644b5b1a14a4cdaaa47e637f9e1d12bf0e25df0cb9fe5.png)

<!-- page_break -->

- Critical word first and early restart

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter System and Memory .

## 4.1.2.4 eFuse Controller

ESP32-S3 contains a 4-Kbit eFuse to store parameters, which are burned and read by an eFuse controller.

## Feature List

- 4 Kbits in total, with 1792 bits reserved for users, e.g., encryption key and device ID
- One-time programmable storage
- Configurable write protection
- Configurable read protection
- Various hardware encoding schemes to protect against data corruption

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter eFuse Controller .

## 4.1.3 System Components

This subsection describes the essential components that contribute to the overall functionality and control of the system.

## 4.1.3.1 IO MUX and GPIO Matrix

The IO MUX and GPIO Matrix in the ESP32-S3 chip provide flexible routing of peripheral input and output signals to the GPIO pins. These peripherals enhance the functionality and performance of the chip by allowing the configuration of I/O, support for multiplexing, and signal synchronization for peripheral inputs.

## Feature List

- GPIO Matrix:
- -A full-switching matrix between the peripheral input/output signals and the GPIO pins
- -175 digital peripheral input signals can be sourced from the input of any GPIO pins
- -The output of any GPIO pins can be from any of the 184 digital peripheral output signals
- -Supports signal synchronization for peripheral inputs based on APB clock bus
- -Provides input signal filter
- -Supports sigma delta modulated output
- -Supports GPIO simple input and output

## · IO MUX:

- -Provides one configuration register IO\_MUX\_GPIO n \_REG for each GPIO pin. The pin can be configured to
* perform GPIO function routed by GPIO matrix

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000038_143591eb7646c3a25ab79319c781b300624194a9f940e92c14940d436c0e70b9.png)

<!-- page_break -->

* or perform direct connection bypassing GPIO matrix
- -Supports some high-speed digital signals (SPI, JTAG, UART) bypassing GPIO matrix for better high-frequency digital performance (IO MUX is used to connect these pins directly to peripherals)
- RTC IO MUX:
- -Controls low power feature of 22 RTC GPIO pins
- -Controls analog functions of 22 RTC GPIO pins
- -Redirects 22 RTC input/output signals to RTC system

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter IO MUX and GPIO Matrix .

## 4.1.3.2 Reset

ESP32-S3 provides four reset levels, namely CPU Reset, Core Reset, System Reset, and Chip Reset.

## Feature List

- Support four reset levels:
- -CPU Reset: only resets CPU x core. CPU x can be CPU0 or CPU1 here. Once such reset is released, programs will be executed from CPU x reset vector. Each CPU core has its own reset logic. If CPU Reset is from CPU0, the sensitive registers will be reset, too.
- -Core Reset: resets the whole digital system except RTC, including CPU0, CPU1, peripherals, Wi-Fi, Bluetooth ® LE (BLE), and digital GPIOs.
- -System Reset: resets the whole digital system, including RTC.
- -Chip Reset: resets the whole chip.
- Support software reset and hardware reset:
- -Software reset is triggered by CPU x configuring its corresponding registers. Refer to ESP32-S3 Technical Reference Manual &gt; Chapter Low-power Management for more details.
- -Hardware reset is directly triggered by the circuit.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Reset and Clock .

## 4.1.3.3 Clock

## CPU Clock

The CPU clock has three possible sources:

- External main crystal clock
- Internal fast RC oscillator (typically about 17 .5 MHz, adjustable)
- PLL clock

The application can select the clock source from the three clocks above. The selected clock source drives the CPU clock directly, or after division, depending on the application. Once the CPU is reset, the default clock source would be the external main crystal clock divided by 2.

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000039_ff77e41af37cce0c14fab8001d704287bb9605da01cf5f35300c53a2bc214cfb.png)

<!-- page_break -->

## Note:

ESP32-S3 is unable to operate without an external main crystal clock.

## RTC Clock

The RTC slow clock is used for RTC counter, RTC watchdog and low-power controller. It has three possible sources:

- External low-speed (32 kHz) crystal clock
- Internal slow RC oscillator (typically about 136 kHz, adjustable)
- Internal fast RC oscillator divided clock (derived from the internal fast RC oscillator divided by 256)

The RTC fast clock is used for RTC peripherals and sensor controllers. It has two possible sources:

- External main crystal clock divided by 2
- Internal fast RC oscillator (typically about 17 .5 MHz, adjustable)

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Reset and Clock .

## 4.1.3.4 Interrupt Matrix

The interrupt matrix embedded in ESP32-S3 independently allocates peripheral interrupt sources to the two CPUs' peripheral interrupts, to timely inform CPU0 or CPU1 to process the interrupts once the interrupt signals are generated.

## Feature List

- 99 peripheral interrupt sources as input
- Generate 26 peripheral interrupts to CPU0 and 26 peripheral interrupts to CPU1 as output. Note that the remaining six CPU0 interrupts and six CPU1 interrupts are internal interrupts.
- Disable CPU non-maskable interrupt (NMI) sources
- Query current interrupt status of peripheral interrupt sources

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Interrupt Matrix .

## 4.1.3.5 Power Management Unit (PMU)

ESP32-S3 has an advanced Power Management Unit (PMU). It can be flexibly configured to power up different power domains of the chip to achieve the best balance between chip performance, power consumption, and wakeup latency.

The integrated Ultra-Low-Power (ULP) coprocessors allow ESP32-S3 to operate in Deep-sleep mode with most of the power domains turned off, thus achieving extremely low-power consumption.

Configuring the PMU is a complex procedure. To simplify power management for typical scenarios, there are the following predefined power modes that power up different combinations of power domains:

- Active mode - The CPU, RF circuits, and all peripherals are on. The chip can process data, receive, transmit, and listen.

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000040_4e9f11cac573093fc8b8987a48aa1bb30903ea39601ebcc63a18437e22d2e121.png)

<!-- page_break -->

- Modem-sleep mode - The CPU is on, but the clock frequency can be reduced. The wireless connections can be configured to remain active as RF circuits are periodically switched on when required.
- Light-sleep mode - The CPU stops running, and can be optionally powered on. The RTC peripherals, as well as the ULP coprocessor can be woken up periodically by the timer. The chip can be woken up via all wake up mechanisms: MAC, RTC timer, or external interrupts. Wireless connections can remain active. Some groups of digital peripherals can be optionally powered off.
- Deep-sleep mode - Only RTC is powered on. Wireless connection data is stored in RTC memory.

For power consumption in different power modes, see Section 5.6 Current Consumption .

Figure 4-2 Components and Power Domains and the following T able 4-1 show the distribution of chip components between power domains and power subdomains .

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000041_d304a8507e88ded28bcdc68d4b85e98f66e15cf9f2990f1e0e80d9e7abece6f2.png)

## Power distribution

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000042_1954437744dbabf3a1e621ca31aa61b94df6979d6842fbccaeca296be0735008.png)

Figure 4-2. Components and Power Domains

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000043_f31b222886a87dc8a261936e4e1950686b15506ce1fbeeb41f56b64a38331991.png)

<!-- page_break -->

Table 4-1. Components and Power Domains

| Power Power   | RTC   | RTC                 | Digital   | Digital   | Digital                 | Digital                   | Analog   | Analog        | Analog    | Analog   | Analog      |
|---------------|-------|---------------------|-----------|-----------|-------------------------|---------------------------|----------|---------------|-----------|----------|-------------|
| Mode Domain   |       | Optional RTC Periph |           | CPU       | Optional Digital Periph | Wireless Digital Circuits |          | RC_ FAST_ CLK | XTAL_ CLK | PLL      | RF Circuits |
| Active        | ON    | ON                  | ON        | ON        | ON                      | ON                        | ON       | ON            | ON        | ON       | ON          |
| Modem-sleep   | ON    | ON                  | ON        | ON        | ON                      | ON 1                      | ON       | ON            | ON        | ON       | OFF 2       |
| Light-sleep   | ON    | ON                  | ON        | OFF 1     | ON 1                    | OFF 1                     | ON       | OFF           | OFF       | OFF      | OFF 2       |
| Deep-sleep    | ON    | ON 1                | OFF       | OFF       | OFF                     | OFF                       | ON       | OFF           | OFF       | OFF      | OFF         |

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Low Power Management .

## 4.1.3.6 System Timer

ESP32-S3 integrates a 52-bit system timer, which has two 52-bit counters and three comparators.

## Feature List

- Counters with a clock frequency of 16 MHz
- Three types of independent interrupts generated according to alarm value
- Two alarm modes: target mode and period mode
- 52-bit target alarm value and 26-bit periodic alarm value
- Read sleep time from RTC timer when the chip is awaken from Deep-sleep or Light-sleep mode
- Counters can be stalled if the CPU is stalled or in OCD mode

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter System Timer .

## 4.1.3.7 General Purpose Timers

ESP32-S3 is embedded with four 54-bit general-purpose timers, which are based on 16-bit prescalers and 54-bit auto-reload-capable up/down-timers.

## Feature List

- 16-bit clock prescaler, from 2 to 65536
- 54-bit time-base counter programmable to be incrementing or decrementing
- Able to read real-time value of the time-base counter
- Halting and resuming the time-base counter
- Programmable alarm generation
- Timer value reload (Auto-reload at alarm or software-controlled instant reload)

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000044_95ca1db65a5a242fc60be0f3b951123c340d83c2e85e03d70649daac66a5b9b2.png)

<!-- page_break -->

- Level interrupt generation

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Timer Group .

## 4.1.3.8 Watchdog Timers

ESP32-S3 contains three watchdog timers: one in each of the two timer groups (called Main System Watchdog Timers, or MWDT) and one in the RTC Module (called the RTC Watchdog Timer, or RWDT).

During the flash boot process, RWDT and the first MWDT are enabled automatically in order to detect and recover from booting errors.

## Feature List

- Four stages:
- -Each with a programmable timeout value
- -Each stage can be configured, enabled and disabled separately
- Upon expiry of each stage:
- -Interrupt, CPU reset, or core reset occurs for MWDT
- -Interrupt, CPU reset, core reset, or system reset occurs for RWDT
- 32-bit expiry counter
- Write protection, to prevent RWDT and MWDT configuration from being altered inadvertently
- Flash boot protection: If the boot process from an SPI flash does not complete within a predetermined period of time, the watchdog will reboot the entire main system

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Watchdog Timers .

## 4.1.3.9 XTAL32K Watchdog Timers

## Interrupt and Wake-Up

When the XTAL32K watchdog timer detects the oscillation failure of XTAL32K\_CLK, an oscillation failure interrupt RTC\_XTAL32K\_DEAD\_INT (for interrupt description, please refer to

ESP32-S3 Technical Reference Manual &gt; Chapter Low-power Management ) is generated. At this point, the CPU will be woken up if in Light-sleep mode or Deep-sleep mode.

## BACKUP32K\_CLK

Once the XTAL32K watchdog timer detects the oscillation failure of XTAL32K\_CLK, it replaces XTAL32K\_CLK with BACKUP32K\_CLK (with a frequency of 32 kHz or so) derived from RTC\_CLK as RTC's SLOW\_CLK, so as to ensure proper functioning of the system.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter XTAL32K Watchdog Timers .

## 4.1.3.10 Permission Control

In ESP32-S3, the Permission Control module is used to control access to the slaves (including internal memory, peripherals, external flash, and RAM). The host can access its slave only if it has the right permission. In this way, data and instructions are protected from illegitimate read or write.

<!-- page_break -->

The ESP32-S3 CPU can run in both Secure World and Non-secure World where independent permission controls are adopted. The Permission Control module is able to identify which World the host is running and then proceed with its normal operations.

## Feature List

- Manage access to internal memory by:
- -CPU
- -CPU trace module
- -GDMA
- Manage access to external flash and RAM by:
- -MMU
- -SPI1
- -GDMA
- -CPU through Cache
- Manage access to peripherals, supporting
- -independent permission control for each peripheral
- -monitoring non-aligned access
- -access control for customized address range
- Integrate permission lock register
- -All permission registers can be locked with the permission lock register. Once locked, the permission register and the lock register cannot be modified, unless the CPU is reset.
- Integrate permission monitor interrupt
- -In case of illegitimate access, the permission monitor interrupt will be triggered and the CPU will be informed to handle the interrupt.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Permission Control .

## 4.1.3.11 World Controller

ESP32-S3 can divide the hardware and software resources into a Secure World and a Non-Secure World to prevent sabotage or access to device information. Switching between the two worlds is performed by the World Controller.

## Feature List

- Control of the CPU switching between secure and non-secure worlds
- Control of 15 DMA peripherals switching between secure and non-secure worlds
- Record of CPU's world switching logs
- Shielding of the CPU's NMI interrupt

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000045_4f71e3d880c4910fa5b6ed97733b343ae8ac0a4af0ef8a195703ca8146586f16.png)

<!-- page_break -->

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter World Controller .

## 4.1.3.12 System Registers

ESP32-S3 system registers can be used to control the following peripheral blocks and core modules:

- System and memory
- Clock
- Software Interrupt
- Low-power management
- Peripheral clock gating and reset
- CPU Control

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter System Registers .

## 4.1.4 Cryptography and Security Component

This subsection describes the security features incorporated into the chip, which safeguard data and operations.

## 4.1.4.1 SHA Accelerator

ESP32-S3 integrates an SHA accelerator, which is a hardware device that speeds up SHA algorithm significantly.

## Feature List

- All the hash algorithms introduced in FIPS PUB 180-4 Spec.
- -SHA-1
- -SHA-224
- -SHA-256
- -SHA-384
- -SHA-512
- -SHA-512/224
- -SHA-512/256
- -SHA-512/ t
- Two working modes
- -Typical SHA
- -DMA-SHA
- interleaved function when working in Typical SHA working mode
- Interrupt function when working in DMA-SHA working mode

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter SHA Accelerator .

<!-- page_break -->

## 4.1.4.2 AES Accelerator

ESP32-S3 integrates an Advanced Encryption Standard (AES) Accelerator, which is a hardware device that speeds up AES algorithm significantly.

## Feature List

- Typical AES working mode
- -AES-128/AES-256 encryption and decryption
- DMA-AES working mode
- -AES-128/AES-256 encryption and decryption
- -Block cipher mode
* ECB (Electronic Codebook)
* CBC (Cipher Block Chaining)
* OFB (Output Feedback)
* CTR (Counter)
* CFB8 (8-bit Cipher Feedback)
* CFB128 (128-bit Cipher Feedback)
- -Interrupt on completion of computation

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter AES Accelerator .

## 4.1.4.3 RSA Accelerator

The RSA Accelerator provides hardware support for high precision computation used in various RSA asymmetric cipher algorithms.

## Feature List

- Large-number modular exponentiation with two optional acceleration options
- Large-number modular multiplication, up to 4096 bits
- Large-number multiplication, with operands up to 2048 bits
- Operands of different lengths
- Interrupt on completion of computation

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter RSA Accelerator .

## 4.1.4.4 Secure Boot

Secure Boot feature uses a hardware root of trust to ensure only signed firmware (with RSA-PSS signature) can be booted.

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000046_22af64093692101c4b05b6187ea08653e9076dbf74c137c142835f06069a08f8.png)

<!-- page_break -->

## 4.1.4.5 HMAC Accelerator

The Hash-based Message Authentication Code (HMAC) module computes Message Authentication Codes (MACs) using Hash algorithm and keys as described in RFC 2104.

## Feature List

- Standard HMAC-SHA-256 algorithm
- Hash result only accessible by configurable hardware peripheral (in downstream mode)
- Compatible to challenge-response authentication algorithm
- Generates required keys for the RSA Digital Signature Peripheral (RSA\_DS) (in downstream mode)
- Re-enables soft-disabled JTAG (in downstream mode)

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter HMAC Accelerator .

## 4.1.4.6 RSA Digital Signature Peripheral (RSA\_DS)

An RSA Digital Signature Peripheral (RSA\_DS) is used to verify the authenticity and integrity of a message using a cryptographic algorithm.

## Feature List

- RSA\_DS with key length up to 4096 bits
- Encrypted private key data, only decryptable by RSA\_DS
- SHA-256 digest to protect private key data against tampering by an attacker

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter RSA Digital Signature Peripheral (RSA\_DS) .

## 4.1.4.7 External Memory Encryption and Decryption

ESP32-S3 integrates an External Memory Encryption and Decryption module that complies with the XTS-AES standard.

## Feature List

- General XTS-AES algorithm, compliant with IEEE Std 1619-2007
- Software-based manual encryption
- High-speed auto encryption, without software's participation
- High-speed auto decryption, without software's participation
- Encryption and decryption functions jointly determined by registers configuration, eFuse parameters, and boot mode

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter External Memory Encryption and Decryption .

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000047_5457e5f5615ca9a08bb5bc4a18ae7e44a1642038721286cf5f53130c5c9fdf7d.png)

<!-- page_break -->

## 4.1.4.8 Clock Glitch Detection

The Clock Glitch Detection module on ESP32-S3 monitors input clock signals from XTAL\_CLK. If it detects a glitch with a width shorter than 3 ns, input clock signals from XTAL\_CLK are blocked.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Clock Glitch Detection .

## 4.1.4.9 Random Number Generator

The random number generator (RNG) in ESP32-S3 generates true random numbers, which means random number generated from a physical process, rather than by means of an algorithm. No number generated within the specified range is more or less likely to appear than any other number.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Random Number Generator .

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000048_21e5dd7e893b551deff9e24c5d44eb86f5bea3193c61c0dbcfb985f741cff711.png)

<!-- page_break -->

## 4.2 Peripherals

This section describes the chip's peripheral capabilities, covering connectivity interfaces and on-chip sensors that extend its functionality.

## 4.2.1 Connectivity Interface

This subsection describes the connectivity interfaces on the chip that enable communication and interaction with external devices and networks.

## 4.2.1.1 UART Controller

ESP32-S3 has three UART (Universal Asynchronous Receiver Transmitter) controllers, i.e., UART0, UART1, and UART2, which support IrDA and asynchronous communication (RS232 and RS485) at a speed of up to 5 Mbps.

## Feature List

- Three clock sources that can be divided
- Programmable baud rate
- 1024 x 8-bit RAM shared by TX FIFOs and RX FIFOs of the three UART controllers
- Full-duplex asynchronous communication
- Automatic baud rate detection of input signals
- Data bits ranging from 5 to 8
- Stop bits of 1, 1.5, 2, or 3 bits
- Parity bit
- Special character AT\_CMD detection
- RS485 protocol
- IrDA protocol
- High-speed data communication using GDMA
- UART as wake-up source
- Software and hardware flow control

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter UART Controller .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.1.2 I2C Interface

ESP32-S3 has two I2C bus interfaces which are used for I2C master mode or slave mode, depending on the user's configuration.

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000049_61ded0b6a11804f7c977a7f77cc7f63e58beb93a4d90d5334c5cd07af2ca5547.png)

<!-- page_break -->

## Feature List

- Standard mode (100 kbit/s)
- Fast mode (400 kbit/s)
- Up to 800 kbit/s (constrained by SCL and SDA pull-up strength)
- 7-bit and 10-bit addressing mode
- Double addressing mode (slave addressing and slave register addressing)

The hardware provides a command abstraction layer to simplify the usage of the I2C peripheral.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter I2C Controller .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.1.3 I2S Interface

ESP32-S3 includes two standard I2S interfaces. They can operate in master mode or slave mode, in full-duplex mode or half-duplex communication mode, and can be configured to operate with an 8-bit, 16-bit, 24-bit, or 32-bit resolution as an input or output channel. BCK clock frequency, from 10 kHz up to 40 MHz, is supported.

The I2S interface has a dedicated DMA controller. It supports TDM PCM, TDM MSB alignment, TDM LSB alignment, TDM Phillips, and PDM interface.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter I2S Controller .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.1.4 LCD and Camera Controller

The LCD and Camera controller of ESP32-S3 consists of a LCD module and a camera module.

The LCD module is designed to send parallel video data signals, and its bus supports 8-bit ~ 16-bit parallel RGB, I8080, and MOTO6800 interfaces. These interfaces operate at 40 MHz or lower, and support conversion among RGB565, YUV422, YUV420, and YUV411.

The camera module is designed to receive parallel video data signals, and its bus supports an 8-bit ~ 16-bit DVP image sensor, with clock frequency of up to 40 MHz. The camera interface supports conversion among RGB565, YUV422, YUV420, and YUV411.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter LCD and Camera Controller .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000050_da3bfe00cd097eb0b45a6e8e6618b7f0dfe8e504fe5e635bdbfc5ab43109a214.png)

<!-- page_break -->

## 4.2.1.5 Serial Peripheral Interface (SPI)

ESP32-S3 has the following SPI interfaces:

- SPI0 used by ESP32-S3's GDMA controller and cache to access in-package or off-package flash/PSRAM
- SPI1 used by the CPU to access in-package or off-package flash/PSRAM
- SPI2 is a general purpose SPI controller with access to a DMA channel allocated by the GDMA controller
- SPI3 is a general purpose SPI controller with access to a DMA channel allocated by the GDMA controller

## Feature List

- SPI0 and SPI1:
- -Supports Single SPI, Dual SPI, Quad SPI, Octal SPI, QPI, and OPI modes
- -8-line SPI mode supports single data rate (SDR) and double data rate (DDR)
- -Configurable clock frequency with a maximum of 120 MHz for 8-line SPI SDR/DDR modes
- -Data transmission is in bytes
- SPI2:
- -Supports operation as a master or slave
- -Connects to a DMA channel allocated by the GDMA controller
- -Supports Single SPI, Dual SPI, Quad SPI, Octal SPI, QPI, and OPI modes
- -Configurable clock polarity (CPOL) and phase (CPHA)
- -Configurable clock frequency
- -Data transmission is in bytes
- -Configurable read and write data bit order: most-significant bit (MSB) first, or least-significant bit (LSB) first
- -As a master
* Supports 2-line full-duplex communication with clock frequency up to 80 MHz
* Full-duplex 8-line SPI mode supports single data rate (SDR) only
* Supports 1-, 2-, 4-, 8-line half-duplex communication with clock frequency up to 80 MHz
* Half-duplex 8-line SPI mode supports both single data rate (up to 80 MHz) and double data rate (up to 40 MHz)
* Provides six SPI\_CS pins for connection with six independent SPI slaves
* Configurable CS setup time and hold time
- -As a slave
* Supports 2-line full-duplex communication with clock frequency up to 60 MHz
* Supports 1-, 2-, 4-line half-duplex communication with clock frequency up to 60 MHz
* Full-duplex and half-duplex 8-line SPI mode supports single data rate (SDR) only

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000051_12dfca081fba4b792ed20fc82f4e63d2c7b59e78161bf87237e5ba64d72e73e8.png)

<!-- page_break -->

- SPI3:
- -Supports operation as a master or slave
- -Connects to a DMA channel allocated by the GDMA controller
- -Supports Single SPI, Dual SPI, Quad SPI, and QPI modes
- -Configurable clock polarity (CPOL) and phase (CPHA)
- -Configurable clock frequency
- -Data transmission is in bytes
- -Configurable read and write data bit order: most-significant bit (MSB) first, or least-significant bit (LSB) first
- -As a master
* Supports 2-line full-duplex communication with clock frequency up to 80 MHz
* Supports 1-, 2-, 4-line half-duplex communication with clock frequency up to 80 MHz
* Provides three SPI\_CS pins for connection with three independent SPI slaves
* Configurable CS setup time and hold time
- -As a slave
* Supports 2-line full-duplex communication with clock frequency up to 60 MHz
* Supports 1-, 2-, 4-line half-duplex communication with clock frequency up to 60 MHz

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter SPI Controller .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.1.6 Two-Wire Automotive Interface (TWAI ® )

The Two-Wire Automotive Interface (TWAI ® ) is a multi-master, multi-cast communication protocol with error detection and signaling as well as inbuilt message priorities and arbitration.

## Feature List

- Compatible with ISO 11898-1 protocol (CAN Specification 2.0)
- Standard frame format (11-bit ID) and extended frame format (29-bit ID)
- Bit rates from 1 Kbit/s to 1 Mbit/s
- Multiple modes of operation:
- -Normal
- -Listen Only
- -Self-Test (no acknowledgment required)
- 64-byte receive FIFO

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000052_678a454763a836b88fe197fed89b64ca6f7f7e7aa8cc703d96d0bec07d7f3257.png)

<!-- page_break -->

- Acceptance filter (single and dual filter modes)
- Error detection and handling:
- -Error counters
- -Configurable error interrupt threshold
- -Error code capture
- -Arbitration lost capture

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Two-wire Automotive Interface .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.1.7 USB 2.0 OTG Full-Speed Interface

ESP32-S3 features a full-speed USB OTG interface along with an integrated transceiver. The USB OTG interface complies with the USB 2.0 specification.

## General Features

- FS and LS data rates
- HNP and SRP as A-device or B-device
- Dynamic FIFO (DFIFO) sizing
- Multiple modes of memory access
- -Scatter/Gather DMA mode
- -Buffer DMA mode
- -Slave mode
- Can choose integrated transceiver or external transceiver
- Utilizing integrated transceiver with USB Serial/JTAG by time-division multiplexing when only integrated transceiver is used
- Support USB OTG using one of the transceivers while USB Serial/JTAG using the other one when both integrated transceiver or external transceiver are used

## Device Mode Features

- Endpoint number 0 always present (bi-directional, consisting of EP0 IN and EP0 OUT)
- Six additional endpoints (endpoint numbers 1 to 6), configurable as IN or OUT
- Maximum of five IN endpoints concurrently active at any time (including EP0 IN)
- All OUT endpoints share a single RX FIFO
- Each IN endpoint has a dedicated TX FIFO

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000053_4de067715652b4617e35fcd391a99bd88e204745a3a49185c66233d6b8ee74f0.png)

<!-- page_break -->

## Host Mode Features

- Eight channels (pipes)
- -A control pipe consists of two channels (IN and OUT), as IN and OUT transactions must be handled separately. Only Control transfer type is supported.
- -Each of the other seven channels is dynamically configurable to be IN or OUT , and supports Bulk, Isochronous, and Interrupt transfer types.
- All channels share an RX FIFO, non-periodic TX FIFO, and periodic TX FIFO. The size of each FIFO is configurable.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter USB On-The-Go .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.1.8 USB Serial/JTAG Controller

ESP32-S3 integrates a USB Serial/JTAG controller.

## Feature List

- USB Full-speed device.
- Can be configured to either use internal USB PHY of ESP32-S3 or external PHY via GPIO matrix.
- Fixed function device, hardwired for CDC-ACM (Communication Device Class - Abstract Control Model) and JTAG adapter functionality.
- Two OUT Endpoints, three IN Endpoints in addition to Control Endpoint 0; Up to 64-byte data payload size.
- Internal PHY , so no or very few external components needed to connect to a host computer.
- CDC-ACM adherent serial port emulation is plug-and-play on most modern OSes.
- JTAG interface allows fast communication with CPU debug core using a compact representation of JTAG instructions.
- CDC-ACM supports host controllable chip reset and entry into download mode.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter USB Serial/JTAG Controller .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.1.9 SD/MMC Host Controller

ESP32-S3 has an SD/MMC Host controller.

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000054_e79d231ced96570608699cf359e91cf396a03d4bd3bf268f79aa1f98e6fa12d8.png)

<!-- page_break -->

## Feature List

- Secure Digital (SD) memory version 3.0 and version 3.01
- Secure Digital I/O (SDIO) version 3.0
- Consumer Electronics Advanced Transport Architecture (CE-ATA) version 1.1
- Multimedia Cards (MMC version 4.41, eMMC version 4.5 and version 4.51)
- Up to 80 MHz clock output
- Three data bus modes:
- -1-bit
- -4-bit (supports two SD/SDIO/MMC 4.41 cards, and one SD card operating at 1.8 V in 4-bit mode)
- -8-bit

## Note:

When working at 80 MHz, the clock phase adjustment is limited and only phase 0° and 180° are supported. The PCB layout should be optimized accordingly to ensure timing closure.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter SD/MMC Host Controller .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## Feature List

- Can generate a digital waveform with configurable periods and duty cycle. The duty cycle resolution can be up to 14 bits within a 1 ms period
- Multiple clock sources, including APB clock and external main crystal clock
- Can operate when the CPU is in Light-sleep mode
- Gradual increase or decrease of duty cycle, useful for the LED RGB color-fading generator

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter LED PWM Controller .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.1.10 Motor Control PWM (MCPWM)

ESP32-S3 integrates two MCPWMs that can be used to drive digital motors and smart light. Each MCPWM peripheral has one clock divider (prescaler), three PWM timers, three PWM operators, and a capture module. PWM timers are used for generating timing references. The PWM operators generate desired waveform based on the timing references. Any PWM operator can be configured to use the timing references of any PWM timers. Different PWM operators can use the same PWM timer's timing references to produce related PWM

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000055_3587cfb00720f30b3b564cafb866f9b9362ba431326ec9ba46356126133e10da.png)

<!-- page_break -->

signals. PWM operators can also use different PWM timers' values to produce the PWM signals that work alone. Different PWM timers can also be synchronized together.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Motor Control PWM .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.1.11 Remote Control Peripheral (RMT)

The Remote Control Peripheral (RMT) is designed to send and receive infrared remote control signals.

## Feature List

- Four TX channels
- Four RX channels
- Support multiple channels (programmable) transmitting data simultaneously
- Eight channels share a 384 x 32-bit RAM
- Support modulation on TX pulses
- Support filtering and demodulation on RX pulses
- Wrap TX mode
- Wrap RX mode
- Continuous TX mode
- DMA access for TX mode on channel 3
- DMA access for RX mode on channel 7

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Remote Control Peripheral .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.1.12 Pulse Count Controller (PCNT)

The pulse count controller (PCNT) captures pulse and counts pulse edges through multiple modes.

## Feature List

- Four independent pulse counters (units) that count from 1 to 65535
- Each unit consists of two independent channels sharing one pulse counter
- All channels have input pulse signals (e.g. sig\_ch0\_u n ) with their corresponding control signals (e.g. ctrl\_ch0\_u n )
- Independently filter glitches of input pulse signals (sig\_ch0\_u n and sig\_ch1\_u n ) and control signals (ctrl\_ch0\_u n and ctrl\_ch1\_u n ) on each unit

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000056_896757b8b52cac3d090f890fd5c3e48db92988f56850e283570ce20cb2e4b0f0.png)

<!-- page_break -->

- Each channel has the following parameters:
1. Selection between counting on positive or negative edges of the input pulse signal
2. Configuration to Increment, Decrement, or Disable counter mode for control signal's high and low states

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter Pulse Count Controller .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.2 Analog Signal Processing

This subsection describes components on the chip that sense and process real-world data.

## 4.2.2.1 SAR ADC

ESP32-S3 integrates two 12-bit SAR ADCs and supports measurements on 20 channels (analog-enabled pins). For power-saving purpose, the ULP coprocessors in ESP32-S3 can also be used to measure voltage in sleep modes. By using threshold settings or other methods, we can awaken the CPU from sleep modes.

## Note:

Please note that the ADC 2 \_CH… analog functions (see T able 2-8 Analog Functions ) cannot be used with Wi-Fi simultaneously.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter On-Chip Sensors and Analog Signal Processing .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

## 4.2.2.2 Temperature Sensor

The temperature sensor generates a voltage that varies with temperature. The voltage is internally converted via an ADC into a digital value.

The temperature sensor has a range of -40 °C to 125 °C. It is designed primarily to sense the temperature changes inside the chip. The temperature value depends on factors such as microcontroller clock frequency or I/O load. Generally, the chip's internal temperature is higher than the ambient temperature.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter On-Chip Sensors and Analog Signal Processing .

## 4.2.2.3 Touch Sensor

ESP32-S3 has 14 capacitive-sensing GPIOs, which detect variations induced by touching or approaching the GPIOs with a finger or other objects. The low-noise nature of the design and the high sensitivity of the circuit allow relatively small pads to be used. Arrays of pads can also be used, so that a larger area or more points

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000057_6c2ac244e53fddc9e71baa41717f31d2b01cd658874d7338aa7cfd45093711fc.png)

<!-- page_break -->

can be detected. The touch sensing performance can be further enhanced by the waterproof design and digital filtering feature.

## Note:

ESP32-S3 touch sensor has not passed the Conducted Susceptibility (CS) test for now, and thus has limited application scenarios.

For details, see ESP32-S3 Technical Reference Manual &gt; Chapter On-Chip Sensors and Analog Signal Processing .

## Pin Assignment

For details, see Section 2.3.5 Peripheral Pin Assignment .

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000058_c69821bde351371e584b15af66b30c5a9d274484ed100ca32a89996c5307fbbf.png)

<!-- page_break -->

## 4.3 Wireless Communication

This section describes the chip's wireless communication capabilities, spanning radio technology, Wi-Fi, Bluetooth, and 802.15.4.

## 4.3.1 Radio

This subsection describes the fundamental radio technology embedded in the chip that facilitates wireless communication and data exchange.

## 4.3.1.1 2.4 GHz Receiver

The 2.4 GHz receiver demodulates the 2.4 GHz RF signal to quadrature baseband signals and converts them to the digital domain with two high-resolution, high-speed ADCs. To adapt to varying signal channel conditions, ESP32-S3 integrates RF filters, Automatic Gain Control (AGC), DC offset cancelation circuits, and baseband filters.

## 4.3.1.2 2.4 GHz Transmitter

The 2.4 GHz transmitter modulates the quadrature baseband signals to the 2.4 GHz RF signal, and drives the antenna with a high-powered CMOS power amplifier. The use of digital calibration further improves the linearity of the power amplifier.

To compensate for receiver imperfections, additional calibration methods are built into the chip, including:

- Carrier leakage compensation
- I/Q amplitude/phase matching
- Baseband nonlinearities suppression
- RF nonlinearities suppression
- Antenna matching

These built-in calibration routines reduce the cost and time to the market for your product, and eliminate the need for specialized testing equipment.

## 4.3.1.3 Clock Generator

The clock generator produces quadrature clock signals of 2.4 GHz for both the receiver and the transmitter. All components of the clock generator are integrated into the chip, including inductors, varactors, filters, regulators, and dividers.

The clock generator has built-in calibration and self-test circuits. Quadrature clock phases and phase noise are optimized on chip with patented calibration algorithms which ensure the best performance of the receiver and the transmitter.

## 4.3.2 Wi-Fi

This subsection describes the chip's Wi-Fi capabilities, which facilitate wireless communication at a high data rate.

<!-- page_break -->

## 4.3.2.1 Wi-Fi Radio and Baseband

The ESP32-S3 Wi-Fi radio and baseband support the following features:

- 802.11b/g/n
- 802.11n MCS0-7 that supports 20 MHz and 40 MHz bandwidth
- 802.11n MCS32
- 802.11n 0.4 µ s guard-interval
- Data rate up to 150 Mbps
- RX STBC (single spatial stream)
- Adjustable transmitting power

· Antenna diversity: ESP32-S3 supports antenna diversity with an external RF switch. This switch is controlled by one or more GPIOs, and used to select the best antenna to minimize the effects of channel imperfections.

## 4.3.2.2 Wi-Fi MAC

ESP32-S3 implements the full 802.11b/g/n Wi-Fi MAC protocol. It supports the Basic Service Set (BSS) STA and SoftAP operations under the Distributed Control Function (DCF). Power management is handled automatically with minimal host interaction to minimize the active duty period.

The ESP32-S3 Wi-Fi MAC applies the following low-level protocol functions automatically:

- Four virtual Wi-Fi interfaces
- Simultaneous Infrastructure BSS Station mode, SoftAP mode, and Station + SoftAP mode
- RTS protection, CTS protection, Immediate Block ACK
- Fragmentation and defragmentation
- TX/RX A-MPDU, TX/RX A-MSDU
- TXOP
- WMM
- GCMP, CCMP, TKIP, WAPI, WEP, BIP, WPA2-PSK/WPA2-Enterprise, and WPA3-PSK/WPA3-Enterprise
- Automatic beacon monitoring (hardware TSF)
- 802.11mc FTM

## 4.3.2.3 Networking Features

Users are provided with libraries for TCP/IP networking, ESP-WIFI-MESH networking, and other networking protocols over Wi-Fi. TLS 1.2 support is also provided.

## 4.3.3 Bluetooth LE

This subsection describes the chip's Bluetooth capabilities, which facilitate wireless communication for low-power, short-range applications. ESP32-S3 includes a Bluetooth Low Energy subsystem that integrates a

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000059_3f908a2464718d757fce0fe02bfe20dc5c8239c5d6bc002f0348e2ca6a940d8d.png)

<!-- page_break -->

hardware link layer controller, an RF/modem block and a feature-rich software protocol stack. It supports the core features of Bluetooth 5 and Bluetooth Mesh.

## 4.3.3.1 Bluetooth LE PHY

Bluetooth Low Energy radio and PHY in ESP32-S3 support:

- 1 Mbps PHY
- 2 Mbps PHY for high transmission speed and high data throughput
- Coded PHY for high RX sensitivity and long range (125 Kbps and 500 Kbps)
- Class 1 transmit power without external PA
- HW Listen Before T alk (LBT)

## 4.3.3.2 Bluetooth LE Link Controller

Bluetooth Low Energy Link Layer Controller in ESP32-S3 supports:

- LE Advertising Extensions, to enhance broadcasting capacity and broadcast more intelligent data
- Multiple Advertising Sets
- Simultaneous Advertising and Scanning
- Multiple connections in simultaneous central and peripheral roles
- Adaptive Frequency Hopping (AFH) and Channel Assessment
- LE Channel Selection Algorithm #2
- Connection Parameter Update
- High Duty Cycle Non-Connectable Advertising
- LE Privacy v1.2
- LE Data Packet Length Extension
- Link Layer Extended Scanner Filter Policies
- Low Duty Cycle Directed Advertising
- Link Layer Encryption
- LE Ping

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000060_8aca9bcb31b28ce2fe305a4489175557dafea6fe89e7d2a6e7d9a940c063c00f.png)

<!-- page_break -->

## 5 Electrical Characteristics

## 5.1 Absolute Maximum Ratings

Stresses above those listed in T able 5-1 Absolute Maximum Ratings may cause permanent damage to the device. These are stress ratings only and normal operation of the device at these or any other conditions beyond those indicated in Section 5.2 Recommended Operating Conditions is not implied. Exposure to absolute-maximum-rated conditions for extended periods may affect device reliability.

Table 5-1. Absolute Maximum Ratings

| Parameter          | Description                  | Min   |    Max | Unit   |
|--------------------|------------------------------|-------|--------|--------|
| Input power pins 1 | Allowed input voltage        | - 0.3 |    3.6 | V      |
| I output 2         | Cumulative IO output current | -     | 1500   | mA     |
| T STORE            | Storage temperature          | - 40  |  150   | °C     |

## 5.2 Recommended Operating Conditions

For recommended ambient temperature, see Section 1 ESP32-S3 Series Comparison .

Table 5-2. Recommended Operating Conditions

| Parameter 1        | Description               |   Min | Typ   | Max   | Unit   |
|--------------------|---------------------------|-------|-------|-------|--------|
| VDDA, VDD3P3       | Recommended input voltage |   3   | 3.3   | 3.6   | V      |
| VDD3P3_RTC 2       | Recommended input voltage |   3   | 3.3   | 3.6   | V      |
| VDD_SPI (as input) | -                         |   1.8 | 3.3   | 3.6   | V      |
| VDD3P3_CPU 3       | Recommended input voltage |   3   | 3.3   | 3.6   | V      |
| I VDD 4            | Cumulative input current  |   0.5 | -     | -     | A      |

[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=5417&sections=&version=2.2)

<!-- page_break -->

## 5.3 VDD\_SPI Output Characteristics

Table 5-3. VDD\_SPI Internal and Output Characteristics

| Parameter   | Description 1                                                                           |   Typ | Unit   |
|-------------|-----------------------------------------------------------------------------------------|-------|--------|
| R SPI       | VDD_SPI powered by VDD3P3_RTC via R SPI for 3.3 V flash/PSRAM 2                         |    14 | Ω      |
| I SPI       | Output current when VDD_SPI is powered by Flash Voltage Regulator for 1.8 V flash/PSRAM |    40 | mA     |

- VDD\_flash\_min - minimum operating voltage of flash/PSRAM
- I\_flash\_max - maximum operating current of flash/PSRAM

## 5.4 DC Characteristics (3.3 V, 25 °C)

Table 5-4. DC Characteristics (3.3 V, 25 °C)

| Parameter   | Description                                                                | Min          | Typ   | Max          | Unit   |
|-------------|----------------------------------------------------------------------------|--------------|-------|--------------|--------|
| C IN        | Pin capacitance                                                            | -            | 2     | -            | pF     |
| V IH        | High-level input voltage                                                   | 0.75 × VDD 1 | -     | VDD 1 + 0.3  | V      |
| V IL        | Low-level input voltage                                                    | - 0.3        | -     | 0.25 × VDD 1 | V      |
| I IH        | High-level input current                                                   | -            | -     | 50           | nA     |
| I IL        | Low-level input current                                                    | -            | -     | 50           | nA     |
| V OH 2      | High-level output voltage                                                  | 0.8 × VDD 1  | -     | -            | V      |
| V OL 2      | Low-level output voltage                                                   | -            | -     | 0.1 × VDD 1  | V      |
| I OH        | High-level source current (VDD 1 = 3.3 V, V OH >= 2.64 V, PAD_DRIVER = 3)  | -            | 40    | -            | mA     |
| I OL        | Low-level sink current (VDD 1 = 3.3 V, V OL = 0.495 V, PAD_DRIVER = 3)     | -            | 28    | -            | mA     |
| R PU        | Internal weak pull-up resistor                                             | -            | 45    | -            | k Ω    |
| R PD        | Internal weak pull-down resistor                                           | -            | 45    | -            | k Ω    |
| V IH _ nRST | Chip reset release voltage (CHIP_PU voltage is within the specified range) | 0.75 × VDD 1 | -     | VDD 1 + 0.3  | V      |
| V IL _ nRST | Chip reset voltage (CHIP_PU voltage is within the specified range)         | - 0.3        | -     | 0.25 × VDD 1 | V      |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000061_684b2707ff4dab798924daff6f44f34e9dca2bb41e3c698a24f681f5a525771b.png)

<!-- page_break -->

## 5.5 ADC Characteristics

The measurements in this section are taken with an external 100 nF capacitor connected to the ADC, using DC signals as input, and at an ambient temperature of 25 °C with disabled Wi-Fi.

Table 5-5. ADC Characteristics

| Symbol                            | Min   |   Max | Unit   |
|-----------------------------------|-------|-------|--------|
| DNL (Differential nonlinearity) 1 | - 4   |     4 | LSB    |
| INL (Integral nonlinearity)       | - 8   |     8 | LSB    |
| Sampling rate                     | -     |   100 | kSPS 2 |

The calibrated ADC results after hardware calibration and software calibration are shown in T able 5-6. For higher accuracy, you may implement your own calibration methods.

Table 5-6. ADC Calibration Results

| Parameter   | Description                                     | Min   |   Max | Unit   |
|-------------|-------------------------------------------------|-------|-------|--------|
| Total error | ATTEN0, effective measurement range of 0 ~ 850  | - 5   |     5 | mV     |
| Total error | ATTEN1, effective measurement range of 0 ~ 1100 | - 6   |     6 | mV     |
| Total error | ATTEN2, effective measurement range of 0 ~ 1600 | - 10  |    10 | mV     |
| Total error | ATTEN3, effective measurement range of 0 ~ 2900 | - 50  |    50 | mV     |

## 5.6 Current Consumption

## 5.6.1 Current Consumption in Active Mode

The current consumption measurements are taken with a 3.3 V supply at 25 °C ambient temperature.

TX current consumption is rated at a 100% duty cycle.

RX current consumption is rated when the peripherals are disabled and the CPU idle.

Table 5-7. Current Consumption for Wi-Fi (2.4 GHz) in Active Mode

| Work Mode           | RF Condition   | Description                    |   Peak (mA) |
|---------------------|----------------|--------------------------------|-------------|
| Active (RF working) | TX             | 802.11b, 1 Mbps, @21 dBm       |         340 |
| Active (RF working) | TX             | 802.11g, 54 Mbps, @19 dBm      |         291 |
| Active (RF working) | TX             | 802.11n, HT20, MCS7, @18.5 dBm |         283 |
| Active (RF working) | TX             | 802.11n, HT40, MCS7, @18 dBm   |         286 |
| Active (RF working) | RX             | 802.11b/g/n, HT20              |          88 |
| Active (RF working) | RX             | 802.11n, HT40                  |          91 |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000062_d6812c93c9f0b20f9defb3bedc41a3aa91aaef1be6ba455622a6f55bda9a2bf6.png)

<!-- page_break -->

Table 5-8. Current Consumption for Bluetooth LE in Active Mode

| Work Mode           | RF Condition   | Description               |   Peak (mA) |
|---------------------|----------------|---------------------------|-------------|
| Active (RF working) | TX             | Bluetooth LE @ 21.0 dBm   |         335 |
| Active (RF working) | TX             | Bluetooth LE @ 9.0 dBm    |         193 |
| Active (RF working) | TX             | Bluetooth LE @ 0 dBm      |         176 |
| Active (RF working) | TX             | Bluetooth LE @ - 15.0 dBm |         116 |
| Active (RF working) | RX             | Bluetooth LE              |          93 |

## 5.6.2 Current Consumption in Other Modes

The measurements below are applicable to ESP32-S3 and ESP32-S3FH8. Since ESP32-S3R2, ESP32-S3RH2, ESP32-S3R8, ESP32-S3R8V, ESP32-S3R16V, and ESP32-S3FN4R2 are embedded with PSRAM, their current consumption might be higher.

Table 5-9. Current Consumption in Modem-sleep Mode

| Work mode     |   Frequency (MHz) | Description                                                                        | Typ 1 (mA)   | Typ 2 (mA)   |
|---------------|-------------------|------------------------------------------------------------------------------------|--------------|--------------|
| Modem-sleep 3 |                40 | WAITI (Dual core in idle state)                                                    | 13.2         | 18.8         |
| Modem-sleep 3 |                40 | Single core running 32-bit data access instructions, the other core in idle state  | 16.2         | 21.8         |
| Modem-sleep 3 |                40 | Dual core running 32-bit data access instructions                                  | 18.7         | 24.4         |
| Modem-sleep 3 |                40 | Single core running 128-bit data access instructions, the other core in idle state | 19.9         | 25.4         |
| Modem-sleep 3 |                40 | Dual core running 128-bit data access instructions                                 | 23.0         | 28.8         |
| Modem-sleep 3 |                   | WAITI                                                                              | 22.0         | 36.1         |
| Modem-sleep 3 |                   | Single core running 32-bit data access instructions, the other core in idle state  | 28.4         | 42.6         |
| Modem-sleep 3 |                80 | Dual core running 32-bit data access instructions                                  | 33.1         | 47 .3        |
| Modem-sleep 3 |                   | Single core running 128-bit data access instructions, the other core in idle state | 35.1         | 49.6         |
| Modem-sleep 3 |                   | Dual core running 128-bit data access instructions                                 | 41.8         | 56.3         |
| Modem-sleep 3 |               160 | WAITI                                                                              | 27 .6        | 42.3         |
| Modem-sleep 3 |               160 | Single core running 32-bit data access instructions, the other core in idle state  | 39.9         | 54.6         |
| Modem-sleep 3 |               160 | Dual core running 32-bit data access instructions                                  | 49.6         | 64.1         |
| Modem-sleep 3 |               160 | Single core running 128-bit data access instructions, the other core in idle state | 54.4         | 69.2         |
| Modem-sleep 3 |               160 | Dual core running 128-bit data access instructions                                 | 66.7         | 81.1         |
| Modem-sleep 3 |               240 | WAITI                                                                              | 32.9         | 47 .6        |
| Modem-sleep 3 |               240 | Single core running 32-bit data access instructions, the other core in idle state  | 51.2         | 65.9         |
| Modem-sleep 3 |               240 | Dual core running 32-bit data access instructions                                  | 66.2         | 81.3         |
| Modem-sleep 3 |               240 | Single core running 128-bit data access instructions, the other core in idle state | 72.4         | 87 .9        |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000063_7b6813897047f9232e69c98777bdfdd8bae98a0ca5facf2404e9ad4f1e835fb4.png)

<!-- page_break -->

Table 5-9 - cont'd from previous page

| Work mode   | Frequency (MHz)   | Description                                        |   Typ 1 (mA) | Typ 2 (mA)   |
|-------------|-------------------|----------------------------------------------------|--------------|--------------|
|             |                   | Dual core running 128-bit data access instructions |         91.7 | 107 .9       |

Table 5-10. Current Consumption in Low-Power Modes

| Work mode     | Description                                                           |   Typ ( µ A) |
|---------------|-----------------------------------------------------------------------|--------------|
| Light-sleep 1 | VDD_SPI and Wi-Fi are powered down, and all GPIOs are high-impedance. |          240 |
| Deep-sleep    | The ULP co-processor ULP-FSM                                          |          170 |
| Deep-sleep    | is powered on 2 ULP-RISC-V                                            |          190 |
| Deep-sleep    | ULP sensor-monitored pattern 3                                        |           18 |
| Deep-sleep    | RTC memory and RTC peripherals are powered up.                        |            8 |
| Deep-sleep    | RTC memory is powered up. RTC peripherals are powered down.           |            7 |
| Power off     | CHIP_PU is set to low level. The chip is shut down.                   |            1 |

## 5.7 Memory Specifications

The data below is sourced from the memory vendor datasheet. These values are guaranteed through design and/or characterization but are not fully tested in production. Devices are shipped with the memory erased.

Table 5-11. Flash Specifications

| Parameter   | Description                  | Min     | Typ   | Max   | Unit   |
|-------------|------------------------------|---------|-------|-------|--------|
| VCC         | Power supply voltage (1.8 V) | 1.65    | 1.80  | 2.00  | V      |
| VCC         | Power supply voltage (3.3 V) | 2.7     | 3.3   | 3.6   | V      |
| F C         | Maximum clock frequency      | 80      | -     | -     | MHz    |
| -           | Program/erase cycles         | 100,000 | -     | -     | cycles |
| T RET       | Data retention time          | 20      | -     | -     | years  |
| T PP        | Page program time            | -       | 0.8   | 5     | ms     |
| T SE        | Sector erase time (4 KB)     | -       | 70    | 500   | ms     |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000064_3e2d495f692ae84e8b27bee06ce921580c05ba476aee7cc5ef90f0bea97799c2.png)

<!-- page_break -->

Table 5-11 - cont'd from previous page

| Parameter   | Description              | Min   |   Typ |   Max | Unit   |
|-------------|--------------------------|-------|-------|-------|--------|
| T BE 1      | Block erase time (32 KB) | -     |   0.2 |     2 | s      |
| T BE 2      | Block erase time (64 KB) | -     |   0.3 |     3 | s      |
| T CE        | Chip erase time (16 Mb)  | -     |   7   |    20 | s      |
| T CE        | Chip erase time (32 Mb)  | -     |  20   |    60 | s      |
| T CE        | Chip erase time (64 Mb)  | -     |  25   |   100 | s      |
| T CE        | Chip erase time (128 Mb) | -     |  60   |   200 | s      |
| T CE        | Chip erase time (256 Mb) | -     |  70   |   300 | s      |

Table 5-12. PSRAM Specifications

| Parameter   | Description                  |   Min | Typ   | Max   | Unit   |
|-------------|------------------------------|-------|-------|-------|--------|
| VCC         | Power supply voltage (1.8 V) |  1.62 | 1.80  | 1.98  | V      |
| VCC         | Power supply voltage (3.3 V) |  2.7  | 3.3   | 3.6   | V      |
| F C         | Maximum clock frequency      | 80    | -     | -     | MHz    |

## 5.8 Reliability

Table 5-13. Reliability Qualifications

| Test Item                                        | Test Conditions                                                                                                               | Test Standard                   |
|--------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| HTOL (High Temperature Operating Life)           | 125 °C, 1000 hours                                                                                                            | JESD22-A108                     |
| ESD (Electro-Static Discharge Sensitivity)       | HBM (Human Body Mode) 1 ± 2000 V                                                                                              | JS-001                          |
| ESD (Electro-Static Discharge Sensitivity)       | CDM (Charge Device Mode) 2 ± 1000 V                                                                                           | JS-002                          |
| Latch up                                         | Current trigger ± 200 mA                                                                                                      | JESD78                          |
| Latch up                                         | Voltage trigger 1.5 × VDD max                                                                                                 | JESD78                          |
| Preconditioning                                  | Bake 24 hours @125 °C Moisture soak (level 3: 192 hours @30 °C, 60% RH) IR reflow solder: 260 + 0 °C, 20 seconds, three times | J-STD-020, JESD47 , JESD22-A113 |
| TCT (Temperature Cycling Test)                   | - 65 °C / 150 °C, 500 cycles                                                                                                  | JESD22-A104                     |
| uHAST (Highly Accelerated Stress Test, unbiased) | 130 °C, 85% RH, 96 hours                                                                                                      | JESD22-A118                     |
| HTSL (High Temperature Storage Life)             | 150 °C, 1000 hours                                                                                                            | JESD22-A103                     |
| LTSL (Low Temperature Storage Life)              | - 40 °C, 1000 hours                                                                                                           | JESD22-A119                     |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000065_4675d3c2bc021d3ce870027b7e441635a0a94f8c5781f5c499abbd1ee7c50436.png)

<!-- page_break -->

## 6 RF Characteristics

This section contains tables with RF characteristics of the Espressif product.

The RF data is measured at the antenna port, where RF cable is connected, including the front-end loss. The front-end circuit is a 0 Ω resistor.

Devices should operate in the center frequency range allocated by regional regulatory authorities. The target center frequency range and the target transmit power are configurable by software. See ESP RF Test Tool and Test Guide for instructions.

Unless otherwise stated, the RF tests are conducted with a 3.3 V (±5%) supply at 25 ºC ambient temperature.

## 6.1 Wi-Fi Radio

Table 6-1. Wi-Fi RF Characteristics

| Name                                        | Description      |
|---------------------------------------------|------------------|
| Center frequency range of operating channel | 2412 ~ 2484 MHz  |
| Wi-Fi wireless standard                     | IEEE 802.11b/g/n |

## 6.1.1 Wi-Fi RF Transmitter (TX) Characteristics

Table 6-2. TX Power with Spectral Mask and EVM Meeting 802.11 Standards

| Rate                | Min (dBm)   |   Typ (dBm) | Max (dBm)   |
|---------------------|-------------|-------------|-------------|
| 802.11b, 1 Mbps     | -           |        21   | -           |
| 802.11b, 11 Mbps    | -           |        21   | -           |
| 802.11g, 6 Mbps     | -           |        20.5 | -           |
| 802.11g, 54 Mbps    | -           |        19   | -           |
| 802.11n, HT20, MCS0 | -           |        19.5 | -           |
| 802.11n, HT20, MCS7 | -           |        18.5 | -           |
| 802.11n, HT40, MCS0 | -           |        19.5 | -           |
| 802.11n, HT40, MCS7 | -           |        18   | -           |

Table 6-3. TX EVM Test 1

| Rate                       | Min (dB)   | Typ (dB)   | Limit (dB)   |
|----------------------------|------------|------------|--------------|
| 802.11b, 1 Mbps, @21 dBm   | -          | - 24.5     | - 10         |
| 802.11b, 11 Mbps, @21 dBm  | -          | - 24.5     | - 10         |
| 802.11g, 6 Mbps, @20.5 dBm | -          | - 21.5     | - 5          |
| 802.11g, 54 Mbps, @19 dBm  | -          | - 28.0     | - 25         |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000066_d13072fb8abe816edbdf0014b8df5b50900713fc4f4c00cf492384f81c283ae0.png)

<!-- page_break -->

Table 6-3 - cont'd from previous page

| Rate                           | Min (dB)   | Typ (dB)   | Limit (dB)   |
|--------------------------------|------------|------------|--------------|
| 802.11n, HT20, MCS0, @19.5 dBm | -          | - 23.0     | - 5          |
| 802.11n, HT20, MCS7, @18.5 dBm | -          | - 29.5     | - 27         |
| 802.11n, HT40, MCS0, @19.5 dBm | -          | - 23.0     | - 5          |
| 802.11n, HT40, MCS7, @18 dBm   | -          | - 29.5     | - 27         |

## 6.1.2 Wi-Fi RF Receiver (RX) Characteristics

For RX tests, the PER (packet error rate) limit is 8% for 802.11b, and 10% for 802.11g/n.

Table 6-4. RX Sensitivity

| Rate                | Min (dBm)   | Typ (dBm)   | Max (dBm)   |
|---------------------|-------------|-------------|-------------|
| 802.11b, 1 Mbps     | -           | - 98.4      | -           |
| 802.11b, 2 Mbps     | -           | - 95.4      | -           |
| 802.11b, 5.5 Mbps   | -           | - 93.0      | -           |
| 802.11b, 11 Mbps    | -           | - 88.6      | -           |
| 802.11g, 6 Mbps     | -           | - 93.2      | -           |
| 802.11g, 9 Mbps     | -           | - 91.8      | -           |
| 802.11g, 12 Mbps    | -           | - 91.2      | -           |
| 802.11g, 18 Mbps    | -           | - 88.6      | -           |
| 802.11g, 24 Mbps    | -           | - 86.0      | -           |
| 802.11g, 36 Mbps    | -           | - 82.4      | -           |
| 802.11g, 48 Mbps    | -           | - 78.2      | -           |
| 802.11g, 54 Mbps    | -           | - 76.5      | -           |
| 802.11n, HT20, MCS0 | -           | - 92.6      | -           |
| 802.11n, HT20, MCS1 | -           | - 91.0      | -           |
| 802.11n, HT20, MCS2 | -           | - 88.2      | -           |
| 802.11n, HT20, MCS3 | -           | - 85.0      | -           |
| 802.11n, HT20, MCS4 | -           | - 81.8      | -           |
| 802.11n, HT20, MCS5 | -           | - 77 .4     | -           |
| 802.11n, HT20, MCS6 | -           | - 75.8      | -           |
| 802.11n, HT20, MCS7 | -           | - 74.2      | -           |
| 802.11n, HT40, MCS0 | -           | - 90.0      | -           |
| 802.11n, HT40, MCS1 | -           | - 88.0      | -           |
| 802.11n, HT40, MCS2 | -           | - 85.2      | -           |
| 802.11n, HT40, MCS3 | -           | - 82.0      | -           |
| 802.11n, HT40, MCS4 | -           | - 79.0      | -           |
| 802.11n, HT40, MCS5 | -           | - 74.4      | -           |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000067_88dd4701bc44451801e6ee4405c488b39b33eb5d1a20f57d1ece25890cd51244.png)

<!-- page_break -->

Table 6-4 - cont'd from previous page

| Rate                | Min (dBm)   | Typ (dBm)   | Max (dBm)   |
|---------------------|-------------|-------------|-------------|
| 802.11n, HT40, MCS6 | -           | - 72.8      | -           |
| 802.11n, HT40, MCS7 | -           | - 71.4      | -           |

Table 6-5. Maximum RX Level

| Rate                | Min (dBm)   |   Typ (dBm) | Max (dBm)   |
|---------------------|-------------|-------------|-------------|
| 802.11b, 1 Mbps     | -           |           5 | -           |
| 802.11b, 11 Mbps    | -           |           5 | -           |
| 802.11g, 6 Mbps     | -           |           5 | -           |
| 802.11g, 54 Mbps    | -           |           0 | -           |
| 802.11n, HT20, MCS0 | -           |           5 | -           |
| 802.11n, HT20, MCS7 | -           |           0 | -           |
| 802.11n, HT40, MCS0 | -           |           5 | -           |
| 802.11n, HT40, MCS7 | -           |           0 | -           |

Table 6-6. RX Adjacent Channel Rejection

| Rate                | Min (dB)   |   Typ (dB) | Max (dB)   |
|---------------------|------------|------------|------------|
| 802.11b, 1 Mbps     | -          |         35 | -          |
| 802.11b, 11 Mbps    | -          |         35 | -          |
| 802.11g, 6 Mbps     | -          |         31 | -          |
| 802.11g, 54 Mbps    | -          |         20 | -          |
| 802.11n, HT20, MCS0 | -          |         31 | -          |
| 802.11n, HT20, MCS7 | -          |         16 | -          |
| 802.11n, HT40, MCS0 | -          |         25 | -          |
| 802.11n, HT40, MCS7 | -          |         11 | -          |

## 6.2 Bluetooth LE Radio

Table 6-7. Bluetooth LE Frequency

| Parameter                             |   Min (MHz) | Typ (MHz)   |   Max (MHz) |
|---------------------------------------|-------------|-------------|-------------|
| Center frequency of operating channel |        2402 | -           |        2480 |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000068_218dcf52e78f4b067fe9d9c4355d38d9a63a02a59a399c60d41f41b19e268090.png)

<!-- page_break -->

## 6.2.1 Bluetooth LE RF Transmitter (TX) Characteristics

Table 6-8. Transmitter Characteristics - Bluetooth LE 1 Mbps

| Parameter                          | Description                                          | Min     | Typ      | Max   | Unit   |
|------------------------------------|------------------------------------------------------|---------|----------|-------|--------|
| RF transmit power                  | RF power control range                               | - 24.00 | 0        | 20.00 | dBm    |
| RF transmit power                  | Gain control step                                    | -       | 3.00     | -     | dB     |
| Carrier frequency offset and drift | Max &#124; f n &#124; n =0 , 1 , 2 , ..k             | -       | 2.50     | -     | kHz    |
| Carrier frequency offset and drift | Max &#124; f 0 - f n &#124;                          | -       | 2.00     | -     | kHz    |
| Carrier frequency offset and drift | Max &#124; f n - f n - 5 &#124;                      | -       | 1.39     | -     | kHz    |
| Carrier frequency offset and drift | &#124; f 1 - f 0 &#124;                              | -       | 0.80     | -     | kHz    |
| Modulation characteristics         | ∆ f 1 avg                                            | -       | 249.00   | -     | kHz    |
| Modulation characteristics         | Min ∆ f 2 max (for at least 99.9% of all ∆ f 2 max ) | -       | 198.00   | -     | kHz    |
| Modulation characteristics         | ∆ f 2 avg / ∆ f 1 avg                                | -       | 0.86     | -     | -      |
| In-band spurious emissions         | ±2 MHz offset                                        | -       | - 37 .00 | -     | dBm    |
| In-band spurious emissions         | ±3 MHz offset                                        | -       | - 42.00  | -     | dBm    |
| In-band spurious emissions         | >±3 MHz offset                                       | -       | - 44.00  | -     | dBm    |

Table 6-9. Transmitter Characteristics - Bluetooth LE 2 Mbps

| Parameter                          | Description                                          | Min     | Typ      | Max   | Unit   |
|------------------------------------|------------------------------------------------------|---------|----------|-------|--------|
| RF transmit power                  | RF power control range                               | - 24.00 | 0        | 20.00 | dBm    |
| RF transmit power                  | Gain control step                                    | -       | 3.00     | -     | dB     |
| Carrier frequency offset and drift | Max &#124; f n &#124; n =0 , 1 , 2 , ..k             | -       | 2.50     | -     | kHz    |
| Carrier frequency offset and drift | Max &#124; f 0 - f n &#124;                          | -       | 1.90     | -     | kHz    |
| Carrier frequency offset and drift | Max &#124; f n - f n - 5 &#124;                      | -       | 1.40     | -     | kHz    |
| Carrier frequency offset and drift | &#124; f 1 - f 0 &#124;                              | -       | 1.10     | -     | kHz    |
| Modulation characteristics         | ∆ f 1 avg                                            | -       | 499.00   | -     | kHz    |
| Modulation characteristics         | Min ∆ f 2 max (for at least 99.9% of all ∆ f 2 max ) | -       | 416.00   | -     | kHz    |
| Modulation characteristics         | ∆ f 2 avg / ∆ f 1 avg                                | -       | 0.89     | -     | -      |
| In-band spurious emissions         | ±4 MHz offset                                        | -       | - 43.80  | -     | dBm    |
| In-band spurious emissions         | ±5 MHz offset                                        | -       | - 45.80  | -     | dBm    |
| In-band spurious emissions         | >±5 MHz offset                                       | -       | - 47 .00 | -     | dBm    |

Table 6-10. Transmitter Characteristics - Bluetooth LE 125 Kbps

| Parameter                          | Description                              | Min     |   Typ | Max   | Unit   |
|------------------------------------|------------------------------------------|---------|-------|-------|--------|
| RF transmit power                  | RF power control range                   | - 24.00 |  0    | 20.00 | dBm    |
| RF transmit power                  | Gain control step                        | -       |  3    | -     | dB     |
| Carrier frequency offset and drift | Max &#124; f n &#124; n =0 , 1 , 2 , ..k | -       |  0.8  | -     | kHz    |
| Carrier frequency offset and drift | Max &#124; f 0 - f n &#124;              | -       |  0.98 | -     | kHz    |
| Carrier frequency offset and drift | &#124; f n - f n - 3 &#124;              | -       |  0.3  | -     | kHz    |
| Carrier frequency offset and drift | &#124; f 0 - f 3 &#124;                  | -       |  1    | -     | kHz    |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000069_262e5f197bd16fb92ca3cdfbca5e27cbb67f727cbca2146ce594e776f744b4e6.png)

<!-- page_break -->

Table 6-10 - cont'd from previous page

| Parameter                  | Description                                          | Min   | Typ      | Max   | Unit   |
|----------------------------|------------------------------------------------------|-------|----------|-------|--------|
| Modulation characteristics | ∆ f 1 avg                                            | -     | 248.00   | -     | kHz    |
| Modulation characteristics | Min ∆ f 1 max (for at least 99.9% of all ∆ f 1 max ) | -     | 222.00   | -     | kHz    |
| In-band spurious emissions | ±2 MHz offset                                        | -     | - 37 .00 | -     | dBm    |
| In-band spurious emissions | ±3 MHz offset                                        | -     | - 42.00  | -     | dBm    |
| In-band spurious emissions | >±3 MHz offset                                       | -     | - 44.00  | -     | dBm    |

Table 6-11. Transmitter Characteristics - Bluetooth LE 500 Kbps

| Parameter                          | Description                                          | Min     | Typ      | Max   | Unit   |
|------------------------------------|------------------------------------------------------|---------|----------|-------|--------|
| RF transmit power                  | RF power control range                               | - 24.00 | 0        | 20.00 | dBm    |
| RF transmit power                  | Gain control step                                    | -       | 3.00     | -     | dB     |
| Carrier frequency offset and drift | Max &#124; f n &#124; n =0 , 1 , 2 , ..k             | -       | 0.70     | -     | kHz    |
| Carrier frequency offset and drift | Max &#124; f 0 - f n &#124;                          | -       | 0.90     | -     | kHz    |
| Carrier frequency offset and drift | &#124; f n - f n - 3 &#124;                          | -       | 0.85     | -     | kHz    |
| Carrier frequency offset and drift | &#124; f 0 - f 3 &#124;                              | -       | 0.34     | -     | kHz    |
| Modulation characteristics         | ∆ f 2 avg                                            | -       | 213.00   | -     | kHz    |
| Modulation characteristics         | Min ∆ f 2 max (for at least 99.9% of all ∆ f 2 max ) | -       | 196.00   | -     | kHz    |
| In-band spurious emissions         | ±2 MHz offset                                        | -       | - 37 .00 | -     | dBm    |
| In-band spurious emissions         | ±3 MHz offset                                        | -       | - 42.00  | -     | dBm    |
| In-band spurious emissions         | >±3 MHz offset                                       | -       | - 44.00  | -     | dBm    |

## 6.2.2 Bluetooth LE RF Receiver (RX) Characteristics

Table 6-12. Receiver Characteristics - Bluetooth LE 1 Mbps

| Parameter                           | Description         | Min   | Typ     | Max   | Unit   |
|-------------------------------------|---------------------|-------|---------|-------|--------|
| Sensitivity @30.8% PER              | -                   | -     | - 97 .5 | -     | dBm    |
| Maximum received signal @30.8% PER  | -                   | -     | 8       | -     | dBm    |
| Co-channel C/I                      | F = F0 MHz          | -     | 9       | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 + 1 MHz      | -     | - 3     | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 - 1 MHz      | -     | - 3     | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 + 2 MHz      | -     | - 28    | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 - 2 MHz      | -     | - 30    | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 + 3 MHz      | -     | - 31    | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 - 3 MHz      | -     | - 33    | -     | dB     |
| Adjacent channel selectivity C/I    | F > F0 + 3 MHz      | -     | - 32    | -     | dB     |
| Adjacent channel selectivity C/I    | F > F0 - 3 MHz      | -     | - 36    | -     | dB     |
| Image frequency                     | -                   | -     | - 32    | -     | dB     |
| Adjacent channel to image frequency | F = F image + 1 MHz | -     | - 39    | -     | dB     |
| Adjacent channel to image frequency | F = F image - 1 MHz | -     | - 31    | -     | dB     |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000070_c6f4e6a8f04978269c248ab243008f9f842adda520518365364734aa87b1fe3f.png)

<!-- page_break -->

Table 6-12 - cont'd from previous page

| Parameter                        | Description          | Min   | Typ   | Max   | Unit   |
|----------------------------------|----------------------|-------|-------|-------|--------|
| Out-of-band blocking performance | 30 MHz ~ 2000 MHz    | -     | - 9   | -     | dBm    |
| Out-of-band blocking performance | 2003 MHz ~ 2399 MHz  | -     | - 19  | -     | dBm    |
| Out-of-band blocking performance | 2484 MHz ~ 2997 MHz  | -     | - 16  | -     | dBm    |
| Out-of-band blocking performance | 3000 MHz ~ 12.75 GHz | -     | - 5   | -     | dBm    |
| Intermodulation                  | -                    | -     | - 31  | -     | dBm    |

Table 6-13. Receiver Characteristics - Bluetooth LE 2 Mbps

| Parameter                           | Description          | Min   | Typ    | Max   | Unit   |
|-------------------------------------|----------------------|-------|--------|-------|--------|
| Sensitivity @30.8% PER              | -                    | -     | - 93.5 | -     | dBm    |
| Maximum received signal @30.8% PER  | -                    | -     | 3      | -     | dBm    |
| Co-channel C/I                      | F = F0 MHz           | -     | 10     | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 + 2 MHz       | -     | - 8    | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 - 2 MHz       | -     | - 5    | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 + 4 MHz       | -     | - 31   | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 - 4 MHz       | -     | - 33   | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 + 6 MHz       | -     | - 37   | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 - 6 MHz       | -     | - 37   | -     | dB     |
| Adjacent channel selectivity C/I    | F > F0 + 6 MHz       | -     | - 40   | -     | dB     |
| Adjacent channel selectivity C/I    | F > F0 - 6 MHz       | -     | - 40   | -     | dB     |
| Image frequency                     | -                    | -     | - 31   | -     | dB     |
| Adjacent channel to image frequency | F = F image + 2 MHz  | -     | - 37   | -     | dB     |
| Adjacent channel to image frequency | F = F image - 2 MHz  | -     | - 8    | -     | dB     |
| Out-of-band blocking performance    | 30 MHz ~ 2000 MHz    | -     | - 16   | -     | dBm    |
| Out-of-band blocking performance    | 2003 MHz ~ 2399 MHz  | -     | - 20   | -     | dBm    |
| Out-of-band blocking performance    | 2484 MHz ~ 2997 MHz  | -     | - 16   | -     | dBm    |
| Out-of-band blocking performance    | 3000 MHz ~ 12.75 GHz | -     | - 16   | -     | dBm    |
| Intermodulation                     | -                    | -     | - 30   | -     | dBm    |

Table 6-14. Receiver Characteristics - Bluetooth LE 125 Kbps

| Parameter                          | Description    | Min   | Typ     | Max   | Unit   |
|------------------------------------|----------------|-------|---------|-------|--------|
| Sensitivity @30.8% PER             | -              | -     | - 104.5 | -     | dBm    |
| Maximum received signal @30.8% PER | -              | -     | 8       | -     | dBm    |
| Co-channel C/I                     | F = F0 MHz     | -     | 6       | -     | dB     |
| Adjacent channel selectivity C/I   | F = F0 + 1 MHz | -     | - 6     | -     | dB     |
| Adjacent channel selectivity C/I   | F = F0 - 1 MHz | -     | - 5     | -     | dB     |
| Adjacent channel selectivity C/I   | F = F0 + 2 MHz | -     | - 32    | -     | dB     |
| Adjacent channel selectivity C/I   | F = F0 - 2 MHz | -     | - 39    | -     | dB     |
| Adjacent channel selectivity C/I   | F = F0 + 3 MHz | -     | - 35    | -     | dB     |
| Adjacent channel selectivity C/I   | F = F0 - 3 MHz | -     | - 45    | -     | dB     |
| Adjacent channel selectivity C/I   | F > F0 + 3 MHz | -     | - 35    | -     | dB     |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000071_011f5ddadc809e86165684d05448a58d2bd9c370091336bb33e5b07f4f426c5d.png)

<!-- page_break -->

Table 6-14 - cont'd from previous page

| Parameter                           | Description         | Min   | Typ   | Max   | Unit   |
|-------------------------------------|---------------------|-------|-------|-------|--------|
|                                     | F > F0 - 3 MHz      | -     | - 48  | -     | dB     |
| Image frequency                     | -                   | -     | - 35  | -     | dB     |
| Adjacent channel to image frequency | F = F image + 1 MHz | -     | - 49  | -     | dB     |
| Adjacent channel to image frequency | F = F image - 1 MHz | -     | - 32  | -     | dB     |

Table 6-15. Receiver Characteristics - Bluetooth LE 500 Kbps

| Parameter                           | Description         | Min   | Typ   | Max   | Unit   |
|-------------------------------------|---------------------|-------|-------|-------|--------|
| Sensitivity @30.8% PER              | -                   | -     | - 101 | -     | dBm    |
| Maximum received signal @30.8% PER  | -                   | -     | 8     | -     | dBm    |
| Co-channel C/I                      | F = F0 MHz          | -     | 4     | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 + 1 MHz      | -     | - 5   | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 - 1 MHz      | -     | - 5   | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 + 2 MHz      | -     | - 28  | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 - 2 MHz      | -     | - 36  | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 + 3 MHz      | -     | - 36  | -     | dB     |
| Adjacent channel selectivity C/I    | F = F0 - 3 MHz      | -     | - 38  | -     | dB     |
| Adjacent channel selectivity C/I    | F > F0 + 3 MHz      | -     | - 37  | -     | dB     |
| Adjacent channel selectivity C/I    | F > F0 - 3 MHz      | -     | - 41  | -     | dB     |
| Image frequency                     | -                   | -     | - 37  | -     | dB     |
| Adjacent channel to image frequency | F = F image + 1 MHz | -     | - 44  | -     | dB     |
| Adjacent channel to image frequency | F = F image - 1 MHz | -     | - 28  | -     | dB     |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000072_60a12e3b7b1aa29b94b6bebb3270665fce65a4de8042ffa413d99d2120bfe712.png)

<!-- page_break -->

## 7 Packaging

- For information about tape, reel, and product marking, please refer to ESP32-S3 Chip Packaging Information .
- The pins of the chip are numbered in anti-clockwise order starting from Pin 1 in the top view. For pin numbers and pin names, see also Figure 2-1 ESP32-S3 Pin Layout (Top View) .
- The recommended land pattern source file (asc) is available for download. You can import the file with software such as PADS and Altium Designer.
- All ESP32-S3 chip variants have identical land pattern (see Figure 7-1) except ESP32-S3FH4R2 has a bigger EPAD (see Figure 7-2). The source file (asc) may be adopted for ESP32-S3FH4R2 by altering the size of the EPAD (see dimensions D2 and E2 in Figure 7-2).

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000073_c6adf2eac3a61e687f7b7d0d798e03ac220745b386a539f994fbd1686ebc581d.png)

Figure 7-1. QFN56 (7×7 mm) Package

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000074_f2af56c5350ba1769fcba899d50ccc2b5b4ee560a75dc91bdfa284ce1e3d11b5.png)

<!-- page_break -->

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000075_46a5b51a1ad6f6bbdd320ef3deb69c679b69eb7f7291d3735d65ff0f28def64b.png)

Figure 7-2. QFN56 (7×7 mm) Package (Only for ESP32-S3FH4R2)

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000076_5512a1ba0bc4b1a326ba7488521ff83e9b93ad84fb0e53bc3f83d14c0a3e62a7.png)

)25(+23( &amp;21),'(17,$/ %

<!-- page_break -->

79

## ESP32-S3 Consolidated Pin Overview

Table 7-1. Consolidated Pin Overview

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000077_ce52fc14fc10b3c7161642ec14ce721ab1e7bf0b0fe56b7177c65f29a78c3b15.png)

|         |                   |                                          | Pin Settings   | Pin Settings   | RTC IO MUX Function   | RTC IO MUX Function         | Analog        | Analog   | Function          | Function             |             |               | IO MUX Function      | IO MUX Function   | IO MUX Function   | IO MUX Function     | F3            | F3      |        |        |
|---------|-------------------|------------------------------------------|----------------|----------------|-----------------------|-----------------------------|---------------|----------|-------------------|----------------------|-------------|---------------|----------------------|-------------------|-------------------|---------------------|---------------|---------|--------|--------|
| Pin No. | Pin Name          | Pin Type Pin Providing Power             | At Reset       | After Reset    | F0                    | F3                          | F0            | F1       |                   | F0                   | Type        | F1            | Type                 | F2                | Type              | Type                | F4            |         | Type   | Type   |
| 1 2     | LNA_IN VDD3P3     | Analog Power                             |                |                |                       |                             |               |          |                   |                      |             |               |                      |                   |                   |                     |               |         |        |        |
| 3       | VDD3P3            | Power                                    |                |                |                       |                             |               |          |                   |                      |             |               |                      |                   |                   |                     |               |         |        |        |
| 4       | CHIP_PU           | Analog VDD3P3_RTC                        |                |                |                       |                             |               |          |                   |                      |             |               |                      |                   |                   |                     |               |         |        |        |
| 5       |                   |                                          |                |                |                       |                             |               |          |                   |                      |             |               |                      |                   |                   |                     |               |         |        |        |
|         | GPIO0             | IO VDD3P3_RTC                            | WPU, IE        | WPU, IE        | RTC_GPIO0             | sar_i2c_scl_0               |               |          |                   | GPIO0                | I/O/T       | GPIO0         | I/O/T                |                   |                   |                     |               |         |        |        |
| 6 7     | GPIO1             | IO VDD3P3_RTC IO VDD3P3_RTC              | IE             | IE             | RTC_GPIO1 RTC_GPIO2   | sar_i2c_sda_0               | TOUCH1 TOUCH2 |          | ADC1_CH0 ADC1_CH1 | GPIO1 GPIO2          | I/O/T I/O/T | GPIO1 GPIO2   | I/O/T                |                   |                   |                     |               |         |        |        |
| 8       | GPIO2 GPIO3       | IO VDD3P3_RTC                            | IE IE          | IE IE          | RTC_GPIO3             | sar_i2c_scl_1 sar_i2c_sda_1 |               | TOUCH3   | ADC1_CH2          | GPIO3                | I/O/T       | GPIO3         | I/O/T I/O/T          |                   |                   |                     |               |         |        |        |
| 9       | GPIO4             | IO VDD3P3_RTC                            |                |                | RTC_GPIO4             |                             | TOUCH4        |          | ADC1_CH3 GPIO4    | I/O/T                |             | GPIO4         | I/O/T                |                   |                   |                     |               |         |        |        |
| 10      | GPIO5             | IO VDD3P3_RTC                            |                |                | RTC_GPIO5             |                             | TOUCH5        | ADC1_CH4 |                   | GPIO5                | I/O/T       | GPIO5         | I/O/T                |                   |                   |                     |               |         |        |        |
| 11      | GPIO6             | IO VDD3P3_RTC                            |                |                | RTC_GPIO6             |                             | TOUCH6        | ADC1_CH5 |                   | GPIO6                | I/O/T       | GPIO6         | I/O/T                |                   |                   |                     |               |         |        |        |
| 12      | GPIO7             | IO VDD3P3_RTC                            |                |                | RTC_GPIO7             |                             | TOUCH7        | ADC1_CH6 | GPIO7             | I/O/T                |             | GPIO7         | I/O/T                |                   |                   |                     |               |         |        |        |
| 13      | GPIO8             | IO VDD3P3_RTC                            |                |                | RTC_GPIO8             |                             | TOUCH8        | ADC1_CH7 | GPIO8             | I/O/T                | GPIO8       |               | I/O/T                |                   |                   | SUBSPICS1           | O/T           |         |        |        |
| 14      | GPIO9             | IO VDD3P3_RTC                            |                | IE             | RTC_GPIO9             |                             | TOUCH9        |          | ADC1_CH8          | GPIO9                | I/O/T GPIO9 |               | I/O/T                |                   |                   | SUBSPIHD            | I1/O/T        | FSPIHD  | I1/O/T | I1/O/T |
| 15      | GPIO10            | IO VDD3P3_RTC                            |                | IE             | RTC_GPIO10            |                             | TOUCH10       |          | ADC1_CH9          | GPIO10               | I/O/T       | GPIO10        | I/O/T FSPIIO4        |                   | I1/O/T            | SUBSPICS0 O/T       |               | FSPICS0 | I1/O/T | I1/O/T |
| 16      | GPIO11            | IO VDD3P3_RTC                            |                | IE             | RTC_GPIO11            |                             | TOUCH11       |          | ADC2_CH0          | GPIO11               | I/O/T       | GPIO11        | I/O/T                | FSPIIO5           | I1/O/T            | SUBSPID             | I1/O/T        | FSPID   | I1/O/T | I1/O/T |
| 17      | GPIO12            | IO VDD3P3_RTC                            |                | IE             | RTC_GPIO12            |                             | TOUCH12       |          | ADC2_CH1          | GPIO12               | I/O/T       | GPIO12        | I/O/T                | FSPIIO6           | I1/O/T            | SUBSPICLK           | O/T           | FSPICLK | I1/O/T | I1/O/T |
| 18      | GPIO13            | IO VDD3P3_RTC                            |                | IE             | RTC_GPIO13            |                             | TOUCH13       |          | ADC2_CH2          | GPIO13               | I/O/T       | GPIO13        | I/O/T                | FSPIIO7           | I1/O/T            | SUBSPIQ             | I1/O/T        | FSPIQ   | I1/O/T | I1/O/T |
| 19      | GPIO14            | IO VDD3P3_RTC                            |                | IE             | RTC_GPIO14            |                             | TOUCH14       |          | ADC2_CH3          | GPIO14               | I/O/T       | GPIO14        | I/O/T                | FSPIDQS           | O/T               |                     | I1/O/T        | FSPIWP  | I1/O/T | I1/O/T |
| 20      | VDD3P3_RTC        | Power                                    |                |                |                       |                             |               |          |                   |                      |             |               |                      |                   |                   | SUBSPIWP            |               |         |        |        |
| 21      | XTAL_32K_P        | IO VDD3P3_RTC                            |                |                | RTC_GPIO15            |                             | XTAL_32K_P    |          | ADC2_CH4          | GPIO15               | I/O/T       | GPIO15        | I/O/T                | U0RTS             | O                 |                     |               |         |        |        |
| 22      | XTAL_32K_N        | IO VDD3P3_RTC                            |                |                | RTC_GPIO16            |                             |               |          |                   |                      | I/O/T       | GPIO16        | I/O/T                | U0CTS             | I1                |                     |               |         |        |        |
| 23      | GPIO17            | IO VDD3P3_RTC                            |                |                | RTC_GPIO17            |                             | XTAL_32K_N    |          | ADC2_CH5          | GPIO16               | I/O/T       | GPIO17        |                      | U1TXD             | O                 |                     |               |         |        |        |
| 24      | GPIO18            | IO VDD3P3_RTC                            |                | IE IE          | RTC_GPIO18            |                             |               | ADC2_CH7 | ADC2_CH6          | GPIO17 GPIO18        | I/O/T       | GPIO18        | I/O/T I/O/T          | U1RXD             | I1                | CLK_OUT3            | O             |         |        |        |
| 25 26   | GPIO19 GPIO20     | IO VDD3P3_RTC IO VDD3P3_RTC              | USB_PU         | USB_PU         | RTC_GPIO19 RTC_GPIO20 |                             | USB_D- USB_D+ |          | ADC2_CH8 ADC2_CH9 | GPIO19 GPIO20        | I/O/T I/O/T | GPIO19 GPIO20 | I/O/T I/O/T          | U1RTS U1CTS       | O I1              | CLK_OUT2 O CLK_OUT1 | O             |         |        |        |
| 27      | GPIO21            | IO VDD3P3_RTC                            |                |                | RTC_GPIO21            |                             |               |          |                   | GPIO21               | I/O/T       | GPIO21        | I/O/T                |                   |                   |                     |               |         |        |        |
| 28      | SPICS1            | IO                                       | WPU, IE        |                |                       |                             |               |          |                   |                      |             |               | I/O/T                |                   |                   |                     |               |         |        |        |
| 29      | VDD_SPI           | VDD_SPI Power                            |                | WPU, IE        |                       |                             |               |          |                   | SPICS1               | O/T         | GPIO26        |                      |                   |                   |                     |               |         |        |        |
| 30      | SPIHD             | VDD_SPI                                  | WPU, IE        | WPU, IE        |                       |                             |               |          |                   | SPIHD                | I1/O/T      | GPIO27        | I/O/T                |                   |                   |                     |               |         |        |        |
| 31      | SPIWP             | IO IO                                    | WPU, IE        | WPU, IE        |                       |                             |               |          |                   | SPIWP                | I1/O/T      | GPIO28        | I/O/T                |                   |                   |                     |               |         |        |        |
| 32      | SPICS0            | VDD_SPI IO VDD_SPI                       | WPU,           | WPU, IE        |                       |                             |               |          |                   | SPICS0               | O/T         | GPIO29        | I/O/T                |                   |                   |                     |               |         |        |        |
| 33      | SPICLK            | IO VDD_SPI                               | IE WPU, IE     | WPU, IE        |                       |                             |               |          |                   | SPICLK               | O/T         | GPIO30        | I/O/T                |                   |                   |                     |               |         |        |        |
| 34      | SPIQ              | IO VDD_SPI                               | WPU, IE        | WPU, IE        |                       |                             |               |          |                   | SPIQ                 | I1/O/T      | GPIO31        | I/O/T                |                   |                   |                     |               |         |        |        |
| 35      | SPID              | IO VDD_SPI                               | WPU, IE        | WPU, IE        |                       |                             |               |          |                   | SPID                 | I1/O/T      | GPIO32        | I/O/T                |                   |                   |                     |               |         |        |        |
| 36      | SPICLK_N SPICLK_P | IO VDD_SPI/VDD3P3_CPU VDD_SPI/VDD3P3_CPU | IE             | IE             |                       |                             |               |          |                   | SPICLK_P_DIFF        | O/T O/T     | GPIO48 GPIO47 | I/O/T                | SUBSPICLK_P_DIFF  | O/T               |                     |               |         |        |        |
| 37 38   | GPIO33            | IO IO VDD_SPI/VDD3P3_CPU                 | IE             | IE             |                       |                             |               |          |                   | SPICLK_N_DIFF GPIO33 | I/O/T       | GPIO33        | I/O/T I/O/T          | SUBSPICLK_N_DIFF  | O/T               |                     |               |         |        |        |
| 39      |                   | IO VDD_SPI/VDD3P3_CPU                    |                | IE             |                       |                             |               |          |                   | GPIO34               |             | GPIO34        | I/O/T                | FSPIHD            | I1/O/T            | SUBSPIHD            | I1/O/T        | SPIIO4  |        |        |
| 40      | GPIO34            | IO VDD_SPI/VDD3P3_CPU                    |                | IE             |                       |                             |               |          |                   | GPIO35               | I/O/T I/O/T | GPIO35        | I/O/T                | FSPICS0           | I1/O/T            | SUBSPICS0 SUBSPID   | O/T           | SPIIO5  |        |        |
|         | GPIO35            | VDD_SPI/VDD3P3_CPU                       |                | IE             |                       |                             |               |          |                   |                      |             |               |                      | FSPID FSPICLK     | I1/O/T I1/O/T     |                     | I1/O/T        | SPIIO6  |        |        |
| 41      | GPIO36            | IO                                       |                | IE             |                       |                             |               |          | GPIO37            | GPIO36               | I/O/T       | GPIO36        | I/O/T                | FSPIQ             | I1/O/T            | SUBSPICLK SUBSPIQ   | O/T           | SPIIO7  |        |        |
| 42 43   | GPIO37            | IO VDD_SPI/VDD3P3_CPU IO                 |                | IE             |                       |                             |               |          |                   | GPIO38               | I/O/T       | GPIO37        | I/O/T                | FSPIWP            | I1/O/T            | SUBSPIWP            | I1/O/T I1/O/T | SPIDQS  |        |        |
|         | GPIO38            | VDD3P3_CPU IO VDD3P3_CPU                 |                | IE             |                       |                             |               |          |                   | MTCK                 | I/O/T       | GPIO38 GPIO39 | I/O/T I/O/T          | CLK_OUT3          | O                 | SUBSPICS1           | O/T           |         |        |        |
| 44 45   | MTCK MTDO         | IO VDD3P3_CPU                            |                | IE IE          |                       |                             |               |          |                   | MTDO                 | I1 O/T      | GPIO40        | I/O/T CLK_OUT2       |                   | O                 |                     |               |         |        |        |
| 46 47   | VDD3P3_CPU        | Power VDD3P3_CPU                         |                |                |                       |                             |               |          |                   |                      |             |               |                      |                   |                   |                     |               |         |        |        |
|         | MTDI              | IO                                       |                | IE             |                       |                             |               |          |                   | MTDI                 | I1          | GPIO41        | I/O/T                | CLK_OUT1          | O                 |                     |               |         |        |        |
| 48      |                   |                                          |                |                |                       |                             |               |          |                   |                      | I1          |               |                      |                   |                   |                     |               |         |        |        |
|         | MTMS              | IO VDD3P3_CPU                            |                | IE             |                       |                             |               |          |                   | MTMS                 |             | GPIO42        | I/O/T                |                   |                   |                     |               |         |        |        |
| 49      | U0TXD             | IO VDD3P3_CPU                            | WPU, IE        | WPU, IE        |                       |                             |               |          |                   | U0TXD                | O           | GPIO43        | I/O/T I/O/T CLK_OUT2 | CLK_OUT1          | O                 |                     |               |         |        |        |
| 50      | U0RXD             | IO VDD3P3_CPU                            | WPU, IE        | WPU, IE        |                       |                             |               |          |                   | U0RXD                | I1          | GPIO44        |                      |                   | O                 |                     |               |         |        |        |

*

For details, see Section 2

Pins

. Regarding highlighted

<!-- page_break -->

## Datasheet Versioning

| Datasheet Version            | Status              | Watermark                               | Definition                                                                                                                                                                                              |
|------------------------------|---------------------|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| v0.1 ~ v0.5 (excluding v0.5) | Draft               | Confidential                            | This datasheet is under development for products in the design stage. Specifications may change without prior notice.                                                                                   |
| v0.5 ~ v1.0 (excluding v1.0) | Preliminary release | Preliminary                             | This datasheet is actively updated for products in the verification stage. Specifications may change before mass production, and the changes will be documentation in the datasheet's Revision History. |
| v1.0 and higher              | Official release    | -                                       | This datasheet is publicly released for products in mass production. Specifications are finalized, and major changes will be communicated via Product Change Notifications (PCN).                       |
| Any version                  | -                   | Not Recommended for New Design (NRND) 1 | This datasheet is updated less frequently for products not recommended for new designs.                                                                                                                 |
| Any version                  | -                   | End of Life (EOL) 2                     | This datasheet is no longer mtained for products that have reached end of life.                                                                                                                         |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000078_190ccfebfda807dd23f42b3d8496c72d92dcb99428b444fa875da6b128a48562.png)

<!-- page_break -->

## Glossary

## module

A self-contained unit integrated within the chip to extend its capabilities, such as cryptographic modules, RF modules 2

## peripheral

A hardware component or subsystem within the chip to interface with the outside world 2

## in-package flash

Flash integrated directly into the chip's package, and external to the chip die 4, 13

## off-package flash

Flash external to the chip's package 20

## strapping pin

A type of GPIO pin used to configure certain operational settings during the chip's power-up, and can be reconfigured as normal GPIO after the chip's reset 32

## eFuse parameter

A parameter stored in an electrically programmable fuse (eFuse) memory within a chip. The parameter can be set by programming EFUSE\_PGM\_DATA n \_REG registers, and read by reading a register field named after the parameter 32

## SPI boot mode

A boot mode in which users load and execute the existing code from SPI flash 33

## joint download boot mode

A boot mode in which users can download code into flash via the UART or other interfaces (see T able 3-3 Chip Boot Mode Control &gt; Note), and load and execute the downloaded code from the flash or SRAM 33

## eFuse

A one-time programmable (OTP) memory which stores system and user parameters, such as MAC address, chip revision number, flash encryption key, etc. Value 0 indicates the default state, and value 1 indicates the eFuse has been programmed 39

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000079_b11de4316fec379145d7228e2995f2065ce8dc8bbfd90039a455b1abab4d99fc.png)

<!-- page_break -->

## Related Documentation and Resources

## Related Documentation

- ESP32-S3 Technical Reference Manual - Detailed information on how to use the ESP32-S3 memory and peripherals.
- ESP32-S3 Hardware Design Guidelines - Guidelines on how to integrate the ESP32-S3 into your hardware product.
- ESP32-S3 Series SoC Errata - Descriptions of known errors in ESP32-S3 series of SoCs.
- Certificates https:/ /espressif.com/en/support/documents/certificates
- ESP32-S3 Product/Process Change Notifications (PCN)

[https:/ /espressif.com/en/support/documents/pcns?keys=ESP32-S3](https://espressif.com/en/support/documents/pcns?keys=ESP32-S3)

- ESP32-S3 Advisories - Information on security, bugs, compatibility, component reliability. https:/ /espressif.com/en/support/documents/advisories?keys=ESP32-S3
- Documentation Updates and Update Notification Subscription https:/ /espressif.com/en/support/download/documents

## Developer Zone

- ESP-IDF Programming Guide for ESP32-S3 - Extensive documentation for the ESP-IDF development framework.
- ESP-IDF and other development frameworks on GitHub. https:/ /github.com/espressif
- ESP32 BBS Forum - Engineer-to-Engineer (E2E) Community for Espressif products where you can post questions, share knowledge, explore ideas, and help solve problems with fellow engineers. https:/ /esp32.com/
- ESP-FAQ - A summary document of frequently asked questions released by Espressif. https:/ /espressif.com/projects/esp-faq/en/latest/index.html
- The ESP Journal - Best Practices, Articles, and Notes from Espressif folks. https:/ /blog.espressif.com/
- See the tabs SDKs and Demos , Apps , Tools , AT Firmware . https:/ /espressif.com/en/support/download/sdks-demos

## Products

- ESP32-S3 Series SoCs - Browse through all ESP32-S3 SoCs. https:/ /espressif.com/en/products/socs?id=ESP32-S3

·

ESP32-S3 Series Modules

- Browse through all ESP32-S3-based modules.

[https:/ /espressif.com/en/products/modules?id=ESP32-S3](https://espressif.com/en/products/modules?id=ESP32-S3)

- ESP32-S3 Series DevKits - Browse through all ESP32-S3-based devkits. https:/ /espressif.com/en/products/devkits?id=ESP32-S3
- ESP Product Selector - Find an Espressif hardware product suitable for your needs by comparing or applying filters. https:/ /products.espressif.com/#/product-selector?language=en

## Contact Us

- See the tabs Sales Questions , Technical Enquiries , Circuit Schematic &amp; PCB Design Review , Get Samples (Online stores), Become Our Supplier , Comments &amp; Suggestions . https:/ /espressif.com/en/contact-us/sales-questions

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000080_67d1b12383c2c5d63fa3f95ff67f238c29f01127a101bced11dd6fd77adc13dc.png)

<!-- page_break -->

## Revision History

| Date       | Version   | Release notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-03-05 | v2.2      | • Renamedthe Digital Signature module to 'RSA Digital Signature Peripheral (RSA_DS)' • Updated Figure 4-1 Address Mapping Structure • Added a note in Section 4.2.1.9 SD/MMC Host Controller • Updated table 5-10 Current Consumption in Low-Power Modes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 2025-11-28 | v2.1      | • Updated the status of ESP32-S3R2 to End of Life and added chip variant ESP32-S3RH2 • Updated 'Ordering Code' to 'Part Number' in Table 1-1 ESP32-S3 Series Comparison • Added Section 1.3 Chip Revision and chip version information in Table 1-1 ESP32-S3 Series Comparison • Added Section 2.3.5 Peripheral Pin Assignment and updated the Pin As- signment part for each subsection in Section 4.2 Peripherals • Updated Figure 3-1 Visualization of Timing Parameters for the Strapping Pins • Added Section 5.7 Memory Specifications • Added Table 5-8 Current Consumption for Bluetooth LE in Active Mode in Section 5.6 Current Consumption • Added Appendix Datasheet Status Definitions and Glossary • Other structural, formatting, and content improvements |
| 2025-04-24 | v2.0      | • Updated the status of ESP32-S3R8V to End of Life • Updated the CoreMark ® score in Section CPU and Memory • Updated Figure 4.1.2 Memory Organization in Section 4-1 Address Map- ping Structure • Updated the temperature sensor's measurement range in Section 4.2.2.2 Temperature Sensor • Added some notes in Chapter 6 RF Characteristics • Updated the source file link for the recommended land pattern in Chapter 7 Packaging                                                                                                                                                                                                                                                                                                                                    |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000081_2827116e3bbef3ac47546d740ea00e1fb661c3c16f0c12743fd4a72489aa5632.png)

<!-- page_break -->

## Cont'd from previous page

| Date       | Version   | Release notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|------------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2024-09-11 | v1.9      | • Updated descriptions on the title page • Updated feature descriptions in Section Features and adjusted the format • Updated the pin introduction in Section 2.2 Pin Overview and adjusted the format • Updated descriptions in Section 2.3 IO Pins , and divided Section RTCand Analog Pin Functions into Section 2.3.3 Analog Functions and Section 2.3.2 RTC Functions • Updated Section Strapping Pins to Section 3 Boot Configurations • Adjusted the structure and section order in Section 4 Functional Descrip- tion , deleted Section Peripheral Pin Configurations , and added the Pin Assignment part in each subsection in Section 4.2 Peripherals |
| 2023-11-24 | v1.8      | • Added chip variant ESP32-S3R16V and updated related information • Added the second and third table notes in Table 1-1 ESP32-S3 Series Comparison • Updated Section 3.1 Chip Boot Mode Control • Updated Section 5.5 ADC Characteristics • Other minor updates                                                                                                                                                                                                                                                                                                                                                                                                 |
| 2023-06    | v1.7      | • Removed the sample status for ESP32-S3FH4R2 • Updated Figure ESP32-S3 Functional Block Diagram and Figure 4-2 Com- ponents and Power Domains • Added the predefined settings at reset and after reset for GPIO20 in Table 2-1 Pin Overview • Updated notes for Table 2-4 IO MUX Functions • Updated the clock name 'FOSC_CLK' to 'RC_FAST_CLK' in Section 4.1.3.5 Power Management Unit (PMU) • Updated descriptions in Section 4.2.1.5 Serial Peripheral Interface (SPI) and Section 4.1.4.3 RSA Accelerator • Other minor updates                                                                                                                           |

Cont'd on next page

<!-- page_break -->

## Cont'd from previous page

| Date    | Version   | Release notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|---------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2023-02 | v1.6      | • Improved the content in the following sections: - Section Product Overview - Section 2 Pins - Section 4.1.3.5 Power Management Unit (PMU) - Section 4.2.1.5 Serial Peripheral Interface (SPI) - Section 5.1 Absolute Maximum Ratings - Section 5.2 Recommended Operating Conditions - Section 5.3 VDD_SPI Output Characteristics - Section 5.5 ADC Characteristics • Added ESP32-S3 Consolidated Pin Overview • Updated the notes in Section 1 ESP32-S3 Series Comparison and Section 7 Packaging • Updated the effective measurement range in Table 5-5 ADC Characteris- tics • Updated the Bluetooth maximum transmit power • Other minor updates |
| 2022-12 | v1.5      | • Removed the 'External PA is supported' feature from Section Features • Updated the ambient temperature for ESP32-S3FH4R2 from - 40 ∼ 105 °C to - 40 ∼ 85 °C • Added two notes in Section 7                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 2022-11 | v1.4      | • Added the package information for ESP32-S3FH4R2 in Section 7 • Added ESP32-S3 Series SoC Errata in Section • Other minor updates                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 2022-09 | v1.3      | • Added a note about the maximum ambient temperature of R8 series chips to Table 1-1 and Table 5-2 • Added information about power-up glitches for some pins in Section 2.2 • Added the information about VDD3P3 power pins to Table 2.2 and Sec- tion 2.5.2 • Updated section 4.3.3.1 • Added the fourth note in Table 2-1 • Updated the minimum and maximum values of Bluetooth LE RF transmit power in Section 6.2.1 • Other minor updates                                                                                                                                                                                                         |
| 2022-07 | v1.2      | • Updated description of ROM code printing in Section 3 • Updated Figure ESP32-S3 Functional Block Diagram • Update Section 5.6 • Deleted the hyperlinks in Application                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

Cont'd on next page

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000082_dc743f57ea0b4fd8215917e66f56160c08057ecc35917c77c4f6d5e869c8d814.png)

<!-- page_break -->

## Cont'd from previous page

| Date       | Version   | Release notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2022-04    | v1.1      | • Synchronized eFuse size throughout • Updated pin description in Table 2-1 • Updated SPI resistance in Table 5-3 • Added information about chip ESP32-S3FH4R2                                                                                                                                                                                                                                                                                                                                                                                                               |
| 2022-01    | v1.0      | • Added wake-up sources for Deep-sleep mode • Added Table 3-4 for default configurations of VDD_SPI • Added ADC calibration results in Table 5-5 • Added typical values when all peripherals and peripheral clocks are en- abled to Table 5-9 • Added more descriptions of modules/peripherals in Section 4 • Updated Figure ESP32-S3 Functional Block Diagram • Updated JEDEC specification • Updated Wi-Fi RF data in Section 5.6 • Updated temperature for ESP32-S3R8 and ESP32-S3R8V • Updated description of Deep-sleep mode in Table 5-10 • Updated wording throughout |
| 2021-10-12 | v0.6.1    | Updated text description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 2021-09-30 | v0.6      | • Updated to chip revision 1 by swapping pin 53 and pin 54 (XTAL_P and XTAL_N) • Updated Figure ESP32-S3 Functional Block Diagram • Added CoreMark score in section Features • Updated Section 3 • Added data for cumulative IO output current in Table 5-1 • Added data for Modem-sleep current consumption in Table 5-9 • Updated data in section 5.6, 6.1, and 6.2 • Updated wording throughout                                                                                                                                                                           |
| 2021-07-19 | v0.5.1    | • Added 'for chip revision 0' on cover, in footer and watermark to indicate that the current and previous versions of this datasheet are for chip ver- sion 0 • Corrected a few typos                                                                                                                                                                                                                                                                                                                                                                                        |
| 2021-07-09 | v0.5      | Preliminary version                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000083_c5754e12cf95b5d35445984d5ebc48869024b0a39b8d77b89504830cb92ef376.png)

<!-- page_break -->

![Image](manuals/processed/esp32-s3-datasheet-en/artifacts/image_000084_cada247bcf9e40debc1c37f7ec8f244cae8797ca04e9062b4bd0f7c92722f198.png)

## Disclaimer and Copyright Notice

Information in this document, including URL references, is subject to change without notice.

ALL THIRD PARTY'S INFORMATION IN THIS DOCUMENT IS PROVIDED AS IS WITH NO WARRANTIES TO ITS AUTHENTICITY AND ACCURACY.

NO WARRANTY IS PROVIDED TO THIS DOCUMENT FOR ITS MERCHANTABILITY, NON-INFRINGEMENT, FITNESS FOR ANY PARTICULAR PURPOSE, NOR DOES ANY WARRANTY OTHERWISE ARISING OUT OF ANY PROPOSAL, SPECIFICATION OR SAMPLE.

All liability , including liability for infringement of any proprietary rights, relating to use of information in this document is disclaimed. No licenses express or implied, by estoppel or otherwise, to any intellectual property rights are granted herein.

The Wi-Fi Alliance Member logo is a trademark of the Wi-Fi Alliance. The Bluetooth logo is a registered trademark of Bluetooth SIG.

All trade names, trademarks and registered trademarks mentioned in this document are property of their respective owners, and are hereby acknowledged.

Copyright © 2026 Espressif Systems (Shanghai) Co., Ltd. All rights reserved.

[www.espressif.com](https://www.espressif.com/)