#!/usr/bin/python3

import socket
import re
import hashlib
import sys
import struct
import array
import base64
import threading
import urllib.request
import urllib.parse
import select
import random

# Variable global para controlar el bucle del servidor en el reto 6
seguir_thread = True 
# Variable global para almacenar el identifier del reto 
ultimo_reto = None 

# obtener_contrasena: para obtener el identifier de un reto
def obtener_contrasena(codigo):
    # Inicializamos una cadena vacia para el identifier
    contrasena = ""

    # Verificamos si la cadena "identifier:" esta en el codigo
    if "identifier:" in codigo:
        # Si esta, dividimos el codigo en "identifier:" y tomamos la segunda parte (índice 1)
        contrasena = codigo.split("identifier:")[1].strip() 

        # Luego dividimos la contrasena en lineas y tomamos la primera linea (índice 0)
        contrasena = contrasena.split('\n')
        contrasena = contrasena[0]

    # Devolvemos la contraseña
    return contrasena

# establecer_conexion_udp: para establecer una conexion UDP con un servidor
def establecer_conexion_udp(puerto):
        
        # Creamos un socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Vinculamos el socket a todas las interfaces de red ('') en el puerto especificado
        sock.bind(('', puerto))
        
        return sock

# establecer_conexion_tcp: para establecer una conexion TCP con un servidor
def establecer_conexion_tcp(host, puerto):
    sock = None
    try:
        # Creamos un socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Establecemos la conexion con el servidor
        sock.connect((host, puerto))
    except socket.error as e:
        print(f"Error al establecer la conexión TCP: {e}")
    return sock

# recibir_respuesta: para recibir la respuesta de un socket
def recibir_respuesta(sock):
    respuesta = b''
    try:
        while True:
            # Recibimos los datos del socket
            parte = sock.recv(1024)
            # Si no hay mas datos, salimos del bucle
            if not parte:
                break
            # Concatenamos los datos recibidos, formando la respuesta completa
            respuesta += parte
    except socket.error as e:
        print(f"Error al recibir datos del socket: {e}")
    return respuesta.decode()

# imprimir_y_cerrar: para imprimir el enunciado, la contrasena y cerrar el socket
def imprimir_y_cerrar(repuesta,contrasena, sock, numero_reto):
   
    print(f"mi clave para el reto {numero_reto} es:")
    print(contrasena)
    print("----------------------------------------------------------------------------------") 
    print(repuesta)  
    try:
        sock.close()
    except Exception as e:
        print(f"Error al cerrar el socket: {e}")

# Reto 0: Para empezar la Yinkana, obtener la contraseña inicial y empezar el reto 1.
def reto0():

    # Creamos el socket
    sock = socket.socket()
    # Conectamos a rick
    sock.connect(('rick', 2000))
    # Recibimos el enunciado
    msg = sock.recv(1024)

    print(msg.decode())

    # Enviamos el usuario
    sock.sendall("fleet_owl".encode())
    # Recibimos el enunciado del reto 1
    msg, _ = sock.recvfrom(1024)

    
    codigo = msg.decode()

    # Obtenemos la contrasena y cerramos el socket
    contrasena= obtener_contrasena(codigo)
    imprimir_y_cerrar(codigo,contrasena, sock, 1)
    return contrasena
    
#--------------------RETO 1---------------------

# procesar_mensaje: para procesar el mensaje recibido en el reto 1
def procesar_mensaje(contrasena, msg):
    # Verificamos si la cadena "upper-code?" está en el mensaje
    if "upper-code?" in msg:
        # Si está, convertimos la contraseña a mayusculas
        nueva_contrasena = contrasena.upper()
        # Devolvemos la nueva contraseña
        return nueva_contrasena
    

# reto1: Test Chamber 1: UDP
def reto1(contrasena):
        
        # Generamos un puerto aleatorio entre 1024 y 65535, excluyendo los puertos bien conocidos y reservados
        puerto = random.randint(1024, 65535)
        # Establecemos la conexion UDP
        sock=establecer_conexion_udp(puerto)
        
        # Enviamos el mensaje con el puerto y la contraseña
        mensaje = f"{puerto} {contrasena}"
        addr = ('rick', 4000)
        sock.sendto(mensaje.encode(), addr)
        msg, server = sock.recvfrom(1024)

        # Procesamos el mensaje recibido, llamanado a procesar_mensaje cambiando la contrasena a mayusculas
        nueva_contrasena = procesar_mensaje(contrasena, msg.decode())
        #print(nueva_contrasena)
        sock.sendto(nueva_contrasena.encode(), server) 
        
        # Recibimos la respuesta del servidor
        msg, server = sock.recvfrom(1024)
        
        # Obtenemos la contraseña del siguiente reto
        contrasena= obtener_contrasena(msg.decode())
        imprimir_y_cerrar(msg.decode(),contrasena, sock, 2)
        return contrasena
    

