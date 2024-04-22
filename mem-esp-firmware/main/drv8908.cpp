#include "drv8908.hpp"

#include <esp_log.h>

// The DRV8908 datasheet allows frequencies of up to 5 MHz.  However,
// given that we need nowhere near as much, and the sloppy design of
// the board, we choose to go considerably lower.
static const int SPI_HZ = 1000000;

static const char *TAG = "DRV8908";

static const uint8_t DAISY_CHAIN_HEADER = 0b10000010;
static const uint8_t DAISY_CHAIN_NO_FAULT_CLEAR = 0b10000000;
static const uint8_t DAISY_CHAIN_FAULT_CLEAR = 0b10100000;

static const uint8_t DRV8908_CHIP_ID = 0b010;
static const uint8_t REG_OP_CTRL_1 = 0x08;
static const uint8_t REG_OP_CTRL_2 = 0x09;
static const uint8_t REG_OLD_CTRL_1 = 0x1f;

static bool is_status_byte(uint8_t byte)
{
	return (byte & 0b11000000) == 0b11000000;
}

static uint8_t get_chip_id(uint8_t config_register)
{
	return (config_register >> 4) & 0b111;
}

static uint8_t make_register_read(uint8_t register_address)
{
	assert(register_address <= 0b111111);
	return 0b01000000 | register_address;
}

static uint8_t make_register_write(uint8_t register_address)
{
	assert(register_address <= 0b111111);
	return register_address;
}

Drv8908::Drv8908(spi_host_device_t spi_host,
                 gpio_num_t chip_select_pin,
                 gpio_num_t fault_pin)
{
	this->fault_pin = fault_pin;

	spi_device_interface_config_t device_config {
		// SPI clock is idle low (CPOL = 0),
		// data is read on falling edge and written on rising edge (CPHA = 1).
		.mode = 1,
		.clock_speed_hz = SPI_HZ,
		.spics_io_num = chip_select_pin,
		.queue_size = 1,
	};

	ESP_ERROR_CHECK(spi_bus_add_device(spi_host, &device_config, &spi_device));

	bus_mode = probe_bus_for_chip_count();

	disable_open_load_detection();
}

BusMode Drv8908::probe_bus_for_chip_count()
{
	static constexpr unsigned PATTERN_LENGTH = 6;

	uint8_t test_pattern[PATTERN_LENGTH] = {
		// Daisy chain header for two devices
		0b10000010,
		0b10000000,
		// Read CONFIG_CTRL register at address 0x07 (twice)
		0b00000111,
		0b00000111,
		// Dummy data (twice)
		0b00000000,
		0b00000000
	};

	uint8_t test_reply[PATTERN_LENGTH]{};

	spi_transaction_t test_transaction = {
		.length = PATTERN_LENGTH * CHAR_BIT,
		.tx_buffer = test_pattern,
		.rx_buffer = test_reply,
	};

	ESP_LOGD(TAG, "Probing bus for chip count");
	ESP_ERROR_CHECK(spi_device_polling_transmit(spi_device, &test_transaction));
	ESP_LOGD(TAG, "Reply: %02x %02x %02x %02x %02x %02x",
	         test_reply[0], test_reply[1], test_reply[2], test_reply[3], test_reply[4], test_reply[5]);

	bool first_is_status = is_status_byte(test_reply[0]);
	bool second_is_status = is_status_byte(test_reply[1]);

	if (first_is_status && second_is_status) {
		uint8_t first_chip_id = get_chip_id(test_reply[5]);
		uint8_t second_chip_id = get_chip_id(test_reply[4]);

		ESP_LOGI(TAG, "Found two chips on SPI bus, IDs %x and %x", first_chip_id, second_chip_id);

		if (first_chip_id != DRV8908_CHIP_ID ||
		    second_chip_id != DRV8908_CHIP_ID) {
			ESP_LOGE(TAG, "Unexpected chip IDs");
			abort();
		}

		return BusMode::TWO_CHIPS;

	} else if (first_is_status && !second_is_status) {
		uint8_t first_chip_id = get_chip_id(test_reply[4]);

		ESP_LOGI(TAG, "Found one chip on SPI bus, ID %x", first_chip_id);

		if (first_chip_id != DRV8908_CHIP_ID) {
			ESP_LOGE(TAG, "Unexpected chip ID");
			abort();
		}

		return BusMode::ONE_CHIP;

	} else {
		ESP_LOGE(TAG, "Bus probe failed");
		abort();
	}
}

