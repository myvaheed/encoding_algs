import os
import io

START_BITS = 9
CLEAR = 256
FIRST = 257

class LempZivCoding:
    def __init__(self, path):
        self.path = path
        self.dictionary = {}
        self.dict_index = FIRST
        self.dict_size_max = pow(2, START_BITS)


    def bits(self, sequence, n_bits, i_index, bits_index):
        i_ix = i_index
        b_ix = bits_index
        part = ''

        while (len(part) < n_bits and len(sequence) > i_ix):
            i = bin(sequence[i_ix])[2:]
            while (len(i) % 8 > 0):
                i = '0' + i

            if b_ix > 0:
                i = i[:-1*b_ix]

            part = i + part
            i_ix += 1
            b_ix = 0

        if (len(part) < n_bits):
            if i_ix < len(sequence):
                raise ValueError("%d < %d && %d < %d" % (len(part), n_bits, i_ix, len(sequence)))
            else:
                b = None
        else:
            b = part[-1*n_bits:]

            r = len(part) - len(b)

            if r > 0:
                i_ix -= 1
                b_ix = 8 - r

        return (b, i_ix, b_ix)

    def dict_init(self):
        self.dictionary = {i:chr(i) for i in range(256)}
        self.dict_index = FIRST
        self.dict_size_max = pow(2, START_BITS)

    def decompressLZ(self, compressed):
        i_size = len(compressed)
        n_bits = START_BITS

        result = io.StringIO()
        i_index = 0
        bits_index = 0
        w = ''
        n = 0

        self.dict_init()

        b, i_index, bits_index = self.bits(compressed, n_bits, 0, 0)
        kw = int(b, 2)
        w = chr(kw)
        result.write(w)

        while (i_index < i_size):
            b, i_index, bits_index = self.bits(compressed, n_bits, i_index, bits_index)

            if b is None:
                print("EOF. Breaking loop... (%d, %d)" % (i_index, i_size))
                break

            kw = int(b, 2)
            
            if kw in self.dictionary:
                entry = self.dictionary[kw]
            elif kw == self.dict_index:
                entry = w + w[0]
            else:
                raise ValueError('%d: Bad keyword (%d)' % (n, kw))

            result.write(entry)

            if self.dict_index < self.dict_size_max:
                self.dictionary[self.dict_index] = w + entry[0]
                self.dict_index += 1

            w = entry

            if self.dict_index == self.dict_size_max:
                n_bits += 1
                self.dict_size_max = pow(2, n_bits)
                # print('New bit size: %d' % n_bits)
            n += 1
        return result.getvalue()
    
    def decompress(self, input_path):
        filename, _ = os.path.splitext(self.path)
        output_path = filename + "_decomp" + ".txt"

        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            compressed = file.read()
            decompressed = self.decompressLZ(compressed)
            output.write(decompressed)
            comp_size = len(compressed)
            decomp_size = len(decompressed)

            print('Compressed size: %d' % comp_size)
            print('Decompressed size: %d' % decomp_size)
            factor = 1.0 - float(comp_size)/float(decomp_size)
            print('Compression fraction: %f' % factor)

        
        print("Decompressed")

    def int_to_bin(self, i, n):
        b = bin(i)[2:]
        while (len(b) < n):
            b = '0' + b
        return b

    def reset_dict(self):
        self.dictionary = {chr(i): i for i in range(256)}
        self.dict_index = FIRST
        self.dict_size_max = pow(2, START_BITS)

    def compressLZ(self, data):
        n_bits = START_BITS

        self.reset_dict()

        o_bytes = bytearray()
        o_buffer = ''
        w = ''

        for c in data:
            wc = w + c
            if wc in self.dictionary:
                w = wc
            else:
                o_buffer = self.int_to_bin(self.dictionary[w], n_bits) + o_buffer

                if self.dict_index == self.dict_size_max:
                    n_bits += 1
                    self.dict_size_max = pow(2, n_bits)
                    # print('New bit size: %d' % n_bits)

                if self.dict_index < self.dict_size_max:
                    self.dictionary[wc] = self.dict_index
                    self.dict_index += 1

                w = c

                if len(o_buffer) > 8:
                    o_bytes.append(int(o_buffer[-8:], 2))
                    o_buffer = o_buffer[:-8]

        if w:
            o_buffer = self.int_to_bin(self.dictionary[w], n_bits) + o_buffer

        while (len(o_buffer) > 0):
            if len(o_buffer) > 8:
                o_bytes.append(int(o_buffer[-8:], 2))
                o_buffer = o_buffer[:-8]
            else:
                o_bytes.append(int(o_buffer, 2))
                o_buffer = ''

        return bytes(o_bytes)
    
    def compress(self):
        filename, _ = os.path.splitext(self.path)
        output_path = filename + ".bin"
        
        with open(self.path, "r") as f, open(output_path, 'wb') as output:
            data = f.read()
            compressed = self.compressLZ(data)
            output.write(compressed)
            print('Input size: %d' % len(data))
            return output_path


lzw = LempZivCoding("./samp1.txt")
 
output_file = lzw.compress()
lzw.decompress(output_file)