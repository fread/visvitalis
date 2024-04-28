#pragma once

#include "drv8908.hpp"
#include "gpio_interface.hpp"
#include "memory.hpp"

class MemoryController
	: public GpioListener {
private:
	Memory &memory;
	Drv8908 &output_driver;

	uint8_t current_address;
	RwState current_rw_state;

	bool shutdown;

public:
	MemoryController(Memory &memory, Drv8908 &output_driver);

	virtual ~MemoryController();

	virtual void on_address_change(uint8_t new_address);

	virtual void on_write_pin_change(RwState new_state);

	virtual void on_write_cycle_complete(uint8_t new_data);

	virtual void invalidate();
};