#--------------------RETO 2---------------------

# contar_palabras: para contar las palabras recibidas en el reto 2
def contar_palabras(palabras, total_msg, total_longitud_palabra):

    # Recorremos las palabras recibidas
    for palabra in palabras:
        longitud = len(palabra)

        # Si la longitud de la palabra actual mas la longitud total supera 1000 y la longitud total es mayor o igual a 1000, salimos del bucle
        if total_longitud_palabra + longitud >= 1000 and total_longitud_palabra>= 1000:
            break

        # Convertimos la longitud a cadena y la añadimos al mensaje total
        
        total_msg += str(longitud) + ' '
        total_longitud_palabra += longitud

    # Si la longitud total no supera 1000, vaciamos el mensaje total y la longitud total
    if total_longitud_palabra < 1000:
        total_msg = ''
        total_longitud_palabra= 0

    # Devolvemos el mensaje total y la longitud total
    return total_msg, total_longitud_palabra

# procesar_palabras: para procesar las palabras recibidas en el reto 2
def procesar_palabras(sock, total_longitud_palabra):
    total_msg = ''
    msg = b''

    try:
        # Recibimos los datos del socket
        while True:
            msg += sock.recv(1024)
            # Dividimos los datos en palabras
            palabras = msg.decode().split()
            # Llamamos a contar_palabras
            total_msg, total_longitud_palabra = contar_palabras(palabras, total_msg, total_longitud_palabra)

            # Si no hay más datos o la longitud total supera 1000, salimos del bucle
            if not msg or total_longitud_palabra >= 1000:
                break
    except (socket.error) as e:
        print(f"Error al recibir datos del socket: {e}")
        
   
    
    
    # Eliminamos los espacios en blanco al final del mensaje total y lo devolvemos
    return total_msg.rstrip()

# reto2: Test Chamber 2: Words len
def reto2(contrasena):
    
    final = '--'
    total_longitud_palabra = 0

    # Establecemos la conexion con el servidor
    sock = establecer_conexion_tcp("rick", 3010)
    # Llamamos a procesar_palabras
    total_msg = procesar_palabras(sock, total_longitud_palabra)
    total_msg = f'{contrasena} {total_msg} {final}'
    #print(total_msg)
    # Enviamos el mensaje total al servidor
    sock.sendall(total_msg.encode())
    
    contrasena = ""
    # Recibimos la respuesta del servidor
    respuesta = recibir_respuesta(sock)
    
    # Obtenemos la contrasena del siguiente reto
    contrasena = obtener_contrasena(respuesta) 
    imprimir_y_cerrar(respuesta,contrasena, sock, 3)
    return contrasena
    

#--------------------RETO 3---------------------
# recibir_hasta_palindromo: para recibir datos del socket hasta encontrar un palindromo
def recibir_hasta_palindromo(sock):
    datos_recibidos = ''

    try:
        while True:
            respuesta = sock.recv(1024)

            if not respuesta:
                break

            datos_recibidos += respuesta.decode()

            # Uso la libreria re para encontrar palabras:
            # \b busca coincidencias en el inicio o fin de una palabra
            # \w+ busca una o más letras o números
            # r es para indicar que es una expresion regular
            # Entonces: \b\w+\b busca palabras completas

            palabras = re.findall(r'\b\w+\b', datos_recibidos)

            # Comprobamos si alguna de las palabras es un palindromo
            if any(es_palindromo(palabra) for palabra in palabras):
                break
    except (socket.error) as e:
        print(f"Error al recibir datos del socket: {e}")
        
    return datos_recibidos, palabras

