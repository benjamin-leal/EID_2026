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
VIOLETA = (170, 100, 255)
GRANATE = (150, 30, 60)

FINALES = ("Victoria", "Game Over")

COLORES_BALA = {
    "basica": CIAN,
    "parabolica": NARANJA,
    "circunferencia": MAGENTA,
}
NOMBRES_MUNICION = {
    "basica": "Basica",
    "parabolica": "Parabolica",
    "circunferencia": "Circunferencia",
}
COOLDOWNS = {
    "basica": 250,
    "parabolica": 700,
    "circunferencia": 1500,
}

DATOS_ENEMIGOS = {
    1: {
        "ancho": 34, "alto": 34, "vida": 6, "dano": 1,
        "velocidad": 2.2, "A": 30, "B": 0.012,
        "recibe": {"basica": 2, "parabolica": 3, "circunferencia": 6},
    },
    2: {
        "ancho": 44, "alto": 44, "vida": 12, "dano": 2,
        "velocidad": 1.7, "A": 40, "B": 0.016,
        "recibe": {"basica": 2, "parabolica": 4, "circunferencia": 6},
    },
    3: {
        "ancho": 56, "alto": 40, "vida": 18, "dano": 3,
        "velocidad": 1.3, "A": 45, "B": 0.008,
        "recibe": {"basica": 2, "parabolica": 6, "circunferencia": 9},
    },
    4: {
        "ancho": 120, "alto": 70, "vida": 80, "dano": 5,
        "velocidad": 1.0, "A": 35, "B": 0.007,
        "recibe": {"basica": 2, "parabolica": 5, "circunferencia": 10},
    },
}

