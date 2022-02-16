import pickle, logging
import argparse
import hashlib

# For locks: RSM_UNLOCKED=0 , RSM_LOCKED=1 
RSM_UNLOCKED = bytearray(b'\x00') * 1
RSM_LOCKED = bytearray(b'\x01') * 1
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
  rpc_paths = ('/RPC2',)

# Generic Checksum size 128 bits
#CHECKSUM_SIZE = 16
# CHECKSUM_PER_BLOCK = BLOCK_SIZE//CHECKSUM_SIZE = 8
# TOTAL_CHECKSUM = TOTAL_NUM_BLOCKS*2 = 512
# TOTAL_CHECKSUM_BLOCK = TOTAL_CHECKSUM //CHECKSUM_PER_BLOCK =64

class DiskBlocks():
  def __init__(self, total_num_blocks, block_size):
    # This class stores the raw block array
    self.block = []

    #Checksum Impl.
    self.checksum_block = {}

    # Initialize raw blocks 
    for i in range (0, total_num_blocks):
      putdata = bytearray(block_size)
      self.block.insert(i,putdata)
      self.checksum_block[i] = 0

if __name__ == "__main__":

  # Construct the argument parser
  ap = argparse.ArgumentParser()
  ap.add_argument('-nb', '--total_num_blocks', type=int, help='an integer value')
  ap.add_argument('-bs', '--block_size', type=int, help='an integer value')
  ap.add_argument('-port', '--port', type=int, help='an integer value')
  ap.add_argument('-sid', '--server_id', type=int, help='an integer value')
  ap.add_argument('-cblk', '--checksum_blocks', type=int, help='an integer value')


  args = ap.parse_args()

  if args.total_num_blocks:
    TOTAL_NUM_BLOCKS = args.total_num_blocks
  else:
    print('Must specify total number of blocks') 
    quit()

  if args.block_size:
    BLOCK_SIZE = args.block_size
  else:
    print('Must specify block size')
    quit()

  if args.port:
    PORT = args.port
  else:
    print('Must specify port number')
    quit()

  if args.server_id or args.server_id == 0:
      SID = args.server_id
  else:
    print('Must specify server number')
    quit()    
  # initialize blocks
  RawBlocks = DiskBlocks(TOTAL_NUM_BLOCKS, BLOCK_SIZE)
  CORRUPTED_BLOCK = -1
  if args.checksum_blocks is not None or args.checksum_blocks == 0:
    CORRUPTED_BLOCK = args.checksum_blocks
    print("Corrupted Block: " + str(CORRUPTED_BLOCK))
  # Create server
  server = SimpleXMLRPCServer(("127.0.0.1", PORT), requestHandler=RequestHandler) 


  def Get(block_number):
    result = RawBlocks.block[block_number]
    # Grab Results and compute new checksum
    checksum_value = RawBlocks.checksum_block.get[block_number]
    # Check for block corruption
    if (block_number == CORRUPTED_BLOCK):
      print("Before Corruption: " + str(result))
      RawBlocks.block[block_number] = bytearray(b'\xFF') * BLOCK_SIZE
      checksum_value = hashlib.md5((RawBlocks.block[block_number])).hexdigest()
    # Compare checksum and return -1 if its corrupted
    if checksum_value != RawBlocks.checksum_block.get[block_number]:
      return (-1)
    return result

    
    """"
    check_sum = str(result)
    check_sum = hashlib.md5(bytes(check_sum,'utf-8')).digest()
    previous_check_sum = RawBlocks.checksum_block[block_number]
    #Check if its the first time checksum is created if so 
    #need to just return data.

    if(previous_check_sum == bytearray(CHECKSUM_SIZE)):

        return result
    #Check if checksum has been corrupted
    if(previous_check_sum != check_sum):
      print("Checksum Error current checksum :" + check_sum)
      print("Checksum Error previous checksum :" + previous_check_sum)
      return -1
    return result
    """


  server.register_function(Get)

  def Put(block_number, data):
    RawBlocks.block[block_number] = bytearray(data.data)
    #Compute CheckSum
    check_sum = hashlib.md5(RawBlocks.block[block_number]).hexdigest()
    # Store back to checksum_block
    RawBlocks.checksum_block[block_number] = check_sum

    return 0

  server.register_function(Put)

  # Run the server's main loop
  print ("Running block server with nb=" + str(TOTAL_NUM_BLOCKS) + ", bs=" + str(BLOCK_SIZE) + " on port " + str(PORT))
  server.serve_forever()