# invertir_palabras: para invertir las palabras de una cadena
def invertir_palabras(cadena_entrada):
     palabras = cadena_entrada.split(' ')
     palabras_invertidas = []

     for palabra in palabras:
          
          # Si la palabra es un numero, la añadimos tal cual, como especifica el enunciado del reto
          if palabra.isdigit():
                palabras_invertidas.append(palabra)
          else:
            # Si no, invertimos la palabra y la añadimos a la lista
                palabras_invertidas.append(palabra[::-1])

     return ' '.join(palabras_invertidas)

# es_palindromo: para comprobar si una palabra es un palindromo
def es_palindromo(palabra):
     #Comprueba si la palabra no es un número y tiene mas de 2 caracteres
     if not palabra.isdigit() and len(palabra)>2:
          return palabra == palabra[::-1]

# reto3: Test Chamber 3: Reverse words
def reto3(contrasena):
     
     sock = establecer_conexion_tcp("rick", 6500)
     sock.sendall(contrasena.encode())
     # Llamamos a recibir_hasta_palindromo
     datos_recibidos, palabras = recibir_hasta_palindromo(sock)

     # min() devuelve el menor de los valores de la lista
     # find() devuelve la posicion de la primera ocurrencia de una palabra en una cadena
     # index_palindrome es la posicion de la primera palabra palindroma en los datos recibidos    
     index_palindrome = min(datos_recibidos.find(palabra) for palabra in palabras if es_palindromo(palabra))
     rever_datos = invertir_palabras(datos_recibidos[:index_palindrome])
     #print(rever_datos)
     sock.sendall((rever_datos + ' --').encode())

     contrasena=""

     # Llamamos a recibir_respuesta y al resto de funciones
     respuesta = recibir_respuesta(sock)

     contrasena= obtener_contrasena(respuesta)
     imprimir_y_cerrar(respuesta,contrasena, sock, 4)
     return contrasena

     

#--------------------RETO 4---------------------

# recibir_datos_calcular_sha224: para recibir los datos del socket y calcular el resumen SHA224
def recibir_datos_calcular_sha224(sock):
    try:
        
        # Recibimos el mensaje con el tamano y contenido
        respuesta = sock.recv(1024) 

        
        # Dividir los datos en size y contenido, similar al split
        size, _, contenido = respuesta.partition(b':') 
        size = int(size)
        
        # Asegurarse de recibir todos los datos
        while len(contenido) < size:
            contenido += sock.recv(1024)

        # Calculamos el resumen SHA224 del archivo binario recibido
        # Como funciona el sha224:
        # sha224() devuelve un objeto hash SHA-224 vacio
        # digest() devuelve el valor hash binario de contenido
        sha224_digest = hashlib.sha224(contenido).digest()

    except (socket.error, ValueError) as e:
        print(f"Error al recibir datos o calcular SHA224: {e}")
        

    return sha224_digest

# reto4: Test Chamber 4: SHA224
def reto4(contrasena):
    
    sock = establecer_conexion_tcp("rick", 9004)
    
    sock.sendall(contrasena.encode())
    
    # Llamamos a recibir_datos_calcular_sha224
    sha224_digest = recibir_datos_calcular_sha224(sock)
    #print(sha224_digest)

    # Enviamos el resultado del resumen SHA224 al servidor
    sock.sendall(sha224_digest)

    # Llamamos al resto de funciones
    respuesta = recibir_respuesta(sock)
    
    
    contrasena = obtener_contrasena(respuesta)
    imprimir_y_cerrar(respuesta,contrasena, sock, 5)
    return contrasena
    

#--------------------RETO 5---------------------

# construir_mensaje_wyp: para construir un mensaje WYP
def construir_mensaje_wyp(tipo, codigo, suma_comprobacion, secuencia, carga):
     
     # como funciona el struct.pack:
     # ! indica que se va a utilizar el formato de red (big-endian)
     # 3s indica que se va a empaquetar una cadena de 3 bytes (WYP según el enunciado son 3 bytes)
     # B indica que se va a empaquetar un entero sin signo de 1 byte (tipo)
     # HHH indica que se van a empaquetar 3 enteros sin signo de 2 bytes (codigo, suma_comprobacion, secuencia)
        
     encabezado = struct.pack("!3sBHHH", b'WYP', tipo, codigo, suma_comprobacion, secuencia)
     # El resultado es una cadena de bytes que contiene el encabezado WYP y la carga util codificada en base64
     return encabezado + carga


# AUTHOR: David Villa Alises
# cksum: para calcular el checksum de un paquete

