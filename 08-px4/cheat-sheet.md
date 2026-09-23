# Cheat Sheet 08: PX4: параметри, uORB і логи

- `await drone.param.get_param_float("MPC_XY_VEL_MAX")`
- `await drone.param.set_param_float(name, value)`
- `async for p in drone.param.get_all_params()`
- `ULog("log.ulg").data_list` — топіки з семплами
- `data.field_data.keys()` — поля топіка
- PX4 SITL: `make px4_sitl gz_x500`; MAVSDK: `udp://:14540`
