import base64

if __name__ == '__main__':
    print(base64.b64decode(b'VGhlIERlYnVnZ2luZyBCb29r').decode('utf-8'))