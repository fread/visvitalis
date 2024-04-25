#pragma once

#include <array>
#include <cstdint>
#include <climits>
#include <string>

static constexpr unsigned ADDRESS_BITS = sizeof(uint8_t) * CHAR_BIT;
static constexpr unsigned DATA_BITS = sizeof(uint16_t) * CHAR_BIT;

static constexpr unsigned MEMORY_SIZE = 1 << ADDRESS_BITS;

class Memory {
private:
	std::array<uint16_t, MEMORY_SIZE> memory;

public:
	Memory();

	uint16_t read(uint8_t address) const;

	void write(uint8_t address, uint16_t data);

	std::array<uint16_t, MEMORY_SIZE> dump() const;

	std::string show() const;
};
