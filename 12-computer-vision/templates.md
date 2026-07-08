# Шаблони та фрагменти 12

## Шаблон README для проєкту

```markdown
# Project Name

## Опис
Короткий опис проєкту.

## Технології
- Технологія 1
- Технологія 2

## Встановлення
```bash
pip install -r requirements.txt
```

## Запуск
```bash
python main.py
```

## Тести
```bash
pytest
```

## Docker
```bash
docker-compose up
```

## Ліцензія
MIT
```

## Шаблон docker-compose.yml

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
```

## Шаблон GitHub Actions

```yaml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
```

## Шаблон unit-тесту Python

```python
def test_example():
    assert True
```

## Шаблон CMake тесту C++

```cpp
#include <cassert>
int main() {
    assert(2 + 2 == 4);
    return 0;
}
```

## Шаблон ROS2 node

```python
import rclpy
from std_msgs.msg import String

rclpy.init()
node = rclpy.create_node('node')
pub = node.create_publisher(String, 'topic', 10)
```

## Шаблон FastAPI endpoint

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}
```

## Шаблон React компоненту

```jsx
export default function Component({ data }) {
  return <div>{data}</div>;
}
```
