# Лабораторна робота 14: React + Leaflet GCS

## Мета

Створити веб-GCS: мапа Leaflet з маркером і трейлом, телеметрія через WebSocket і чиста логіка кадрів, покрита тестами Node.

## Передумови

- Node.js 20+
- `create-next-app`

## Структура

Три файли мають лежати в одній теці (у репозиторії — `solution/`; `--target` перевірки вказує на вашу теку):

- `telemetry-format.mjs` — чисті функції обробки кадру телеметрії;
- `telemetry-format.test.mjs` — тести на `node:test`;
- `gcs-page.tsx` — React-компонент GCS з мапою Leaflet і WebSocket.

## Кроки

### 1. Створення проєкту

```bash
npx create-next-app@latest gcs-lab --ts
cd gcs-lab
```

### 2. Встановлення залежностей

```bash
npm install leaflet react-leaflet
npm install -D @types/leaflet
```

У `react-leaflet` 4 типи вбудовані, тому застарілий `@types/react-leaflet` не встановлюйте.

### 3. Чиста логіка — `telemetry-format.mjs`

Експортуйте рівно три функції з цими іменами: `isValidTelemetry(payload)`, `formatTelemetry(payload)`, `appendTrail(trail, point, maxPoints = 100)`. Їх імпортують і тести, і компонент.

```js
// Чисті функції GCS: валідація кадру, форматування, траєкторія.
// Тестуються без React і браузера: node --test telemetry-format.test.mjs

export function isValidTelemetry(payload) {
  if (payload === null || typeof payload !== 'object') {
    return false;
  }
  const { lat, lon, alt, battery } = payload;
  return (
    Number.isFinite(lat) && lat >= -90 && lat <= 90 &&
    Number.isFinite(lon) && lon >= -180 && lon <= 180 &&
    Number.isFinite(alt) && alt >= -500 &&
    Number.isFinite(battery) && battery >= 0 && battery <= 100
  );
}

export function formatTelemetry(payload) {
  return {
    position: [payload.lat, payload.lon],
    altitude: `${payload.alt.toFixed(1)} m`,
    battery: `${Math.round(payload.battery)}%`,
    droneId: payload.drone_id ?? 'unknown',
  };
}

export function appendTrail(trail, point, maxPoints = 100) {
  const next = [...trail, point];
  return next.length > maxPoints ? next.slice(next.length - maxPoints) : next;
}
```

### 4. Тести — `telemetry-format.test.mjs`

Тести мають покривати і валідний кадр, і поганий вхід (NaN/вихід за діапазон), і обмеження трейлу:

```js
import test from 'node:test';
import assert from 'node:assert/strict';

import { appendTrail, formatTelemetry, isValidTelemetry } from './telemetry-format.mjs';

const VALID = { drone_id: 'd1', lat: 50.45, lon: 30.52, alt: 120.4, battery: 87 };

test('accepts a valid telemetry frame', () => {
  assert.equal(isValidTelemetry(VALID), true);
});

test('rejects out-of-range battery and coordinates', () => {
  assert.equal(isValidTelemetry({ ...VALID, battery: 150 }), false);
  assert.equal(isValidTelemetry({ ...VALID, lat: 100 }), false);
  assert.equal(isValidTelemetry(null), false);
  assert.equal(isValidTelemetry({ lat: 'x' }), false);
});

test('formats telemetry for the UI', () => {
  const view = formatTelemetry(VALID);
  assert.deepEqual(view.position, [50.45, 30.52]);
  assert.equal(view.altitude, '120.4 m');
  assert.equal(view.battery, '87%');
});

test('caps the trail length', () => {
  let trail = [];
  for (let i = 0; i < 150; i += 1) {
    trail = appendTrail(trail, [i, i], 100);
  }
  assert.equal(trail.length, 100);
  assert.deepEqual(trail[0], [50, 50]);
});
```

Запуск тестів:

```bash
node --test telemetry-format.test.mjs
```

### 5. Компонент GCS — `gcs-page.tsx`

Компонент мусить містити `'use client'`, `useEffect`, `new WebSocket`, `MapContainer`, `TileLayer`, `Marker`, а URL WebSocket має бути налаштовуваним через `NEXT_PUBLIC_WS_URL` — не константою з `localhost:8000`.

```tsx
'use client';

import { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import { appendTrail, formatTelemetry, isValidTelemetry } from './telemetry-format.mjs';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8000/ws';

interface Telemetry {
  drone_id?: string;
  lat: number;
  lon: number;
  alt: number;
  battery: number;
}

export default function GCSPage() {
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);
  const [trail, setTrail] = useState<[number, number][]>([]);
  const [status, setStatus] = useState('connecting');

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    ws.onopen = () => setStatus('live');
    ws.onclose = () => setStatus('disconnected');
    ws.onmessage = (event) => {
      let payload: unknown;
      try {
        payload = JSON.parse(event.data);
      } catch {
        setStatus('bad-json');
        return;
      }
      if (!isValidTelemetry(payload)) {
        return;
      }
      const frame = payload as Telemetry;
      setTelemetry(frame);
      setTrail((current) => appendTrail(current, [frame.lat, frame.lon]));
    };
    return () => ws.close();
  }, []);

  const view = useMemo(() => (telemetry ? formatTelemetry(telemetry) : null), [telemetry]);
  const position: [number, number] = view ? view.position : [50.45, 30.52];

  return (
    <main style={{ padding: 16 }}>
      <h1>Ground Control Station</h1>
      <p>Status: {status}</p>
      {view && (
        <div>
          <p>Drone: {view.droneId}</p>
          <p>Altitude: {view.altitude}</p>
          <p>Battery: {view.battery}</p>
        </div>
      )}
      <MapContainer center={position} zoom={13} style={{ height: '500px' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Marker position={position}>
          <Popup>Drone position</Popup>
        </Marker>
        {trail.length > 1 && <Polyline positions={trail} />}
      </MapContainer>
    </main>
  );
}
```

Під час інтеграції з Next.js покладіть компонент як `app/page.tsx` (або імпортуйте його) і задайте адресу backend:

```bash
echo 'NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws' > .env.local
```

### 6. Запуск

```bash
npm run dev
```

## Перевірка

Проженіть тести логіки та контракт артефактів:

```bash
node --test telemetry-format.test.mjs
python checks/check_lab.py --target solution
```

У команді `--target` вкажіть свою теку з трьома файлами (у репозиторії — `solution`). Очікуваний рядок: `PASS: логіка GCS покрита тестами, компонент містить мапу і WS`.

У браузері: телеметрія оновлюється, трейл малюється, при зупинці backend стан переходить у offline.

## Розбір збоїв

- Мапа порожня — контейнер без висоти
- `use client` відсутній — SSR-помилка Leaflet
- NaN у координатах ламає карту — потрібна валідація кадру
- WS не підключається — не задано `NEXT_PUBLIC_WS_URL`

## Очікуваний результат

- Next.js проєкт.
- `telemetry-format.mjs` + `telemetry-format.test.mjs` із зеленими тестами.
- `gcs-page.tsx`: мапа з маркером, трейл і панель телеметрії.
