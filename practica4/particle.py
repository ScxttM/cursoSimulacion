from math import sin, cos, radians

import numpy as np
import pygame


def toCartesian(r, θ):
    # Return cartesian coordinates from polar as tuple.
    # Keyword Arguments:
    # r -- magnitude
    # θ -- angle (in degrees)

    return (r*cos(radians(θ)), -r*sin(radians(θ)))


class Particle(pygame.sprite.Sprite):
    def __init__(self, mass, radius, colour, position, velocity):
        pygame.sprite.Sprite.__init__(self)

        self.mass = mass
        self.radius = radius
        self.position = position.astype(float)
        self.velocity = velocity.astype(float)  # in pixels per second

        # Setting the image of the particle
        self.colour = colour
        self.image = pygame.Surface((int(2*radius),)*2).convert_alpha()
        self.image.fill((0, 0, 0, 0))  # Transparent background
        pygame.draw.circle(self.image, colour, (radius, radius), radius)

        # Coordinates to pygame rect
        self.rect = self.image.get_rect()
        self.rect.center = position.copy()
        self.prevpos = position.copy()

        self.currentlyColliding = []  # For wall collisions
        self.updateProperties()

    def testParticleCollision(self, particle, n=1):
        # Checks whether self and particle are colliding
        # n is the number of divisions the collision checks from prevpos

        collided = False

        prevcurrS = self.position - self.prevpos
        prevcurrP = particle.position - particle.prevpos

        for i in range(1, n+1):
            betweenS = self.prevpos + prevcurrS * i/n
            betweenP = particle.prevpos + prevcurrP * i/n

            # The actual collision check!
            if pygame.sprite.collide_rect(self, particle):
                if ((betweenS - betweenP)**2).sum() <= (self.radius + particle.radius)**2:
                    collided = True
                    break

        if not(particle in self.currentlyColliding) or not(self in particle.currentlyColliding):
            if collided:
                self.position = betweenS
                particle.position = betweenP

                self.currentlyColliding.append(particle)
                particle.currentlyColliding.append(self)

                self.particleCollision(particle)

        if not collided:
            try:
                self.currentlyColliding.remove(particle)
                particle.currentlyColliding.remove(self)
            except ValueError:
                pass

        return collided

    def particleCollision(self, particle):
        self.updateProperties()
        particle.updateProperties()

        m1 = self.mass
        m2 = particle.mass

        x1 = self.position
        x2 = particle.position

        v1 = self.velocity
        v2 = particle.velocity

        self.velocity = v1 - (x1-x2) * 2*m2/(m1+m2) * \
            np.dot(v2-v1, x2-x1)/((x1-x2)**2).sum()
        particle.velocity = v2 - (x2-x1) * 2*m1/(m2+m1) * \
            np.dot(v1-v2, x1-x2)/((x2-x1)**2).sum()

        self.updateProperties()
        particle.updateProperties()

    def testWallCollision(self, res):
        # This method is like this to prevent particles getting stuck off-screen...
        if self.rect.left <= 0 and not 'Left Wall' in self.currentlyColliding:
            self.currentlyColliding.append('Left Wall')
            self.velocity[0] *= -1
            return True
        if self.rect.left > 0 and 'Left Wall' in self.currentlyColliding:
            if 'Left Wall' in self.currentlyColliding:
                self.currentlyColliding.remove('Left Wall')

        if self.rect.right >= res[0] and not 'Right Wall' in self.currentlyColliding:
            self.currentlyColliding.append('Right Wall')
            self.velocity[0] *= -1
            return True
        if self.rect.right < res[0] and 'Right Wall' in self.currentlyColliding:
            if 'Right Wall' in self.currentlyColliding:
                self.currentlyColliding.remove('Right Wall')

        if self.rect.top <= 0 and not 'Top Wall' in self.currentlyColliding:
            self.currentlyColliding.append('Top Wall')
            self.velocity[1] *= -1
            return True
        if self.rect.top > 0 and 'Top Wall' in self.currentlyColliding:
            if 'Top Wall' in self.currentlyColliding:
                self.currentlyColliding.remove('Top Wall')

        if self.rect.bottom >= res[1] and not 'Bottom Wall' in self.currentlyColliding:
            self.currentlyColliding.append('Bottom Wall')
            self.velocity[1] *= -1
            return True
        if self.rect.bottom < res[1] and 'Bottom Wall' in self.currentlyColliding:
            if 'Bottom Wall' in self.currentlyColliding:
                self.currentlyColliding.remove('Bottom Wall')

        return False

    def updatePosition(self, milli):
        self.prevpos = self.position.copy()
        self.position += self.velocity * milli/1000
        self.rect.center = tuple(round(x) for x in self.position)

    def updateProperties(self):
        self.speed = np.sqrt((self.velocity**2).sum())

        # For inspection only
        self.momentum = self.mass * self.velocity
        self.KE = 0.5 * self.mass * self.speed**2
