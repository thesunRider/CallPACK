import asyncore,matplotlib
import zlib

Connection_status = False
compression = 1
packet_size = 8192

def zlib_compress(text):
    text_size=sys.getsizeof(text)
    print("\nBfr Compression:",text_size)
    compressed = zlib.compress(text)
    csize=sys.getsizeof(compressed)
    print("\nsize of compressed text",csize)
    return compressed

def zlib_decompress(compressed):
    decompressed=zlib.decompress(compressed)
    return decompressed

def to_binary(data):
    return bins


class data_recv(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(packet_size)
        if data:
            print(":Transmitting ("+str(len(data))+") to dest")


    def handle_close(self):
        self.close()
        Connection_status = False
        print("Connection closed")
            

class proxy(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        print('Incoming connection from %s' % repr(addr))
        Connection_status = True
        handler = data_recv(sock)

server = proxy('localhost', 8080)
asyncore.loop()