#include "gpio_interface.hpp"

#include <algorithm>

static constexpr unsigned PIN_CHANGE_DELAY = 20 / portTICK_PERIOD_MS;
static constexpr unsigned WRITE_CYCLE_SAMPLE_TIME = 5 / portTICK_PERIOD_MS;

static constexpr unsigned MIN_WRITE_SAMPLES = 5;

static void IRAM_ATTR address_pin_change_isr(void *arg)
{
	TimerHandle_t *timer = (TimerHandle_t*) arg;

	int task_should_yield = false;
	xTimerResetFromISR(*timer, &task_should_yield);

	if (task_should_yield == pdTRUE) {
		portYIELD_FROM_ISR();
	}
}

void GpioInterface::address_change_expired(TimerHandle_t timer)
{
	GpioInterface *caller = (GpioInterface*) pvTimerGetTimerID(timer);
	caller->on_address_change();
}

void GpioInterface::on_address_change()
{
	uint8_t new_address = 0;

	for (gpio_num_t address_pin : address_pins) {
		new_address |= gpio_get_level(address_pin);
		new_address <<= 1;
	}

	ESP_ERROR_CHECK(esp_event_post(GPIO_EVENT, ADDRESS_CHANGED, NULL, 0, portMAX_DELAY));
}

static void IRAM_ATTR write_pin_change_isr(void *arg)
{
	int task_should_yield = false;

	ESP_ERROR_CHECK(esp_event_isr_post(GPIO_EVENT, WRITE_PIN_CHANGED, NULL, 0, &task_should_yield));

	if (task_should_yield == pdTRUE) {
		portYIELD_FROM_ISR();
	}
}

void IRAM_ATTR GpioInterface::clock_pin_change_isr(void *arg)
{
	GpioInterface *gpios = (GpioInterface*) arg;

	int task_should_yield = false;
	int level = gpio_get_level(gpios->clock_pin);

	if (level == 1) {
		xTimerResetFromISR(gpios->write_sample_timer, &task_should_yield);
		if (task_should_yield == pdTRUE) {
			portYIELD_FROM_ISR();
		}
	}
}

void GpioInterface::write_sample_expired(TimerHandle_t timer)
{
	GpioInterface *caller = (GpioInterface*) pvTimerGetTimerID(timer);
	caller->on_write_sample();
}

void GpioInterface::on_write_sample()
{
	int clock_pin_state = gpio_get_level(clock_pin);

	if (clock_pin_state == 1) {
		for (int i = 0; i < DATA_BITS; i++) {
			int level = gpio_get_level(data_pins[i]);
			write_samples[i] |= level;
			write_samples[i] <<= 1;
		}
		n_write_samples++;

		xTimerReset(write_sample_timer, portMAX_DELAY);

	} else {
		// Write cycle is finished
		// But only execute the write if we have seen enough samples,
		// i.e. clock has been high for long enough
		if (n_write_samples >= MIN_WRITE_SAMPLES) {
			uint8_t data = 0;

			unsigned limit = std::min(32u, n_write_samples) / 2;

			for (int i = 0; i < DATA_BITS; i++) {
				uint32_t sample = write_samples[i];

				if (__builtin_popcount(sample) > limit) {
					data |= 1 << i;
				}
			}
		}

		for(uint32_t &sample : write_samples) {
			sample = 0;
		}
		n_write_samples = 0;
	}
}

GpioInterface::GpioInterface(std::array<gpio_num_t, ADDRESS_BITS> address_pins,
              std::array<gpio_num_t, DATA_BITS> data_pins,
              gpio_num_t clock_pin,
              gpio_num_t write_pin)
	: address_pins(address_pins),
	  data_pins(data_pins),
	  write_pin(write_pin),
	  clock_pin(clock_pin),
	  write_samples(),
	  n_write_samples(0)
{
	// TODO GPIO setup missing, including activating interrupts

	gpio_install_isr_service(0);

	address_change_timer = xTimerCreate("address change", PIN_CHANGE_DELAY, false, this, address_change_expired);
	for (gpio_num_t address_pin : address_pins) {
		gpio_isr_handler_add(address_pin, address_pin_change_isr, &address_change_timer);
	}

	gpio_isr_handler_add(write_pin, write_pin_change_isr, this);

	write_sample_timer = xTimerCreate("write_sample", WRITE_CYCLE_SAMPLE_TIME, false, this, write_sample_expired);
	gpio_isr_handler_add(clock_pin, clock_pin_change_isr, this);
}
