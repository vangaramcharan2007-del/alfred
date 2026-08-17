import numpy as np

class Vector3D:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        if scalar != 0:
            return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)
        else:
            raise ValueError("Cannot divide by zero")

    def magnitude(self):
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        mag = self.magnitude()
        if mag != 0:
            self.x /= mag
            self.y /= mag
            self.z /= mag

    def cross(self, other):
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

class Matrix3x3:
    def __init__(self, data=None):
        if data is None:
            self.data = np.zeros((3, 3))
        else:
            self.data = np.array(data)

    def __add__(self, other):
        return Matrix3x3(self.data + other.data)

    def __sub__(self, other):
        return Matrix3x3(self.data - other.data)

    def __mul__(self, scalar):
        return Matrix3x3(self.data * scalar)

    def __truediv__(self, scalar):
        if scalar != 0:
            return Matrix3x3(self.data / scalar)
        else:
            raise ValueError("Cannot divide by zero")

    def transpose(self):
        return Matrix3x3(np.transpose(self.data))

    def determinant(self):
        return np.linalg.det(self.data)

    def inverse(self):
        return Matrix3x3(np.linalg.inv(self.data))

    def rotation_matrix(self, angle, axis):
        cos_theta = np.cos(angle)
        sin_theta = np.sin(angle)
        x, y, z = axis
        return Matrix3x3(
            [cos_theta + (1 - cos_theta) * x**2, 2 * x * y * (1 - cos_theta) - z * sin_theta, 2 * x * z * (1 - cos_theta) + y * sin_theta],
            [2 * x * y * (1 - cos_theta) + z * sin_theta, cos_theta + (1 - cos_theta) * y**2, 2 * y * z * (1 - cos_theta) - x * sin_theta],
            [2 * x * z * (1 - cos_theta) - y * sin_theta, 2 * y * z * (1 - cos_theta) + x * sin_theta, cos_theta + (1 - cos_theta) * z**2]
        )

    def quaternion_transform(self, q):
        # Convert quaternion to rotation matrix
        w, x, y, z = q
        R = Matrix3x3([
            [1 - 2*y**2 - 2*z**2, 2*x*y + 2*w*z, 2*x*z - 2*w*y],
            [2*x*y - 2*w*z, 1 - 2*x**2 - 2*z**2, 2*y*z + 2*w*x],
            [2*x*z + 2*w*y, 2*y*z - 2*w*x, 1 - 2*x**2 - 2*y**2]
        ])
        # Apply rotation matrix
        return R * self

class RigidBody3D:
    def __init__(self, mass=1.0, inertia_tensor=np.eye(3), velocity=np.zeros(3), angular_velocity=np.zeros(3)):
        self.mass = mass
        self.inertia_tensor = inertia_tensor
        self.velocity = velocity
        self.angular_velocity = angular_velocity
        self.force_accumulator = np.zeros(3)
        self.torque_accumulator = np.zeros(3)

    def add_force(self, force):
        self.force_accumulator += force

    def add_torque(self, torque):
        self.torque_accumulator += torque

    def update(self, dt):
        # Apply forces and torques
        F = self.force_accumulator / self.mass
        T = self.torque_accumulator / self.inertia_tensor
        self.velocity += F * dt
        self.angular_velocity += T * dt

class NumericalIntegrator:
    def __init__(self, method='RK4'):
        if method == 'Euler':
            self.step = self.euler_step
        elif method == 'Verlet':
            self.step = self.verlet_step
        elif method == 'RK4':
            self.step = self.rk4_step
        else:
            raise ValueError("Unsupported numerical integration method")

    def euler_step(self, dt):
        # Euler step for explicit integrators
        self.position += self.velocity * dt
        self.angular_velocity += self.omega * dt

    def verlet_step(self, dt):
        # Verlet step for implicit integrators
        k1 = self.force / self.mass
        k2 = self.force / self.mass + 0.5 * self.acceleration * dt**2
        self.position += (self.velocity + 0.5 * k1) * dt
        self.velocity += k2 * dt

    def rk4_step(self, dt):
        # RK4 step for implicit integrators
        k1 = self.force / self.mass
        k2 = self.force / self.mass + 0.5 * self.acceleration * dt**2
        k3 = self.force / self.mass + 0.5 * self.acceleration * (dt/2)**2
        k4 = self.force / self.mass + self.acceleration * dt**2
        self.position += (self.velocity + (k1 + 2*k2 + 2*k3 + k4) * dt/6) * dt
        self.velocity += (k1 + 4*k2 + 2*k3 + k4) * dt/6

