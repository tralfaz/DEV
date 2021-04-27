import sys

def EncodeMsg(msg, pad):

  padLen = len(pad)
  padX   = 0

  encodeMsg = ""
  for msgChr in msg:
    encodeOrd = ord(msgChr) ^ ord(pad[padX])
    encodeChr = chr(encodeOrd)
    encodeMsg += encodeChr
    padX = (padX + 1) % padLen

  return encodeMsg


if __name__ == "__main__":

  msg = "Secret Message Never Read!"
  pad = "9hdshe9w8io864r9hnb eowf cej8ufe3fc3afl-93487s"

  encodedMsg = EncodeMsg(msg, pad)
  print "Encoded MSG %r" % encodedMsg
  decodedMsg = EncodeMsg(encodedMsg, pad)
  print "Decoded MSG %r" % decodedMsg
