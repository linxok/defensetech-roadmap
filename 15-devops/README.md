# 15. DevOps для флоту

> Статус: outline

Загорнути систему в контейнери, налаштувати CI/CD і спостережуваність: метрики, логи, алерти.

## Що потрібно зрозуміти

- Docker: багатоетапні збірки, pinned-образи, non-root користувач, healthcheck; `.dockerignore` ріже контекст збірки.
- Compose для локальної розробки, Kubernetes — для масштабу: Deployment, Service, probes, resources, secrets.
- CI має ловити помилки до рев’ю: lint, тести, збірка образу, а для інфраструктурних змін — `docker compose build`.
- Prometheus + Grafana: метрики застосунку і хоста; алерти на SLO (lag черги, error rate, latency p95).
- Логи: структурований JSON із кореляційним id; агрегація — Loki/ELK.
- Секрети: не в git; у K8s — Secrets + RBAC, у CI — захищені змінні.
- Деплой: rolling update, readiness gates, план відкату; для борту — окремий канал оновлень прошивки.

## Контрольні питання

1. Чому образ має запускатися non-root?
2. Які probes потрібні для stateless-сервісу?
3. Як CI перевіряє, що compose-стек збирається?
4. Що алертити в телеметричному пайплайні?
5. Де зберігати секрети?

## Очікуваний результат

Dockerfile, compose і k8s-манифест за чеклістом безпеки (`solution/`) + зелений CI.

## Зв'язок з capstone

Крок 15: capstone розгортається цими ж артефактами; додайте метрики й алерти.

## Типові помилки

- `:latest` в образах — невідтворювані деплої
- Секрети в compose або в git
- Немає healthcheck — compose піднімає сервіс раніше за залежності
- Алерти на все — оператор перестає їх читати

## Первинні джерела

- [Docker: best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) — шари, користувачі, кеш
- [Kubernetes docs](https://kubernetes.io/docs/home/) — probes, resources, secrets
- [Compose file reference](https://docs.docker.com/compose/compose-file/) — healthcheck, depends_on, profiles
- [Prometheus docs](https://prometheus.io/docs/introduction/overview/) — метрики і алерти
- [GitHub Actions](https://docs.github.com/en/actions) — workflow, jobs, cache

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