# Como funciona:
# Si la longitud del paquete es impar, añade un byte nulo al final
# Suma los bytes del paquete de 2 en 2
# Si el sistema es little-endian, inverte los bytes
# Devuelve el checksum

def cksum(pkt):
    
     if len(pkt) % 2 == 1:
          pkt += b'\0'
     s = sum(array.array('H', pkt))
     s = (s >> 16) + (s & 0xffff)
     s += s >> 16
     s = ~s

     if sys.byteorder == 'little':
          s = ((s >> 8) & 0xff) | s << 8

     return s & 0xffff

# decodificar_mensaje_wyp: para decodificar un mensaje WYP
def decodificar_mensaje_wyp(mensaje_codificado):
    try:
        # Definimos el formato del encabezado WYP
        # Especificado en el enunciado y explicado en construir_mensaje_wyp
        formato_encabezado = "!3sBHHH"
        # Calculamos el size del encabezado
        tamano_encabezado = struct.calcsize(formato_encabezado)

        # Desempaquetamos el encabezado
        # mensaje_codificado[:tamano_encabezado] extrae el encabezado del mensaje
        # struct.unpack() desempaqueta el encabezado
        # El resultado es una tupla con los valores desempaquetados

        struct.unpack(formato_encabezado, mensaje_codificado[:tamano_encabezado])

        # Extraemos la carga util (resto del mensaje)
        carga_util = mensaje_codificado[tamano_encabezado:]

        # Decodificamos la carga util en base64
        carga_decodificada = base64.b64decode(carga_util).decode()

    except (struct.error, base64.binascii.Error) as e:
        print(f"Error al desempaquetar el encabezado o decodificar la carga útil: {e}")
       

    return carga_decodificada

# reto5: Test Chamber 5: WYP
def reto5(contrasena):

    try:
        # Crear un socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Codificar la contraseña con base64
        payload_codificado = base64.b64encode(contrasena.encode())

        # Llamamos a cksum metiendo el paquete WYP, el tipo, el codigo, la secuencia y la carga
        suma_comprobacion = cksum(b'WYP' + struct.pack("!BHHH", 0, 0, 0, 1) + payload_codificado)
        
        # Llamamos a construir_mensaje_wyp para construir el mensaje WYP
        # metiendo el tipo, el codigo, la suma de comprobacion, la secuencia y la carga
        mensaje_wyp = construir_mensaje_wyp(0, 0, suma_comprobacion, 1, payload_codificado)
        #print(mensaje_wyp)

        # Enviamos la solicitud WYP
        sock.sendto(mensaje_wyp, ("rick", 6000))

        # Recibimos la respuesta
        respuesta, _ = sock.recvfrom(4096)
        respuesta_decodificada = decodificar_mensaje_wyp(respuesta)
        contrasena= obtener_contrasena(respuesta_decodificada) 
        imprimir_y_cerrar(respuesta_decodificada,contrasena, sock, 6)

    except (socket.error, base64.binascii.Error, struct.error) as e:
        print(f"Error al codificar la contraseña, construir el mensaje WYP, enviar/recibir datos, o decodificar el mensaje WYP: {e}")

       
    return contrasena


#--------------------RETO 6---------------------

# mensaje_identificador: para obtener el la ultimo identificador para el reto 7
def mensaje_identificador(msg_contenido):
        # Inicializamos las variables globales
        global ultimo_reto
        global seguir_thread
        # Obtenemos el nuevo reto
        # Como funciona urllib.parse.unquote:
        # urllib.parse.unquote() decodifica una cadena codificada en URL o un componente de URL
        ultimo_reto = urllib.parse.unquote(msg_contenido)
        
        print(ultimo_reto)
        
        # Paramos el servidor
        seguir_thread = False 

# formar_respuesta_get: al recibir un mensaje GET formamos el mensaje, lo leemos y enviamos una respuesta 
def formar_respuesta_get(msg_contenido):
    # Rfc es la url a la que se va a hacer la petición
        rfc="http://web:81/rfc"+msg_contenido

        # Hacemos la peticion
        # Como funciona urllib.request.urlopen:
        # urllib.request.urlopen() abre una URL

        respuesta_rfc = urllib.request.urlopen(rfc)
        # Leemos la respuesta
        respuesta_rfc= respuesta_rfc.read()
        # Enviamos la respuesta al cliente, formato texto plano
        respuesta = b'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n'+respuesta_rfc
        return respuesta