OLEADAS = {
    1: [(1, 4)],
    2: [(1, 3), (2, 3)],
    3: [(1, 3), (2, 2), (3, 2)],
    4: [(4, 1), (1, 2), (2, 1)],
}

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

    def recibir_golpe(self, rect_enemigo, ahora, dano):
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
        self.vida -= dano
        self.ultimo_golpe = ahora

    def dibujar(self, pantalla):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_golpe < self.inmunidad and (ahora // 100) % 2 == 0:
            return
        r = self.rect
        puntos = [(r.centerx, r.top), r.bottomleft, r.bottomright]
        pygame.draw.polygon(pantalla, AZUL, puntos)
        pygame.draw.circle(pantalla, BLANCO, (r.centerx, r.centery + 6), 6)
        pygame.draw.rect(pantalla, CIAN, (r.centerx - 3, r.bottom - 6, 6, 10))


class Bala:
    def __init__(self, x, y, tipo="basica", sentido=1):
        self.x0 = float(x)
        self.y0 = float(y)
        self.x = self.x0
        self.y = self.y0
        self.tipo = tipo
        self.color = COLORES_BALA[tipo]
        self.t = 0
        self.vx = 0.0
        self.vy = -9.0
        self.gravedad = 0.0
        self.radio = 110
        self.omega = 0.065 * sentido
        self.cx = self.x0
        self.cy = self.y0 - self.radio

        if tipo == "parabolica":
            self.vx = 3.0 * sentido
            self.vy = -12.0
            self.gravedad = 0.22

        if tipo == "basica":
            self.rect = pygame.Rect(0, 0, 6, 14)
        else:
            self.rect = pygame.Rect(0, 0, 10, 10)
        self.rect.center = (round(x), round(y))
        self.estela = []

    def actualizar(self):
        self.estela.append(self.rect.center)
        if len(self.estela) > 6:
            self.estela.pop(0)

        self.t += 1

        if self.tipo == "circunferencia":
            angulo = -math.pi / 2 + self.omega * self.t
            self.x = self.cx + self.radio * math.cos(angulo)
            self.y = self.cy - self.radio * math.sin(angulo)
        else:
            self.x = self.x0 + self.vx * self.t
            self.y = self.y0 + self.vy * self.t + 0.5 * self.gravedad * self.t ** 2

        self.rect.center = (round(self.x), round(self.y))

    def fuera(self):
        if self.tipo == "circunferencia":
            return abs(self.omega) * self.t >= 2 * math.pi
        return (
            self.rect.bottom < 0
            or self.rect.top > ALTO
            or self.rect.right < 0
            or self.rect.left > ANCHO
        )

    def dibujar(self, pantalla):
        total = len(self.estela)

        for i, posicion in enumerate(self.estela):
            tono = atenuar(self.color, (i + 1) / (total + 1))
            pygame.draw.circle(pantalla, tono, posicion, max(1, i // 2))

        brillo = obtener_brillo(self.color, 18)
        zona = brillo.get_rect(center=self.rect.center)
        pantalla.blit(brillo, zona, special_flags=pygame.BLEND_RGB_ADD)

        pygame.draw.ellipse(pantalla, self.color, self.rect)
        if self.tipo == "basica":
            nucleo = self.rect.inflate(-3, -6)
        else:
            nucleo = self.rect.inflate(-5, -5)
        pygame.draw.ellipse(pantalla, BLANCO, nucleo)


class Enemigo:
    contador = 0

    def __init__(self, tipo, x):
        datos = DATOS_ENEMIGOS[tipo]
        n = Enemigo.contador
        Enemigo.contador += 1

        self.tipo = tipo
        self.rect = pygame.Rect(0, 0, datos["ancho"], datos["alto"])
        self.vida_max = datos["vida"]
        self.vida = self.vida_max
        self.dano = datos["dano"]
        self.dano_recibido = datos["recibe"]
        self.velocidad = datos["velocidad"] * random.choice([-1, 1])

        self.A = datos["A"] + (n % 4) * 3
        self.B = datos["B"] + (n % 3) * 0.002
        self.C = round(n * 0.9, 2)
        if tipo == 4:
            self.D = 120
        else:
            self.D = 110 + (n % 6) * 35

        self.x = float(x)
        self.rect.center = (round(self.x), round(self.f(self.x)))

    def f(self, x):
        return self.A * math.sin(self.B * x + self.C) + self.D

    def recibir_dano(self, tipo_bala):
        self.vida -= self.dano_recibido[tipo_bala]

    def actualizar_movimiento(self, lista_enemigos):
        proximo_x = self.x + self.velocidad
        proximo_y = self.f(proximo_x)

        prueba = self.rect.copy()
        prueba.center = (round(proximo_x), round(proximo_y))

        debe_rebotar = prueba.left <= 0 or prueba.right >= ANCHO
        if not debe_rebotar:
            for otro in lista_enemigos:
                if otro is not self and prueba.colliderect(otro.rect):
                    debe_rebotar = True
                    break

        if debe_rebotar:
            self.velocidad = -self.velocidad
        else:
            self.x = proximo_x
            self.rect.center = (round(proximo_x), round(proximo_y))

        self.rect.clamp_ip(pygame.Rect(0, 0, ANCHO, ALTO))

    def dibujar(self, pantalla):
        ticks = pygame.time.get_ticks()
        r = self.rect

        if self.tipo == 1:
            puntos = [r.topleft, r.topright, (r.centerx, r.bottom)]
            pygame.draw.polygon(pantalla, ROJO, puntos)
            pygame.draw.circle(pantalla, BLANCO, (r.centerx, r.top + 12), 6)
            pygame.draw.circle(pantalla, NEGRO, (r.centerx, r.top + 13), 3)

        elif self.tipo == 2:
            puntos = [
                (r.centerx, r.top), r.midright,
                (r.centerx, r.bottom), r.midleft,
            ]
            pygame.draw.polygon(pantalla, NARANJA, puntos)
            pygame.draw.polygon(pantalla, AMARILLO, puntos, 3)
            radio = 7 + int(3 * math.sin(ticks * 0.012))
            pygame.draw.circle(pantalla, ROJO, r.center, radio)

        elif self.tipo == 3:
            cuerpo = pygame.Rect(r.left, r.top + 16, r.width, r.height - 16)
            domo = pygame.Rect(0, 0, 28, 24)
            domo.midbottom = (r.centerx, r.top + 26)
            pygame.draw.ellipse(pantalla, CIAN, domo)
            pygame.draw.ellipse(pantalla, VIOLETA, cuerpo)
            activa = (ticks // 150) % 3
            for i in range(3):
                luz = (r.left + 12 + i * 16, cuerpo.centery)
                color = AMARILLO if i == activa else GRIS
                pygame.draw.circle(pantalla, color, luz, 4)

        else:
            puntos = [
                (r.left + 15, r.top), (r.right - 15, r.top),
                (r.right, r.top + 25), (r.right - 20, r.bottom),
                (r.left + 20, r.bottom), (r.left, r.top + 25),
            ]
            pygame.draw.polygon(pantalla, GRANATE, puntos)
            pygame.draw.polygon(pantalla, ROJO, puntos, 3)
            color_ojo = AMARILLO if (ticks // 400) % 2 == 0 else NARANJA
            for dx in (-24, 24):
                centro = (r.centerx + dx, r.top + 32)
                pygame.draw.circle(pantalla, color_ojo, centro, 9)
                pygame.draw.circle(pantalla, NEGRO, centro, 4)
            pygame.draw.rect(pantalla, GRIS, (r.left + 22, r.bottom - 4, 12, 14))
            pygame.draw.rect(pantalla, GRIS, (r.right - 34, r.bottom - 4, 12, 14))

        if self.tipo != 4:
            proporcion = max(self.vida, 0) / self.vida_max
            pygame.draw.rect(pantalla, GRIS, (r.left, r.top - 8, r.width, 4))
            pygame.draw.rect(
                pantalla, VERDE, (r.left, r.top - 8, int(r.width * proporcion), 4)
            )


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
        self.ultimo_disparo = {tipo: -10000 for tipo in COOLDOWNS}
        self.municion = "basica"
        self.lado_parabola = 1
        self.estado = "Jugando"
        self.temblor = 0
        self.intensidad = 0
        self.oleada_actual = 0
        self.aviso = 0
        self.siguiente_oleada()

    def crear_enemigo(self, tipo):
        enemigo = None
        for _ in range(100):
            x = random.randint(80, ANCHO - 80)
            enemigo = Enemigo(tipo, x)
            zona = enemigo.rect.inflate(30, 30)
            libre = True
            for otro in self.enemigos:
                if zona.colliderect(otro.rect):
                    libre = False
                    break
            if libre:
                break
        self.enemigos.append(enemigo)

    def siguiente_oleada(self):
        self.oleada_actual += 1
        for tipo, cantidad in OLEADAS[self.oleada_actual]:
            for _ in range(cantidad):
                self.crear_enemigo(tipo)
        self.aviso = 120

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
                    elif evento.key == pygame.K_2:
                        self.municion = "parabolica"
                    elif evento.key == pygame.K_3:
                        self.municion = "circunferencia"

        return True

    def disparar(self, teclas):
        if not teclas[pygame.K_SPACE]:
            return

        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo[self.municion] < COOLDOWNS[self.municion]:
            return

        x = self.nave.rect.centerx
        y = self.nave.rect.top

        if self.municion == "basica":
            self.balas.append(Bala(x, y, "basica"))

        elif self.municion == "parabolica":
            self.balas.append(Bala(x, y, "parabolica", self.lado_parabola))
            self.lado_parabola = -self.lado_parabola

        else:
            for sentido in (1, -1):
                self.balas.append(Bala(x, y, "circunferencia", sentido))

        self.ultimo_disparo[self.municion] = ahora
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

        if self.aviso > 0:
            self.aviso -= 1

        teclas = pygame.key.get_pressed()
        self.nave.mover(teclas)
        self.disparar(teclas)

        for bala in self.balas:
            bala.actualizar()

        self.balas = [b for b in self.balas if not b.fuera()]

        for bala in self.balas[:]:
            for enemigo in self.enemigos:
                if bala.rect.colliderect(enemigo.rect):
                    enemigo.recibir_dano(bala.tipo)
                    self.balas.remove(bala)
                    if enemigo.vida <= 0:
                        self.enemigos.remove(enemigo)
                    break

        ahora = pygame.time.get_ticks()

        for enemigo in self.enemigos:
            enemigo.actualizar_movimiento(self.enemigos)

            if (
                enemigo.rect.colliderect(self.nave.rect)
                and ahora - self.nave.ultimo_golpe >= self.nave.inmunidad
            ):
                self.nave.recibir_golpe(enemigo.rect, ahora, enemigo.dano)
                self.activar_temblor(12, 5)

        if self.nave.vida <= 0:
            self.estado = "Game Over"
        elif not self.enemigos:
            if self.oleada_actual < len(OLEADAS):
                self.siguiente_oleada()
            else:
                self.estado = "Victoria"

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

    def dibujar_barra_jefe(self):
        jefe = None
        for enemigo in self.enemigos:
            if enemigo.tipo == 4:
                jefe = enemigo
        if jefe is None:
            return
        ancho_max = 250
        alto = 16
        x = ANCHO - ancho_max - 5
        y = ALTO - alto - 5
        proporcion = max(jefe.vida, 0) / jefe.vida_max
        pygame.draw.rect(self.pantalla, GRIS, (x, y, ancho_max, alto))
        pygame.draw.rect(self.pantalla, ROJO, (x, y, int(ancho_max * proporcion), alto))
        pygame.draw.rect(self.pantalla, BLANCO, (x, y, ancho_max, alto), 1)
        etiqueta = self.fuente.render("JEFE", True, BLANCO)
        self.pantalla.blit(etiqueta, (x - 55, y - 2))

    def dibujar_municion(self):
        color = COLORES_BALA[self.municion]
        if self.oleada_actual == 4:
            fase = "Jefe final"
        else:
            fase = f"Oleada {self.oleada_actual}"
        nombre = NOMBRES_MUNICION[self.municion]
        texto = f"{fase} | Municion: {nombre} (1/2/3)"
        self.pantalla.blit(self.fuente.render(texto, True, color), (10, 10))

        ahora = pygame.time.get_ticks()
        espera = COOLDOWNS[self.municion] - (ahora - self.ultimo_disparo[self.municion])
        if espera <= 0:
            estado = "Recarga: lista"
        else:
            estado = f"Recarga: {espera / 1000:.1f} s"
        self.pantalla.blit(self.fuente.render(estado, True, BLANCO), (10, 34))

    def dibujar_centrado(self, texto, y, color=BLANCO, fuente=None):
        imagen = (fuente or self.fuente).render(texto, True, color)
        x = ANCHO // 2 - imagen.get_width() // 2
        self.pantalla.blit(imagen, (x, y))

    def dibujar_aviso(self):
        if self.aviso <= 0 or self.estado != "Jugando":
            return
        if self.oleada_actual == 4:
            texto = "JEFE FINAL"
        else:
            texto = f"OLEADA {self.oleada_actual}"
        self.dibujar_centrado(texto, 380, AMARILLO, self.fuente_titulo)

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
        self.dibujar_barra_jefe()
        self.dibujar_municion()
        self.dibujar_aviso()
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