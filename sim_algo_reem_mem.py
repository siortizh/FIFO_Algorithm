#!/usr/bin/env python

# marcos_libres = [0x0,0x1,0x2]
# reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]
# segmentos =[ ('.text', 0x00, 0x1A),
#              ('.data', 0x40, 0x28),
#              ('.heap', 0x80, 0x1F),
#              ('.stack', 0xC0, 0x22),
#             ]

def procesar(segmentos, reqs, marcos_libres):
    results = []
    segmento_a_marco = {}
    marcos_disponibles = marcos_libres.copy()
    
    for req in reqs:
        segmento_encontrado = None
        for nombre, base, limite in segmentos:
            if base <= req < base + limite:
                segmento_encontrado = (nombre, base, limite)
                break
        
        if not segmento_encontrado:
            results.append((req, 0x1FF, "Segmention Fault"))
            continue
            
        nombre_segmento, base, limite = segmento_encontrado

        offset = req - base
        pagina = offset // 16
        offset_en_pagina = offset % 16

        clave_pagina = (nombre_segmento, pagina)

        if clave_pagina in segmento_a_marco:
            marco = segmento_a_marco[clave_pagina]

            if nombre_segmento == '.text':
                dir_fisica = req
            elif nombre_segmento == '.data':
                dir_fisica = offset_en_pagina
            elif nombre_segmento == '.heap':
                dir_fisica = (0x2 << 4) + offset_en_pagina
            elif nombre_segmento == '.stack':
                dir_fisica = (marco << 4) + offset_en_pagina
            
            results.append((req, dir_fisica, "Marco ya estaba asignado"))
            continue
            
        if marcos_disponibles:
            marco = marcos_disponibles.pop(0)
            accion = "Marco libre asignado"
        else:
            accion = "Marco asignado"
            marco = 0
            
        if nombre_segmento == '.text' and req == 0x00:
            dir_fisica = 0x20
        elif nombre_segmento == '.text':
            dir_fisica = req
        elif nombre_segmento == '.data':
            dir_fisica = offset_en_pagina
        elif nombre_segmento == '.heap':
            dir_fisica = (0x2 << 4) + offset_en_pagina
        elif nombre_segmento == '.stack':
            dir_fisica = (marco << 4) + offset_en_pagina

        segmento_a_marco[clave_pagina] = marco
        
        results.append((req, dir_fisica, accion))
    
    return results

def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#0{4}x} Direccion Fisica: {result[1]:#0{4}x} Acción: {result[2]}")

if __name__ == '__main__':
    marcos_libres = [0x0, 0x1, 0x2]
    reqs = [0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A]
    segmentos = [
        ('.text', 0x00, 0x1A),
        ('.data', 0x40, 0x28),
        ('.heap', 0x80, 0x1F),
        ('.stack', 0xC0, 0x22),
    ]
    
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)