# gestor_cliente: para gestionar un cliente en el servidor del reto 6
def gestor_cliente(cliente_socket):
    msg = cliente_socket.recv(1024)
    #print("[*] Recibido: {}".format(msg.decode()))
    msg_decodificado = msg.decode()
    # Obtenemos  el mensaje a enviar o conteniendo el identifier del ultimo reto
    msg_contenido= msg_decodificado.split()[1] 
    # Si el mensaje contiene "identifier", obtenemos la contraseña del reto 7
    # Los mensajes que recibo se pueden ver quitando el comentario del print de arriba 
    if 'identifier' in msg_contenido:
       
        mensaje_identificador(msg_contenido)
        # Cerramos el socket
        cliente_socket.close()
        

    # Si no contiene "identifier", obtenemos el RFC de los mensajes de tipo GET
    else:
        

        respuesta=formar_respuesta_get(msg_contenido)
        # Enviamos la respuesta al cliente
        cliente_socket.send(respuesta)
        # Cerramos el socket
        cliente_socket.close()

# arrancar_servidor: crea un servidor web, que gestionas las conexiones
def arrancar_servidor(puerto):
    # Inicializamos la variable global seguir_thread
    global seguir_thread  
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', puerto))
        # Escuchamos hasta 5 conexiones
        server.listen(5)
        # Ponemos el socket en modo no bloqueante
        # Porque si no, el servidor se queda esperando a que llegue una conexión  
        server.setblocking(0) 

        #print(f"Escuchando en puerto {puerto}")
        
        # Bucle para aceptar conexiones
        while seguir_thread:

            # Usamos select para comprobar si hay conexiones pendientes
            # select.select() devuelve tres listas de sockets:
            # Los que estan listos para leer,
            # los que estan listos para escribir y los que estan listos para errores
            # Uso select para comprobar si hay conexiones pendientes y esperar 1 segundo
            siguiente_a_leer, _, _ = select.select([server], [], [], 1)  
            if siguiente_a_leer: 
                # Aceptamos la conexion
                cliente, _ = siguiente_a_leer[0].accept()

                # Creamos un hilo para gestionar el cliente
                gest_cliente = threading.Thread(target=gestor_cliente, args=(cliente,))
                # Iniciamos el hilo
                gest_cliente.start()
    except (socket.error, select.error, threading.ThreadError) as e:
        print(f"Error al iniciar el servidor: {e}")
    server.close()

#reto6: Test Chamber 6: Web Server Get
def reto6(contrasena):
    # Rango de puertos 1024-65535, todos menos los bien conocidos y los reservados
    puerto = random.randint(1024, 65535)
    msg = "{} {}".format(contrasena, puerto)
    sock=establecer_conexion_tcp('rick', 8003)
    sock.sendall(msg.encode())
    arrancar_servidor(puerto)
    sock.close()
    
#--------------------RETO 7---------------------

#reto7: The end
def reto7():
    # Inicializamos la variable global ultimo_reto conteniendo la contrasena del reto 7
    global ultimo_reto
    ultimo_reto=obtener_contrasena(ultimo_reto)
    # Establecemos la conexion con el servidor del reto 7
    sock = establecer_conexion_tcp("rick", 33333)
    # Enviamos la contrasena del reto 7
    sock.sendall(ultimo_reto.encode('utf-8'))
    # Recibimos la respuesta del servidor
    respuesta = recibir_respuesta(sock)
    imprimir_y_cerrar(respuesta,ultimo_reto, sock, 7)
    # Cerramos el socket y termina la Yinkana
    sock.close()


# Funcion principal conteniedo el reto 0, que a su vez llama al resto de retos
def main():
   # Cada reto devuelve la contrasena para el siguiente, excepto el 6 que llama a la varriable global para ello
   contrasena_reto1=reto0()
   contrasena_reto2=reto1(contrasena_reto1)
   contrasena_reto3=reto2(contrasena_reto2)
   contrasena_reto4=reto3(contrasena_reto3)
   contrasena_reto5=reto4(contrasena_reto4)
   contrasena_reto6=reto5(contrasena_reto5)
   reto6(contrasena_reto6)
   reto7()


# Llamamos a la funcion principal
if __name__ == "__main__":
    main()