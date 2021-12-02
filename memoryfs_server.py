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
CHECKSUM_SIZE = 16
# CHECKSUM_PER_BLOCK = BLOCK_SIZE//CHECKSUM_SIZE = 8
# TOTAL_CHECKSUM = TOTAL_NUM_BLOCKS*2 = 512
# TOTAL_CHECKSUM_BLOCK = TOTAL_CHECKSUM //CHECKSUM_PER_BLOCK =64

class DiskBlocks():
  def __init__(self, total_num_blocks, block_size):
    # This class stores the raw block array
    self.block = []

    #Checksum Impl.
    self.checksum_block = []

    # Initialize raw blocks 
    for i in range (0, total_num_blocks):
      putdata = bytearray(block_size)
      checksum_block = bytearray(CHECKSUM_SIZE)

      self.block.insert(i,putdata)
      self.checksum_block.insert(i,checksum_block)

if __name__ == "__main__":

  # Construct the argument parser
  ap = argparse.ArgumentParser()
  ap.add_argument('-nb', '--total_num_blocks', type=int, help='an integer value')
  ap.add_argument('-bs', '--block_size', type=int, help='an integer value')
  ap.add_argument('-port', '--port', type=int, help='an integer value')
  ap.add_argument('-sid', '--server_id', type=int, help='an integer value')
  ap.add_argument('-clbk', '--checksum_blocks', type=int, help='an integer value')



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

  #if args.sid:
  #    SID = args.sid
 # else:
  #  print('Must specify server number')
  #  quit()    
  # initialize blocks
  RawBlocks = DiskBlocks(TOTAL_NUM_BLOCKS, BLOCK_SIZE)

  # Create server
  server = SimpleXMLRPCServer(("127.0.0.1", PORT), requestHandler=RequestHandler) 

  def Get(block_number):
    result = RawBlocks.block[block_number]
    # Grab Results and compute new checksum
    check_sum = str(result)
    print("Stupid")
    check_sum = hashlib.md5(bytes(check_sum,'utf-8')).digest()
    print("Fuck")
    previous_check_sum = RawBlocks.checksum_block[block_number]
    print("a")
    #Check if its the first time checksum is created if so 
    #need to just return data.

    if(previous_check_sum == bytearray(CHECKSUM_SIZE)):

        return result
    print('d')
    #Check if checksum has been corrupted
    if(previous_check_sum != check_sum):
      print("Checksum Error current checksum :" + check_sum)
      print("Checksum Error previous checksum :" + previous_check_sum)
      return -1
    return result

  server.register_function(Get)

  def Put(block_number, data):
    RawBlocks.block[block_number] = data
    ## Broken Block placement can go here
    
    #Compute CheckSum
    check_sum = str(data)
    check_sum = hashlib.md5(bytes(check_sum,'utf-8')).digest()
    
    # Store back to checksum_block
    RawBlocks.checksum_block[block_number] = check_sum

    return 0

  server.register_function(Put)

  def RSM(block_number):
    result = RawBlocks.block[block_number]
    # RawBlocks.block[block_number] = RSM_LOCKED
    RawBlocks.block[block_number] = bytearray(RSM_LOCKED.ljust(BLOCK_SIZE,b'\x01'))
    return result

  server.register_function(RSM)

  # Run the server's main loop
  print ("Running block server with nb=" + str(TOTAL_NUM_BLOCKS) + ", bs=" + str(BLOCK_SIZE) + " on port " + str(PORT))
  server.serve_forever()

