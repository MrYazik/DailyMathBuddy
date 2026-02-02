#!/usr/bin/env bash
set -euo pipefail

# run_bot.sh — скрипт для запуска бота и автоматического перезапуска при падении
# Комментарии на русском поясняют действия скрипта.
#
# Как использовать:
# 1) Сделайте исполняемым: chmod +x run_bot.sh
# 2) Запустите: ./run_bot.sh
#    или: bash run_bot.sh
# 3) Для однократного запуска (без перезапуска) передайте аргумент --once:
#    ./run_bot.sh --once

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Если есть файл .env — автоматически экспортируем переменные из него
# Это удобно для хранения токена в локальном .env (который должен быть в .gitignore)
if [ -f ".env" ]; then
  echo "Загружаю переменные из .env..."
  # Экспортируем все переменные из .env в окружение
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

# Если есть виртуальное окружение .venv — будем использовать его python
if [ -d ".venv" ]; then
  PY_BIN="$PROJECT_DIR/.venv/bin/python"
else
  # fallback на системный python3
  PY_BIN="$(command -v python3 || true)"
  if [ -z "$PY_BIN" ]; then
    echo "Python не найден. Запустите install_for_ubuntu.sh или установите python3." >&2
    exit 1
  fi
fi

# Опция --once — запустить один раз и не перезапускать
ONCE=false
if [ "${1:-}" = "--once" ]; then
  ONCE=true
fi

# Проверим, установлен ли токен в окружении — это защитит от запуска без токена
if [ -z "${DAILY_MATH_BOT_TOKEN:-}" ]; then
  echo "Внимание: переменная DAILY_MATH_BOT_TOKEN не установлена."
  echo "Установите её в .env или экспортируйте перед запуском: export DAILY_MATH_BOT_TOKEN=..."
  exit 1
fi

echo "Использую Python: $PY_BIN"

# Главный цикл: запускаем bot.py, при падении ждём 5 секунд и перезапускаем
while true; do
  echo "[`date +%Y-%m-%dT%H:%M:%S`] Запускаю бота..."
  "$PY_BIN" bot.py
  EXIT_CODE=$?
  echo "[`date +%Y-%m-%dT%H:%M:%S`] Бот завершился с кодом $EXIT_CODE"

  if [ "$ONCE" = true ]; then
    echo "Флаг --once задан — прекращаю перезапуски."
    break
  fi

  echo "Перезапуск через 5 секунд..."
  sleep 5
done

echo "Скрипт завершил работу." 
