#pragma once

#include <array>

#include <driver/gpio.h>

struct GpioAssignment {
	static constexpr std::array<gpio_num_t, 8> address_in = {
		GPIO_NUM_21,
		GPIO_NUM_47,
		GPIO_NUM_9,
		GPIO_NUM_10,
		GPIO_NUM_14,
		GPIO_NUM_13,
		GPIO_NUM_12,
		GPIO_NUM_11,
	};

	static constexpr std::array<gpio_num_t, 8> data_in = {
		GPIO_NUM_1,
		GPIO_NUM_2,
		GPIO_NUM_42,
		GPIO_NUM_41,
		GPIO_NUM_4,
		GPIO_NUM_5,
		GPIO_NUM_6,
		GPIO_NUM_7,
	};

	static constexpr gpio_num_t clock_in = GPIO_NUM_18;
	static constexpr gpio_num_t write_not_read_in = GPIO_NUM_15;

	static constexpr gpio_num_t driver_fault_in = GPIO_NUM_3;

	static constexpr gpio_num_t sdi_out = GPIO_NUM_45;
	static constexpr gpio_num_t sdi_in = GPIO_NUM_46;
	static constexpr gpio_num_t sdi_clock = GPIO_NUM_40;
	static constexpr gpio_num_t driver_chip_select = GPIO_NUM_39;
};
