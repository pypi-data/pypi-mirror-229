from Crypto.Hash import MD5
from Crypto.Cipher import AES, Blowfish
from binascii import a2b_hex, b2a_hex

def md5hex(data):
    """ return hex string of md5 of the given string """
    h = MD5.new(data.encode('utf-8'))
    return b2a_hex(h.digest())


def hexaescrypt(data, key):
    """ returns hex string of aes encrypted data """
    c = AES.new( key, AES.MODE_ECB)
    return b2a_hex(c.encrypt(data))


def calcbfkey(songid):
    """ Calculate the Blowfish decrypt key for a given songid """
    h = md5hex(songid).decode('utf-8')
    key = "g4el58wc0zvf9na1"
    
    return "".join(
        chr( 
            ord( h[ i ]     ) ^ 
            ord( h[ i + 16] ) ^ 
            ord( key[i]     )
            ) for i in range( 16 )
    )


def blowfishDecrypt(data, key):
    """ CBC decrypt data with key """
    c = Blowfish.new( key , 
                      Blowfish.MODE_CBC, 
                      a2b_hex( "0001020304050607" )
                      )
    return c.decrypt(data)


def decryptfile(fh, key, fo):
    """
    Decrypt data from file <fh>, and write to file <fo>.
    decrypt using blowfish with <key>.
    Only every third 2048 byte block is encrypted.
    """
    blockSize = 0x800 #2048 byte
    i = 0
    
    while True:
        data = fh.read( blockSize )
        if not data:
            break

        isEncrypted  = ( (i % 3) == 0 )
        isWholeBlock = len(data) == blockSize
        
        if isEncrypted and isWholeBlock:
            data = blowfishDecrypt(data, key)
            
        fo.write(data)
        i += 1