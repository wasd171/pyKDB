from PIL import Image
import numpy as np
import random
import os
import shutil
import stat
import itertools
import time
import sys

#Global variables

#Pixel/bit. Default is 4
times = 4

#Describes the level of image bit corruption. Default is 0.01
corruption = 0.01


# Function definitions


# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rProgress: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), round(progress*100, 2), status)
    sys.stdout.write(text)
    sys.stdout.flush()

def divide(lst, sz):
    return [np.array(lst[i:i + sz])for i in range(0, len(lst), sz)]


def delta_func(delta):
    if delta > 0:
        return 0
    elif delta < 0:
        return 1


def check_RGB_border(x):

    if x < 0:
        return 0
    elif x > 255:
        return 255
    else:
        return x


def get_bit(image, coor):

    sigma = 2
    (x, y) = coor
    pix_blue = image.getpixel(coor)[2]
    res = 0

    for i in range(x - sigma, x + sigma):
        res += image.getpixel((i, y))[2]
    for j in range(y - sigma, y + sigma):
        res += image.getpixel((x, j))[2]
    res = (res - 2 * pix_blue) / (4.0 * sigma)

    delta = res - pix_blue

    return delta


def set_bit(image, bit, coor):

    temp_image = image.copy()
    bright = (0.298, 0.586, 0.114)
    pix = np.array(image.getpixel(coor))
    new_pix = pix
    Lambda = np.array([p * q for p, q in zip(pix, bright)])

    if bit == '0':
        new_pix = pix - corruption * Lambda
    elif bit == '1':
        new_pix = pix + corruption * Lambda

    new_pix = tuple(new_pix.round().astype(int))
    new_pix = tuple(map(check_RGB_border, new_pix))
    temp_image.putpixel(coor, new_pix)

    return temp_image


def convert_str2bit(message):

    bit_message = bin(int.from_bytes(message.encode(), 'big'))
    return bit_message[2:]


def convert_bit2str(bit_message):

    bit_message = '0b' + bit_message
    n = int(bit_message, 2)
    message = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    message = message.decode('utf-8', 'replace')
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
    size = image.size
    key = []

    for bit in bit_message:
        for _ in itertools.repeat(None, times):
            cond = True
            while cond:
                temp_coor = random_coor(size)
                while (temp_coor in key):
                    temp_coor = random_coor(size)
                temp_image = set_bit(image, bit, temp_coor)
                cond = (str(delta_func(get_bit(temp_image, temp_coor))) != bit)
            key.append(temp_coor)
            image = temp_image.copy()
            update_progress(len(key)/(times*len(bit_message)))

    image.save("output/res_image.bmp")
    image.close()
    temp_image.close()

    with open("output/key.txt", 'a') as file:
        for coor in key:
            file.write("{}\n".format(coor))

    print("Encoding done!")

    return


def KDB_decode(image, key_path):

    key_file = open(key_path, 'r')
    key = []
    for line in key_file:
        key.append(eval(line))

    print("Decoding started!")

    raw_bit_message = []
    for coor in key:
        raw_bit_message.append(get_bit(image, coor))
        update_progress(len(raw_bit_message)/len(key))
    raw_bit_message = divide(raw_bit_message, times)

    bit_message = np.array(tuple(map(np.mean, raw_bit_message)))
    bit_message = np.array(tuple(map(delta_func, bit_message)))
    bit_message = np.char.mod('%d', bit_message)
    bit_message = ''.join(bit_message)

    message = convert_bit2str(bit_message)
    print("Decoding done!")

    return message


def behaviour(mode):
    if (mode == 'e'):
        image_path = input("Please enter the path to your image!\n")
        message = input("Please input your message!\n")
        KDB_encode(Image.open(image_path), message)
    elif (mode == 'd'):
        image_path = input("Please enter the path to your image!\n")
        key_path = input("Please enter the path to your keyfile!\n")
        message = KDB_decode(Image.open(image_path), key_path)

        print("BEGIN MESSAGE\n"+"="*17)
        print(message)
        print("="*17+"\nEND MESSAGE")

# Main code

print("Hello!\nWould you like to encode your message or decode it?")
mode = input("(e/d?)    ")

cond = True

while (cond):
    if not ((mode.lower() == 'e') or (mode.lower() == 'd')):
        mode = input("Please enter 'e' or 'd'!\n").lower()
    else:
        cond = False

behaviour(mode)