class BroadphaseCollisionDetection:
    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.grid = {}

    def add_object(self, object):
        # Add an object to the broadphase collision detection grid
        for i in range(object.position.x // self.grid_size, (object.position.x + object.size.x) // self.grid_size):
            for j in range(object.position.y // self.grid_size, (object.position.y + object.size.y) // self.grid_size):
                if (i, j) not in self.grid:
                    self.grid[(i, j)] = []
                self.grid[(i, j)].append(object)

    def remove_object(self, object):
        # Remove an object from the broadphase collision detection grid
        for i in range(object.position.x // self.grid_size, (object.position.x + object.size.x) // self.grid_size):
            for j in range(object.position.y // self.grid_size, (object.position.y + object.size.y) // self.grid_size):
                if (i, j) in self.grid:
                    self.grid[(i, j)].remove(object)

    def detect_collisions(self):
        # Detect collisions between objects
        collisions = []
        for i in range(len(self.grid)):
            for j in range(i + 1, len(self.grid)):
                for obj1 in self.grid[i]:
                    for obj2 in self.grid[j]:
                        if obj1 != obj2 and obj1.is_colliding(obj2):
                            collisions.append((obj1, obj2))
        return collisions

class NarrowphaseCollisionDetection:
    def __init__(self):
        pass

    def sphere_to_sphere_collision(self, sphere1, sphere2):
        # Sphere-to-Sphere collision detection
        distance = np.linalg.norm(sphere1.position - sphere2.position)
        if distance < sphere1.radius + sphere2.radius:
            return True
        else:
            return False

    def box_to_box_collision(self, box1, box2):
        # Box-to-Box collision detection
        min_distance = float('inf')
        for i in range(3):
            min_distance = min(min_distance, max(box1.min[i], box2.max[i]) - min(box1.max[i], box2.min[i]))
        return min_distance < (box1.size[i] + box2.size[i]) / 2

    def separating_axis_theorem(self, obj1, obj2):
        # Separating Axis Theorem for collision detection
        axes = [
            Vector3D(1, 0, 0),
            Vector3D(0, 1, 0),
            Vector3D(0, 0, 1)
        ]
        for axis in axes:
            projection1 = obj1.position.dot(axis) + obj1.size * axis.dot(obj1.velocity)
            projection2 = obj2.position.dot(axis) + obj2.size * axis.dot(obj2.velocity)
            if projection1 > projection2 + obj2.size[axis]:
                return False
        return True

class ImpulseBasedContactResolution:
    def __init__(self, restitution=0.5, dynamic_friction=0.5, static_friction=0.5):
        self.restitution = restitution
        self.dynamic_friction = dynamic_friction
        self.static_friction = static_friction

    def resolve_contact(self, obj1, obj2, normal):
        # Resolve contact using impulse-based contact resolution
        velocity_dot_normal = obj1.velocity.dot(normal)
        if velocity_dot_normal > 0:
            # Static friction
            friction = self.static_friction * velocity_dot_normal
            obj1.velocity -= friction * normal
            obj2.velocity += friction * normal
        else:
            # Dynamic friction
            restitution_factor = 1 - self.restitution
            relative_velocity = obj1.velocity - obj2.velocity
            impulse = (relative_velocity.dot(normal) + restitution_factor * velocity_dot_normal) / (obj1.mass + obj2.mass)
            obj1.velocity -= impulse * normal
            obj2.velocity += impulse * normal

class WorldSimulationManager:
    def __init__(self, dt=0.01):
        self.dt = dt
        self.gravity = Vector3D(0, -9.81, 0)
        self.damping = 0.5
        self.constraint_iterations = 10

    def step(self, objects):
        # Step the world simulation with given objects and time delta
        for obj in objects:
            obj.add_force(self.gravity)
            obj.update(self.dt)

        broadphase = BroadphaseCollisionDetection()
        for obj in objects:
            broadphase.add_object(obj)

        collisions = broadphase.detect_collisions()

        for collision in collisions:
            obj1, obj2 = collision
            normal = (obj1.position - obj2.position).normalize()
            if self.separating_axis_theorem(obj1, obj2):
                impulse = ImpulseBasedContactResolution().resolve_contact(obj1, obj2, normal)
            else:
                # Handle collision manually using other methods like sphere-sphere or box-box collision detection

        for obj in objects:
            obj.velocity *= 1 - self.damping
            obj.angular_velocity *= 1 - self.damping

if __name__ == "__main__":
    # Create a world simulation manager
    world = WorldSimulationManager()

    # Create some rigid bodies
    objects = []
    for i in range(5):
        mass = 1.0 + i * 0.2
        inertia_tensor = np.eye(3) * mass
        position = Vector3D(i * 10, 0, 0)
        velocity = Vector3D(0, 0, 0)
        angular_velocity = Vector3D(0, 0, 0)
        objects.append(RigidBody3D(mass, inertia_tensor, velocity, angular_velocity))

    # Run the simulation
    for _ in range(100):
        world.step(objects)

        # Visualize the objects (this is a placeholder for actual visualization code)
        print("Objects:", [obj.position for obj in objects])