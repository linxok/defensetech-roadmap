# Cheat Sheet 09: ROS2: мости телеметрії

- `ros2 pkg create --build-type ament_python drone_bridge --dependencies rclpy std_msgs`
- `colcon build && source install/setup.bash`
- `ros2 run drone_bridge telemetry_bridge`
- `ros2 topic list/echo/hz`
- `node.create_publisher(String, "drone/telemetry", 10)`
- `rclpy.spin(node)` + `destroy_node()` у finally
