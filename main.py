import pygame
import random

ANCHO = 800
ALTO = 600
FPS = 60

NEGRO = (10, 10, 20)
BLANCO = (240, 240, 240)
AZUL = (80, 160, 255)
ROJO = (230, 70, 70)
VERDE = (90, 220, 120)
AMARILLO = (250, 220, 80)


class Nave:
    def __init__(self):
        self.ancho = 40
        self.alto = 40
        self.rect = pygame.Rect(0, 0, self.ancho, self.alto)
        self.rect.midbottom = (ANCHO // 2, ALTO - 20)
        self.velocidad = 5
        self.vida = 10

    def mover(self, teclas):
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
        if teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
        if teclas[pygame.K_UP]:
            self.rect.y -= self.velocidad
        if teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidad
        self.rect.clamp_ip(pygame.Rect(0, 0, ANCHO, ALTO))

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, AZUL, self.rect)


class Bala:
    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, 6, 14)
        self.rect.midbottom = (x, y)
        self.velocidad = 9

    def actualizar(self):
        self.rect.y -= self.velocidad

    def fuera(self):
        return self.rect.bottom < 0

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, AMARILLO, self.rect)


class Enemigo:
    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, 36, 36)
        self.rect.center = (x, y)
        self.velocidad = random.choice([-2, 2])
        self.vida = 3

    def actualizar(self):
        self.rect.x += self.velocidad
        if self.rect.left <= 0 or self.rect.right >= ANCHO:
            self.velocidad = -self.velocidad
        self.rect.clamp_ip(pygame.Rect(0, 0, ANCHO, ALTO))

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, ROJO, self.rect)


class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Juego Arcade")
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.SysFont(None, 28)
        self.reiniciar()

    def reiniciar(self):
        self.nave = Nave()
        self.balas = []
        self.enemigos = []
        self.ultimo_disparo = 0
        self.cadencia = 250
        self.terminado = False
        self.crear_enemigos(4)

    def crear_enemigos(self, cantidad):
        for i in range(cantidad):
            x = random.randint(40, ANCHO - 40)
            y = 60 + i * 50
            self.enemigos.append(Enemigo(x, y))

    def eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                if evento.key == pygame.K_r and self.terminado:
                    self.reiniciar()
        return True

    def disparar(self, teclas):
        ahora = pygame.time.get_ticks()
        if teclas[pygame.K_SPACE] and ahora - self.ultimo_disparo >= self.cadencia:
            self.balas.append(Bala(self.nave.rect.centerx, self.nave.rect.top))
            self.ultimo_disparo = ahora

    def actualizar(self):
        if self.terminado:
            return
        teclas = pygame.key.get_pressed()
        self.nave.mover(teclas)
        self.disparar(teclas)

        for bala in self.balas:
            bala.actualizar()
        self.balas = [b for b in self.balas if not b.fuera()]

        for enemigo in self.enemigos:
            enemigo.actualizar()

        for bala in self.balas[:]:
            for enemigo in self.enemigos[:]:
                if bala.rect.colliderect(enemigo.rect):
                    self.balas.remove(bala)
                    enemigo.vida -= 1
                    if enemigo.vida <= 0:
                        self.enemigos.remove(enemigo)
                    break

        for enemigo in self.enemigos[:]:
            if enemigo.rect.colliderect(self.nave.rect):
                self.enemigos.remove(enemigo)
                self.nave.vida -= 1

        if self.nave.vida <= 0:
            self.terminado = True

    def dibujar_texto(self, texto, x, y, color=BLANCO):
        imagen = self.fuente.render(texto, True, color)
        self.pantalla.blit(imagen, (x, y))

    def dibujar(self):
        self.pantalla.fill(NEGRO)
        self.nave.dibujar(self.pantalla)
        for bala in self.balas:
            bala.dibujar(self.pantalla)
        for enemigo in self.enemigos:
            enemigo.dibujar(self.pantalla)
        self.dibujar_texto("Vida: " + str(self.nave.vida), 10, 10, VERDE)
        if self.terminado:
            self.dibujar_texto("GAME OVER - R para reiniciar", ANCHO // 2 - 140, ALTO // 2)
        pygame.display.flip()

    def correr(self):
        activo = True
        while activo:
            self.reloj.tick(FPS)
            activo = self.eventos()
            self.actualizar()
            self.dibujar()
        pygame.quit()


if __name__ == "__main__":
    Juego().correr()
