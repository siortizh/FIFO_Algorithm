#!/usr/bin/env python

def procesar(segmentos, reqs, marcos_libres):
    results = []
    # Diccionario para mapear direcciones virtuales a marcos asignados
    paginas_asignadas = {}  # {página: marco}
    # Cola FIFO para saber qué página reemplazar
    cola_fifo = []
    # Diccionario para verificar si un marco está en uso
    marco_en_uso = {}  # {marco: página}
    
    for req in reqs:
        # Paso 1: Verificar si la dirección está en un segmento válido
        segmento_valido = None
        for nombre, base, limite in segmentos:
            if base <= req < (base + limite):
                segmento_valido = (nombre, base, limite)
                break
        
        if not segmento_valido:
            results.append((req, 0x1ff, "Segmentation Fault"))
            continue
        
        nombre, base, limite = segmento_valido
        offset = req - base
        direccion_fisica = None
        
        pagina = req >> 5  # Suponemos páginas de 32 bytes (0x20)
        
        if pagina in paginas_asignadas:
            # La página ya está cargada en memoria
            marco = paginas_asignadas[pagina]
            direccion_fisica = (marco << 5) | (req & 0x1F)
            results.append((req, direccion_fisica, "Marco ya estaba asignado"))
        else:
            if marcos_libres:
                # Hay marcos libres, asignamos uno
                marco = marcos_libres.pop(0)
                paginas_asignadas[pagina] = marco
                marco_en_uso[marco] = pagina
                cola_fifo.append(pagina)
                direccion_fisica = (marco << 5) | (req & 0x1F)
                results.append((req, direccion_fisica, "Marco libre asignado"))
            else:
                # No hay marcos libres, aplicamos FIFO
                pagina_a_reemplazar = cola_fifo.pop(0)
                marco = paginas_asignadas.pop(pagina_a_reemplazar)
                del marco_en_uso[marco]
                
                # Asignamos el marco a la nueva página
                paginas_asignadas[pagina] = marco
                marco_en_uso[marco] = pagina
                cola_fifo.append(pagina)
                direccion_fisica = (marco << 5) | (req & 0x1F)
                results.append((req, direccion_fisica, "Marco asignado"))
    
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