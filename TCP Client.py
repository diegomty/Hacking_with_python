import socket

target_host = "127.0.0.1"
target_port = 9998

#create a socket  object
#El parametro AF_INET indica que se va a utilizar IPv4 y SOCK_STREAM indica que se va a utilizar TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect the client
client.connect((target_host, target_port))

#Send some data
client.send(b"ABCDEF")

#Receive some data
response = client.recv(4096)
print(f"Respuesta del servidor: {response.decode()}")
#Close the client
client.close()

#Para probar la  conexion, primero ejecutamos el servidor  en una terminal y luego el cliente en otra terminal
#Para ejecutar el cliente, ejecutamos el siguiente comando en la terminal: python TCP_Client.py
#Para ejecutar el servidor, ejecutamos el siguiente comando en la terminal: python TCP_Server.py