#include "HashBase.h"
#include <stdint.h>
#include <stddef.h>
import numpy


def ROTL64(x, s):
  return (x << s) | (x >> (64 - s))

def MUL5_64(x):
  return x * 5

def fmix64(blk):
  fmc1 = numpy.uint64(0xff51afd7ed558ccd)
  fmc2 = numpy.uint64(0xc4ceb9fe1a85ec53)
  blk ^= (blk >> 33)
  blk *= fmc1
  blk ^= (blk >> 33)
  blk *= fmc2
  blk ^= (blk >> 33)
  return blk


hashMURMUR3F = numpy.uint32(1)


class MurmurHash3F(object): # : public HashBase {
#public:
#    virtual int32_t getHashBitSz(void) const;
#    virtual int32_t getSeedBitSz(void) const;
#    virtual int32_t getAlgoID(void) const;
#    virtual int32_t getBlkByteSz(void) const;
#    virtual bool isValid(void) const;
#    virtual bool isReady(void) const;
#    virtual const char* getHash(void) const;
#    virtual const uint64_t getDataCount(void) const;
#    virtual void init(/*in*/ const void* seed = NULL);
#    virtual void hashBlock(/*in*/ const void* data, /*in*/ uint64_t sz, /*in*/ const void* seed = NULL);
#    virtual void hashStreamIntrn(/*in*/ const void* data, /*in*/ uint64_t sz);
#    virtual void hashStreamFinal(void);
#    virtual bool operator==(const void* data) const;
#    virtual bool operator==(const HashBase& h) const;

  def __init__(self):
    self.f_byte_cnt = numpy.uint64(0)
    self.f_hash     = [ numpy.uint64(0), numpy.uint64(0)]
    self.f_tail     = [ numpy.uint64(0), numpy.uint64(0)]
    self.f_tail_sz  = numpy.uint32(0)
    self.f_valid    = True
    self.f_ready    = False

  def getHashBitSz(self):
    return numpy.uint32(128)

  def getSeedBitSz(self):
    return numpy.uint32(128)

  def getAlgoID(self):
    return hashMURMUR3F

  def getBlkByteSz(self):
    numpy.int32(16)

  def isValid(self):
    return self.f_valid

  def isReady(self):
    return self.f_ready

  def getHash(self):
    return struct.pack('QQ', self.f_hash[0], self.f-hash[1])

  def getDataCount(self):
    return self.f_byte_cnt + self.f_tail_sz

  def init(self, seed=None):
    if not seed:
      self.f_hash[0] = numpy.uint64(0)
      self.f_hash[1] = numpy.uint64(0)
    elif type(seed) is str:
      self.f_hash[0], self.f_hash[1] = struct.unpack('QQ', seed)
    else:
      self.f_hash[0],self.f_hash[1] = numpy.uint64(seed[0]),numpy.uint64(seed[0])
    f_byte_cnt = numpy.uint64(0)
    f_tail_sz = numpy.uint32(0)

  def hashBlock(data, sz, seed):
    self.init(seed)
    self.hashStreamIntrn(data, sz)
    self.hashStreamFinal()

  def hashStreamIntrn(data, sz):
    dptr = 0
    if self.f_tail_sz != numpy.uint32(0):
      if not data or not sz:  # final round
        murmurHash3F_stream_cont(self.f_tail, self.f_tail_sz,
                                 self.f_hash, self.f_hash)
        self.f_byte_cnt += self.f_tail_sz
        self.f_tail_sz = numpy.uint32(0)
      else:
        v_tadd = numpy.int32(16 - self.f_tail_sz)
        if numpy.int64t(sz) >= v_tadd:
          sz -= v_tadd;
          tptr = struct.pack('QQ', self.f_tail[0], self.f_tail[1])
          tptr = tptr[v_tadd:] + data[dptr]
          tvs = struct.unpack("QQ", tptr[0:16])
          self.t_tail = [numpy.uint64(tvs[0]), numpy.uint64(tv[1])]
          murmurHash3F_stream_cont(self.f_tail, 16, self.f_hash, self.f_hash)
          self.f_tail_sz = numpy.uint32(0)
          self.f_byte_cnt += 16
        else:
          self.f_tail_sz += sz
          dptr += sz
          tail = ""
          for dx in range(sz, 0, -1):
            tail = data[dptr+sz] + tail
          tail = "\0" * (16-sz) + tail
          tvs = struct.unpack("QQ", tail)
          self.t_tail = [numpy.uint64(tvs[0]), numpy.uint64(tv[1])]

    if sz:
      self.f_tail_sz = sz & 0x0f
      sz &= ~0x0f
      murmurHash3F_stream_cont(data[dptr:], sz, self.f_hash, self.f_hash)
      self.f_byte_cnt += sz
      if self.f_tail_sz:
        self.f_tail[0] = [numpy.uint64(0), numpy.uint64(0)]
        dptr += sz
        tail = data[dptr:] + '\0' * (16-self.f_tail_sz)
        tvs = struct.unpack("QQ", tail)
        self.t_tail = [numpy.uint64(tvs[0]), numpy.uint64(tv[1])]

  def hashStreamFinal(self):
    if self.f_tail_sz:
      hashStreamIntrn(None, 0)
    murmurHash3F_stream_final(self.f_byte_cnt, self.f_hash)
    self.f_ready = True

  def __eq__(self, other):
    if type(other) is str:
      ohash = struct.unpack("QQ", data[0:8])
      return self.f_hash[0] == ohash[0] and self.f_hash[1] == ohash[1]
    else:
      return other and self.isValid() and other.isValid() and \
             self.isReady() and other.isReady() and \
             self.getAlgoID() == other.getAlgoID() and \
             self.f_hash == other.f_hash


