def limit_error(limit : str):
    '''
    Evitar que rompa el código cuando no se introduce el rango de 'limit' adecuado 
    (numero 'int' entre 0 y 500)
    '''
    try:
        limit = int(input(limit))
    except:
        limit = 600
    
    return limit