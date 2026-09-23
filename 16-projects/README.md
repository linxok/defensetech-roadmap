# 16. Портфоліо-проєкти

> Статус: outline

Перетворити навчальні артефакти на 2–3 сильні публічні проєкти з об’єктивними критеріями готовності.

## Що потрібно зрозуміти

- Один end-to-end проєкт із тестами і демо важить більше, ніж десять навчальних репозиторіїв — рекрутер дивиться 2 хвилини.
- README проєкту: проблема → архітектура → запуск → метрики → обмеження. Скріншот/відео обов’язкові.
- DoD (Definition of Done) — бінарні критерії, а не «працює у мене».
- Capstone покриває більшість вимог; решта проєктів — або компоненти capstone, або глибокі спеціалізації (CV, логи).
- Історія для співбесіди: STAR + числа (латентність, обсяг, час).
- Відкритий код: 1–2 внески в pymavlink/MAVSDK/ArduPilot docs — сильніший сигнал, ніж ще один pet-проєкт.

## Контрольні питання

1. Які 5 критеріїв DoD ви застосовуєте до кожного проєкту?
2. Як показати проєкт за 2 хвилини?
3. Які метрики обов’язково виміряти?
4. Як описати внесок у спільній роботі?
5. Що робити з невдалими експериментами?

## Очікуваний результат

1–2 публічні репозиторії з README, тестами, CI і демо (стартовий шаблон: `solution/starter-template/`).

## Зв'язок з capstone

Розділ «Метрики для портфоліо» у `capstone/README.md`: фіналізувати capstone — README з архітектурою, демо-відео, тести, CI.

## Типові помилки

- Репозиторій без README і скріншотів
- Тільки happy path у тестах
- «Навчальний проєкт №5» замість одного сильного
- Немає чисел: «швидко» замість «p95 = 120 мс»

## Первинні джерела

- [GitHub: README guidelines](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) — структура README
- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) — історія змін
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) — повідомлення комітів
- [GitHub Actions: Building and testing Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python) — CI для репозиторію
- [Semantic Versioning](https://semver.org/) — версії релізів

## Додатково

- [STAR method (The Muse)](https://www.themuse.com/advice/star-interview-method) — формат історій для співбесіди
- [Choose a License](https://choosealicense.com/) — вибір ліцензії для репозиторію

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
