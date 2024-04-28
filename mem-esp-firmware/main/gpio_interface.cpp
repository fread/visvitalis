#include "gpio_interface.hpp"

#include <algorithm>
#include <ranges>

#include <esp_log.h>

const char *TAG = "GPIO_INTERFACE";

static constexpr unsigned PIN_CHANGE_DELAY = 100 / portTICK_PERIOD_MS;
static constexpr unsigned WRITE_CYCLE_SAMPLE_TIME = 20 / portTICK_PERIOD_MS;

static constexpr unsigned MIN_WRITE_SAMPLES = 5;

static void IRAM_ATTR reset_timer_isr(void *arg)
{
	TimerHandle_t *timer = (TimerHandle_t*) arg;

	int task_should_yield = false;
	if (xTimerResetFromISR(*timer, &task_should_yield) != pdPASS) {
		// TODO emergency stop
		abort();
	}

	if (task_should_yield == pdTRUE) {
		portYIELD_FROM_ISR();
	}
}

void GpioInterface::address_change_expired(TimerHandle_t timer)
{
	GpioInterface *_this = (GpioInterface*) pvTimerGetTimerID(timer);
	_this->on_address_change();
}

void GpioInterface::on_address_change()
{
	uint8_t new_address = 0;

	for (gpio_num_t address_pin : std::ranges::reverse_view(address_pins)) {
		new_address <<= 1;
		new_address |= gpio_get_level(address_pin);
	}

	listener->on_address_change(new_address);
}

void IRAM_ATTR GpioInterface::write_pin_change_isr(void *arg)
{
	GpioInterface *_this = (GpioInterface*) arg;

	int task_should_yield = false;
	int level = gpio_get_level(_this->write_pin);

	if (xTimerPendFunctionCallFromISR(
		    on_write_pin_change, _this, level, &task_should_yield) != pdPASS) {
		// TODO emergency stop
		abort();
	}

	if (task_should_yield == pdTRUE) {
		portYIELD_FROM_ISR();
	}
}

void GpioInterface::on_write_pin_change(void *arg1, uint32_t level)
{
	GpioInterface *_this = (GpioInterface*) arg1;
	RwState state = (level == 1) ? RwState::WRITE : RwState::READ;
	_this->listener->on_write_pin_change(state);
}

void GpioInterface::write_sample_expired(TimerHandle_t timer)
{
	GpioInterface *_this = (GpioInterface*) pvTimerGetTimerID(timer);
	_this->on_write_sample();
}

void GpioInterface::on_write_sample()
{
	int clock_pin_state = gpio_get_level(clock_pin);
	int write_pin_state = gpio_get_level(write_pin);

	if (clock_pin_state == 1 && write_pin_state == 1) {
		for (int i = 0; i < DATA_IN_BITS; i++) {
			int level = gpio_get_level(data_pins.at(i));
			write_samples.at(i) <<= 1;
			write_samples.at(i) |= level;
		}
		n_write_samples++;

		if (xTimerReset(write_sample_timer, portMAX_DELAY) != pdPASS) {
			ESP_LOGE(TAG, "write_sample_timer is stuck");
			// TODO emergency stop
			abort();
		}

	} else {
		// Write cycle is finished
		// But only execute the write if we have seen enough samples,
		// i.e. clock has been high for long enough
		ESP_LOGI(TAG, "%u samples", n_write_samples);

		if (n_write_samples >= MIN_WRITE_SAMPLES) {
			uint8_t data = 0;

			unsigned limit = std::min(32u, n_write_samples) / 2;

			for (int i = 0; i < DATA_IN_BITS; i++) {
				uint32_t sample = write_samples.at(i);

				if (__builtin_popcount(sample) > limit) {
					data |= 1 << i;
				}
			}

			listener->on_write_cycle_complete(data);
		}

		for(uint32_t &sample : write_samples) {
			sample = 0;
		}
		n_write_samples = 0;
	}
}

GpioInterface::GpioInterface(std::array<gpio_num_t, ADDRESS_BITS> address_pins,
                             std::array<gpio_num_t, DATA_IN_BITS> data_pins,
                             gpio_num_t clock_pin,
                             gpio_num_t write_pin,
                             GpioListener *listener)
	: address_pins(address_pins),
	  data_pins(data_pins),
	  write_pin(write_pin),
	  clock_pin(clock_pin),
	  listener(listener),
	  write_samples(),
	  n_write_samples(0)
{
	ESP_ERROR_CHECK(gpio_install_isr_service(0));

	address_change_timer = xTimerCreate("address change", PIN_CHANGE_DELAY, false, this, address_change_expired);
	if (address_change_timer == NULL) {
		ESP_LOGE(TAG, "Could not create address change timer");
		abort();
	}
	for (gpio_num_t address_pin : address_pins) {
		ESP_ERROR_CHECK(gpio_isr_handler_add(address_pin, reset_timer_isr, &address_change_timer));
	}

	ESP_ERROR_CHECK(gpio_isr_handler_add(write_pin, write_pin_change_isr, this));

	write_sample_timer = xTimerCreate("write_sample", WRITE_CYCLE_SAMPLE_TIME, false, this, write_sample_expired);
	if (write_sample_timer == NULL) {
		ESP_LOGE(TAG, "Could not create write sample timer");
		abort();
	}
	ESP_ERROR_CHECK(gpio_isr_handler_add(clock_pin, reset_timer_isr, &write_sample_timer));

	{
		uint64_t gpio_mask = 0;
		for (gpio_num_t address_pin : address_pins) {
			gpio_mask |= 1ull << address_pin;
		}
		gpio_config_t config {
			.pin_bit_mask = gpio_mask,
			.mode = GPIO_MODE_INPUT,
			.pull_up_en = GPIO_PULLUP_DISABLE,
			.pull_down_en = GPIO_PULLDOWN_ENABLE,
			.intr_type = GPIO_INTR_ANYEDGE,
		};
		ESP_ERROR_CHECK(gpio_config(&config));
	}

	{
		uint64_t gpio_mask = 0;
		for (gpio_num_t data_pin : data_pins) {
			gpio_mask |= 1ull << data_pin;
		}
		gpio_config_t config {
			.pin_bit_mask = gpio_mask,
			.mode = GPIO_MODE_INPUT,
			.pull_up_en = GPIO_PULLUP_DISABLE,
			.pull_down_en = GPIO_PULLDOWN_ENABLE,
			.intr_type = GPIO_INTR_DISABLE,
		};
		ESP_ERROR_CHECK(gpio_config(&config));
	}

	{
		uint64_t gpio_mask = 1ull << write_pin;

		gpio_config_t config {
			.pin_bit_mask = gpio_mask,
			.mode = GPIO_MODE_INPUT,
			.pull_up_en = GPIO_PULLUP_DISABLE,
			.pull_down_en = GPIO_PULLDOWN_ENABLE,
			.intr_type = GPIO_INTR_ANYEDGE,
		};
		ESP_ERROR_CHECK(gpio_config(&config));
	}

	{
		uint64_t gpio_mask = 1ull << clock_pin;

		gpio_config_t config {
			.pin_bit_mask = gpio_mask,
			.mode = GPIO_MODE_INPUT,
			.pull_up_en = GPIO_PULLUP_DISABLE,
			.pull_down_en = GPIO_PULLDOWN_ENABLE,
			.intr_type = GPIO_INTR_POSEDGE,
		};
		ESP_ERROR_CHECK(gpio_config(&config));
	}

	on_address_change();

	int level = gpio_get_level(write_pin);
	on_write_pin_change(this, level);
}
