#include "parser.hpp"

#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

namespace {

std::vector<std::uint8_t> make_frame(std::uint8_t sequence, std::uint8_t system_id,
                                     std::uint8_t component_id, std::uint32_t message_id,
                                     const std::vector<std::uint8_t>& payload,
                                     std::uint8_t crc_extra) {
    std::vector<std::uint8_t> frame{
        mavlink::kMagicV2,
        static_cast<std::uint8_t>(payload.size()),
        0,
        0,
        sequence,
        system_id,
        component_id,
        static_cast<std::uint8_t>(message_id & 0xFFU),
        static_cast<std::uint8_t>((message_id >> 8U) & 0xFFU),
        static_cast<std::uint8_t>((message_id >> 16U) & 0xFFU),
    };
    frame.insert(frame.end(), payload.begin(), payload.end());
    const std::uint16_t crc = mavlink::frame_crc(frame, crc_extra);
    frame.push_back(static_cast<std::uint8_t>(crc & 0xFFU));
    frame.push_back(static_cast<std::uint8_t>(crc >> 8U));
    return frame;
}

}  // namespace

int main() {
    // 1. Синтетичний фрейм: структура, CRC, пошкодження.
    const auto frame = make_frame(42, 7, 1, 33, {0x01, 0x02, 0x03}, 104);
    assert(mavlink::frame_size(frame) == frame.size());

    const auto parsed = mavlink::parse_header(frame);
    assert(parsed.has_value());
    assert(parsed->sequence == 42);
    assert(parsed->system_id == 7);
    assert(parsed->component_id == 1);
    assert(parsed->message_id == 33);
    assert(parsed->payload.size() == 3);
    assert(!parsed->signed_frame);

    assert(mavlink::checksum_valid(frame, 104));
    assert(!mavlink::checksum_valid(frame, 105));

    auto corrupted = frame;
    corrupted[11] ^= 0xFFU;
    assert(!mavlink::checksum_valid(corrupted, 104));

    auto bad_magic = frame;
    bad_magic[0] = 0xFE;
    assert(!mavlink::parse_header(bad_magic).has_value());

    const std::span<const std::uint8_t> truncated(frame.data(), 5);
    assert(!mavlink::parse_header(truncated).has_value());

    // 2. Еталонний фрейм, згенерований pymavlink:
    //    GLOBAL_POSITION_INT (id=33, crc_extra=104), system=7, seq=42.
    const std::vector<std::uint8_t> reference{
        0xfd, 0x1c, 0x00, 0x00, 0x2a, 0x07, 0x01, 0x21, 0x00, 0x00, 0xe8, 0x03,
        0x00, 0x00, 0x08, 0x13, 0x12, 0x1e, 0x50, 0x80, 0x31, 0x12, 0xc0, 0xd4,
        0x01, 0x00, 0xa0, 0x86, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x28, 0x23, 0xe3, 0xc3,
    };
    assert(reference.size() == 40);
    assert(mavlink::checksum_valid(reference, 104));
    assert(!mavlink::checksum_valid(reference, 105));

    const auto reference_parsed = mavlink::parse_header(reference);
    assert(reference_parsed.has_value());
    assert(reference_parsed->message_id == 33);
    assert(reference_parsed->sequence == 42);
    assert(reference_parsed->system_id == 7);
    assert(reference_parsed->component_id == 1);
    assert(reference_parsed->payload.size() == 28);

    std::cout << "parser tests passed: " << frame.size() << " bytes, reference ok\n";
    return 0;
}
