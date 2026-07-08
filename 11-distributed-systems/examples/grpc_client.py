import grpc
import telemetry_pb2
import telemetry_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = telemetry_pb2_grpc.TelemetryStub(channel)
frame = telemetry_pb2.TelemetryFrame(drone_id="001", lat=50.45, lon=30.52, alt=100)
ack = stub.StreamTelemetry(iter([frame]))
print(ack)
