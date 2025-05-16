import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import numpy as np

# Create figure and axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 3D coordinates for a cube (8 vertices)
x = [0, 1, 1, 0, 0, 1, 1, 0]
y = [0, 0, 1, 1, 0, 0, 1, 1]
z = [0, 0, 0, 0, 1, 1, 1, 1]

# Connecting the vertices to form a cube
vertices = [
    [0, 1], [0, 4], [0, 2], [1, 3], [1, 5],
    [1, 6], [2, 3], [2, 6], [3, 7], [4, 5],
    [4, 7], [5, 6], [6, 7], [0, 4], [1, 5]
]

# Plot the cube's edges
lines = []
for vertex in vertices:
    line, = ax.plot([x[vertex[0]], x[vertex[1]]], 
                    [y[vertex[0]], y[vertex[1]]], 
                    [z[vertex[0]], z[vertex[1]]], 'bo-', markersize=5)
    lines.append(line)

# Set labels
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

# Function to update the view for animation
def update(frame):
    # Rotate the plot by changing the viewing angle
    ax.view_init(elev=20, azim=frame)  # Adjust the `elev` and `azim` values to control the rotation
    return lines

# Create animation
ani = FuncAnimation(fig, update, frames=np.arange(0, 360, 1), interval=50, blit=True)

# Show the plot
plt.show()
