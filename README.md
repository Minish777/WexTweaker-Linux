```markdown
# WexTweaker

<p align="center">
<strong>Минималистичный инструмент для настройки Linux</strong>
</p>

<p align="center">
<a href="#установка">Установка</a> • 
<a href="#использование">Использование</a> • 
<a href="#структура">Структура</a> • 
<a href="#лицензия">Лицензия</a>
</p>

---

## 📦 Установка

**Установка одной командой:**

```bash
curl -sSL https://raw.githubusercontent.com/Minish777/WexTweaker-Linux/refs/heads/main/setup.sh | sudo bash
```

**Или вручную:**

```bash
git clone https://github.com/Minish777/WexTweaker-Linux.git
cd WexTweaker-Linux
sudo ./setup.sh
```

## 🚀 Использование

После установки запускайте утилиту:

```bash
sudo wextweaker
```

**Доступные команды:**

```bash
# Основные команды
sudo wextweaker --help      # Справка
sudo wextweaker --info      # Информация о системе
sudo wextweaker --optimize  # Оптимизация

# Управление
sudo wextweaker --update    # Обновление
sudo wextweaker --uninstall # Удаление
```

## 📁 Структура проекта

```
WexTweaker-Linux/
├── WexTweaker.py     # Основной скрипт
├── setup.sh          # Установщик
├── uninstall.sh      # Удаление
├── README.md         # Документация
└── LICENSE           # Лицензия MIT
```

## 📄 Лицензия

MIT License. Полный текст в файле [LICENSE](LICENSE).

---

<p align="center">
<sub>Репозиторий: <a href="https://github.com/Minish777/WexTweaker-Linux">github.com/Minish777/WexTweaker-Linux</a></sub>
</p>
```
