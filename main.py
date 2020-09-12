import asyncore
import matplotlib.pyplot as plt
import zlib,socket

import numpy as np
import MFSKDemodulator, DePacketizer, MFSKSymbolDecoder, time, logging, sys
from scipy.io import wavfile
import MFSKModulator,Packetizer
import sounddevice as sd


#Networkrelated variables
Connection_status = False
compression = 1
packet_size = 8192
port_host = 8080

#Audio Related variables
symbol_rate = 200#15.625
base_freq = 1500
bits_per_symbol = 4

preamble_tones = [0,15,0,15,0,15,0,15,0,15,0,15,0,15,0,15,0,15,0,15,0,15,0,15,0,15,0,15,0,15]

#non changeables
symb_dec = ''
packet_extract = ''
handler = ''


def zlib_compress(text):
    text_size=sys.getsizeof(text)
    compressed = zlib.compress(text)
    csize=sys.getsizeof(compressed)
    return compressed

def zlib_decompress(compressed):
    decompressed=zlib.decompress(compressed)
    return decompressed

def recover_packet(payload):
    print 'Packet recieved:',payload
    handler.handle_sent_data(payload)


def parse_symbol(tone):
        tone_bits = symb_dec.tone_to_bits(tone['symbol'])
        packet_extract.process_data(tone_bits)


def wavhndl_to_data():
    global symb_dec,packet_extract
    symb_dec = MFSKSymbolDecoder.MFSKSymbolDecoder(num_tones=16, gray_coded=True)

    # De-Packetizer
    packet_extract = DePacketizer.DePacketizer(callback=recover_packet)

    #get symbol back
    demod = MFSKDemodulator.MFSKDemodulator(callback=parse_symbol)
    fs, data = wavfile.read('generated_MFSK16_packets.wav')

    # Convert to float
    if(data.dtype == np.int16):
        data = data.astype(np.float)/2**16
    elif(data.dtype == np.int32):
        data = data.astype(np.float)/2**32

    # Feed the demod the entire file.
    demod.consume(data)


def data_to_wavhndl(data):
    mod = MFSKModulator.MFSKModulator(symbol_rate = symbol_rate, tone_spacing = symbol_rate, start_silence=5, base_freq=base_freq)
    p = Packetizer.Packetizer()

    mod.modulate_symbol(preamble_tones)
    #adding msg together
    fs = p.pack_message(data)

    tx_bits = np.unpackbits(np.fromstring(fs, dtype=np.uint8))
    print(str(tx_bits))
    mod.modulate_bits(bits_per_symbol,tx_bits)

    out = mod.get_mem()
    return out

class data_recv(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(packet_size)
        modulated = data_to_wavhndl(data)
        sd.play(modulated[0],modulated[1])
        if data:
            print ":Transmitting ("+str(len(modulated[0]))+") to dest"
            print "Array:",modulated
            print "data sent:",data
        


    def handle_close(self):
        self.close()
        Connection_status = False

    def handle_sent_data(self,data):
        self.send(data)
            

class proxy(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        global handler
        Connection_status = True
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            handler = data_recv(sock)

wavhndl_to_data()
#server = proxy('localhost', port_host)
#asyncore.loop()