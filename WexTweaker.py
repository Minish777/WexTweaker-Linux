#!/usr/bin/env python3
"""
WexTweaks Linux Optimizer - Оптимизатор Linux для игр и производительности
Версия: 1.0 Linux Edition
"""

import os
import sys
import subprocess
import shutil
import json
import platform
import time
import getpass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import readline

class LinuxTweaker:
    def __init__(self):
        self.distro = self.detect_distro()
        self.arch = platform.machine()
        self.username = getpass.getuser()
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, ".config", "wextweaks")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.log_file = os.path.join(self.config_dir, "wextweaks.log")
        self.backup_dir = os.path.join(self.config_dir, "backups")
        
        # Создаем директории
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Цвета для терминала
        self.colors = {
            'RED': '\033[91m',
            'GREEN': '\033[92m',
            'YELLOW': '\033[93m',
            'BLUE': '\033[94m',
            'MAGENTA': '\033[95m',
            'CYAN': '\033[96m',
            'WHITE': '\033[97m',
            'BOLD': '\033[1m',
            'RESET': '\033[0m'
        }
        
        self.load_config()
        self.check_sudo()
        
    def color(self, text: str, color: str) -> str:
        """Добавляет цвет к тексту"""
        return f"{self.colors.get(color, '')}{text}{self.colors['RESET']}"
    
    def print_banner(self):
        """Печать баннера"""
        self.clear_screen()
        print(self.color("╔══════════════════════════════════════════════════════════════╗", "BLUE"))
        print(self.color("║", "BLUE") + self.color("          ⚡ WEXTWEAKS LINUX OPTIMIZER v1.0 ⚡           ", "YELLOW") + self.color("║", "BLUE"))
        print(self.color("║", "BLUE") + self.color("        Оптимизация Linux для игр и производительности      ", "CYAN") + self.color("║", "BLUE"))
        print(self.color("╚══════════════════════════════════════════════════════════════╝", "BLUE"))
        print()
        print(self.color(f"Дистрибутив: ", "YELLOW") + self.color(f"{self.distro['name']} {self.distro['version']}", "WHITE"))
        print(self.color(f"Архитектура: ", "YELLOW") + self.color(f"{self.arch}", "WHITE"))
        print(self.color(f"Пользователь: ", "YELLOW") + self.color(f"{self.username}", "WHITE"))
        print(self.color("=" * 64, "BLUE"))
    
    def clear_screen(self):
        """Очистка экрана"""
        os.system('clear')
    
    def detect_distro(self) -> Dict:
        """Определение дистрибутива"""
        distro_info = {
            'name': 'Unknown',
            'version': 'Unknown',
            'id': 'unknown',
            'package_manager': 'unknown'
        }
        
        # Проверяем /etc/os-release
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('NAME='):
                        distro_info['name'] = line.split('=')[1].strip().strip('"')
                    elif line.startswith('VERSION_ID='):
                        distro_info['version'] = line.split('=')[1].strip().strip('"')
                    elif line.startswith('ID='):
                        distro_info['id'] = line.split('=')[1].strip().strip('"')
        
        # Определяем менеджер пакетов
        if distro_info['id'] in ['ubuntu', 'debian', 'linuxmint', 'pop']:
            distro_info['package_manager'] = 'apt'
        elif distro_info['id'] in ['arch', 'manjaro', 'endeavouros']:
            distro_info['package_manager'] = 'pacman'
        elif distro_info['id'] in ['fedora', 'centos', 'rhel', 'rocky']:
            distro_info['package_manager'] = 'dnf'
        elif distro_info['id'] in ['opensuse', 'suse']:
            distro_info['package_manager'] = 'zypper'
        elif distro_info['id'] in ['gentoo']:
            distro_info['package_manager'] = 'emerge'
        
        return distro_info
    
    def check_sudo(self):
        """Проверка прав sudo"""
        try:
            result = subprocess.run(['sudo', '-n', 'true'], 
                                  capture_output=True, 
                                  text=True)
            self.has_sudo = result.returncode == 0
        except:
            self.has_sudo = False
    
    def load_config(self):
        """Загрузка конфигурации"""
        self.config = {
            'optimizations': [],
            'installed_packages': [],
            'last_run': None,
            'gamemode_enabled': False,
            'wine_optimized': False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config.update(json.load(f))
            except:
                pass
    
    def save_config(self):
        """Сохранение конфигурации"""
        self.config['last_run'] = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except:
            pass
    
    def log(self, message: str, level: str = "INFO"):
        """Логирование"""
        timestamp = time.strftime('%H:%M:%S')
        level_colors = {
            'INFO': 'CYAN',
            'SUCCESS': 'GREEN',
            'WARNING': 'YELLOW',
            'ERROR': 'RED',
            'INSTALL': 'MAGENTA'
        }
        
        color = level_colors.get(level, 'WHITE')
        icon = {
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'INSTALL': '📦'
        }.get(level, '•')
        
        log_line = f"[{timestamp}] {icon} {message}"
        print(self.color(log_line, color))
        
        # Запись в файл
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"[{timestamp}] {level}: {message}\n")
        except:
            pass
    
    def run_command(self, cmd: str, desc: str = "", sudo: bool = False) -> bool:
        """Выполнение команды"""
        if desc:
            self.log(f"Выполняю: {desc}", "INFO")
        
        try:
            if sudo and self.has_sudo:
                cmd = f"sudo {cmd}"
            
            result = subprocess.run(cmd, 
                                  shell=True, 
                                  capture_output=True, 
                                  text=True,
                                  timeout=300)
            
            if result.returncode == 0:
                if desc:
                    self.log(f"Успешно: {desc}", "SUCCESS")
                return True
            else:
                self.log(f"Ошибка (код {result.returncode}): {desc}", "ERROR")
                if result.stderr:
                    self.log(f"Детали: {result.stderr[:200]}", "WARNING")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"Таймаут: {desc}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Исключение: {str(e)}", "ERROR")
            return False
    
    def install_packages(self, packages: List[str], desc: str = ""):
        """Установка пакетов в зависимости от дистрибутива"""
        if not packages:
            return True
        
        pm = self.distro['package_manager']
        install_cmd = ""
        
        if pm == 'apt':
            install_cmd = f"apt-get install -y {' '.join(packages)}"
        elif pm == 'pacman':
            install_cmd = f"pacman -S --noconfirm {' '.join(packages)}"
        elif pm == 'dnf':
            install_cmd = f"dnf install -y {' '.join(packages)}"
        elif pm == 'zypper':
            install_cmd = f"zypper install -y {' '.join(packages)}"
        elif pm == 'emerge':
            install_cmd = f"emerge -av {' '.join(packages)}"
        else:
            self.log(f"Неизвестный менеджер пакетов: {pm}", "ERROR")
            return False
        
        return self.run_command(install_cmd, desc, sudo=True)
    
    def create_backup(self, file_path: str) -> bool:
        """Создание резервной копии файла"""
        if not os.path.exists(file_path):
            return True
        
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = os.path.basename(file_path)
            backup_path = os.path.join(self.backup_dir, f"{filename}.backup_{timestamp}")
            
            shutil.copy2(file_path, backup_path)
            self.log(f"Создан бэкап: {backup_path}", "INFO")
            return True
        except Exception as e:
            self.log(f"Ошибка создания бэкапа: {e}", "ERROR")
            return False
    
    # ========== ОСНОВНЫЕ ФУНКЦИИ ОПТИМИЗАЦИИ ==========
    
    def full_optimization(self):
        """Полная оптимизация системы"""
        self.print_banner()
        print(self.color("🚀 ПОЛНАЯ ОПТИМИЗАЦИЯ LINUX", "YELLOW"))
        print(self.color("=" * 64, "BLUE"))
        
        print(self.color("Будет выполнено:", "WHITE"))
        print("  1. 📦 Установка игровых пакетов и утилит")
        print("  2. 🎮 Настройка GameMode и игровых оптимизаций")
        print("  3. ⚡ Оптимизация системных параметров")
        print("  4. 🖥️  Настройка графического стека")
        print("  5. 🧹 Очистка системы и обслуживание")
        print("  6. 🔧 Дополнительные настройки")
        
        print(self.color("\n⚠️  Для некоторых действий требуются права sudo", "RED"))
        
        input(self.color("\nНажмите Enter для продолжения или Ctrl+C для отмены...", "CYAN"))
        
        optimizations = [
            (self.install_gaming_packages, "Установка игровых пакетов"),
            (self.setup_gamemode, "Настройка GameMode"),
            (self.optimize_sysctl, "Оптимизация системных параметров"),
            (self.optimize_filesystem, "Оптимизация файловой системы"),
            (self.setup_wine_proton, "Настройка Wine/Proton"),
            (self.clean_system, "Очистка системы"),
            (self.optimize_desktop, "Оптимизация рабочего стола")
        ]
        
        for func, name in optimizations:
            print(self.color(f"\n▶ {name}...", "BLUE"))
            func()
            time.sleep(1)
        
        print(self.color("\n✅ Оптимизация завершена!", "GREEN"))
        print(self.color("💡 Советы:", "YELLOW"))
        print("  • Перезагрузите компьютер для применения изменений")
        print("  • Для игр используйте команду: gamemoderun %command%")
        print("  • Проверьте настройки драйверов видеокарты")
        
        self.config['optimizations'].append({
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'full_optimization'
        })
        self.save_config()
        
        input(self.color("\nНажмите Enter для возврата в меню...", "CYAN"))
    
    def install_gaming_packages(self):
        """Установка игровых пакетов"""
        self.log("Установка игровых пакетов...", "INSTALL")
        
        # Базовые пакеты для всех дистрибутивов
        common_packages = [
            'gamemode', 'mangohud', 'vkbasalt', 'goverlay',
            'lutris', 'steam', 'wine', 'winetricks',
            'vulkan-tools', 'mesa-utils', 'glxinfo'
        ]
        
        # Дистрибутив-специфичные пакеты
        distro_packages = {
            'apt': [
                'ubuntu-restricted-extras', 'libavcodec-extra',
                'vulkan-utils', 'mesa-vulkan-drivers',
                'lib32-mesa-vulkan-drivers', 'lib32-vulkan-icd-loader'
            ],
            'pacman': [
                'lib32-gamemode', 'lib32-mangohud',
                'vulkan-radeon', 'lib32-vulkan-radeon',
                'vulkan-intel', 'lib32-vulkan-intel'
            ],
            'dnf': [
                'vulkan', 'vulkan-loader', 'mesa-vulkan-drivers',
                'mesa-dri-drivers', 'ffmpeg-libs'
            ]
        }
        
        # Выбираем пакеты для нашего дистрибутива
        packages_to_install = common_packages.copy()
        if self.distro['package_manager'] in distro_packages:
            packages_to_install.extend(distro_packages[self.distro['package_manager']])
        
        # Фильтруем уже установленные пакеты
        installed = self.config.get('installed_packages', [])
        packages_to_install = [pkg for pkg in packages_to_install if pkg not in installed]
        
        if packages_to_install:
            success = self.install_packages(packages_to_install, "Игровые пакеты")
            if success:
                self.config['installed_packages'].extend(packages_to_install)
                self.save_config()
        else:
            self.log("Все игровые пакеты уже установлены", "SUCCESS")
    
    def setup_gamemode(self):
        """Настройка GameMode"""
        self.log("Настройка GameMode...", "INFO")
        
        # Проверяем установлен ли gamemode
        if not self.run_command("which gamemoded", "Проверка GameMode"):
            self.install_packages(['gamemode'], "Установка GameMode")
        
        # Создаем конфигурацию gamemode
        gamemode_conf = """[general]
# Задержка перед запуском (мс)
start_delay=0

# Управление renice (приоритет процессов)
renice=10

# Применять к потомкам
apply_gamescope_to_children=0

# Отключить screensaver
desktop_phosphor_disable=0
inhibit_screensaver=1

# Настройки процессора
cpu governor=performance

# Настройки GPU
gpu_frequency=maximum

# Настройки ввода
softrealtime=auto

[filter]
# Приложения для которых включать gamemode
whitelist=steam
whitelist=lutris
whitelist=wine
whitelist=proton
"""
        
        # Записываем конфигурацию
        gamemode_dir = os.path.join(self.home_dir, ".config", "gamemode.ini")
        try:
            with open(gamemode_dir, 'w') as f:
                f.write(gamemode_conf)
            self.log("Конфигурация GameMode создана", "SUCCESS")
        except Exception as e:
            self.log(f"Ошибка создания конфига: {e}", "ERROR")
        
        # Оптимизация для конкретных игр
        self.setup_game_optimizations()
        
        self.config['gamemode_enabled'] = True
        self.save_config()
    
    def setup_game_optimizations(self):
        """Настройка оптимизаций для конкретных игр"""
        optimizations_dir = os.path.join(self.home_dir, ".config", "wextweaks", "game_optimizations")
        os.makedirs(optimizations_dir, exist_ok=True)
        
        # Настройки для CS:GO
        csgo_conf = """#!/bin/bash
# Оптимизации для CS:GO
export __GL_SHADER_DISK_CACHE_SKIP_CLEANUP=1
export MANGOHUD=1
export VKBASALT_ENABLE=1
# Оптимизация PulseAudio для низкой задержки
export PULSE_LATENCY_MSEC=30
"""
        
        # Настройки для Dota 2
        dota_conf = """#!/bin/bash
# Оптимизации для Dota 2
export __GL_THREADED_OPTIMIZATIONS=1
export __GL_SYNC_TO_VBLANK=0
# Использование Vulkan если доступно
export MESA_LOADER_DRIVER_OVERRIDE=radeonsi
"""
        
        try:
            with open(os.path.join(optimizations_dir, "csgo.sh"), 'w') as f:
                f.write(csgo_conf)
            os.chmod(os.path.join(optimizations_dir, "csgo.sh"), 0o755)
            
            with open(os.path.join(optimizations_dir, "dota2.sh"), 'w') as f:
                f.write(dota_conf)
            os.chmod(os.path.join(optimizations_dir, "dota2.sh"), 0o755)
            
            self.log("Оптимизации для игр созданы", "SUCCESS")
        except Exception as e:
            self.log(f"Ошибка создания оптимизаций: {e}", "ERROR")
    
    def optimize_sysctl(self):
        """Оптимизация sysctl параметров"""
        self.log("Оптимизация sysctl...", "INFO")
        
        # Создаем бэкап текущего sysctl.conf
        if os.path.exists('/etc/sysctl.conf'):
            self.create_backup('/etc/sysctl.conf')
        
        sysctl_optimizations = """# WexTweaks оптимизации для игр и производительности

# Увеличение буферов TCP/IP
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728

# Отключение медленного старта TCP
net.ipv4.tcp_slow_start_after_idle = 0

# Включение окон масштабирования TCP
net.ipv4.tcp_window_scaling = 1

# Увеличение максимального количества соединений
net.core.somaxconn = 65535

# Увеличение размера очереди принятых пакетов
net.core.netdev_max_backlog = 5000

# Оптимизация для низкой задержки
net.ipv4.tcp_low_latency = 1
net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_sack = 0

# Увеличение лимитов файловых дескрипторов
fs.file-max = 2097152
fs.nr_open = 2097152

# Оптимизация памяти и свопа
vm.swappiness = 10
vm.vfs_cache_pressure = 50
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5

# Включение Transparent Huge Pages для производительности
vm.nr_hugepages = 8

# Увеличение размера сегментов shared memory
kernel.shmmax = 68719476736
kernel.shmall = 4294967296

# Ускорение загрузки системы
vm.dirty_writeback_centisecs = 1500

# Оптимизация для SSD
vm.dirty_background_bytes = 16777216
vm.dirty_bytes = 50331648
"""
        
        # Записываем оптимизации во временный файл
        temp_file = '/tmp/wextweaks_sysctl.conf'
        try:
            with open(temp_file, 'w') as f:
                f.write(sysctl_optimizations)
            
            # Применяем изменения
            self.run_command(f"cat {temp_file} | sudo tee -a /etc/sysctl.conf", "Добавление оптимизаций sysctl", sudo=True)
            self.run_command("sudo sysctl -p", "Применение sysctl настроек", sudo=True)
            self.log("Sysctl оптимизирован", "SUCCESS")
        except Exception as e:
            self.log(f"Ошибка оптимизации sysctl: {e}", "ERROR")
    
    def optimize_filesystem(self):
        """Оптимизация файловой системы"""
        self.log("Оптимизация файловой системы...", "INFO")
        
        # Определяем файловую систему
        fs_type = "ext4"  # По умолчанию
        try:
            result = subprocess.run("findmnt -n -o FSTYPE /", shell=True, capture_output=True, text=True)
            fs_type = result.stdout.strip()
        except:
            pass
        
        optimizations = []
        
        if fs_type in ['ext4', 'ext3', 'ext2']:
            # Оптимизации для ext4
            optimizations.append("sudo tune2fs -O dir_index /dev/root 2>/dev/null")
            optimizations.append("sudo tune2fs -O has_journal /dev/root 2>/dev/null")
            # Отключаем atime для увеличения производительности
            optimizations.append("sudo sed -i 's/relatime/noatime,g' /etc/fstab")
            
        elif fs_type in ['btrfs']:
            # Оптимизации для btrfs
            optimizations.append("sudo btrfs filesystem defrag -r / 2>/dev/null")
            
        elif fs_type in ['xfs']:
            # Оптимизации для xfs
            optimizations.append("sudo xfs_fsr / 2>/dev/null")
        
        # Общие оптимизации
        # Включаем writeback для SSD
        optimizations.append("echo 'vm.dirty_writeback_centisecs = 1500' | sudo tee -a /etc/sysctl.conf")
        optimizations.append("echo 'vm.dirty_expire_centisecs = 3000' | sudo tee -a /etc/sysctl.conf")
        
        for cmd in optimizations:
            self.run_command(cmd, f"Оптимизация {fs_type}", sudo=True)
    
    def setup_wine_proton(self):
        """Настройка Wine и Proton"""
        self.log("Настройка Wine/Proton...", "INFO")
        
        # Создаем wineprefix для игр
        wineprefix = os.path.join(self.home_dir, ".wine_wextweaks")
        
        # Настройки для Wine
        wine_optimizations = f"""
# Экспортируем wineprefix
export WINEPREFIX="{wineprefix}"

# Используем 64-bit архитектуру
export WINEARCH="win64"

# Оптимизации производительности Wine
export WINEDEBUG="-all"
export STAGING_SHARED_MEMORY=1
export STAGING_WRITECOPY=1

# Использование CSMT если доступно
export CSMT=enabled

# Ускорение OpenGL
export __GL_SHADER_DISK_CACHE=1
export __GL_SHADER_DISK_CACHE_PATH="{wineprefix}/shadercache"
export __GL_SHADER_DISK_CACHE_SKIP_CLEANUP=1

# Оптимизация для многопоточности
export WINE_CPU_TOPOLOGY=auto

# Отключение встроенного PulseAudio (используем нативный)
export PULSE_LATENCY_MSEC=30
"""
        
        # Записываем настройки
        wine_config = os.path.join(self.config_dir, "wine_optimizations.sh")
        try:
            with open(wine_config, 'w') as f:
                f.write(wine_optimizations)
            os.chmod(wine_config, 0o755)
            
            # Создаем wineprefix если не существует
            if not os.path.exists(wineprefix):
                self.run_command(f"source {wine_config} && wine wineboot", "Создание wineprefix")
            
            # Устанавливаем шрифты и библиотеки
            self.run_command(f"WINEPREFIX={wineprefix} winetricks corefonts vcrun2019 vcrun2015", "Установка компонентов Wine")
            
            self.config['wine_optimized'] = True
            self.save_config()
            self.log("Wine оптимизирован", "SUCCESS")
        except Exception as e:
            self.log(f"Ошибка настройки Wine: {e}", "ERROR")
    
    def clean_system(self):
        """Очистка системы"""
        self.log("Очистка системы...", "INFO")
        
        clean_commands = []
        
        # Команды очистки в зависимости от менеджера пакетов
        if self.distro['package_manager'] == 'apt':
            clean_commands = [
                "sudo apt-get autoremove -y",
                "sudo apt-get autoclean -y",
                "sudo apt-get clean -y",
                "sudo rm -rf /var/cache/apt/archives/*",
                "sudo journalctl --vacuum-time=7d"
            ]
        elif self.distro['package_manager'] == 'pacman':
            clean_commands = [
                "sudo pacman -Sc --noconfirm",
                "sudo pacman -Rns $(pacman -Qtdq) --noconfirm 2>/dev/null || true",
                "sudo rm -f /var/cache/pacman/pkg/*"
            ]
        elif self.distro['package_manager'] == 'dnf':
            clean_commands = [
                "sudo dnf autoremove -y",
                "sudo dnf clean all",
                "sudo rm -rf /var/cache/dnf/*"
            ]
        
        # Общие команды очистки
        clean_commands.extend([
            # Очистка кэша временных файлов
            f"rm -rf {self.home_dir}/.cache/*",
            f"rm -rf {self.home_dir}/.thumbnails/*",
            f"rm -rf /tmp/* 2>/dev/null || true",
            
            # Очистка кэша приложений
            f"rm -rf {self.home_dir}/.local/share/Trash/*",
            
            # Очистка старых логов
            "sudo find /var/log -type f -name '*.log' -mtime +30 -delete",
            "sudo find /var/log -type f -name '*.gz' -delete",
            
            # Очистка кэша systemd
            "sudo systemd-tmpfiles --clean"
        ])
        
        for cmd in clean_commands:
            self.run_command(cmd, "Очистка системы", sudo='sudo' in cmd)
        
        self.log("Система очищена", "SUCCESS")
    
    def optimize_desktop(self):
        """Оптимизация рабочего стола"""
        self.log("Оптимизация рабочего стола...", "INFO")
        
        # Определяем окружение рабочего стола
        desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        
        if 'gnome' in desktop_env or 'ubuntu' in desktop_env:
            self.optimize_gnome()
        elif 'kde' in desktop_env or 'plasma' in desktop_env:
            self.optimize_kde()
        elif 'xfce' in desktop_env:
            self.optimize_xfce()
        else:
            self.log(f"Неизвестное окружение: {desktop_env}", "WARNING")
    
    def optimize_gnome(self):
        """Оптимизация GNOME"""
        self.log("Оптимизация GNOME...", "INFO")
        
        gnome_commands = [
            # Отключение анимаций
            "gsettings set org.gnome.desktop.interface enable-animations false",
            
            # Отключение эффектов
            "gsettings set org.gnome.desktop.interface enable-hot-corners false",
            
            # Ускорение меню
            "gsettings set org.gnome.shell.app-switcher current-workspace-only true",
            
            # Отключение поиска в Dash
            "gsettings set org.gnome.desktop.search-providers disable-external true",
            
            # Оптимизация окон
            "gsettings set org.gnome.mutter center-new-windows true",
            "gsettings set org.gnome.mutter dynamic-workspaces false",
            
            # Отключение ненужных расширений
            "gsettings set org.gnome.shell disable-user-extensions false",
            
            # Оптимизация для игр (отключение композитора)
            "gsettings set org.gnome.mutter experimental-features '[\"kms-modifiers\"]'",
        ]
        
        for cmd in gnome_commands:
            self.run_command(cmd, f"Настройка GNOME: {cmd[:50]}...")
    
    def optimize_kde(self):
        """Оптимизация KDE Plasma"""
        self.log("Оптимизация KDE Plasma...", "INFO")
        
        kde_commands = [
            # Отключение эффектов рабочего стола
            "kwriteconfig5 --file kwinrc --group Compositing --key Enabled false",
            
            # Отключение анимаций
            "kwriteconfig5 --file kwinrc --group Plugins --key blurEnabled false",
            "kwriteconfig5 --file kwinrc --group Plugins --key slideEnabled false",
            
            # Оптимизация для игр
            "kwriteconfig5 --file kwinrc --group Compositing --key GLCore true",
            "kwriteconfig5 --file kwinrc --group Compositing --key OpenGLIsUnsafe false",
            
            # Перезагрузка KWin для применения настроек
            "qdbus org.kde.KWin /KWin reconfigure"
        ]
        
        for cmd in kde_commands:
            self.run_command(cmd, f"Настройка KDE: {cmd[:50]}...")
    
    def optimize_xfce(self):
        """Оптимизация Xfce"""
        self.log("Оптимизация Xfce...", "INFO")
        
        xfce_commands = [
            # Отключение композитора для игр
            "xfconf-query -c xfwm4 -p /general/use_compositing -s false",
            
            # Уменьшение задержки меню
            "xfconf-query -c xfce4-panel -p /panels/panel-1/leave-opacity -s 1",
            
            # Оптимизация оконного менеджера
            "xfconf-query -c xfwm4 -p /general/box_move -s false",
            "xfconf-query -c xfwm4 -p /general/box_resize -s false",
        ]
        
        for cmd in xfce_commands:
            self.run_command(cmd, f"Настройка Xfce: {cmd[:50]}...")
    
    def system_info(self):
        """Информация о системе"""
        self.print_banner()
        print(self.color("📊 ИНФОРМАЦИЯ О СИСТЕМЕ", "YELLOW"))
        print(self.color("=" * 64, "BLUE"))
        
        # Информация о процессоре
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                model_match = re.search(r'model name\s*:\s*(.+)', cpu_info)
                cpu_model = model_match.group(1) if model_match else "Неизвестно"
                
                cores = cpu_info.count('processor\t:')
                print(self.color("Процессор:", "CYAN") + f" {cpu_model}")
                print(self.color("Ядер:", "CYAN") + f" {cores}")
        except:
            pass
        
        # Информация о памяти
        try:
            with open('/proc/meminfo', 'r') as f:
                mem_info = f.read()
                total_match = re.search(r'MemTotal:\s*(\d+)', mem_info)
                free_match = re.search(r'MemFree:\s*(\d+)', mem_info)
                
                if total_match and free_match:
                    total_mb = int(total_match.group(1)) // 1024
                    free_mb = int(free_match.group(1)) // 1024
                    used_mb = total_mb - free_mb
                    usage = (used_mb / total_mb) * 100
                    
                    print(self.color("Память:", "CYAN") + f" {used_mb} МБ / {total_mb} МБ ({usage:.1f}%)")
        except:
            pass
        
        # Информация о диске
        try:
            result = subprocess.run("df -h /", shell=True, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                disk_info = lines[1].split()
                print(self.color("Диск (/):", "CYAN") + f" {disk_info[2]} использовано из {disk_info[1]} ({disk_info[4]})")
        except:
            pass
        
        # Информация о GPU
        try:
            # Проверяем NVIDIA
            nvidia_result = subprocess.run("nvidia-smi --query-gpu=name --format=csv,noheader", 
                                         shell=True, capture_output=True, text=True)
            if nvidia_result.returncode == 0:
                print(self.color("Видеокарта:", "CYAN") + f" NVIDIA {nvidia_result.stdout.strip()}")
            else:
                # Проверяем AMD
                amd_result = subprocess.run("lspci | grep -i vga | grep -i amd", 
                                          shell=True, capture_output=True, text=True)
                if amd_result.stdout:
                    print(self.color("Видеокарта:", "CYAN") + f" {amd_result.stdout.strip()}")
                else:
                    # Проверяем Intel
                    intel_result = subprocess.run("lspci | grep -i vga | grep -i intel", 
                                                shell=True, capture_output=True, text=True)
                    if intel_result.stdout:
                        print(self.color("Видеокарта:", "CYAN") + f" {intel_result.stdout.strip()}")
        except:
            pass
        
        # Статус оптимизаций
        print(self.color("\n⚡ СТАТУС ОПТИМИЗАЦИЙ:", "YELLOW"))
        print(self.color("GameMode:", "CYAN") + f" {'Включен' if self.config['gamemode_enabled'] else 'Выключен'}")
        print(self.color("Wine оптимизирован:", "CYAN") + f" {'Да' if self.config['wine_optimized'] else 'Нет'}")
        print(self.color("Установлено пакетов:", "CYAN") + f" {len(self.config.get('installed_packages', []))}")
        
        if self.config.get('optimizations'):
            print(self.color("\n📅 ПОСЛЕДНИЕ ОПТИМИЗАЦИИ:", "YELLOW"))
            for opt in self.config['optimizations'][-5:]:
                print(f"  • {opt.get('time', '')} - {opt.get('type', 'optimization')}")
        
        print(self.color("\n💡 СОВЕТЫ:", "GREEN"))
        print("  • Для игр запускайте через: gamemoderun %command%")
        print("  • Проверьте драйвера видеокарты")
        print("  • Используйте Proton для игр Steam")
        print("  • MangoHud для мониторинга FPS: mangohud %command%")
        
        input(self.color("\nНажмите Enter для возврата...", "CYAN"))
    
    def create_restore_point(self):
        """Создание точки восстановления"""
        self.log("Создание точки восстановления...", "INFO")
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(self.backup_dir, f"system_backup_{timestamp}.tar.gz")
        
        # Файлы для бэкапа
        files_to_backup = [
            '/etc/sysctl.conf',
            '/etc/fstab',
            f'{self.home_dir}/.bashrc',
            f'{self.home_dir}/.profile',
            f'{self.home_dir}/.config/gamemode.ini',
            self.config_file
        ]
        
        # Фильтруем существующие файлы
        existing_files = [f for f in files_to_backup if os.path.exists(f)]
        
        if existing_files:
            cmd = f"sudo tar -czf {backup_file} {' '.join(existing_files)}"
            if self.run_command(cmd, "Создание бэкапа системы", sudo=True):
                self.log(f"Точка восстановления создана: {backup_file}", "SUCCESS")
            else:
                self.log("Не удалось создать точку восстановления", "ERROR")
        else:
            self.log("Нет файлов для бэкапа", "WARNING")
    
    def restore_settings(self):
        """Восстановление настроек"""
        self.print_banner()
        print(self.color("↺ ВОССТАНОВЛЕНИЕ НАСТРОЕК", "YELLOW"))
        print(self.color("=" * 64, "BLUE"))
        
        print(self.color("⚠️  Внимание: Будут восстановлены стандартные настройки", "RED"))
        print(self.color("Что будет восстановлено:", "WHITE"))
        print("  1. Сброс настроек sysctl")
        print("  2. Восстановление конфигурации GameMode")
        print("  3. Сброс настроек рабочего стола")
        print("  4. Очистка оптимизаций")
        
        confirm = input(self.color("\nПродолжить? (y/n): ", "RED"))
        if confirm.lower() != 'y':
            return
        
        # Восстанавливаем sysctl из бэкапа
        sysctl_backup = os.path.join(self.backup_dir, "sysctl.conf.backup*")
        if self.run_command(f"ls {sysctl_backup} 2>/dev/null | head -1", "Поиск бэкапа sysctl"):
            latest_backup = subprocess.run(f"ls -t {sysctl_backup} | head -1", 
                                         shell=True, capture_output=True, text=True)
            if latest_backup.stdout.strip():
                backup_file = latest_backup.stdout.strip()
                self.run_command(f"sudo cp {backup_file} /etc/sysctl.conf", "Восстановление sysctl", sudo=True)
                self.run_command("sudo sysctl -p", "Применение sysctl", sudo=True)
        
        # Восстанавливаем конфиг gamemode
        gamemode_conf = os.path.join(self.home_dir, ".config", "gamemode.ini")
        if os.path.exists(gamemode_conf):
            os.remove(gamemode_conf)
            self.log("Конфиг GameMode удален", "SUCCESS")
        
        # Сбрасываем настройки
        self.config = {
            'optimizations': [],
            'installed_packages': [],
            'last_run': time.strftime('%Y-%m-%d %H:%M:%S'),
            'gamemode_enabled': False,
            'wine_optimized': False
        }
        self.save_config()
        
        self.log("Настройки восстановлены", "SUCCESS")
        input(self.color("\nНажмите Enter для продолжения...", "CYAN"))
    
    def show_menu(self):
        """Показать главное меню"""
        self.print_banner()
        
        menu_items = [
            ("1", "🚀 ПОЛНАЯ ОПТИМИЗАЦИЯ", "Всё в один клик для игр"),
            ("2", "📦 УСТАНОВКА ИГРОВЫХ ПАКЕТОВ", "Steam, Wine, GameMode и т.д."),
            ("3", "🎮 НАСТРОЙКА GAMEMODE", "Оптимизации для игр"),
            ("4", "⚡ ОПТИМИЗАЦИЯ СИСТЕМЫ", "Sysctl, файловая система"),
            ("5", "🖥️  ОПТИМИЗАЦИЯ РАБОЧЕГО СТОЛА", "GNOME, KDE, Xfce"),
            ("6", "🧹 ОЧИСТКА СИСТЕМЫ", "Удаление мусора и кэшей"),
            ("7", "💾 ТОЧКА ВОССТАНОВЛЕНИЯ", "Создать бэкап настроек"),
            ("8", "📊 ИНФОРМАЦИЯ О СИСТЕМЕ", "Проверка состояния"),
            ("9", "↺ ВОССТАНОВИТЬ НАСТРОЙКИ", "Вернуть стандартные настройки"),
            ("0", "🚪 ВЫХОД", "Завершение работы")
        ]
        
        for key, title, desc in menu_items:
            print(self.color(f"  [{key}] {title}", "GREEN"))
            print(self.color(f"      {desc}", "WHITE"))
            print()
        
        print(self.color("=" * 64, "BLUE"))
        
        if not self.has_sudo:
            print(self.color("⚠️  Нет прав sudo! Некоторые функции недоступны", "RED"))
        
        choice = input(self.color("\nВыберите действие (0-9): ", "YELLOW"))
        
        return choice
    
    def run(self):
        """Главный цикл программы"""
        try:
            while True:
                choice = self.show_menu()
                
                if choice == '1':
                    self.full_optimization()
                elif choice == '2':
                    self.install_gaming_packages()
                    input(self.color("\nНажмите Enter...", "CYAN"))
                elif choice == '3':
                    self.setup_gamemode()
                    input(self.color("\nНажмите Enter...", "CYAN"))
                elif choice == '4':
                    self.optimize_sysctl()
                    self.optimize_filesystem()
                    input(self.color("\nНажмите Enter...", "CYAN"))
                elif choice == '5':
                    self.optimize_desktop()
                    input(self.color("\nНажмите Enter...", "CYAN"))
                elif choice == '6':
                    self.clean_system()
                    input(self.color("\nНажмите Enter...", "CYAN"))
                elif choice == '7':
                    self.create_restore_point()
                    input(self.color("\nНажмите Enter...", "CYAN"))
                elif choice == '8':
                    self.system_info()
                elif choice == '9':
                    self.restore_settings()
                elif choice == '0':
                    print(self.color("\nСпасибо за использование WexTweaks Linux! 🐧", "GREEN"))
                    print(self.color("Не забудьте перезагрузиться для применения изменений!", "YELLOW"))
                    time.sleep(2)
                    break
                else:
                    print(self.color("Неверный выбор!", "RED"))
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print(self.color("\n\nПрограмма завершена", "YELLOW"))
        except Exception as e:
            print(self.color(f"\nКритическая ошибка: {e}", "RED"))
            import traceback
            traceback.print_exc()
            input(self.color("\nНажмите Enter для выхода...", "CYAN"))

def main():
    """Точка входа"""
    # Проверяем, что мы на Linux
    if platform.system() != "Linux":
        print("Эта программа работает только на Linux!")
        sys.exit(1)
    
    # Проверяем версию Python
    if sys.version_info < (3, 7):
        print("Требуется Python 3.7 или выше!")
        sys.exit(1)
    
    print("Загрузка WexTweaks Linux Optimizer...")
    time.sleep(1)
    
    app = LinuxTweaker()
    app.run()

if __name__ == "__main__":
    main()