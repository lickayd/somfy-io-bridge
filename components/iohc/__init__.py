"""Somfy IO (io-homecontrol) radio component.

Thin ESPHome wrapper around a vendored port of
https://github.com/rspaargaren/iohomecontrol (Apache-2.0), itself building on
https://github.com/Velocet/iown-homecontrol's protocol documentation. The
other files in this same directory are the ported radio/protocol files
(flat layout required - see iohc.h for why).

Radio pins (SPI + DIO0/DIO2 + optional scan LED) are YAML-configurable below
- see iohc_pins.h for the runtime struct this feeds. Defaults match Dennis's
ESP32-S3-DevKitC-1 (N16R8) + separate SX1276 module wiring, kept apart from
the CC1101/RTS SPI bus (GPIO10-14). Override any of them for a different
board (e.g. a LilyGO T3 LoRa32: sclk=5, miso=19, mosi=27, cs=18, rst=23,
dio0=26, dio1=33, dio2=32, led=25). Protocol-level constants (preamble, sync
bytes, channel plan) stay fixed in iohc_board_config.h - those are properties
of io-homecontrol/the SX1276 chip family itself, not of any particular board.
"""

import re

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID

CODEOWNERS = ["@danielpetrovic"]
MULTI_CONF = False

iohc_ns = cg.esphome_ns.namespace("iohc")
IOHCComponent = iohc_ns.class_("IOHCComponent", cg.Component)

CONF_CONTROLLER_ADDRESS = "controller_address"
CONF_SYSTEM_KEY = "system_key"

CONF_SCLK_PIN = "sclk_pin"
CONF_MISO_PIN = "miso_pin"
CONF_MOSI_PIN = "mosi_pin"
CONF_CS_PIN = "cs_pin"
CONF_RST_PIN = "rst_pin"
CONF_DIO0_PIN = "dio0_pin"
CONF_DIO1_PIN = "dio1_pin"
CONF_DIO2_PIN = "dio2_pin"
CONF_LED_PIN = "led_pin"

# Plain GPIO numbers, not esphome's pin-schema GPIOPin objects: the vendored
# radio stack (SX1276Helpers.cpp/iohcRadio.cpp) talks to these with raw
# Arduino pinMode()/digitalWrite()/attachInterrupt() calls, never through
# ESPHome's own GPIOPin abstraction, so there's nothing for a GPIOPin object
# to plug into here - an int is what set_radio_pins() actually needs.
_pin = cv.int_range(min=-1, max=48)

def validate_hex_string(length):
    pattern = re.compile(rf"^[0-9a-fA-F]{{{length}}}$")

    def validator(value):
        value = cv.string_strict(value)
        if value == "":
            return value  # not set - auto-generate and persist on-device instead
        if not pattern.match(value):
            raise cv.Invalid(f"must be exactly {length} hex characters (or empty to auto-generate)")
        return value.lower()

    return validator


# Dennis's ESP32-S3-DevKitC-1 (N16R8) + separate SX1276 module wiring - see
# this __init__.py's own module docstring above for the LilyGO equivalents.
CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(IOHCComponent),
        cv.Optional(CONF_SCLK_PIN, default=4): _pin,
        cv.Optional(CONF_MISO_PIN, default=6): _pin,
        cv.Optional(CONF_MOSI_PIN, default=5): _pin,
        cv.Optional(CONF_CS_PIN, default=7): _pin,
        cv.Optional(CONF_RST_PIN, default=15): _pin,
        cv.Optional(CONF_DIO0_PIN, default=16): _pin,
        # Not wired on most installs (including Dennis's) - kept
        # configurable for completeness, matches RADIO_DIO1_PIN's own
        # historical "not wired, placeholder" status in the old board
        # config header.
        cv.Optional(CONF_DIO1_PIN, default=2): _pin,
        cv.Optional(CONF_DIO2_PIN, default=18): _pin,
        # -1 (default) = no scan/RX LED wired. Set to a real GPIO to get the
        # old LilyGO-board behavior (blinks on receive).
        cv.Optional(CONF_LED_PIN, default=-1): _pin,
        # This bridge's own 2W controller identity (the box/TaHoma-like
        # role, see iohc_controller2w.h) - one shared identity for the whole
        # bridge, unlike each cover's own per-motor node/key. Optional:
        # bonded identity from YAML/secrets.yaml instead of a randomly
        # generated one that only lives in this board's own flash. If a
        # board ever dies, a replacement flashed with the same
        # controller_address/system_key reproduces the exact same identity
        # - no re-bonding needed for any already-2W-bonded motor. Leave
        # unset to keep the original random-generate-and-persist-on-device
        # behavior - this is the current default for every install, since
        # no real 2W bond has yet succeeded on any of them (see
        # io-2w-protocol.md). controller_address = 6 hex chars (3 bytes),
        # system_key = 32 hex chars (16 bytes, AES-128).
        cv.Optional(CONF_CONTROLLER_ADDRESS, default=""): validate_hex_string(6),
        cv.Optional(CONF_SYSTEM_KEY, default=""): cv.sensitive(validate_hex_string(32)),
    }
).extend(cv.COMPONENT_SCHEMA)


RadioPins = cg.global_ns.namespace("IOHC").struct("RadioPins")


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    if config[CONF_CONTROLLER_ADDRESS]:
        cg.add(var.set_fixed_controller_address(config[CONF_CONTROLLER_ADDRESS]))
    if config[CONF_SYSTEM_KEY]:
        cg.add(var.set_fixed_system_key(config[CONF_SYSTEM_KEY]))

    pins = cg.StructInitializer(
        RadioPins,
        ("sclk", config[CONF_SCLK_PIN]),
        ("miso", config[CONF_MISO_PIN]),
        ("mosi", config[CONF_MOSI_PIN]),
        ("cs", config[CONF_CS_PIN]),
        ("rst", config[CONF_RST_PIN]),
        ("dio0", config[CONF_DIO0_PIN]),
        ("dio1", config[CONF_DIO1_PIN]),
        ("dio2", config[CONF_DIO2_PIN]),
        ("led", config[CONF_LED_PIN]),
    )
    cg.add(var.set_radio_pins(pins))
