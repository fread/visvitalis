#include "memory.hpp"

#include <format>
#include <sstream>

Memory::Memory()
	: memory{}
{

}

uint16_t Memory::read(uint8_t address) const
{
	return memory[address];
}

void Memory::write(uint8_t address, uint16_t data)
{
	memory[address] = data;
}

std::array<uint16_t, MEMORY_SIZE> Memory::dump() const
{
	return memory;
}

std::string Memory::show() const
{
	bool show_one_byte = true;

	for (uint16_t word : memory) {
		if (word > 0xff) {
			show_one_byte = false;
			break;
		}
	}

	std::stringstream result;

	for (int i = 0; i < MEMORY_SIZE; i++) {
		uint16_t word = memory[i];

		if (word == 0x0000) {
			if (show_one_byte) {
				result << "..";
			} else {
				result << "....";
			}
		} else {
			if (show_one_byte) {
				result << std::format("{:02x}", word);
			} else {
				result << std::format("{:04x}", word);
			}
		}

		if (i % 16 == 15) {
			result << std::endl;
		} else {
			result << " ";
		}
	}

	return result.str();
}
