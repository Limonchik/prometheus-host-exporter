from flask import Flask, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge
import os
import socket

app = Flask(__name__)

# Создаем метрику типа хоста
host_type = Gauge('host_type', 'Type of host', ['type'])


# Определяем тип хоста
def determine_host_type():
    # Сброс всех значений
    host_type.labels('vm').set(0)
    host_type.labels('container').set(0)
    host_type.labels('physical').set(0)

    # Проверка на контейнер
    if os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv'):
        host_type.labels('container').set(1)
        return

    # Проверка на виртуальную машину (простая эвристика)
    with open('/proc/cpuinfo', 'r') as f:
        cpuinfo = f.read().lower()
        if 'vmware' in cpuinfo or 'kvm' in cpuinfo or 'virtualbox' in cpuinfo or 'hypervisor' in cpuinfo:
            host_type.labels('vm').set(1)
            return

    # Если ничего не определено, считаем физическим хостом
    host_type.labels('physical').set(1)


@app.route('/')
def metrics():
    determine_host_type()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    # Инициализируем метрики
    determine_host_type()
    # Запускаем сервер
    app.run(host='0.0.0.0', port=8080)