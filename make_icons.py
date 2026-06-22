#!/usr/bin/env python3
# Genera los iconos PNG de la PWA (pixel-art, sin dependencias externas).
import zlib, struct, os

GRID = 16
BG     = (12, 15, 20)    # #0c0f14 fondo
GREEN  = (132, 168, 93)  # #84a85d piel zombie
DGREEN = (94, 127, 64)   # #5e7f40 sombra
LGREEN = (158, 194, 115) # #9ec273 luz
RED    = (178, 43, 43)   # #b22b2b ojos
BLACK  = (21, 23, 28)    # #15171c cuencas
WHITE  = (230, 236, 240) # #e6ecf0 dientes
MOUTH  = (74, 18, 18)    # boca

def make_grid():
    px = [[BG for _ in range(GRID)] for _ in range(GRID)]
    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < GRID and 0 <= y < GRID:
                    px[y][x] = c
    rect(3, 2, 12, 14, DGREEN)   # contorno cabeza
    rect(4, 3, 11, 13, GREEN)    # relleno
    rect(5, 3, 10, 4, LGREEN)    # brillo frente
    rect(5, 6, 6, 8, BLACK)      # cuenca izq
    rect(9, 6, 10, 8, BLACK)     # cuenca der
    px[7][5] = px[7][6] = RED     # ojo izq
    px[7][9] = px[7][10] = RED    # ojo der
    px[8][8] = px[9][8] = DGREEN  # cicatriz central
    rect(5, 10, 10, 12, MOUTH)   # boca
    for x in range(5, 11, 2):     # dientes
        px[10][x] = WHITE
    px[11][4] = DGREEN; px[12][11] = DGREEN  # puntadas
    return px

def write_png(path, size, grid, margin=0.0):
    inner = size * (1 - 2 * margin)
    off = (size - inner) / 2
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # tipo de filtro de la fila
        for x in range(size):
            c = BG
            if margin > 0:
                ix, iy = x - off, y - off
                if 0 <= ix < inner and 0 <= iy < inner:
                    gx = min(int(ix * GRID / inner), GRID - 1)
                    gy = min(int(iy * GRID / inner), GRID - 1)
                    c = grid[gy][gx]
            else:
                gx = min(int(x * GRID / size), GRID - 1)
                gy = min(int(y * GRID / size), GRID - 1)
                c = grid[gy][gx]
            raw += bytes((c[0], c[1], c[2], 255))
    comp = zlib.compress(bytes(raw), 9)
    def chunk(typ, data):
        return struct.pack(">I", len(data)) + typ + data + \
               struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # RGBA 8-bit
    with open(path, "wb") as f:
        f.write(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

os.makedirs("icons", exist_ok=True)
g = make_grid()
write_png("icons/icon-180.png", 180, g)
write_png("icons/icon-192.png", 192, g)
write_png("icons/icon-512.png", 512, g)
write_png("icons/icon-512-maskable.png", 512, g, margin=0.14)
print("Iconos generados en icons/")
