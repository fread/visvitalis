#include <stdio.h>

#include <ranges>

#include <driver/spi_master.h>
#include <esp_console.h>
#include <esp_log.h>

#include "drv8908.hpp"
#include "gpio_assignment.hpp"
#include "gpio_interface.hpp"
#include "memory.hpp"
#include "memory_controller.hpp"

static const char *TAG = "MAIN";

class GpioDebug
	: public GpioListener {
	virtual void on_address_change(uint8_t new_address) {
		ESP_LOGI(TAG, "address change 0x%02x\n", new_address);
	}
	virtual void on_write_pin_change(RwState new_state) {
		if (new_state == RwState::READ) {
			ESP_LOGI(TAG, "read\n");
		} else {
			ESP_LOGI(TAG, "write\n");
		}
	}
	virtual void on_write_cycle_complete(uint8_t new_data) {
		ESP_LOGI(TAG, "data write 0x%02x\n", new_data);
	}
};

extern "C" void app_main(void)
{
	printf("hello world\n");

	Memory mem;

	for (int i = 0; i < 255; i++) {
		mem.write(i, (3 * i) % 256);
	}

	GpioDebug gpio_debug;

	spi_bus_config_t spi_config {
		.mosi_io_num = GpioAssignment::sdi_out,
		.miso_io_num = GpioAssignment::sdi_in,
		.sclk_io_num = GpioAssignment::sdi_clock,
		.max_transfer_sz = 6,
	};

	ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &spi_config, SPI_DMA_DISABLED));

	Drv8908 output_driver(SPI2_HOST,
	                      GpioAssignment::driver_chip_select,
	                      GpioAssignment::driver_fault_in);

	MemoryController mc(mem, output_driver);

	GpioInterface gpios(
		GpioAssignment::address_in,
		GpioAssignment::data_in,
		GpioAssignment::clock_in,
		GpioAssignment::write_not_read_in,
		&mc
		);


	esp_console_dev_uart_config_t uart_config {
		.channel = 0,
		.baud_rate = 115200,
		.tx_gpio_num = -1,
		.rx_gpio_num = -1,
	};
	esp_console_repl_config_t repl_config {
		.max_history_len = 10,
		.history_save_path = NULL,
		.task_stack_size = 4096,
		.task_priority = tskIDLE_PRIORITY,
		.prompt = "mem> ",
	};
	esp_console_repl_t *repl;

	ESP_ERROR_CHECK(esp_console_new_repl_uart(&uart_config, &repl_config, &repl));

	// esp_console_start_repl(repl);

	printf("Setup complete\n");
	while(1) {
		vTaskDelay(1000 / portTICK_PERIOD_MS);

		uint8_t new_address = 0;
		for (gpio_num_t address_pin : std::ranges::reverse_view(GpioAssignment::data_in)) {
			new_address <<= 1;
			new_address |= gpio_get_level(address_pin);
		}
		ESP_LOGI(TAG, "%02x", new_address);

	}
}
