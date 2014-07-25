from PIL import Image
import numpy as np
import random
import os
import shutil
import stat
#import binascii

# Function definitions


def check_RGB_border(x):

    if x < 0:
        return 0
    elif x > 255:
        return 255
    else:
        return x


def set_bit(image, bit, coor):

    bright = (0.298, 0.586, 0.114)
    u = 100
    pix = np.array(image.getpixel(coor))
    new_pix = pix
    Lambda = np.array([p * q for p, q in zip(pix, bright)])
    if bit == '0':
        new_pix = pix - u * Lambda
    elif bit == '1':
        new_pix = pix + u * Lambda
    new_pix = tuple(new_pix.round().astype(int))
    new_pix = tuple(map(check_RGB_border, new_pix))
    image.putpixel(coor, new_pix)

    return


def get_bit(image, coor):

    sigma = 2
    (x, y) = coor
    pix_blue = image.getpixel(coor)[-1]
    res = 0

    for i in range(x - sigma, x + sigma):
        res += image.getpixel((i, y))[-1]
    for j in range(y - sigma, y + sigma):
        res += image.getpixel((x, j))[-1]
    res = (res - 2 * pix_blue) / (4.0 * sigma)

    delta = res - pix_blue
    #print(pix_blue, res, delta)
    if delta > 0:
        return '0'
    elif delta < 0:
        return '1'
    else:
        print("ERROR!")


def convert_str2bit(message):

    bit_message = bin(int.from_bytes(message.encode(), 'big'))
    return bit_message[2:]


def convert_bit2str(bit_message):

    bit_message = '0b' + bit_message
    n = int(bit_message, 2)
    message = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
    return message


def random_coor(size):

    dist = 10
    size = tuple(np.array(size) - [dist, dist])
    coor = tuple(map(random.randint, (dist, dist), size))

    return coor


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def KDB_encode(image, message):

    print("Encoding started!")

    if os.path.exists("output"):
        shutil.rmtree("output", onerror=remove_readonly)
    os.mkdir("output")

    bit_message = convert_str2bit(message)
    print(bit_message)
    size = image.size
    key = []

    for bit in bit_message:
        temp_coor = random_coor(size)
        if not temp_coor in key:
            key.append(temp_coor)
            set_bit(image, bit, temp_coor)

    image.save("output/cyphered.bmp")

    with open("output/key.txt", 'a') as file:
        for coor in key:
            file.write("{}\n".format(coor))

    print("Done!")

    return


def KDB_decode(image, key):

    print("Decoding started!")

    bit_message = ''
    for coor in key:
        bit_message += get_bit(image, coor)

    print(bit_message)
    message = convert_bit2str(bit_message)
    print("Done!")

    return message

# Main code

print("Hello!\n Would you like to encode your message or decode it?")
mode = input("(e/d?)    ")

cond = True

while (cond):
    if not ((mode.lower() == 'e') or (mode.lower() == 'd')):
        mode = input("Please enter 'e' or 'd'!\n")
    else:
        cond = False




#keyfile = open("output/key.txt", 'r')

#key = []
# for line in keyfile:
    # key.append(eval(line))
# print(key)

#im_new = Image.open("output/cyphered.bmp")
#print(KDB_decode(im_new, key))