def murmurHash3F_stream_cont(data, sz, hash, seed=None):
  """Calculate the 128-bit MurmurHash3 of a set of multiple data blocks.
  Arguments:
    const_char* data    pointer to the data buffer to calculate the digest for
    uint32_t    sz      size of the input buffer
    uint64_t    hash[2] buffer to put the calculated digest into
    uint64_t    seed[2] the nonce/salt to initialize the hashing
                        e.g. result of a previous stream_cont round
  """
  cc1 = numpy.uint64(0x87c37b91114253d5)
  cc2 = numpy.uint64(0x4cf5ad432745937f)
  cc3 = numpy.uint32(0x52dce729)
  cc4 = numpy.uint32(0x38495ab5)

  hv1 = numpy.uint64(0)
  hv2 = numpy.uint64(0)
  if seed is None:
    hv1 = seed[0]
    hv2 = seed[1]

  tail_sz = numpy.uint32(sz & 0x0f)
  #  const uint64_t* dptr = (const uint64_t*)data;
  dptr = 0
  idx = numpy.uint64(sz >> 4)
  while idx > 0:
    tv1 = numpy.uint64(struct.unpack('Q', data[dptr:dptr+8])[0])
    dptr += 8
    tv2 = numpy.uint64(struct.unpack('Q', data[dptr:dptr+8])[0])

    tv1 *= cc1
    tv1 = ROTL64(tv1, 31)
    tv1 *= cc2
    hv1 ^= tv1

    hv1 = ROTL64(hv1, 27)
    hv1 += hv2;
    hv1 = MUL5_64(hv1) + cc3

    tv2 *= cc2
    tv2 = ROTL64(tv2, 33)
    tv2 *= cc1
    hv2 ^= tv2

    hv2 = ROTL64(hv2, 31)
    hv2 += hv1
    hv2 = MUL5_64(hv2) + cc4

    idx -= 1
    dptr += 8
    #end while

  if tail_sz:
    tv1 = numpy.uint64(0)
    tv2 = numpy.uint64(0)
    tail_ptr = struct.unpack('B'*tail_sz, data[dptr:])
    for tdx in range(tail_sz, 0, -1):
      if tdx == 15:
        tv2 = numpy.uint64(tail_ptr[14]) << 48
      elif tdx == 14:
        tv2 |= numpy.uint64(tail_ptr[13]) << 40
      elif tdx == 13:
        tv2 |= numpy.uint64(tail_ptr[12]) << 32
      elif tdx == 12:
        tv2 |= numpy.uint32(struct.unpack('I', data[dptr+8:dptr+12]))
        tv1 = struct.unpack('Q', data[dptr])[0]
        break
      elif tdx == 11:
        tv2 = uint64_t(tail_ptr[10]) << 16
      elif tdx == 10:
        tv2 |= uint64_t(tail_ptr[9]) << 8
      elif tdx == 9:
        tv2 |= tail_ptr[8]
      elif tdx == 8:
        tv1 = numpy.uint64(struct.unpack('Q', data[dptr:dptr+8])[0])
        break
      elif tdx == 7:
        tv1 = numpy.uint64(tail_ptr[6]) << 48
      elif tdx == 6:
        tv1 |= numpy.uint64(tail_ptr[5]) << 40
      elif tdx == 5:
        tv1 |= numpy.uint64(tail_ptr[4]) << 32
      elif tdx == 4:
        tv1 |= numpy.uint32(struct.unpack('I',data[dptr:dptr+4])[0])
        break
      elif tdx == 3:
        tv1 = numpy.uint64(tail_ptr[2]) << 16
      elif tdx == 2:
        tv1 |= numpy.uint64(tail_ptr[1]) << 8
      elif tdx == 1:
        tv1 |= tail_ptr[0]
    #end for
    tv2 *= cc2
    tv2 = ROTL64(tv2, 33)
    tv2 *= cc1
    hv2 ^= tv2
    tv1 *= cc1
    tv1 = ROTL64(tv1, 31)
    tv1 *= cc2
    hv1 ^= tv1
    #end if tail_sz

  hash[0] = hv1
  hash[1] = hv2


