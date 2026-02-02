
#!/usr/bin/env bash
set -euo pipefail

# install_linux.sh — установщик для Ubuntu 24.04
# Этот скрипт выполняет все шаги, необходимые для запуска проекта:
# 1) Обновляет индекс пакетов apt
# 2) Устанавливает системные зависимости (python3, инструменты сборки и т.д.)
# 3) Создаёт виртуальное окружение в `.venv`
# 4) Обновляет pip и устанавливает Python-зависимости из `requirements.txt`
# 5) Создаёт файл `.env.example` с примером переменной окружения
# 6) Выводит рекомендации по защите токенов и инструкции по запуску
#
# Использование: запустите от root или через sudo:
#   sudo bash install_linux.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Если скрипт не запущен от root, используем sudo для apt-команд
if [ "$EUID" -ne 0 ]; then
	SUDO=sudo
else
	SUDO=
fi

# ===== Обновление пакетов apt =====
echo "[1/6] Обновляю пакеты apt..."
$SUDO apt update -y

# ===== Установка системных зависимостей =====
# Устанавливаем Python, venv, pip, компиляторы и библиотеки, часто необходимые
echo "[2/6] Устанавливаю системные зависимости (python3, venv, pip и сборочные инструменты)..."
$SUDO apt install -y python3 python3-venv python3-pip build-essential libssl-dev libffi-dev git curl

# ===== Создание виртуального окружения =====
# Создаём виртуальное окружение `.venv` в корне проекта. Если оно уже есть — пропускаем.
echo "[3/6] Создаю виртуальное окружение в .venv (в корне проекта)..."
PYTHON_BIN="$(command -v python3)"
if [ -z "$PYTHON_BIN" ]; then
	echo "Не найден python3 в PATH — прерываю." >&2
	exit 1
fi

cd "$PROJECT_DIR"
if [ -d ".venv" ]; then
	# Уже существует, не перезаписываем, чтобы не сломать рабочее окружение
	echo "Виртуальное окружение .venv уже существует — пропускаю создание."
else
	# Создаём новое виртуальное окружение с системным python3
	"$PYTHON_BIN" -m venv .venv
fi

uVE_PIP="$PROJECT_DIR/.venv/bin/pip"
VE_PY="$PROJECT_DIR/.venv/bin/python"

# ===== Установка Python-зависимостей =====
# Обновляем pip/setuptools/wheel, затем устанавливаем зависимости из requirements.txt
echo "[4/6] Обновляю pip и устанавливаю зависимости из requirements.txt..."
"$VE_PIP" install --upgrade pip setuptools wheel
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
	"$VE_PIP" install -r "$PROJECT_DIR/requirements.txt"
else
	# Если requirements.txt отсутствует — ничего не делаем. В проекте он есть, но проверка для надёжности.
	echo "Файл requirements.txt не найден — пропускаю установку pip-зависимостей."
fi

# ===== Создание примера .env и рекомендации по секретам =====
# Создаём `.env.example` с примером переменной окружения, чтобы не хранить токены в коде
echo "[5/6] Создаю .env.example и даю рекомендации по работе с секретами..."
cat > "$PROJECT_DIR/.env.example" <<'EOF'
# Пример файла .env — не добавляйте реальные токены в репозиторий
DAILY_MATH_BOT_TOKEN=your_bot_token_here
EOF

# Подсказки пользователю:
echo "Если у вас сейчас есть файл config.py с токеном — удалите его из индекса git, чтобы секрет не попадал в коммиты:"
echo "  git rm --cached config.py && git commit -m 'Stop tracking config.py'"
echo "Рекомендуется использовать переменные окружения или .env (и добавить .env в .gitignore)."

# ===== Завершение и инструкции по запуску =====
echo "[6/6] Готово. Как запустить проект:"
echo "1) Активировать виртуальное окружение: source .venv/bin/activate"
echo "2) Установить переменную окружения токена (или экспортировать в .env):"
echo "   export DAILY_MATH_BOT_TOKEN=your_bot_token_here"
echo "3) Запустить бота: .venv/bin/python bot.py"

echo "Установщик завершил работу."

