# Prometheus Host Type Exporter

## Обзор

Prometheus Host Type Exporter - это микросервис, который экспортирует метрики о типе хоста (виртуальная машина, контейнер или физический сервер) в формате Prometheus. Микросервис может быть развернут как напрямую на виртуальной машине, так и в контейнере Docker.

## Требования

### Для локальной машины (где запускается Ansible)

- Linux/macOS/Windows с WSL
- Ansible 2.9+
- SSH-клиент
- Git

### Для целевого сервера

- Rocky Linux или другой RedHat-подобный дистрибутив (CentOS, AlmaLinux, RHEL)
- sudo-права для пользователя, под которым подключается Ansible
- Доступ по SSH
- Python 3

## Структура проекта

```
.
├── ansible/
│   ├── inventory              # Файл инвентаризации Ansible
│   ├── playbook.yml           # Основной playbook для развертывания
│   └── roles/
│       └── prometheus-exporter/
│           ├── files/
│           │   └── app/
│           │       ├── app.py            # Код микросервиса
│           │       ├── requirements.txt  # Python-зависимости
│           │       └── Dockerfile        # Dockerfile для контейнера
│           ├── tasks/
│           │   ├── main.yml             # Основные задачи
│           │   ├── vm_deploy.yml        # Задачи для развертывания на VM
│           │   └── container_deploy.yml # Задачи для развертывания в контейнере
│           └── templates/
│               └── prometheus_exporter.service.j2  # Шаблон systemd-сервиса
└── deploy.sh                  # Скрипт для удобного запуска развертывания
```

## Подготовка к использованию

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/prometheus-host-exporter.git
cd prometheus-host-exporter
```

### 2. Настройка inventory файла

Откройте файл `ansible/inventory` и укажите IP-адрес и имя пользователя для вашего сервера:

```
[rocky_servers]
rocky_vm ansible_host=YOUR_VM_IP ansible_user=YOUR_SSH_USERNAME
```

Замените `YOUR_VM_IP` и `YOUR_SSH_USERNAME` на реальные значения.

### 3. Проверка подключения

Проверьте, что Ansible может подключиться к вашему серверу:

```bash
ansible -i ansible/inventory rocky_servers -m ping
```

Если всё настроено правильно, вы увидите ответ:

```
rocky_vm | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

## Использование

### Запуск скрипта развертывания

Для запуска развертывания используйте скрипт `deploy.sh`:

```bash
./deploy.sh
```

Скрипт предложит вам выбрать тип развертывания:
1. Развертывание микросервиса напрямую на VM (порт 8080)
2. Развертывание микросервиса в Docker-контейнере (порт 8081)

### Развертывание вручную

Если вы хотите запустить Ansible-playbook вручную:

#### Для развертывания на VM:

```bash
ansible-playbook -i ansible/inventory ansible/playbook.yml -e "deployment_type=vm vm_port=8080" -K
```

#### Для развертывания в Docker-контейнере:

```bash
ansible-playbook -i ansible/inventory ansible/playbook.yml -e "deployment_type=container container_port=8081" -K
```

Опция `-K` заставит Ansible запросить sudo-пароль.

## Технические детали микросервиса

### Описание микросервиса

Микросервис представляет собой HTTP-сервер, написанный на Python с использованием Flask и prometheus_client. Он экспортирует метрики в формате Prometheus на порту 8080 (по умолчанию).

### Метрики

Микросервис экспортирует следующие метрики:

- `host_type{type="vm"}` - 1, если микросервис запущен на виртуальной машине, иначе 0
- `host_type{type="container"}` - 1, если микросервис запущен в контейнере, иначе 0
- `host_type{type="physical"}` - 1, если микросервис запущен на физическом сервере, иначе 0

### Алгоритм определения типа хоста

Для определения типа хоста используется следующая логика:

1. Если найдены файлы `/.dockerenv` или `/run/.containerenv` - считается контейнером
2. Если в выводе `/proc/cpuinfo` найдены строки "vmware", "kvm", "virtualbox" или "hypervisor" - считается виртуальной машиной
3. В других случаях - считается физическим сервером

### Доступ к метрикам

После успешного развертывания метрики доступны по URL:

- Для VM: `http://VM_IP:8080`
- Для контейнера: `http://VM_IP:8081`

## Устранение неполадок

### Проблемы с подключением по SSH

Если Ansible не может подключиться к вашему серверу, проверьте:

1. Правильность указанного IP-адреса и имени пользователя в inventory
2. Возможность подключения по SSH вручную: `ssh YOUR_SSH_USERNAME@YOUR_VM_IP`
3. Наличие SSH-ключей, если они требуются для входа на сервер

### Проблемы с sudo-паролем

Если Ansible выдает ошибку `Missing sudo password` или `Incorrect sudo password`:

1. Убедитесь, что вы используете опцию `-K` при запуске playbook
2. Проверьте, что пользователь имеет sudo-права на сервере
3. Если вы не хотите вводить пароль каждый раз, настройте sudo без пароля на сервере:
   ```
   echo "YOUR_SSH_USERNAME ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/YOUR_SSH_USERNAME
   ```

### Проблемы с портами

Если сервис не отвечает на указанном порту:

1. Проверьте, что служба запущена:
   - Для VM: `sudo systemctl status prometheus_exporter`
   - Для контейнера: `docker ps | grep prometheus-exporter`
2. Проверьте, что порт открыт в файрволле:
   ```
   sudo firewall-cmd --zone=public --add-port=8080/tcp --permanent
   sudo firewall-cmd --zone=public --add-port=8081/tcp --permanent
   sudo firewall-cmd --reload
   ```

## Дополнительные настройки

### Изменение портов

Для изменения портов можно указать нужные значения при запуске playbook:

```bash
ansible-playbook -i ansible/inventory ansible/playbook.yml -e "deployment_type=vm vm_port=9090" -K
ansible-playbook -i ansible/inventory ansible/playbook.yml -e "deployment_type=container container_port=9091" -K
```

### Настройка SSL/TLS

Данный микросервис не поддерживает SSL/TLS напрямую. Для добавления SSL рекомендуется использовать обратный прокси, например, Nginx или HAProxy.

### Добавление автозапуска

Для VM автозапуск уже настроен через systemd-сервис.
Для контейнера используется опция `--restart always` при запуске Docker-контейнера.

## Мониторинг и логи

### Логи для VM-развертывания

```bash
sudo journalctl -u prometheus_exporter
```

### Логи для контейнера

```bash
docker logs prometheus-exporter
```

## Деинсталляция

### Удаление с VM

```bash
sudo systemctl stop prometheus_exporter
sudo systemctl disable prometheus_exporter
sudo rm /etc/systemd/system/prometheus_exporter.service
sudo systemctl daemon-reload
sudo rm -rf /opt/prometheus-exporter
```

### Удаление контейнера

```bash
docker stop prometheus-exporter
docker rm prometheus-exporter
docker rmi prometheus-exporter:latest
```
