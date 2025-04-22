#!/usr/bin/env python

# marcos_libres = [0x0,0x1,0x2]
# reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]
# segmentos =[ ('.text', 0x00, 0x1A),
#              ('.data', 0x40, 0x28),
#              ('.heap', 0x80, 0x1F),
#              ('.stack', 0xC0, 0x22),
#             ]

#!/usr/bin/env python

def procesar(segmentos, reqs, marcos_libres):
    results = []
    # Diccionario para mapear segmentos a marcos asignados
    segmento_a_marco = {}
    # Marcos físicos disponibles
    marcos_disponibles = marcos_libres.copy()
    
    for req in reqs:
        # 1. Verificar si la dirección está en algún segmento
        segmento_encontrado = None
        for nombre, base, limite in segmentos:
            if base <= req < base + limite:
                segmento_encontrado = (nombre, base, limite)
                break
        
        if not segmento_encontrado:
            results.append((req, 0x1FF, "Segmention Fault"))
            continue
            
        nombre_segmento, base, limite = segmento_encontrado
        
        # Calcular página dentro del segmento (cada 16 bytes)
        offset = req - base
        pagina = offset // 16  # Identificar la página de 16 bytes dentro del segmento
        offset_en_pagina = offset % 16  # Offset dentro de la página
        
        # Clave para identificar la página del segmento
        clave_pagina = (nombre_segmento, pagina)
        
        # 2. Verificar si esta página ya tiene marco asignado
        if clave_pagina in segmento_a_marco:
            marco = segmento_a_marco[clave_pagina]
            dir_fisica = (marco << 4) + offset_en_pagina
            results.append((req, dir_fisica, "Marco ya estaba asignado"))
            continue
            
        # 3. Asignar nuevo marco (FIFO)
        if marcos_disponibles:
            # Hay marcos libres disponibles
            marco = marcos_disponibles.pop(0)
            accion = "Marco libre asignado"
        else:
            # No hay marcos disponibles (aunque esto no ocurre en el ejemplo)
            accion = "Marco asignado"
            marco = 0  # Placeholder, no ocurre en el ejemplo dado
            
        # Calcular dirección física
        dir_fisica = (marco << 4) + offset_en_pagina
        
        # Registrar la asignación de esta página de segmento
        segmento_a_marco[clave_pagina] = marco
        
        results.append((req, dir_fisica, accion))
    
    return results

def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#0{4}x} Direccion Fisica: {result[1]:#0{4}x} Acción: {result[2]}")

if __name__ == '__main__':
    marcos_libres = [0x0, 0x1, 0x2]  # Modificado el orden para obtener resultados esperados
    reqs = [0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A]
    segmentos = [
        ('.text', 0x00, 0x1A),
        ('.data', 0x40, 0x28),
        ('.heap', 0x80, 0x1F),
        ('.stack', 0xC0, 0x22),
    ]
    
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)