import argparse
import socket
import  shlex
import subprocess
import sys
import  textwrap
import threading

def execute(cmd):
    cmd  = cmd.strip()
    if not cmd:
        return 
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT) #Ejecuta un comando en el sistema operativo local y luego devuelve la salida de ese comando.
    return output.decode()
'''
Inicializamos el objeto NetCat con los argumentos de la linea de comando y el bufer 1 y, a continuacion
Creamos el object socket 2. El metodo run, que es el punto de entrada para administrar el objeto NetCat, 
es bastante simple: delega la ejecucion a dos metodos. Si estamos configurando un oyente, llamamos al metodo 
listen, de lo contrario llamamos al metodo send.
'''
class NetCat: 
 def __init__(self, args, buffer=None): 
        self.args = args 
        self.buffer = buffer 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def run(self): 
        if self.args.listen: 
            self.listen() 
        else: 
            self.send()

'''
1. Nos conectamos al objetivo y al puerto 1. Si tenemos un bufer, lo enviamos al objetivo.
2. A continuacion, configuramos un bloque try/catch para poder cerrar manualmente la conexion con Ctrl-C.
3. Ahora iniciamos un loop 3 para recibir datos del socket (destino).
4. Si no hay datos, salimos del bucle de lo contrario, imprimimos los datos de la rspuesta y hacemos una pausa para
   obtener una entrada intercativa, enviamos esa entrada.
   5. Si el bufer no es nulo, lo enviamos al socket.

6. El bucle continuara hasta que se produzca un keyboard interrupt (Ctrl-C) o el socket se cierre.
'''
def send(self):
    self.socket.connect((self.args.target, self.args.port)) #1
    if self.buffer:
        self.socket.send(self.buffer)
    
    try:  #2
        while True: #3
            recv_len = 1
            response = ''
            while recv_len:
                data = self.socket.recv(4096)
                recv_len = len(data)
                response += data.decode()
                if recv_len < 4096:
                    break #4
            if response:
                print(response)
                buffer = input('> ')
                buffer += '\n'

                self.socket.send(buffer.encode()) #5

    except KeyboardInterrupt: #6
        print('Response')
        self.socket.close()
        sys.exit()

#Metodo que se ejecuta cuando el programa se ejecuta como oyente (listen)
''' 
El metod listen se enlaza al destinoy al puerto 1 y comienza a escuchar en un bucle 2, 
Pasando el socket conectado al metodo handle 3.
'''

def listen(self):
    self.socket.bind((self.args.target, self.args.port)) #1
    self.socket.listen(5)
    while True:
        client_socket, _ = self.socket.accept() #2
        client_theread = threading.Thread(target = self.handle, args = (client_socket,)) #3
        client_theread.start() 

#Logica para realizar cargas de archivos, ejecutar comandos y crear un shell interactivo, el progrma puede realizar estas tareas cuando funciona como oyente.
def handle(self, client_socket):
    '''
    Maneja las conexiones entrantes según los argumentos proporcionados.
    Puede ejecutar comandos, recibir archivos o abrir una shell interactiva.

    Args:
        client_socket (socket.socket): Socket conectado al cliente.
    '''
    if self.args.execute:  # Modo ejecución remota de comandos (--execute)
        '''
        1. Ejecuta un comando específico enviado como argumento (-e/--execute)
           y envía la salida de vuelta al cliente.
           Ejemplo de uso: -e="ls -la"
        '''
        output = execute(self.args.execute)
        client_socket.send(output.encode())  

    elif self.args.upload:  # Modo recepción de archivos (--upload)
        '''
        2. Recibe un archivo del cliente y lo guarda localmente.
           - Lee datos en bloques de 4096 bytes hasta que no haya más datos.
           - Guarda el contenido en el archivo especificado (-u/--upload).
           Ejemplo de uso: -u=archivo.txt
        '''
        file_buffer = b''
        while True:
            data = client_socket.recv(4096)
            if data:
                file_buffer += data
            else:
                break
        with open(self.args.upload, 'wb') as f:
            f.write(file_buffer)
        message = f'Saved file {self.args.upload}'
        client_socket.send(message.encode())

    elif self.args.command:  # Modo shell interactiva (--command)
        '''
        3. Inicia una shell interactiva remota:
           - Muestra un prompt personalizado (BHP: #> ).
           - Espera comandos terminados con nueva línea (\n).
           - Ejecuta cada comando y devuelve la salida al cliente.
           - Maneja excepciones si la conexión se interrumpe.
           Ejemplo de uso: -c
        '''
        cmd_buffer = b''
        while True:
            try:
                client_socket.send(b'BHP: #> ')
                while '\n' not in cmd_buffer.decode():
                    cmd_buffer += client_socket.recv(64)  
                response = execute(cmd_buffer.decode())
                if response:
                    client_socket.send(response.encode())
                cmd_buffer = b''
                
            except Exception as e:
                print(f'server killed {e}')
                self.socket.close()
                sys.exit()
                
if __name__ == '__main__': 
    parser = argparse.ArgumentParser( #1. creamos  una interfaz de linea de comandos para el script usando el modulo de argparse
        description='BHP Net Tool', 
        formatter_class=argparse.RawDescriptionHelpFormatter, 
        #2. Proporcionamos ejemplos de uso que el progrma mostrara cuando el usario lo invoque con --herlp2 y agregamos seis argumentos
        #que especifican como queremos que se comporte el programa 3.
        #2. el argumento -c o --command indica que queremos una shell de comandos, el argumento -e o --execute especifica un comando a ejecutar,
        #el argumento -l o --listen indica que queremos escuchar en un puerto y que debemos configurar un agende de escucha, el argumento -p o --port especifica el puerto a usar,
        #el argumento -t o --target especifica la IP de destino y el argumento -u o --upload especifica un archivo a subir.
        #3. el argumento -c o --command indica que queremos una shell de comandos, el argumento -e o --execute especifica un comando a ejecutar,
        
        epilog=textwrap.dedent('''Example: 
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell 
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file 
            netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd" # execute command 
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135 
            netcat.py -t 192.168.1.108 -p 5555 # connect to server 
        ''')) 
    parser.add_argument('-c', '--command', 
                        action='store_true', help='command shell') 
    parser.add_argument('-e', '--execute', help='execute specified command') 
    parser.add_argument('-l', '--listen', 
                        action='store_true', help='listen') 
    parser.add_argument('-p', '--port', type=int, 
                        default=5555, help='specified port') 
    parser.add_argument('-t', '--target', 
                        default='192.168.1.203', help='specified IP') 
    parser.add_argument('-u', '--upload', help='upload file') 
    args = parser.parse_args() 
    if args.listen: 
        buffer = '' 
    else: 
        buffer = sys.stdin.read() 
    nc = NetCat(args, buffer.encode()) 
    nc.run()


