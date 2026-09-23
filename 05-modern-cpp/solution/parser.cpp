#include "parser.hpp"

namespace mavlink {
namespace {

// Алгоритм MAVLink: CRC-16/MCRF4XX по байтах (див. mavlink.io).
std::uint16_t accumulate(std::uint8_t data, std::uint16_t crc) {
    std::uint8_t tmp = static_cast<std::uint8_t>(data ^ (crc & 0xFFU));
    tmp = static_cast<std::uint8_t>(tmp ^ (tmp << 4U));
    return static_cast<std::uint16_t>(
        (crc >> 8U) ^ (static_cast<std::uint16_t>(tmp) << 8U) ^
        (static_cast<std::uint16_t>(tmp) << 3U) ^
        (static_cast<std::uint16_t>(tmp) >> 4U));
}

}  // namespace

std::uint16_t x25_crc(std::span<const std::uint8_t> data, std::uint16_t crc) {
    for (const std::uint8_t byte : data) {
        crc = accumulate(byte, crc);
    }
    return crc;
}

std::size_t frame_size(std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kHeaderSize) {
        return 0;
    }
    const std::size_t payload_end = kHeaderSize + bytes[1] + kChecksumSize;
    const bool signed_frame = (bytes[2] & kIncompatSigned) != 0U;
    return signed_frame ? payload_end + kSignatureSize : payload_end;
}

std::uint16_t frame_crc(std::span<const std::uint8_t> frame, std::uint8_t crc_extra) {
    if (frame.size() < kHeaderSize) {
        return 0xFFFFU;
    }
    const std::size_t payload_end = kHeaderSize + frame[1];
    if (frame.size() < payload_end) {
        return 0xFFFFU;
    }
    return accumulate(crc_extra, x25_crc(frame.subspan(1, payload_end - 1)));
}

std::optional<Frame> parse_header(std::span<const std::uint8_t> bytes) {
    if (bytes.size() < kHeaderSize || bytes[0] != kMagicV2) {
        return std::nullopt;
    }
    const std::size_t size = frame_size(bytes);
    if (size == 0 || bytes.size() < size) {
        return std::nullopt;
    }

    Frame frame;
    frame.sequence = bytes[4];
    frame.system_id = bytes[5];
    frame.component_id = bytes[6];
    frame.message_id = static_cast<std::uint32_t>(bytes[7]) |
                       (static_cast<std::uint32_t>(bytes[8]) << 8U) |
                       (static_cast<std::uint32_t>(bytes[9]) << 16U);
    frame.payload.assign(
        bytes.begin() + static_cast<std::ptrdiff_t>(kHeaderSize),
        bytes.begin() + static_cast<std::ptrdiff_t>(kHeaderSize + bytes[1]));
    frame.signed_frame = (bytes[2] & kIncompatSigned) != 0U;
    return frame;
}

bool checksum_valid(std::span<const std::uint8_t> frame, std::uint8_t crc_extra) {
    const std::size_t size = frame_size(frame);
    if (size == 0 || frame.size() < size) {
        return false;
    }
    const std::uint16_t expected = frame_crc(frame, crc_extra);
    const std::size_t crc_offset = kHeaderSize + frame[1];
    const auto actual = static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(frame[crc_offset]) |
        (static_cast<std::uint16_t>(frame[crc_offset + 1]) << 8U));
    return expected == actual;
}

}  // namespace mavlink
