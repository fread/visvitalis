#include <stdio.h>

#include <driver/spi_master.h>
#include <esp_log.h>

#include "drv8908.hpp"
#include "gpio_assignment.hpp"

static const char *TAG = "MAIN";

extern "C" void app_main(void)
{
	printf("hello world\n");

	spi_bus_config_t spi_config = {};
	spi_config.mosi_io_num = GpioAssignment::sdi_out;
	spi_config.miso_io_num = GpioAssignment::sdi_in;
	spi_config.sclk_io_num = GpioAssignment::sdi_clock;
	spi_config.max_transfer_sz = 6;

	ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &spi_config, SPI_DMA_DISABLED));

	Drv8908 output_driver(SPI2_HOST, GpioAssignment::driver_chip_select, GpioAssignment::driver_fault_in);

	while (true) {
		for (int i = 0; i < 65536; i++) {
			ESP_LOGI(TAG, "");
			ESP_LOGI(TAG, "output %d", i);
			output_driver.set_output(i);

			vTaskDelay(10 / portTICK_PERIOD_MS);
		}
	}
}
