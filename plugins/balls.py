
class Ball:
    def __init__(self, dims, np):
        self.speed = 1
        self.angle = np.random.uniform(0, 2 * np.pi)
        self.color = [np.random.randint(0, 255) for _ in range(3)]
        self.x = np.random.uniform(dims[0])
        self.y = np.random.uniform(dims[1])
        self.width = dims[0]
        self.height = dims[1]
        self.np = np
        self.size = 1

    def move(self):
        self.x += self.np.sin(self.angle) * self.speed
        self.y -= self.np.cos(self.angle) * self.speed

    def bounce(self):
        width = self.width
        height = self.height
        if self.x > width - self.size:
            self.x = 2*(width - self.size) - self.x
            self.angle = - self.angle

        elif self.x < self.size:
            self.x = 2*self.size - self.x
            self.angle = - self.angle

        if self.y > height - self.size:
            self.y = 2*(height - self.size) - self.y
            self.angle = self.np.pi - self.angle

        elif self.y < self.size:
            self.y = 2*self.size - self.y
            self.angle = self.np.pi - self.angle


class Runner:

    def __init__(self, dims):
        import numpy as np
        self.np = np
        self.dims = dims
        self.balls = [Ball(dims, np) for _ in range(42)]

    def collide(self, p1, p2):
        np = self.np
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        elasticity = 1
        dist = np.hypot(dx, dy)
        if dist < p1.size + p2.size:
            tangent = np.arctan2(dy, dx)
            angle = 0.5 * np.pi + tangent

            angle1 = 2*tangent - p1.angle
            angle2 = 2*tangent - p2.angle
            speed1 = p2.speed*elasticity
            speed2 = p1.speed*elasticity

            (p1.angle, p1.speed) = (angle1, speed1)
            (p2.angle, p2.speed) = (angle2, speed2)

            p1.x += np.sin(angle)
            p1.y -= np.cos(angle)
            p2.x -= np.sin(angle)
            p2.y += np.cos(angle)

    def run(self):
        np = self.np
        width = self.dims[0]
        height = self.dims[1]
        pixels = np.zeros((width, height, 3), np.uint8)

        for i, ball in enumerate(self.balls):

            ball.move()
            ball.bounce()
            pixels[int(ball.x), int(ball.y)] = ball.color
            
            for ball2 in self.balls[i+1:]:
                self.collide(ball, ball2)
                
        return pixels
