#include "memory_controller.hpp"

#include <esp_log.h>

static const char *TAG = "MEMORY CONTROLLER";

MemoryController::MemoryController(Memory &memory, Drv8908 &output_driver)
	: memory(memory),
	  output_driver(output_driver)
{
	output_driver.set_high_z();
}

MemoryController::~MemoryController()
{
	output_driver.set_high_z();
}

void MemoryController::on_address_change(uint8_t new_address)
{
	ESP_LOGI(TAG, "new address %x", new_address);
	current_address = new_address;
	if (current_rw_state == RwState::READ) {
		output_driver.set_output(memory.read(current_address));
	}
}

void MemoryController::on_write_pin_change(RwState new_state)
{
	current_rw_state = new_state;

	if (current_rw_state == RwState::WRITE) {
		ESP_LOGI(TAG, "state: write");
		output_driver.set_high_z();
	} else {
		ESP_LOGI(TAG, "state: read");
		output_driver.set_output(memory.read(current_address));
	}
}

void MemoryController::on_write_cycle_complete(uint8_t new_data)
{
	ESP_LOGI(TAG, "write cycle %x", new_data);
	memory.write(current_address, new_data);
}
