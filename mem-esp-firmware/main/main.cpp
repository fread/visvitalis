#include <stdio.h>
#include <string.h>

#include <ranges>

#include <driver/spi_master.h>
#include <esp_console.h>
#include <esp_log.h>
#include <linenoise/linenoise.h>

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
	virtual void invalidate() {
		ESP_LOGI(TAG, "invalidate\n");
	}
};

static Memory mem;
static MemoryController *controller;
static Drv8908 *driver;

static int handle_clear_cmd(int argc, char **argv)
{
	for (int i = 0; i < MEMORY_SIZE; i++) {
		mem.write(i, 0);
	}

	return 0;
}

static int handle_write_cmd(int argc, char **argv)
{
	if (argc != 3) {
		printf("Wrong number of arguments (2 expected)\n");
		return 2;
	}

	uint8_t address;
	uint16_t data;

	int success = sscanf(argv[1], "%hhx", &address);
	if (success != 1) {
		printf("Cannot parse address\n");
		return 2;
	}
	success = sscanf(argv[2], "%hx", &data);
	if (success != 1) {
		printf("Cannot parse address\n");
		return 2;
	}

	mem.write(address, data);
	controller->invalidate();

	return 0;
}

static int handle_load_cmd(int argc, char **argv)
{
	int addr = 0;
	char *line = NULL;

	while (addr < MEMORY_SIZE) {
		line = linenoise("");

		if (line == NULL || strcmp(line, "") == 0) {
			goto exit_ok;
			break;
		}

		char *argv[257];

		size_t n_args = esp_console_split_argv(line, argv, 257);

		for (int i = 0; i < n_args; i++) {
			uint16_t data = 0;
			int success = sscanf(argv[i], "%hx", &data);
			if (success != 1) {
				printf("Could not parse value \"%s\"\n", argv[i]);
				goto exit_error;
			}

			mem.write(addr, data);
			addr++;

			if (addr >= MEMORY_SIZE && i < n_args - 1) {
				printf("Warning: extra data at end of line\n");
				goto exit_ok;
			}
		}

		free(line);
	}

exit_ok:
	free(line);
	controller->invalidate();
	return 0;

exit_error:
	free(line);
	controller->invalidate();
	return 2;
}

static int handle_dump_cmd(int argc, char **argv)
{
	std::string contents = mem.show();
	printf("%s\n", contents.c_str());

	return 0;
}

static int handle_reset_fault_cmd(int argc, char **argv)
{
	driver->reset_fault();
	return 0;
}

extern "C" void app_main(void)
{
	printf("hello world\n");

	for (int i = 0; i < MEMORY_SIZE; i++) {
		mem.write(i, (3 * i) % MEMORY_SIZE);
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
	driver = &output_driver;

	MemoryController mc(mem, output_driver);
	controller = &mc;

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

	esp_console_cmd_t clear_cmd {
		.command = "clear",
		.help = "Clear memory (reset to 0x00)",
		.hint = "",
		.func = handle_clear_cmd,
		.argtable = NULL,
	};
	esp_console_cmd_register(&clear_cmd);

	esp_console_cmd_t write_cmd {
		.command = "w",
		.help = "Write into memory",
		.hint = "",
		.func = handle_write_cmd,
		.argtable = NULL,
	};
	esp_console_cmd_register(&write_cmd);

	esp_console_cmd_t load_cmd {
		.command = "load",
		.help = "Load a memory image",
		.hint = "",
		.func = handle_load_cmd,
		.argtable = NULL,
	};
	esp_console_cmd_register(&load_cmd);

	esp_console_cmd_t dump_cmd {
		.command = "dump",
		.help = "dump memory contents",
		.hint = "",
		.func = handle_dump_cmd,
		.argtable = NULL,
	};
	esp_console_cmd_register(&dump_cmd);

	esp_console_cmd_t reset_fault_cmd {
		.command = "reset_fault",
		.help = "reset driver fault flag",
		.hint = "",
		.func = handle_reset_fault_cmd,
		.argtable = NULL,
	};
	esp_console_cmd_register(&reset_fault_cmd);

	printf("Setup complete\n");

	esp_console_start_repl(repl);
	while(1) {
		vTaskDelay(1000 / portTICK_PERIOD_MS);
	}
}
