#--------------------------------------------
#   Name: Nikhil Nayyar
#   ID: 1614962
#   CMPUT 274, Fall 2020
#
#   Assignment #2: Huffman
#--------------------------------------------

import bitio
import huffman
import pickle

def read_tree(tree_stream):
    '''Read a description of a Huffman tree from the given compressed
    tree stream, and use the pickle module to construct the tree object.
    Then, return the root node of the tree itself.

    Args:
      tree_stream: The compressed stream to read the tree from.

    Returns:
      A Huffman tree root constructed according to the given description.
    '''
    tree = pickle.load(tree_stream)       
    return tree

def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """

    traverse = 1

    # Continously read bits via bitreader
    while traverse:
        bit = bitreader.readbit()

        # Traverse the tree going either right or left based on the bit value
        if bit == 1:
            path = tree.getRight()
            tree = path
        elif bit == 0:
            path = tree.getLeft()
            tree = path

        # If a leaf node was reached, end the while loop and stop reading bits
        try:
            leaf_val = path.getValue()
            traverse = 0
        except:
            # Continue traversing the tree if not at a leaf node
            pass

    return leaf_val 


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.
    '''

    # load the tree
    tree = read_tree(compressed)

    # Instantiate the Bit Reader and Bit Writer objects
    read_bit = bitio.BitReader(compressed)
    write_val = bitio.BitWriter(uncompressed)

    # Continously decode the bytes from the compressed file until EOF is
    # reached
    try:
        while True:
            val = decode_byte(tree, read_bit)
            write_val.writebits(val, 8)
    except:
        pass # EOF

    # flush the bitwriter
    write_val.flush()
    return

def write_tree(tree, tree_stream):
    '''Write the specified Huffman tree to the given tree_stream
    using pickle.

    Args:
      tree: A Huffman tree.
      tree_stream: The binary file to write the tree to.
    '''
    pickle.dump(tree, tree_stream)
    return

def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''
    # write the tree to the compressed file
    write_tree(tree, compressed)

    # make an encoding table for compression
    encoding_table = huffman.make_encoding_table(tree)

    # Instantiate the Bit Writer and Bit Reader objects
    write_bit = bitio.BitWriter(compressed)
    bitreading = bitio.BitReader(uncompressed)

    # Continusly write the new bit sequences to the compresses file stream
    # until EOF of the uncompressed stream is reached
    write_fil = 1
    numbits = 0

    while write_fil:

        try:
            # Read the full uncompressed byte and find its encoded bit pattern
            onebyte = bitreading.readbits(8)
            comp_bits = encoding_table[onebyte]

            # Write the appropriate bits based on the encoded bit pattern
            for i in range(len(comp_bits)):
                if comp_bits[i] == True:
                    write_bit.writebit(True)
                elif comp_bits[i] == False:
                    write_bit.writebit(False)
                numbits += 1

        except:
            write_fil = 0

    # After writing the compressed bit sequences for the contents of the
    #uncompressed input stream, add the end of file bit sequence

    end_of_file = encoding_table[None]
    for i in range(len(end_of_file)):
        if end_of_file[i] == True:
            write_bit.writebit(True)
        elif end_of_file[i] == False:
            write_bit.writebit(False)
        numbits +=1

    # After counting alL the bits that were written, if the total is not a 
    # multiple of 8, add zeros to form complete bytes
    add_zeros = numbits % 8
    for i in range(add_zeros):
        write_bit.writebit(False)

    # flush the bitwriter at the end of writing bits
    write_bit.flush()
    return

