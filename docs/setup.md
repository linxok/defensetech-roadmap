# Налаштування середовища

## Операційна система

Рекомендується Ubuntu 22.04 LTS або WSL2 на Windows.

## Базові інструменти

```bash
sudo apt update
sudo apt install -y git build-essential cmake python3-pip python3-venv libopencv-dev nodejs npm docker.io docker-compose
```

## Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

Важкі CV/AI-залежності (модулі 12–13) — окремо:
`pip install -r requirements-optional.txt`.

Модуль 11 (gRPC) має власне середовище через конфлікт protobuf
із mavsdk: `python3 -m venv venv-grpc && venv-grpc/bin/pip install -r requirements-grpc.txt`.

## ROS2

Встановіть ROS2 Humble за офіційною інструкцією:
https://docs.ros.org/en/humble/Installation.html

## ArduPilot SITL

```bash
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y
./waf configure --board sitl
./waf copter
sim_vehicle.py -v ArduCopter --console --map
```

## PX4 SITL

```bash
git clone https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot
make px4_sitl gz_x500
```

## Docker

```bash
sudo systemctl enable docker
sudo usermod -aG docker $USER
```