def murmurHash3F_stream_final(sz, hash):
  """Finalize the calculation of the 32-bit MurmurHash3 from a set of
  multiple data blocks.
  Arguments:
    uint64   sz       cumulative length
    uint64*  hash     buffer to put the calculated digest into
  """
  hv1 = numpy.uint64(hash[0])
  hv2 = numpy.uint64(hash[1])

  hv1 ^= sz
  hv2 ^= sz

  hv1 += hv2
  hv2 += hv1

  hv1 = fmix64(hv1)
  hv2 = fmix64(hv2)

  hv1 += hv2
  hash[0] = hv1
  hash[1] = hv2 + hv1


def murmurHash3F(data, sz, hash, seed=None):
  """Calculate the 128-bit MurmurHash3
  Arguments:
    char*     data     pointer to the data buffer to calculate the digest for
    uint64_t  sz       size of the input buffer
    uint64_t  hash[2]  buffer to put the calculated digest into
    uint64_t  seed[2]  the nonce/salt to initialize the hashing
  """
  murmurHash3F_stream_cont(data, sz, hash, seed)
  murmurHash3F_stream_final(sz, hash)



if __name__ == "__main__":
  import sys
  fp = open(sys.argv[1], "rb")

  hash = MurmurHash3F()
  hash.init()

  EOF = True
  while not EOF:
    buf = fp.read(512)
    if buf:
      hash.hashStreamIntrn(buf, len(buf))
    else:
      EOF = True

  hash.hashStreamFinal()

  print "Hash Data Count %s" % hashM3F.getDataCount()
#printf("Hash Size %db %dB\n", hashM3F.getHashBitSz(), hashM3F.getHashBitSz()>>3);
#unsigned long csVal[2] = { 0 };
#memcpy(csVal, hashM3F.getHash(), sizeof(csVal));
#printf("%08lX %08lX\n", csVal[0], csVal[1]);

