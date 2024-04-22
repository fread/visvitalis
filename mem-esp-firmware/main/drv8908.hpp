#pragma once

#include <driver/gpio.h>
#include <driver/spi_master.h>

enum class BusMode {
	ONE_CHIP,
	TWO_CHIPS,
};

class Drv8908 {
private:
	spi_device_handle_t spi_device;
	gpio_num_t fault_pin;
	BusMode bus_mode;

	BusMode probe_bus_for_chip_count();

	void disable_open_load_detection();

	uint8_t transmit_one_chip(uint8_t address, uint8_t data);
	uint8_t transmit_two_chips(uint8_t address, uint8_t data);
	uint8_t transmit_two_chips(uint8_t address1, uint8_t data1, uint8_t address2, uint8_t data2);

	void set_h_bridges(uint32_t h_bridge_settings);

public:
	Drv8908(spi_host_device_t spi_host,
	        gpio_num_t chip_select_pin,
		gpio_num_t fault_pin);

	void set_output(uint16_t value);

	void set_high_z();
};
