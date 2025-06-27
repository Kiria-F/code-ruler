import os
import subprocess
import sys
from pathlib import Path


class Global:
    here = Path(__file__).resolve().parent
    requirements = here / 'requirements.txt'
    venv_dir = here / '.venv'
    if requirements.exists():
        python_bin = venv_dir / 'bin' / 'python' if os.name != 'nt' else venv_dir / 'Scripts' / 'python.exe'
    else:
        python_bin = Path(sys.executable)
    python_path = here
    script = here / 'main.py'
    
    @staticmethod
    def read_conf():
        config_file = Global.here / 'launcher.conf'
        if not config_file.exists():
            return
        with open(config_file, 'r') as f:
            lines = f.read().splitlines()
        for line in lines:
            key, value = line.split('=', 1)
            if key == 'requirements':
                Global.requirements = Global.here / value
            if key == 'venv_dir':
                Global.venv_dir = Global.here / value
            if key == 'python_path':
                Global.python_path = Global.here / value
            if key == 'script':
                Global.script = Global.here / value



def clear_screen():
    command = 'cls' if os.name == 'nt' else 'clear'
    os.system(command)


def create_venv():
    clear_screen()
    print('\n📦 Создаём виртуальное окружение...\n')
    subprocess.check_call([sys.executable, '-m', 'venv', str(Global.venv_dir)])


def install_requirements():
    clear_screen()
    print('\n📥 Устанавливаем зависимости...\n')
    subprocess.check_call([str(Global.python_bin), '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([str(Global.python_bin), '-m', 'pip', 'install', '-r', str(Global.requirements)])


def main():
    Global.read_conf()
    if Global.requirements.exists() and not Global.python_bin.exists():
        create_venv()
        install_requirements()
    if not Global.script.exists():
        print(f'🚨 Скрипт {Global.script} не найден. Проверьте конфигурацию.')
        return

    if not Global.python_path.exists():
        print(f'🚨 PYTHONPATH {Global.python_path} не найден. Проверьте конфигурацию.')
        return

    env = os.environ.copy()
    env['PYTHONPATH'] = str(Global.python_path)
    env['APP_ROOT_DIR'] = str(Global.here)

    clear_screen()
    # os.execve(str(Global.python_bin), [str(Global.python_bin), str(Global.script)], env)

    subprocess.run([str(Global.python_bin), str(Global.script)] + sys.argv[1:], env=env)


if __name__ == '__main__':
    main()
