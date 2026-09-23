// Мінімальний парсер MAVLink v2-фреймів: заголовок, payload, CRC.
#pragma once

#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

namespace mavlink {

inline constexpr std::uint8_t kMagicV2 = 0xFD;
inline constexpr std::size_t kHeaderSize = 10;
inline constexpr std::size_t kChecksumSize = 2;
inline constexpr std::size_t kSignatureSize = 13;
inline constexpr std::uint8_t kIncompatSigned = 0x01;

struct Frame {
    std::uint8_t sequence{};
    std::uint8_t system_id{};
    std::uint8_t component_id{};
    std::uint32_t message_id{};
    std::vector<std::uint8_t> payload;
    bool signed_frame{};
};

// CRC-16/MCRF4XX, який використовує MAVLink.
std::uint16_t x25_crc(std::span<const std::uint8_t> data, std::uint16_t crc = 0xFFFF);

// CRC фрейму: байти від payload length до кінця payload + crc_extra.
std::uint16_t frame_crc(std::span<const std::uint8_t> frame, std::uint8_t crc_extra);

// Повертає Frame, якщо заголовок і довжина коректні (CRC не перевіряється).
std::optional<Frame> parse_header(std::span<const std::uint8_t> bytes);

// Повна перевірка: заголовок + CRC + підпис (довжина).
bool checksum_valid(std::span<const std::uint8_t> frame, std::uint8_t crc_extra);

std::size_t frame_size(std::span<const std::uint8_t> bytes);

}  // namespace mavlink
