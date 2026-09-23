# Приклади 14: Наземна станція (GCS)

У `examples/` — фрагменти GCS для проєкту `create-next-app`:
`gcs-page.tsx`, `package.json` (залежності), `tsconfig.json`, `next-env.d.ts`.
Еталон із тестами логіки: `solution/`.

Щоб запустити приклад, створіть Next.js-проєкт, встановіть залежності й покладіть `gcs-page.tsx` як `app/page.tsx`:

```bash
npx create-next-app@latest gcs-ui --ts
cd gcs-ui
npm install leaflet react-leaflet
npm install -D @types/leaflet
```

Задайте адресу WebSocket і запустіть dev-сервер:

```bash
echo 'NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws' > .env.local
npm run dev
```