void Drv8908::disable_open_load_detection()
{
	uint8_t address = make_register_write(REG_OLD_CTRL_1);
	uint8_t data = 0b11111111;

	switch (bus_mode) {
	case BusMode::ONE_CHIP:
		transmit_one_chip(address, data);
		break;

	case BusMode::TWO_CHIPS:
		transmit_two_chips(address, data);
		break;
	}
}

uint8_t Drv8908::transmit_one_chip(uint8_t address, uint8_t data)
{
	static constexpr unsigned BUFFER_LENGTH = 2;

	uint8_t tx_buffer[BUFFER_LENGTH] = { address, data };
	uint8_t rx_buffer[BUFFER_LENGTH]{};

	spi_transaction_t spi_transaction = {
		.length = BUFFER_LENGTH * CHAR_BIT,
		.tx_buffer = tx_buffer,
		.rx_buffer = rx_buffer,
	};

	ESP_LOGD(TAG, "Sending to one chip: %02x %02x", tx_buffer[0], tx_buffer[1]);
	ESP_ERROR_CHECK(spi_device_polling_transmit(spi_device, &spi_transaction));
	ESP_LOGD(TAG, "Reply: %02x %02x", rx_buffer[0], rx_buffer[1]);

	return rx_buffer[1];
}

std::array<uint8_t, 2> Drv8908::transmit_two_chips(uint8_t address, uint8_t data)
{
	return transmit_two_chips(address, data, address, data);
}

std::array<uint8_t, 2> Drv8908::transmit_two_chips(uint8_t address1, uint8_t data1, uint8_t address2, uint8_t data2)
{
	static constexpr unsigned BUFFER_LENGTH = 6;

	uint8_t tx_buffer[BUFFER_LENGTH] = {
		DAISY_CHAIN_HEADER, DAISY_CHAIN_NO_FAULT_CLEAR,
		address1, address2,
		data1, data2
	};
	uint8_t rx_buffer[BUFFER_LENGTH]{};

	spi_transaction_t spi_transaction = {
		.length = BUFFER_LENGTH * CHAR_BIT,
		.tx_buffer = tx_buffer,
		.rx_buffer = rx_buffer,
	};

	ESP_LOGD(TAG, "Sending to two chips: %02x %02x %02x %02x %02x %02x",
	         tx_buffer[0], tx_buffer[1], tx_buffer[2], tx_buffer[3], tx_buffer[4], tx_buffer[5]);
	ESP_ERROR_CHECK(spi_device_polling_transmit(spi_device, &spi_transaction));
	ESP_LOGD(TAG, "Reply: %02x %02x %02x %02x %02x %02x",
	         rx_buffer[0], rx_buffer[1], rx_buffer[2], rx_buffer[3], rx_buffer[4], rx_buffer[5]);

	return std::array { rx_buffer[4], rx_buffer[5] };
}

void Drv8908::set_h_bridges(uint32_t h_bridge_settings)
{
	uint8_t data[4] = {
		static_cast<uint8_t>((h_bridge_settings >> 24) & 0xff),
		static_cast<uint8_t>((h_bridge_settings >> 16) & 0xff),
		static_cast<uint8_t>((h_bridge_settings >> 8) & 0xff),
		static_cast<uint8_t>((h_bridge_settings) & 0xff)
	};

	uint8_t ctrl_1 = make_register_write(REG_OP_CTRL_1);
	uint8_t ctrl_2 = make_register_write(REG_OP_CTRL_2);

	switch (bus_mode) {
	case BusMode::ONE_CHIP:
		transmit_one_chip(ctrl_2, data[2]);
		transmit_one_chip(ctrl_1, data[3]);
		break;

	case BusMode::TWO_CHIPS:
		transmit_two_chips(ctrl_2, data[2], ctrl_2, data[0]);
		transmit_two_chips(ctrl_1, data[3], ctrl_1, data[1]);
		break;
	}
}

void Drv8908::set_output(uint16_t value)
{
	// For a set bit, activate the high side driver, i.e. set 10
	// For an unset bit, activate the low side driver, i.e. set 01
	uint32_t h_bridge_settings = 0;
	for (int bit = 0; bit < 16; bit++) {
		if (value & 1 << bit) {
			h_bridge_settings |= 0b10 << (bit * 2);
		} else {
			h_bridge_settings |= 0b01 << (bit * 2);
		}
	}

	set_h_bridges(h_bridge_settings);
}

void Drv8908::set_high_z()
{
	set_h_bridges(0);
}
