#pragma once

#include <array>

#include <driver/gpio.h>
#include <esp_event.h>
#include <freertos/FreeRTOS.h>
#include <freertos/timers.h>

#include "memory.hpp"

ESP_EVENT_DECLARE_BASE(GPIO_EVENT);

enum {
	ADDRESS_CHANGED,
	WRITE_PIN_CHANGED,
	WRITE_CYCLE_DONE,
} gpio_event_t;

class GpioInterface {
private:
	std::array<gpio_num_t, ADDRESS_BITS> address_pins;
	std::array<gpio_num_t, DATA_BITS> data_pins;
	gpio_num_t write_pin;
	gpio_num_t clock_pin;

	TimerHandle_t address_change_timer;
	TimerHandle_t write_sample_timer;

	std::array<uint32_t, 8> write_samples;
	unsigned n_write_samples;

	static void address_change_expired(TimerHandle_t timer);
	void on_address_change();

	static void write_sample_expired(TimerHandle_t timer);
	void on_write_sample();

	static void clock_pin_change_isr(void *arg);

public:
	GpioInterface(std::array<gpio_num_t, ADDRESS_BITS> address_pins,
	              std::array<gpio_num_t, DATA_BITS> data_pins,
	              gpio_num_t clock_pin,
	              gpio_num_t write_pin);
};
