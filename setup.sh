#!/bin/bash
# WexTweaks Linux - Установщик

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${YELLOW}          ⚡ WEXTWEAKS LINUX УСТАНОВЩИК ⚡          ${BLUE}║${NC}"
echo -e "${BLUE}║${GREEN}         Оптимизация Linux для игр и скорости       ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не найден! Установите Python3.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} найден${NC}"

# Установка зависимостей
echo -e "\n${YELLOW}📦 Установка зависимостей...${NC}"

# Определяем дистрибутив
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    DISTRO=$(uname -s)
fi

case $DISTRO in
    ubuntu|debian|linuxmint|pop)
        echo -e "${BLUE}Дистрибутив: Ubuntu/Debian${NC}"
        sudo apt update
        sudo apt install -y python3-pip python3-tk git
        ;;
    arch|manjaro)
        echo -e "${BLUE}Дистрибутив: Arch/Manjaro${NC}"
        sudo pacman -Syu --noconfirm python python-pip git tk
        ;;
    fedora)
        echo -e "${BLUE}Дистрибутив: Fedora${NC}"
        sudo dnf install -y python3-pip python3-tkinter git
        ;;
    *)
        echo -e "${YELLOW}⚠️  Неизвестный дистрибутив. Установите вручную:${NC}"
        echo "  • python3"
        echo "  • python3-pip"
        echo "  • git"
        ;;
esac

# Создание виртуального окружения
echo -e "\n${YELLOW}🐍 Создание виртуального окружения...${NC}"
python3 -m venv wextweaks_env

# Активация и установка пакетов
echo -e "\n${YELLOW}📦 Установка Python пакетов...${NC}"
source wextweaks_env/bin/activate
pip install --upgrade pip

# Скачивание программы
echo -e "\n${YELLOW}⬇️  Скачивание WexTweaks...${NC}"
if [ ! -f "wextweaks_linux.py" ]; then
    echo "Скачивание основной программы..."
    # Здесь можно добавить скачивание с GitHub
fi

# Создание ярлыка
echo -e "\n${YELLOW}🔗 Создание ярлыков...${NC}"

# Ярлык для запуска
cat > wextweaks_launcher.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source wextweaks_env/bin/activate
python3 wextweaks_linux.py
EOF

chmod +x wextweaks_launcher.sh

# Десктоп файл
cat > ~/.local/share/applications/wextweaks.desktop << EOF
[Desktop Entry]
Name=WexTweaks Linux
Comment=Оптимизатор Linux для игр
Exec=$(pwd)/wextweaks_launcher.sh
Icon=$(pwd)/icon.png
Terminal=true
Type=Application
Categories=Utility;System;
Keywords=optimizer;gaming;linux;
EOF

echo -e "\n${GREEN}✅ Установка завершена!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}🚀 Запустить WexTweaks:${NC}"
echo -e "  1. Через терминал: ${GREEN}./wextweaks_launcher.sh${NC}"
echo -e "  2. Из меню приложений: ${GREEN}WexTweaks Linux${NC}"
echo -e "  3. Прямой запуск: ${GREEN}python3 wextweaks_linux.py${NC}"
echo ""
echo -e "${YELLOW}💡 Для полного функционала запускайте с sudo:${NC}"
echo -e "  ${GREEN}sudo python3 wextweaks_linux.py${NC}"
echo ""
echo -e "${BLUE}🎮 Удачи в играх и высокой производительности!${NC}"