import asyncio

class TelemetryProtocol:
    def datagram_received(self, data, addr):
        print(f"from {addr}: {data.hex()}")

async def main():
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: TelemetryProtocol(),
        local_addr=("0.0.0.0", 14550)
    )
    print("UDP server on 14550")
    await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
