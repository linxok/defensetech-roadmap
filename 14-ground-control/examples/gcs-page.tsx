"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface Telemetry {
  drone_id: string;
  lat: number;
  lon: number;
  alt: number;
  battery: number;
}

export default function GCSPage() {
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (event) => setTelemetry(JSON.parse(event.data));
    return () => ws.close();
  }, []);

  const position: [number, number] = telemetry
    ? [telemetry.lat, telemetry.lon]
    : [50.45, 30.52];

  return (
    <main style={{ padding: 16 }}>
      <h1>Ground Control Station</h1>
      {telemetry && (
        <div>
          <p>Drone: {telemetry.drone_id}</p>
          <p>Altitude: {telemetry.alt} m</p>
          <p>Battery: {telemetry.battery}%</p>
        </div>
      )}
      <MapContainer center={position} zoom={13} style={{ height: "500px" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Marker position={position}>
          <Popup>Drone position</Popup>
        </Marker>
      </MapContainer>
    </main>
  );
}
