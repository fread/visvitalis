#include <stdio.h>

#include <driver/spi_master.h>
#include <esp_log.h>

#include "drv8908.hpp"
#include "gpio_assignment.hpp"
#include "gpio_interface.hpp"
#include "memory.hpp"

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

	GpioDebug gpio_debug;

	GpioInterface gpios(
		GpioAssignment::address_in,
		GpioAssignment::data_in,
		GpioAssignment::clock_in,
		GpioAssignment::write_not_read_in,
		&gpio_debug
		);

	printf("Setup complete\n");
	while(1) {
		vTaskDelay(1000 / portTICK_PERIOD_MS);
	}
}

void output_driver_test()
{
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

	while (true) {
		for (int i = 0; i < 65536; i++) {
			output_driver.set_output(i);

			vTaskDelay(10 / portTICK_PERIOD_MS);
		}
	}
}
