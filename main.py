import math
import random
import pygame

ANCHO = 800
ALTO = 600
FPS = 60

NEGRO = (10, 10, 20)
BLANCO = (240, 240, 240)
AZUL = (80, 160, 255)
ROJO = (230, 70, 70)
VERDE = (90, 220, 120)
AMARILLO = (250, 220, 80)
GRIS = (50, 50, 60)
CIAN = (0, 220, 255)
NARANJA = (255, 165, 0)
MAGENTA = (255, 0, 255)

FINALES = ("Victoria","Game Over")

BRILLOS = {}


def atenuar(color, factor):
    return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))


def obtener_brillo(color, radio):
    clave = (color, radio)
    if clave not in BRILLOS:
        superficie = pygame.Surface((radio * 2, radio * 2))
        for r in range(radio, 0, -1):
            factor = (1 - r / radio) ** 2 * 0.7
            pygame.draw.circle(superficie, atenuar(color, factor), (radio, radio), r)
        BRILLOS[clave] = superficie
    return BRILLOS[clave]


class Estrella:
    CAPAS = [(1, 0.5, 70), (1, 1.0, 110), (2, 1.8, 170)]

    def __init__(self):
        self.x = random.randint(0, ANCHO)
        self.y = random.randint(0, ALTO)
        self.tamano, self.velocidad, nivel = random.choice(self.CAPAS)
        self.color = (nivel, nivel, min(255, nivel + 30))

    def actualizar(self):
        self.y += self.velocidad
        if self.y > ALTO:
            self.y = 0
            self.x = random.randint(0, ANCHO)

    def dibujar(self, pantalla):
        forma = (int(self.x), int(self.y), self.tamano, self.tamano)
        pygame.draw.rect(pantalla, self.color, forma)


class Nave:
    def __init__(self):
        self.ancho = 40
        self.alto = 40
        self.rect = pygame.Rect(0, 0, self.ancho, self.alto)
        self.rect.midbottom = (ANCHO // 2, ALTO - 20)
        self.velocidad = 5
        self.vida_max = 10
        self.vida = self.vida_max
        self.ultimo_golpe = -1000
        self.inmunidad = 1000
        self.retroceso = 0
        self.fuerza = 12
        self.dir_x = 0.0
        self.dir_y = 0.0

    def mover(self, teclas):
        if self.retroceso > 0:
            self.rect.x += round(self.dir_x * self.fuerza)
            self.rect.y += round(self.dir_y * self.fuerza)
            self.retroceso -= 1
        else:
            if teclas[pygame.K_LEFT]:
                self.rect.x -= self.velocidad
            if teclas[pygame.K_RIGHT]:
                self.rect.x += self.velocidad
            if teclas[pygame.K_UP]:
                self.rect.y -= self.velocidad
            if teclas[pygame.K_DOWN]:
                self.rect.y += self.velocidad
        self.rect.clamp_ip(pygame.Rect(0, 0, ANCHO, ALTO))

    def recibir_golpe(self, rect_enemigo, ahora):
        dx = self.rect.centerx - rect_enemigo.centerx
        dy = self.rect.centery - rect_enemigo.centery
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            dx = 0
            dy = 1
            distancia = 1
        self.dir_x = dx / distancia
        self.dir_y = dy / distancia
        self.retroceso = 10
        self.vida -= 1
        self.ultimo_golpe = ahora

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, AZUL, self.rect)



