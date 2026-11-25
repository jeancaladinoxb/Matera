def es_entero_positivo(valor: object) -> bool:
    # bool es subclase de int: True no es un id válido
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0
