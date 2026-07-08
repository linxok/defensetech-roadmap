# Лабораторна робота 14: React + Leaflet GCS

## Мета

Створити простий веб-інтерфейс GCS з мапою і панеллю телеметрії.

## Передумови

- Node.js 18+
- `create-next-app`

## Кроки

### 1. Створення проєкту

```bash
npx create-next-app@latest gcs-lab
```

### 2. Встановлення залежностей

```bash
cd gcs-lab
npm install leaflet react-leaflet
npm install -D @types/leaflet @types/react-leaflet
```

### 3. Компонент мапи

```jsx
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function DroneMap({ position }) {
  return (
    <MapContainer center={position} zoom={13} style={{ height: '400px' }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Marker position={position} />
    </MapContainer>
  );
}
```

### 4. Панель телеметрії

```jsx
export function TelemetryPanel({ alt, battery }) {
  return (
    <div>
      <p>Altitude: {alt} m</p>
      <p>Battery: {battery}%</p>
    </div>
  );
}
```

### 5. Запуск

```bash
npm run dev
```

## Очікуваний результат

- Next.js проєкт.
- Мапа з маркером.
- Панель телеметрії.
