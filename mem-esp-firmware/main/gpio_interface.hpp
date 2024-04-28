#pragma once

#include <array>

#include <driver/gpio.h>
#include <freertos/FreeRTOS.h>
#include <freertos/timers.h>

#include "memory.hpp"

enum class RwState {
	READ,
	WRITE
};

class GpioListener {
public:
	virtual ~GpioListener() {}

	virtual void on_address_change(uint8_t new_address) = 0;
	virtual void on_write_pin_change(RwState new_state) = 0;
	virtual void on_write_cycle_complete(uint8_t new_data) = 0;
	virtual void invalidate() = 0;
};

class GpioInterface {
private:
	std::array<gpio_num_t, ADDRESS_BITS> &address_pins;
	std::array<gpio_num_t, DATA_IN_BITS> &data_pins;
	gpio_num_t write_pin;
	gpio_num_t clock_pin;

	GpioListener *listener;

	TimerHandle_t address_change_timer;
	TimerHandle_t write_sample_timer;

	std::array<uint32_t, DATA_IN_BITS> write_samples;
	unsigned n_write_samples;

	static void address_change_expired(TimerHandle_t timer);
	void on_address_change();

	static void write_pin_change_isr(void *arg);
	static void on_write_pin_change(void *arg1, uint32_t level);

	static void clock_pin_change_isr(void *arg);
	static void write_sample_expired(TimerHandle_t timer);
	void on_write_sample();


public:
	GpioInterface(std::array<gpio_num_t, ADDRESS_BITS> address_pins,
	              std::array<gpio_num_t, DATA_IN_BITS> data_pins,
	              gpio_num_t clock_pin,
	              gpio_num_t write_pin,
	              GpioListener *listener);
};
