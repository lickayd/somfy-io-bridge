#pragma once

// Runtime-configurable radio pin mapping (replaces the old compile-time
// RADIO_*_PIN #defines that used to live in iohc_board_config.h). Needed
// because the board this bridge runs on varies per install (LilyGO T3
// LoRa32, a bare ESP32-S3-DevKitC-1 with a separate SX1276 module, etc.) -
// see iohc/__init__.py's pin options for how these get set from YAML before
// IOHCComponent::setup() starts the radio.
//
// Defaults below match Dennis's ESP32-S3-DevKitC-1 (N16R8) + separate
// SX1276 module wiring (a second SPI bus, kept apart from the CC1101/RTS
// bus on GPIO10-14) - see markisen-somfy-v2.yaml. They only matter as a
// fallback if a YAML install doesn't set radio pins explicitly, which
// shouldn't normally happen since iohc/__init__.py always calls
// set_radio_pins() with its own (possibly different) schema defaults.

#include <cstdint>

namespace IOHC {

struct RadioPins {
  int8_t sclk = 4;
  int8_t miso = 6;
  int8_t mosi = 5;
  int8_t cs = 7;
  int8_t rst = 15;
  int8_t dio0 = 16;
  int8_t dio1 = 2;   // not wired on most installs, kept for completeness
  int8_t dio2 = 18;
  // -1 disables the scan/RX activity LED entirely (pinMode()/digitalWrite()
  // calls are skipped) - most installs (like Dennis's) have nothing wired
  // here, unlike the LilyGO board this was originally written for.
  int8_t led = -1;
};

// One shared instance - the vendored radio stack (SX1276Helpers.cpp,
// iohcRadio.cpp) is itself a single-instance-per-device global design
// (iohcRadio::getInstance()), so a single global pin set matches that
// existing architecture rather than introducing per-instance state it has
// no way to thread through.
extern RadioPins g_radio_pins;

}  // namespace IOHC
