#pragma once

// Protocol-level constants only. Board-specific RADIO_*_PIN/BOARD_LED_PIN/
// I2C_*_PIN/DISPLAY_OLED_RST_PIN values used to live here as compile-time
// #defines (one fixed board per build) - they're now runtime-configurable
// via iohc_pins.h/IOHC::g_radio_pins, set from YAML (see iohc/__init__.py's
// pin options), because this bridge runs on more than one board layout
// (LilyGO T3 LoRa32, a bare ESP32-S3-DevKitC-1 + separate SX1276 module,
// ...) and a single hardcoded header can't serve all of them at once.
//
// Everything below is a property of io-homecontrol itself (or of the
// SX1276/SX1278 chip family in general), not of any particular board, so it
// stays a compile-time constant.

#include "iohc_pins.h"

#define RADIO_SX127X
#define Regulatory_Domain_EU_868

#define SPI_CLK_FRQ 10000000

#define BOARD_TCXO_WAKEUP_TIME 0
#define BOARD_READY_AFTER_POR 10000

#define PREAMBLE_MSB 0x00
#define PREAMBLE_LSB 52  // ~13.5ms of 0xAA preamble

#define SYNC_BYTE_1 0xff
#define SYNC_BYTE_2 0x33

#define CHANNEL1 868250000  // 2W
#define CHANNEL2 868950000  // 1W 2W
#define CHANNEL3 869850000  // 2W

#define FREQS2SCAN {CHANNEL2, CHANNEL1, CHANNEL3}
// iohcRadio's own ISR-driven auto-hop (tickerCounter()/num_freqs) stays
// permanently disabled - it's a genuine hardware interrupt and can preempt
// mid-instruction, which would race against the retune()-then-send()
// sequence every TX call site relies on. 3-channel RX coverage (Finding 31)
// instead comes from esphome::iohc::IOHCComponent::maybe_hop_(), a
// cooperative (non-interrupt) hop checked every loop() tick - see that
// function's own comment for why this is the safe way to do it.
#define MAX_FREQS 1