class Bala:
    def __init__(self, x, y, color=CIAN, tipo="basica",
                 vx=0, vy=-9):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(0, 0, 6, 14)
        self.rect.center = (x, y)

        self.velocidad_x = vx
        self.velocidad_y = vy
        self.gravedad = 0.22
        self.tipo = tipo
        self.color = color
        self.estela = []

    def actualizar(self):
        self.estela.append(self.rect.center)

        if len(self.estela) > 6:
            self.estela.pop(0)

        self.x += self.velocidad_x
        self.y += self.velocidad_y

        if self.tipo == "parabolica":
            self.velocidad_y += self.gravedad

        self.rect.center = (round(self.x), round(self.y))

    def fuera(self):
        return (
            self.rect.bottom < 0
            or self.rect.top > ALTO
            or self.rect.right < 0
            or self.rect.left > ANCHO
        )

    def dibujar(self, pantalla):
        total = len(self.estela)

        for i, posicion in enumerate(self.estela):
            tono = atenuar(
                self.color, (i + 1) / (total + 1)
            )
            pygame.draw.circle(
                pantalla, tono, posicion, max(1, i // 2)
            )

        brillo = obtener_brillo(self.color, 18)
        zona = brillo.get_rect(center=self.rect.center)
        pantalla.blit(
            brillo, zona, special_flags=pygame.BLEND_RGB_ADD
        )

        pygame.draw.ellipse(pantalla, self.color, self.rect)
        pygame.draw.ellipse(
            pantalla, BLANCO, self.rect.inflate(-3, -6)
        )


class Enemigo:
    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, 36, 36)
        self.rect.center = (x, y)
        self.velocidad = random.choice([-2, 2])
        self.vida = 6
        self.dano_recibido = {
            "basica": 2,
            "parabolica": 3,
            "conica": 6
        }
        self.dano = 1

    def recibir_dano(self, tipo):
        self.vida -= self.dano_recibido[tipo]

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
        self.ventana = pygame.display.set_mode((ANCHO, ALTO))
        self.pantalla = pygame.Surface((ANCHO, ALTO))
        pygame.display.set_caption("Juego Arcade")
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.SysFont(None, 28)
        self.fuente_titulo = pygame.font.SysFont(None, 72)
        self.estrellas = [Estrella() for _ in range(90)]
        self.reiniciar()
        self.estado = "Inicio"

    def reiniciar(self):
        self.nave = Nave()
        self.balas = []
        self.enemigos = []
        self.ultimo_disparo = 0
        self.cadencia = 250
        self.cooldown_parabolica = 600 
        self.cooldown_conica = 1000
        self.municion = "basica"
        self.nombre_municion = "Basica"
        self.estado = "Jugando"
        self.temblor = 0
        self.intensidad = 0
        self.crear_enemigos(4)

    def crear_enemigos(self, cantidad):
        for i in range(cantidad):
            x = random.randint(40, ANCHO - 40)
            y = 60 + i * 50
            self.enemigos.append(Enemigo(x, y))

    def activar_temblor(self, frames, intensidad):
        self.temblor = max(self.temblor, frames)
        self.intensidad = max(self.intensidad, intensidad)

    def desplazamiento(self):
        if self.temblor <= 0:
            return (0, 0)
        return (
            random.randint(-self.intensidad, self.intensidad),
            random.randint(-self.intensidad, self.intensidad),
        )


    def eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False

                if evento.key == pygame.K_RETURN and self.estado == "Inicio":
                    self.estado = "Jugando"

                if evento.key == pygame.K_r and self.estado in FINALES:
                    self.reiniciar()

                if self.estado == "Jugando":
                    if evento.key == pygame.K_1:
                        self.municion = "basica"
                        self.nombre_municion = "Basica"

                    elif evento.key == pygame.K_2:
                        self.municion = "parabolica"
                        self.nombre_municion = "Parabolica"

                    elif evento.key == pygame.K_3:
                        self.municion = "conica"
                        self.nombre_municion = "Conica"

        return True

    
    
    def disparar(self, teclas):
        ahora = pygame.time.get_ticks()

        if self.municion == "basica":
            cooldown_actual = self.cadencia
        elif self.municion == "parabolica":
            cooldown_actual = self.cooldown_parabolica
        else:
            cooldown_actual = self.cooldown_conica

        if (
            teclas[pygame.K_SPACE]
            and ahora - self.ultimo_disparo >= cooldown_actual
        ):
            x = self.nave.rect.centerx
            y = self.nave.rect.top

            if self.municion == "basica":
                self.balas.append(
                    Bala(x, y, CIAN, "basica", 0, -9)
                )

            elif self.municion == "parabolica":
                self.balas.append(
                    Bala(x, y, NARANJA, "parabolica", 2.5, -9)
                )

            elif self.municion == "conica":
                angulos = [-40, -20, 0, 20, 40]

                for angulo in angulos:
                    radianes = math.radians(angulo)
                    vx = 9 * math.sin(radianes)
                    vy = -9 * math.cos(radianes)

                    self.balas.append(
                        Bala(
                            x, y, MAGENTA,
                            "conica", vx, vy
                        )
                    )

            self.ultimo_disparo = ahora
            self.activar_temblor(2, 1)

    def actualizar(self):

        for estrella in self.estrellas:
            estrella.actualizar()

        if self.temblor > 0:
            self.temblor -= 1
        else:
            self.intensidad = 0

        if self.estado != "Jugando":
            return

        teclas = pygame.key.get_pressed()
        self.nave.mover(teclas)
        self.disparar(teclas)

        for bala in self.balas:
            bala.actualizar()

        self.balas = [b for b in self.balas if not b.fuera()]

        for bala in self.balas[:]:
            for enemigo in self.enemigos[:]:
                
                if bala.rect.colliderect(enemigo.rect):
                    self.balas.remove(bala)
                    enemigo.recibir_dano(bala.tipo)
                    
                    if enemigo.vida <= 0:
                        self.enemigos.remove(enemigo)
                        break

        ahora = pygame.time.get_ticks()

        for enemigo in self.enemigos:
            enemigo.actualizar()

            if (
                enemigo.rect.colliderect(self.nave.rect)
                and ahora - self.nave.ultimo_golpe >= self.nave.inmunidad
            ):
                self.nave.recibir_golpe(enemigo.rect, ahora)
                self.activar_temblor(12, 5)

        if self.nave.vida <= 0:
            self.estado = "Game Over"
        elif not self.enemigos:
            self.estado = "Victoria"

    def dibujar_texto(self, texto, x, y, color=BLANCO):
        imagen = self.fuente.render(texto, True, color)
        self.pantalla.blit(imagen, (x, y))

    def dibujar_barra_vida(self):
        ancho_max = 200
        alto = 16
        margen = 5
        x = margen
        y = ALTO - alto - margen
        proporcion = max(self.nave.vida, 0) / self.nave.vida_max
        relleno = int(ancho_max * proporcion)
        pygame.draw.rect(self.pantalla, GRIS, (x, y, ancho_max, alto))
        pygame.draw.rect(self.pantalla, VERDE, (x, y, relleno, alto))
        pygame.draw.rect(self.pantalla, BLANCO, (x, y, ancho_max, alto), 1)

    def dibujar_municion(self):
        colores = {
            "basica": CIAN,
            "parabolica": NARANJA,
            "conica": MAGENTA,
        }

        color = colores[self.municion]
        texto = f"Municion: {self.nombre_municion} (1/2/3)"

        imagen = self.fuente.render(texto, True, color)
        self.pantalla.blit(imagen, (10, 10))

    def dibujar_centrado(self, texto, y, color=BLANCO, fuente=None):
        imagen = (fuente or self.fuente).render(texto, True, color)
        x = ANCHO // 2 - imagen.get_width() // 2
        self.pantalla.blit(imagen, (x, y))

    def dibujar_pantalla_estado(self):
        if self.estado == "Jugando":
            return
        velo = pygame.Surface((ANCHO, ALTO))
        velo.set_alpha(150)
        velo.fill(NEGRO)
        self.pantalla.blit(velo, (0, 0))
        if self.estado == "Inicio":
            titulo, color, ayuda = "JUEGO ARCADE", CIAN, "ENTER para empezar"
        elif self.estado == "Victoria":
            titulo, color, ayuda = "VICTORIA", VERDE, "R para jugar de nuevo"
        else:
            titulo, color, ayuda = "Game Over", ROJO, "R para reiniciar"
        self.dibujar_centrado(titulo, ALTO // 2 - 50, color, self.fuente_titulo)
        self.dibujar_centrado(ayuda, ALTO // 2 + 10)

    def dibujar(self):
        self.pantalla.fill(NEGRO)
        for estrella in self.estrellas:
            estrella.dibujar(self.pantalla)
        self.nave.dibujar(self.pantalla)
        for bala in self.balas:
            bala.dibujar(self.pantalla)
        for enemigo in self.enemigos:
            enemigo.dibujar(self.pantalla)
        self.dibujar_barra_vida()
        self.dibujar_municion()
        self.dibujar_pantalla_estado()
        self.ventana.fill(NEGRO)
        self.ventana.blit(self.pantalla, self.desplazamiento())
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
