import socket

target_host = "www.google.com"
target_port = 80

#create a socket  object
#El parametro AF_INET indica que se va a utilizar IPv4 y SOCK_STREAM indica que se va a utilizar TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect the client
client.connect((target_host, target_port))

#Send some data
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

#Receive some data
response = client.recv(4096)
print(response.decode())
client.close()