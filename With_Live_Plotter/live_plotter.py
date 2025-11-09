import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
from collections import deque
import math
import csv

# Configuration
LISTEN_PORT = 5000
MAX_POINTS = 500  # Max data points to display

# Data storage
timestamps = deque(maxlen=MAX_POINTS)
commands = deque(maxlen=MAX_POINTS)
distances = deque(maxlen=MAX_POINTS)
x_pos = deque(maxlen=MAX_POINTS)
y_pos = deque(maxlen=MAX_POINTS)
obstacle_markers = []  # Store obstacle locations and distances

# Simulated position tracking (simple model)
current_x, current_y = 0, 0
current_angle = 90  # degrees (0 = right, 90 = up)

# Movement constants (adjust based on your robot's speed/timing)
FORWARD_STEP = 5   # cm per update
BACKWARD_STEP = 5
TURN_ANGLE = 15    # degrees per turn command
OBSTACLE_THRESHOLD = 15  # cm (must match ESP32 code)

# UDP Setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", LISTEN_PORT))
sock.settimeout(0.1)

print(f"[INFO] Movement Logger started on port {LISTEN_PORT}")
print("[INFO] Waiting for ESP32 telemetry...")
print("[INFO] Make sure your PC IP is set correctly in the ESP32 code (TELEMETRY_IP = '192.168.4.2')")

# Matplotlib setup
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('ESP32 Robot Movement Visualization with Obstacles', fontsize=16)

def update_position(cmd):
    """Simple 2D position tracking based on commands"""
    global current_x, current_y, current_angle
    
    if cmd == 'F':
        current_x += FORWARD_STEP * math.cos(math.radians(current_angle))
        current_y += FORWARD_STEP * math.sin(math.radians(current_angle))
    elif cmd == 'B':
        current_x -= BACKWARD_STEP * math.cos(math.radians(current_angle))
        current_y -= BACKWARD_STEP * math.sin(math.radians(current_angle))
    elif cmd == 'L':
        current_angle += TURN_ANGLE
    elif cmd == 'R':
        current_angle -= TURN_ANGLE
    # 'S' (stop) doesn't change position

def check_obstacle_marker(distance):
    """
    Check if the distance is below obstacle threshold
    and mark the current robot position as obstacle location
    """
    
    if distance < OBSTACLE_THRESHOLD and distance > 0:
        # Obstacle detected at current robot position
        obstacle_markers.append({
            'x': current_x,
            'y': current_y,
            'distance': distance,
            'angle': current_angle,
            'time': len(timestamps)
        })
        print(f"[OBSTACLE] Detected at ({current_x:.1f}, {current_y:.1f}) - Distance: {distance} cm")

def update_plot(frame):
    """Update plots with new data"""
    try:
        data, addr = sock.recvfrom(128)
        telemetry = data.decode().strip()
        
        # Parse telemetry format: "F,20,1000" or "OBSTACLE,15,1000"
        parts = telemetry.split(',')
        
        if len(parts) >= 3:
            cmd = parts[0]
            dist = int(parts[1])
            timestamp = int(parts[2])
            
            # Check for obstacle detection
            if cmd == "OBSTACLE":
                check_obstacle_marker(dist)
            else:
                # Update position
                update_position(cmd)
                
                # Store data
                timestamps.append(len(timestamps))
                commands.append(cmd)
                distances.append(dist)
                x_pos.append(current_x)
                y_pos.append(current_y)
                
                # Check if this movement resulted in obstacle detection
                check_obstacle_marker(dist)
                
                print(f"[DATA] Cmd: {cmd} | Distance: {dist} cm | Pos: ({current_x:.1f}, {current_y:.1f})")
            
    except socket.timeout:
        pass
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Clear and redraw
    ax1.clear()
    ax2.clear()
    
    # Plot 1: Robot trajectory (X-Y path) with obstacles
    ax1.plot(x_pos, y_pos, 'b-', linewidth=2, label='Path', alpha=0.7)
    ax1.plot(x_pos, y_pos, 'bo', markersize=3, alpha=0.5)
    
    # Mark current position
    if len(x_pos) > 0:
        ax1.plot(x_pos[-1], y_pos[-1], 'go', markersize=12, label='Current Position', zorder=5)
    
    # Mark obstacles on trajectory
    if obstacle_markers:
        obs_x = [obs['x'] for obs in obstacle_markers]
        obs_y = [obs['y'] for obs in obstacle_markers]
        obs_dist = [obs['distance'] for obs in obstacle_markers]
        
        ax1.scatter(obs_x, obs_y, c='red', s=200, marker='X', 
                   label=f'Obstacles ({len(obstacle_markers)})', zorder=4, edgecolors='darkred', linewidth=2)
        
        # Add distance annotations to obstacles
        for obs in obstacle_markers:
            ax1.annotate(f"{obs['distance']}cm", 
                        xy=(obs['x'], obs['y']), 
                        xytext=(5, 5), 
                        textcoords='offset points',
                        fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    ax1.set_xlabel('X Position (cm)')
    ax1.set_ylabel('Y Position (cm)')
    ax1.set_title('Robot 2D Trajectory with Obstacles')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')
    ax1.axis('equal')
    
    # Plot 2: Distance sensor readings over time (highlight obstacles)
    ax2.plot(timestamps, distances, 'b-', linewidth=2, label='Distance')
    
    # Highlight obstacle threshold line
    ax2.axhline(y=OBSTACLE_THRESHOLD, color='r', linestyle='--', linewidth=2, label=f'Obstacle Threshold ({OBSTACLE_THRESHOLD}cm)')
    
    # Mark obstacle detection points
    if obstacle_markers:
        obs_times = [obs['time'] for obs in obstacle_markers]
        obs_dists = [obs['distance'] for obs in obstacle_markers]
        ax2.scatter(obs_times, obs_dists, c='red', s=100, marker='X', 
                   label='Obstacle Detected', zorder=4, edgecolors='darkred', linewidth=2)
    
    ax2.set_xlabel('Time (samples)')
    ax2.set_ylabel('Distance (cm)')
    ax2.set_title('Ultrasonic Sensor Readings with Obstacle Detection')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper right')

print("[INFO] Starting real-time visualization...")
print("[INFO] Close the plot window to end the session and save data.\n")

ani = FuncAnimation(fig, update_plot, interval=100, cache_frame_data=False)
plt.show()

# After closing the plot window
sock.close()
print("\n[INFO] Session ended. Data logged.")

# Save data to CSV
with open('robot_movement_log.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'Command', 'Distance_cm', 'X_Position', 'Y_Position'])
    for i in range(len(timestamps)):
        writer.writerow([timestamps[i], commands[i], distances[i], x_pos[i], y_pos[i]])

# Save obstacle data
with open('robot_obstacles_log.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Time', 'X_Position', 'Y_Position', 'Distance_cm', 'Robot_Angle_deg'])
    for obs in obstacle_markers:
        writer.writerow([obs['time'], f"{obs['x']:.2f}", f"{obs['y']:.2f}", obs['distance'], f"{obs['angle']:.2f}"])

print("[INFO] Movement data saved to 'robot_movement_log.csv'")
print(f"[INFO] {len(obstacle_markers)} obstacles detected and saved to 'robot_obstacles_log.csv'")
print("[INFO] All done!")
