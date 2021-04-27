import ctypes
import fcntl
import io
import os
import struct
import sys
import threading
import uuid

__LOG = None #open("sbstatefile.log", "w")
def LOG(msg):
    if __LOG:
        __LOG.write(msg+"\n"); __LOG.flush()


try:
    if not sys.argv[0] or not os.path.dirname(sys.argv[0]):
        cwd = "."
    else:
        cwd = os.path.dirname(sys.argv[0])
    libm3fapi = ctypes.cdll.LoadLibrary(os.path.join(cwd, "libm3fapi.so"))
except Exception as exc:
    LOG("ERROR: LoadLibrary: %s path=%s" % (exc, os.path.join(cwd, "libm3fapi.so")))
    libm3fapi = None
                              
class MurmurHash3F(object):

    def __init__(self):
        if not libm3fapi:
            return
        libm3fapi.MurmurHash3F_new.argtypes = []
        libm3fapi.MurmurHash3F_new.restype = ctypes.c_void_p
        libm3fapi.MurmurHash3F_count.argtypes = []
        libm3fapi.MurmurHash3F_count.restype = ctypes.c_uint64
        libm3fapi.MurmurHash3F_finish.argtypes = []
        libm3fapi.MurmurHash3F_finish.restype = ctypes.c_void_p
        libm3fapi.MurmurHash3F_hash.argtypes = []
        libm3fapi.MurmurHash3F_hash.restype = ctypes.POINTER(ctypes.c_ubyte*16)
        libm3fapi.MurmurHash3F_init.argtypes = []
        libm3fapi.MurmurHash3F_init.restype = ctypes.c_void_p
        libm3fapi.MurmurHash3F_update.argtypes = [ctypes.c_void_p,
                                                  ctypes.c_char_p,
                                                  ctypes.c_uint64]
        libm3fapi.MurmurHash3F_update.restype = ctypes.c_void_p
        self.obj = libm3fapi.MurmurHash3F_new()
    def count(self):
        return libm3fapi.MurmurHash3F_count(self.obj)
    def finish(self):
        libm3fapi.MurmurHash3F_finish(self.obj)
    def hash(self):
        return libm3fapi.MurmurHash3F_hash(self.obj)
    def hashbytes(self):
        return ''.join([chr(b) for b in self.hash().contents])
    def init(self):
        libm3fapi.MurmurHash3F_init(self.obj)
    def update(self, data):
        buf = ctypes.create_string_buffer(data)
        libm3fapi.MurmurHash3F_update(self.obj, buf, ctypes.c_uint64(len(data)))


RECAIDTYPE  = 0
RECSTATTYPE = 1
RECAIDLEN   = 49
RECSTATLEN  = 37

RECAIDSTRUCT  = "=iiii16s16s"
RECSTATSTRUCT = "=iiiiiQQ"

# The Data Structures below are used in SBState Interfaces with e.g. PersistencyProvider or SectionBroker

class Assignment(object):
    """Fundamental SBState Interface Type. Unique Identifier of the Work
    Assignment in the DJS Architecture"""

    def __init__(self, phase=-1, col=-1, row=-1, assignId=-1):
        self._phase    = phase     # int
        self._col      = col       # int
        self._row      = row       # int
        self._assignId = assignId  # int

    def __eq__(self, other):
        return self._phase == other._phase and self._col == other._col and \
               self._row == other._row and self._assignId == other._assignId
        
    def __ne__(self, other):
        return self._phase != other._phase or self._col != other._col or \
               self._row != other._row or self._assignId != other._assignId

    def __lt__(self, other):
        retVal = self._phase < other._phase
        if not retVal and self._phase == other._phase:
            retVal = self._row < other._row
            if not retVal and self._row == other._row:
                retVal = self._col < other._col
                if not retVal and self._col == other._col:
                    retVal = self._assignId < other._assignId
        return retVal


class AssignmentIDRec(Assignment):
    """The Record-Identifier of the Assignment's Location. Provides the
    Coordinates (SJM@DC) of the DJS Component that is Controlling the
    execution of the Work Assignment."""
    
    def __init__(self, phase=0, col=0, row=0, aid=0,
                 sjmUUID=uuid.UUID(bytes='\0'*16),
                 dcUUID=uuid.UUID(bytes='\0'*16)):
        super(AssignmentIDRec, self).__init__(phase, col, row, aid)
        self._SJM = sjmUUID
        self._DC  = dcUUID

    def encode(self):
        return struct.pack(RECAIDSTRUCT, self._phase, self._col,
                           self._row, self._assignId,
                           self._SJM.bytes, self._DC.bytes)

    def __eq__(self,other):
        return self._SJM == other._SJM and self._DC == other._DC and \
               super(AssignmentIDRec,self).__eq__(other)
    
    def __ne__(self, other):
        return self._SJM != other._SJM or self._DC != other._DC and \
               super(AssignmentIDRec,self).__ne__(other)

    def __lt__(self, other):
        retVal = super(AssignmentIDRec,self).__lt__(other)
        if not retVal and super(AssignmentIDRec,self).__eq__(other):
            retVal = self._DC < other._DC
            if not retVal and selr._DC == other._DC:
                retVal = self._SJM < other_SJM
        return retVal

    def __str__(self):
        return "AIDRec(aid=%s,phase=%s,row=%s,col=%s,SJM=%s,DC=%s)" % \
                (self._assignId, self._phase, self._row, self._col, self._SJM, self._DC)
    

class AssignmentStateRec(Assignment):
    """The Record documenting the State Transition of the Work Assignment:
    the new State and the TimeStamp of the State Transition Event"""

    def __init__(self, phase=0, col=0, row=0, aid=0,
                 state=0, tvSec=0, tvNSec=0):
        super(AssignmentStateRec,self).__init__(phase, col, row, aid)
        self._stateId = state
        self._tvSec   = long(tvSec)
        self._tvNSec  = long(tvNSec)


    def encode(self):
        return struct.pack(RECSTATSTRUCT, self._phase, self._col,
                           self._row, self._assignId,
                           self._stateId, self._tvSec, self._tvNSec)

    def __eq__(self, other):
        return self._stateId == other._stateId and \
               self._tvSec == other._tvSec and \
               self._tvNSec == other._tvNSec and \
               super(AssignmentStateRec,self).__eq__(other)

    def __ne__(self, other):
        return self._stateId != other._stateId or \
               self._tvSec != other._tvSec or \
               self._tvNSec != other._tvNSec or \
               super(AssignmentStateRec,self).__ne__(other)

    def __lt__(self, other):
        retVal = super(AssignmentStateRec,self).__lt__(other)
        if not retVal and super(AssignmentStateRec,self).__eq__(other):
            retVal = self._tvSec < other._tvSec
            if not retVal and self._tvSec == other._tvSec:
                retVal = self._tvNSec < other._tvNSec
                if not retVal and self._tvNSec == other._tvNSec:
                    retVal = self._stateId < other._stateId
        return retVal;

    def __str__(self):
        return "StateRec(aid=%s,phase=%s,row=%s,col=%s,state=%s(%s),time=%s)" % \
                (self._assignId, self._phase, self._row, self._col, AssignmentStateID.ToStr(self._stateId), self._stateId, self._tv_sec)


#struct AssignmentHint : public Assignment {
#    UUID d_SJM;
#    UUID d_DC;
#    ASSIGNMENTSTATEID d_stateId;
#    struct timespec d_stateTm;
#    AssignmentHint() : Assignment(-1, -1, -1, -1), d_stateId(asANY)
#    {
#        d_stateTm.tv_sec = 0;
#        d_stateTm.tv_nsec = 0;
#    }
#    AssignmentHint(const Assignment& a, ASSIGNMENTSTATEID state = asANY) : Assignment(a), d_stateId(state)
#    {
#    }
#};
#
#struct StateTransition {
#    typedef std::vector<StateTransition> Vec_t;
#
#    StateTransition() : d_stateId(asUNAVAILABLE)
#    {
#        d_stateTm.tv_sec = d_stateTm.tv_nsec = 0;
#    }
#    StateTransition(const AssignmentStateRec& sR) : d_stateTm(sR.d_stateTm), d_stateId(sR.d_stateId)
#    {
#    }
#
#    struct timespec d_stateTm;
#    ASSIGNMENTSTATEID d_stateId;
#};
#
#const std::string& Str(ASSIGNMENTSTATEID as);
#const char* CStr(ASSIGNMENTSTATEID as);
#ASSIGNMENTSTATEID StateIDFromName(const std::string& stateNm);
#
#typedef std::map<std::string, std::string> KVMap_t;  // Type of the Attribute Map


class PersistencyProvider(object):
    DUMMY      = 0
    BASICFILE  = 1
    TABLEFILES = 2

    def __init__(self):
        pass

    @classmethod
    def CreateProvider(cls, ppType, path, bkupSuffix=".bak", writable=True, checkSumProtected=True):
        if ppType == cls.DUMMY:
            store = DummyStore(path, bkupSuffix, writable, checkSumProtect)
        elif ppType == cls.TABLEFILES:
            store = TableFileStore(path, bkupSuffix, writable, checkSumProtect)
        else:
            return None
        store.reset()
        return store

    def Reset(self):
        """Reset the persistent SB State"""
        pass

    def Load(self, kvData, assignments, states):
        """Return Data to construct the SBState object from the persistent state
        Arguments:
          /*out*/ KVMap_t& kvData,
          /*out*/ AssignmentIDRec::Vec_t& assignments,
          /*out*/ AssignmentStateRec::Vec_t& states
        """
        pass

    def StoreAttrs(self, kvData):
        """Write the Update of the Attributes' Values into the Persistent
        SB State Storage"""
        pass

    def UpdateState(self, assignments, stateRecords):
        """Write the Update of the Sections' States into the Persistent
        SB State Storage
        Arguments:
          /*in*/ const AssignmentIDRec::Vec_t& assignments,
          /*in*/ const AssignmentStateRec::Vec_t& stateRecords) = 0;
        """
        pass

    def IsWritable(self):
        """Return if the provider can be modified"""
        pass

    def Verify(self):
        """Validate the current state of the provider"""
        pass
    

class PersistencyFile(object):

    def __init__(self, path, bkUpSuffix=".bak", writable=True, useCheckSum=True):
        self._ioLock = threading.RLock()                        # synchronization object
        self._pathPrim = path                 # file path for the main data file
        self._pathBkUp = None                 # backup file path
        self._csGen    = None                 # hash generator object
        self._fdPrim = None                   # file descriptor for d_pathPrim
        self._fdBack = None                   # file descriptor for d_pathBkUp
        self._recovered = False                # marker that the file was recovered, no need to recreate the backup

        openFlags = "wb" if writable else "rb"
        self._fdPrim = self._fOpenFd(path, openFlags, "Primary")
        if bkUpSuffix or not useCheckSum:
            self._pathBkUp = self._pathPrim + bkUpSuffix
            self._fdBack = self._fOpenFd(self._pathBkUp, openFlags, "Backup")

        if useCheckSum and libm3fapi:
            self_csGen = MurmurHash3F()
            self._csGen.init()

        # flag enabling writing. Set on construction if requested, reset on error
        self._writable = writable and self._fdPrim and (self._fdBack or bkUpSuffix)

    def Append(self, buf, sz):
        """
        Arguments:
          const char* buf,
          size_t      sz
        """
        with self._ioLock:
            retVal = self._writable
            if retVal:
                if self.tell() == 0:
                    # writing to the file(s) has just started, truncate the files
                    retVal = self._resetNoLock()

            if retVal:
                # append a chunk of data to the writable container
                csVal = "\0" * 16  # Checksum data
                csPos = 0          # and
                csLen = 0          # properties
                if self._csGen:    # maintain single checksum record at the very end of file
                    if sz > 0:
                        self._csGen.update(buf[:sz])
                    cs = MurmurHash3F(self._csGen) # Clone the Checksum object to perform the final round of CS calculation
                    cs.finish()          # CS (checksum) is ready now
                    csVal = cs.hash()    # store the actual CS in csVal var
                    csPos = cs.count()           # Total data length
                    csLen = 16 #(cs.getHashBitSz() >> 3) # CS size in bytes

                retVal = self._fAppendFd(self._fdPrim, buf, sz, csVal, csPos, csLen)
                if retVal and self._fdBack:  # backup file is configured and ready
                    retVal = self_fAppendFd(self._fdBack, buf, sz, csVal, csPos, csLen)


            if not retVal:
                self._writable = False
                print "Log::error: Writing to the SB State File '%s' is disabled. The File is not available, not writable, or is " \
                    + "in an Incorrect State." % self._pathPrim

            return retVal

    def IsWritable(self):
        return self._writable

    def Verify(self):
        retVal = True
        with self._ioLock:
            if self._csGen:
                retVal = self._fChkCSumFd(self._fdPrim)
                if self._fdBack:
                    backCSValid = self._fChkCSumFd(self._fdBack)
                    if self._writable:
                        retVal &= backCSValid
                    else:
                        retVal |= backCSValid
        return retVal

    def Read(self, sz):
        buf = None
        with self._ioLock:
            if sz > 0:
                if self._fdPrim: # the primary file must always be open in a usable object
                    # only validate the checksum of files once (when the fpos == 0)
                    doChkSum = self._csGen and self._fdPrim.tell() == 0
                    validPrim = not doChkSum or self._fChkCSumFd(self._fdPrim)
                    readFP = None
                    if validPrim:
                        readFP = self._fdPrim
                    else: # The primary file is damaged
                        print "Log::warn: Missing or damaged Primary SB State File '%s'." % self._pathPrim
                        wasWritable = self._writable
                        self._writable = False
                        if self._fdBack and self.fChkCSumFd(self._fdBack): # The backup file is healthy
                            if wasWritable:
                                print "Log::info: Restoring the damaged Primary SB State File '%s' from the Backup Copy." % \
                                      self._pathPrim
                                if self._fCloneFdFrom(self._fdPrim, self._fdBack): # Copy the backup to the primary file
                                    validPrim = self._writable = self._recovered = True
                                    readFP = self._fdPrim
                                    print "Log::info: The Primary SB State File successfully restored from the Backup Copy."
                                else:
                                    rdBytes = -1
                                    print "Log::error: Failed to restore the Backup SB State File '%s'." % self._pathBkUp
                            else:
                                readFP = self._fdBack
                        else:
                            print "Log::error: Failed to restore the Primary SB State File '%s' " + \
                                  "No valid Backup Copy is available." % self._pathPrim
                    if readFP:
                        buf = self._fReadFd(readFP, sz)
                        if buf:
                            LOG("INFO: Read %s bytes from the SB State file '%s'." % (len(buf), self._fPathFromFd(readFP)))
                            if self._csGen:
                                self._csGen.hashStreamIntrn(buf)
                        tailCond = len(buf) >= 0 and len(buf) < sz
                        if validPrim and self._writable and self._fdBack and tailCond:
                            if not self._recovered: # primary file was correct - copy its contents to the backup file
                                if not self._fCloneFdFrom(self._fdBack, self.d_fdPrim):
                                    buf = None
                                    print "Log::error: Failed to save the Backup SB State File '%s'." % self._pathBkUp
                            else: # no need overwrite the backup file - only fix the fpos
                                self._fdBack.seek(self._fdPrim.ftell(), io.SEEK_SET)
            else:
                buf = ""

        return buf

    def Rewind(self):
        retVal = True
        with self._ioLock:
            try:
                if self._fdPrim:
                    self._fdPrim.seek(0, io.SEEK_SET)
                if self._fdBack:
                    self._fdBack.seek(0, io.SEEK_SET)
            except IOError:
                retVal = False
            if self._csGen:
                self._csGen.init()
        return retVal

    def Reset(self):
        with self._ioLock:
            return self._resetNoLock()
                                                            
    def _resetNoLock(self):
        retVal = True
        if self._fdPrim:
            retVal = self._fTruncateFd(self._fdPrim)
        if self._fdBack:
            retVal &= self._fTruncateFd(self._fdBack)
        if self._csGen:
            self._csGen.init()
        return retVal

    def _fPathFromFd(self, fp):
        if fp == self._fdPrim:
            return self._pathPrim
        elif fp == self._fdBack:
            return d_pathBkUp
        else:
            return "*UNKNOWN*"

    def _fRoleFromFd(self, fp):
        if fp == self._fdPrim:
            return "Primary";
        elif fp == self._fdBack:
            return "Backup";
        else:
            return "*UNKNOWN*";

    def _fOpenFd(self, path, flags, role):
        try:
            fp = file(path, flags)
        except IOError as ioe:
            print "Log::error: Failed to open the %s SB State file '%s'. Error %s." % (role, path, ioe)
            return None

        fcntl.fcntl(fp.fileno(), fcntl.F_SETFD, fcntl.FD_CLOEXEC)
        fp.seek(0, io.SEEK_SET)

        return fp


    def _fReadFd(self, fp, sz):
        buf = None
        if self._csGen:
            #struct stat st;
            #if (fstat(fd, &st) == 0) {
            #    off_t maxBytes = st.st_size - lseek(fd, 0, SEEK_CUR) - (d_csGen->getHashBitSz() >> 3);
            #    if (maxBytes > 0) {
            #        rdBytes = std::min(static_cast<off_t>(sz), maxBytes);
            #    } else {
            #        rdBytes = 0;
            #        retVal = 0;
            #    }
            #} else {
            #    char eMsg[256];
            #    posix_strerror_r(errno, eMsg, sizeof(eMsg));
            #    Log::error("Failed to stat the %s SB State file '%s'. Error %d (%s).",  //
            #               FRoleFromFd(fd), FPathFromFd(fd), errno, eMsg);              //
            #    rdBytes = -1;
            #}
            pass

        try:
            buf = fp.read( sz)
        except IOError, ioe:    
            print "Log::error: Failed to read the %s SB State file '%s'. Error %s." % \
                  (self._fRoleFromFd(fp), self._fFPathFromFd(fp), ioe, eMsg)
        return buf

    def _fAppendFd(self, fp, buf, sz, csVal, csPos,csLen):
        """
        Arguments:
          fp,
          const char* buf,
          size_t sz,
          long csVal[2],
          off_t csPos,
          off_t csLen
        """
        try:
            fp.write(buf[0:sz-1])   # write the contents, overwrite the checksum record
        except IOError, ioe:
            print "Log::error: Failed to write the %s SB State file '%s'. Error %s." % \
                  (self._fRoleFromFd(fp), self._fPathFromFd(fp), ioe)
            return False

        if csPos  >= 0: # update checksum as needed
            try:
                pwrite(fd, csVal, csLen, csPos) # write the checksum, file position not updated
            except IOError, ioe:
                print "Log::error: Failed to write the Checksum for the %s SB State file '%s'. Error %s." % \
                      (self._fRoleFromFd(fp), self._fPathFromFd(fp), ioe)
                return False
        return True

    def _fTruncateFd(self, fp):
        try:
            os.ftruncate(fp.fileno(), 0)
            fp.seek(0, io.SEEK_SET)
            return True
        except IOError as ioe:
            retVal = False
            print "Log::error: Failed to truncate the %s SB State file '%s'. Error %s)." \
                  % (self._fRoleFromFd(fp), self._fPathFromFd(fp), ioe)
            return False

    def _ChkCSumFd(self, fp):
        retVal = fp is not None
        if retVal and self._csGen:
            savePos = fp.tell()        # position must be restored afterwards
            fp.seek(-16, io.SEEK_END)  # file length - size of hash
            csPos = fp.tell() 
#            if (savePos >= 0 && csPos >= 0) {
#                MurmurHash3F csAct;      // Object to calculate the actual file checksum
#                unsigned long csExp[2];  // Expected file checksum (stored at the end of the file)
#                retVal = (::read(fd, csExp, sizeof(csExp)) == sizeof(csExp));
#                off_t curPos = lseek(fd, 0, SEEK_SET);
#                csAct.init(0);
#                while (curPos < csPos) {  // Read/calculate the csAct from the beginning upto csPos
#                    char buf[1024];
#                    ssize_t ctr = std::min(csPos - curPos, (off_t)sizeof(buf));
#                    ctr = ::read(fd, buf, ctr);
#                    if (ctr > 0) {
#                        csAct.hashStreamIntrn(buf, ctr);
#                        curPos += ctr;
#                    } else if (ctr <= 0 && errno != EINTR) {
#                        retVal = false;
#                        Log::error("Failed to read the %s SB State File '%s'.", FRoleFromFd(fd), FPathFromFd(fd));
#                        break;
#                    }
#                }
#                csAct.hashStreamFinal();  // csAct checksum is finalized and is ready to be compared with the expected value
#                retVal &= (curPos == csPos && memcmp(csAct.getHash(), csExp, sizeof(csExp)) == 0);
#                if (retVal) {
#                    Log::debug("Passed Checksum Validation for the %s SB State File '%s'.",  //
#                               FRoleFromFd(fd), FPathFromFd(fd));                            //
#                } else {
#                    Log::error("Failed Checksum Validation for the %s SB State File '%s'.",  //
#                               FRoleFromFd(fd), FPathFromFd(fd));                            //
#                }
#            } else {
#                retVal = false;
#                Log::info("Checksum Validation is not possible: The %s SB State File '%s' is empty or is not flushed "
#                          "to the media.",
#                          FRoleFromFd(fd), FPathFromFd(fd));
#            }
#            lseek(fd, savePos, SEEK_SET);  // restore the original fpos
#        } else {
#            Log::debug("Checksum is not configured for the %s SB State File '%s'.", FRoleFromFd(fd), FPathFromFd(fd));
#        }
#        return retVal;
        pass
        
    def  _fCloneFdFrom(self, fdTo, fdFrom):
    #        retVal = fdTo and fdFrom and self._fTruncateFd(fdTo)
    #        if retVal:
    #            ssize_t rdBytes = -1;
    #            char buf[1024];
    #            off_t savePos = lseek(fdFrom, 0, SEEK_CUR);  // position must be restored afterwards
    #            fdFrom.seek(0, io.SEEK_SET)
    #            fdTo.seek(0, io.SEEK_SET)
    #            while (retVal && (rdBytes = ::read(fdFrom, buf, sizeof(buf))) > 0) {  // read from fdFrom + write to fdTo
    #                ssize_t wrBytes = ::write(fdTo, buf, rdBytes);
    #                retVal = (wrBytes == rdBytes);
    #                if (!retVal) {
    #                    char eMsg[256];
    #                    posix_strerror_r(errno, eMsg, sizeof(eMsg));
    #                    Log::error("Failed or incomplete Write Operation. Populating the %s SB State File '%s' failed. "
    #                           "Error %d (%s).",                     FRoleFromFd(fdTo), FPathFromFd(fdTo), errno, eMsg);
    #                }
    #            }
    #            if (rdBytes == 0) {
    #                lseek(fdFrom, savePos, SEEK_SET);
    #                lseek(fdTo, savePos, SEEK_SET);
    #            } else if (rdBytes < 0) {
    #                retVal = false;
    #                char eMsg[256];
    #                posix_strerror_r(errno, eMsg, sizeof(eMsg));
    #                Log::error("Failed to copy the %s SB State File to  the '%s' File. Error %d (%s).",  //
    #                       FRoleFromFd(fdFrom), FRoleFromFd(fdTo), errno, eMsg);                     //
    #            }
    #        } else {  // abnormal flow
    #            if (fdTo == -1) {
    #                Log::error("Cloning of the SB State file is not possible: Invalid Destination File Descriptor.");
    #            }
    #            if (fdFrom == -1) {
    #                Log::error("Cloning of the SB State file is not possible: Invalid Source File Descriptor.");
    #            }
    #        }
    #        return retVal;
        pass

class AssignmentStateID:
    FAILED       = -128
    UNAVAILABLE  = -127
    CANCELLED    =   -3
    ONHOLD       =   -2
    DISCONNECTED =   -1
    PREPROCESS   =    0
    ASSIGNING    =    1
    ASSIGNED     =    2
    PROCESSING   =    3
    COMPLETE     =    4
    TRANSFERRING =    5
    TRANSFERRED  =    6
    POSTPROCESS  =    7
    SUCCESS      =    8
    ANY          =  126
    ENDOFLIST    =  127

    @classmethod
    def ToStr(cls, id):
        if cls.__dict__.get("__ToStr_") is None:
            cls.__ToStr__ = { v:k for k,v in cls.__dict__.iteritems()
                                      if k[0:2] != "__" }
        return cls.__ToStr__.get(id)
    




class TableFileStore(PersistencyProvider):

    def __init__(self, path, bkupSuffix=".bak", writable=True, useCheckSum=True):
        super(TableFileStore,self).__init__()
        self._pfAttrs   = PersistencyFile(path + "/sbconfig.kv", bkupSuffix, writable, useCheckSum)
        self._pfAStates = PersistencyFile(path + "/sbconfig.astate", bkupSuffix, writable, useCheckSum)
        self._opLock = threading.RLock()

    def Reset(self):
        retVal = self._pfAttrs.Reset()
        retVal &= self._pfAStates.Reset()
        return retVal

    def Rewind(self):
        retVal = self._pfAttrs.Rewind()
        retVal &= self._pfAStates.Rewind()
        return retVal

    def Load(self, kvData, assignments, states):
        """Return Data to construct the SBState object from the persistent state
        Arguments:
          kvData,      /*out*/ KVMap_t
          assignments, /*out*/ AssignmentIDRec::Vec_t&
          states,      /*out*/ AssignmentStateRec::Vec_t& 
        """
        with self._opLock:
            retVal = self._loadAttrData(kvData)
            retVal &= self._loadAStateData(assignments, states)
        return retVal

    def StoreAttrs(self, kvData):
        """Write the Update of the Attributes' Values into the Persistent SB State Storage
        Arguments:
          kvData, /*in*/ const KVMap_t& 
        """
        with self._opLock:
            retVal = self._pfAttrs.Reset()
#            if retVal:
#                char buf[65536];  // buf is expected to be larger than any single KV-record
#                //~ char buf[15]; // testing the encoder buffer assembly logic
#                char* curPtr = buf;  // encoder cursor
#                size_t sz = 0;
#                KVMap_t::const_iterator it;
#                KVMap_t::const_iterator ei = kvData.end();
#                for (it = kvData.begin(); retVal && it != ei; ++it) {
#                    size_t nextSz = sz + it->first.size() + it->second.size() + 2;
#                    if (nextSz > sizeof(buf)) {
#                        retVal = d_pfAttrs.Append(buf, sz);
#                        nextSz -= sz;
#                        curPtr = buf;
#                        assert(nextSz <= sizeof(buf));  // buf is expected to be larger than any single KV-record
#                     }
#                     memcpy(curPtr, it->first.c_str(), it->first.size());
#                     curPtr += it->first.size();
#                     *(curPtr++) = '=';
#                     memcpy(curPtr, it->second.c_str(), it->second.size());
#                     curPtr += it->second.size();
#                     *(curPtr++) = 0;
#                     sz = nextSz;
#                }
#                if (retVal && sz > 0) {
#                    retVal = d_pfAttrs.Append(buf, sz);
#                }
#            }
        return retVal

    def UpdateState(self, assignments, stateRecords):
        """Write the Update of the Sections States into the Persistent SB State Storage
        Arguments:
          assignments,  /*in*/ const AssignmentIDRec::Vec_t&
          stateRecords, /*in*/ const AssignmentStateRec::Vec_t&
        """
        retVal = True
        with self._opLock:
            buf = ""
            for aid in assignments:
                buf += struct.pack('B', RECAIDTYPE) + aid.encode()
            for sr in stateRecords:
                buf += struct.pack('B', RECSTATTYPE) + sr.encode()

            retVal = self._pfAStates.Append(buf, len(buf))
        return retVal;
        
    def IsWritable(self):
        """Return True if the provider can be modified"""
        with self._opLock:
            retVal = self._pfAttrs.IsWritable()
            retVal &= self._pfAStates.IsWritable()
        return retVal

    def Verify(self):
        """Validate the current state of the provider"""
        with self._opLock:
            retVal = self._pfAttrs.Verify()
            retVal &= self._pfAStates.Verify()
        return retVal

#private:
    def _loadAttrData(self, kvData):
        """  KVMap_t& kvData"""
        retVal = self._pfAttrs.Rewind()
        if not retVal:
            return False

        kvData.clear()
        #~ char buf[14]; // testing the buffer assembly logic; assert(sizeof(buf)...) below must be disabled
        rdSz = 0         # number of bytes loaded from the file
        curPos = 0       # parser's cursor position in the buffer
        key = ""
        val = ""

        eof = False
        while not eof:
            buf = self._pfAttrs.Read(65536)
            rdSz = -1 if buf is None else len(buf)
            curPos = 0
            if retVal and rdSz >= 0:
                recParsed = True
                while recParsed and len(buf) - curPos > 0:
                    recParsed = False;
                    if len(key) == 0:
                        kEndPos = buf.find("=", curPos)
                        recParsed = kEndPos > 0
                        if recParsed:
                            key = buf[curPos:kEndPos]
                            curPos = kEndPos + 1
                    if len(key) > 0:
                        vEndPos = buf.find('\0', curPos)
                        recParsed |= vEndPos > 0
                        if vEndPos > 0:
                            val = buf[curPos:vEndPos]
                            curPos = vEndPos + 1
                            kvData[key] = val
                            key = ""
                            val = ""
                        else:
                            val = buf[curPos:]
                            curPos = len(buf)
                            kvData[key] = val
                            key = ""
                            val = ""

            eof = not rdSz > 0 and retVal

        retVal &= rdSz == 0
        return retVal

    def _loadAStateData(self, assignments, states):
        """
        Arguments:
          /*out*/ AssignmentIDRec::Vec_t& assignments,
          /*out*/ AssignmentStateRec::Vec_t& states
        """
        if not self._pfAStates.Rewind():
            return False
        
        del assignments[:] # clear()
        del states[:]      # clear()
        curPos = 0  # parser's cursor position in the buffer
  
        retVal = True
        buf = ""
        eof = False
        while not eof:
            chunk = self._pfAStates.Read(65536)
            if not chunk:
                eof = True
                continue
            else:
                buf = buf[curPos:] + chunk

            curPos = 0
            recParsed = True
            needMore  = False
            while buf and recParsed and not needMore:
                (recType,) = struct.unpack("=B", buf[curPos:curPos+1])
                if recType == RECAIDTYPE:
                    if len(buf)-curPos >= RECAIDLEN:
                        recParsed = self._decodeAIDRec(buf[curPos+1:curPos+RECAIDLEN], assignments)
                        curPos += RECAIDLEN
                    else:
                        needMore = True
                elif recType == RECSTATTYPE:
                    if len(buf)-curPos >= RECSTATLEN:
                        recParsed = self._decodeStateRec(buf[curPos+1:curPos+RECSTATLEN], states)
                        curPos += RECSTATLEN
                    else:
                        needMore = True
                elif len(buf)-curPos == 16:
                    curPos += 16
                    recParsed = False
                elif not eof:
                    retVal = False
                    LOG("ERROR: SB Assignment ID/State Table cannot be parsed: Invalid record type detected %s." % recType)
                        
        retVal &= not buf
        return retVal

    
    def _decodeAIDRec(self, buf, assignments):
        """
        Arguments:
          /*in*/ buf
          /*out*/ AssignmentIDRec::Vec_t& assignments
        """
        if len(buf) != RECAIDLEN-1:
            return False
        aId = AssignmentIDRec()
        fields = struct.unpack(RECAIDSTRUCT, buf)
        aId._phase    = fields[0]
        aId._col      = fields[1]
        aId._row      = fields[2]
        aId._assignId = fields[3]
        aId._SJM      = uuid.UUID(bytes=fields[4])
        aId._DC       = uuid.UUID(bytes=fields[5])
        assignments.append(aId)
        return True

    def _decodeStateRec(self, buf, states):
        """
        Arguments:
          /*in*/  buf
          /*out*/ AssignmentStateRec::Vec_t& states);
        """
        if len(buf) != RECSTATLEN-1:
            return False
        sR = AssignmentStateRec()
        fields = struct.unpack(RECSTATSTRUCT, buf)
        sR._phase     = fields[0]
        sR._col       = fields[1]
        sR._row       = fields[2]
        sR._assignId  = fields[3]
        sR._stateId   = fields[4]
        sR._tv_sec    = fields[5]
        sR._tv_nsec   = fields[6]
        states.append(sR)
        return True

#    bool EncodeAIDRec(/*inout*/ char*& dPtr, /*in*/ const char* dEnd, /*in*/ const AssignmentIDRec& assignment);
#    bool EncodeStateRec(/*inout*/ char*& dPtr, /*in*/ const char* dEnd, /*in*/ const AssignmentStateRec& state);
#    const char* strnchr(const char* haystack, const char needle, ssize_t haystackSz);


#bool TableFileStore::StoreAttrs(/*in*/ const KVMap_t& kvData)
#{
#    Locker sync(d_opLock);
#    bool retVal = d_pfAttrs.Reset();
#    if (retVal) {
#        char buf[65536];  // buf is expected to be larger than any single KV-record
#        //~ char buf[15]; // testing the encoder buffer assembly logic
#        char* curPtr = buf;  // encoder cursor
#        size_t sz = 0;
#        KVMap_t::const_iterator it;
#        KVMap_t::const_iterator ei = kvData.end();
#        for (it = kvData.begin(); retVal && it != ei; ++it) {
#            size_t nextSz = sz + it->first.size() + it->second.size() + 2;
#            if (nextSz > sizeof(buf)) {
#                retVal = d_pfAttrs.Append(buf, sz);
#                nextSz -= sz;
#                curPtr = buf;
#                assert(nextSz <= sizeof(buf));  // buf is expected to be larger than any single KV-record
#            }
#            memcpy(curPtr, it->first.c_str(), it->first.size());
#            curPtr += it->first.size();
#            *(curPtr++) = '=';
#            memcpy(curPtr, it->second.c_str(), it->second.size());
#            curPtr += it->second.size();
#            *(curPtr++) = 0;
#            sz = nextSz;
#        }
#        if (retVal && sz > 0) {
#            retVal = d_pfAttrs.Append(buf, sz);
#        }
#    }
#    return retVal;
#}
#

    def IsWritable(self):
        with self._opLock:
            retVal = self._pfAttrs.IsWritable()
            retVal &= self._pfAStates.IsWritable()
        return retVal

    def Verify(self):
        with self._opLock:
            retVal = self._pfAttrs.Verify()
            retVal &= self._pfAStates.Verify()
        return retVal

#    def EncodeAIDRec(/*inout*/ char*& dPtr, /*in*/ const char* dEnd,
#                                  /*in*/ const AssignmentIDRec& assignment)
#{
#    bool retVal = ((dEnd - dPtr) >= RECAIDLEN);
#    if (retVal) {
#        EncVarIntoBuffer_(dPtr, static_cast<char>(RECAIDTYPE));
#        EncVarIntoBuffer_(dPtr, assignment.d_phase);
#        EncVarIntoBuffer_(dPtr, assignment.d_col);
#        EncVarIntoBuffer_(dPtr, assignment.d_row);
#        EncVarIntoBuffer_(dPtr, assignment.d_assignId);
#        memcpy(dPtr, assignment.d_SJM.bytes(), sizeof(uuid_t));
#        dPtr += sizeof(uuid_t);
#        memcpy(dPtr, assignment.d_DC.bytes(), sizeof(uuid_t));
#        dPtr += sizeof(uuid_t);
#    }
#    return retVal;
#}

#bool TableFileStore::EncodeStateRec(/*inout*/ char*& dPtr, /*in*/ const char* dEnd,
#                                    /*in*/ const AssignmentStateRec& state)
#{
#    bool retVal = ((dEnd - dPtr) >= RECSTATLEN);
#    if (retVal) {
#        EncVarIntoBuffer_(dPtr, static_cast<char>(RECSTATTYPE));
#        EncVarIntoBuffer_(dPtr, state.d_phase);
#        EncVarIntoBuffer_(dPtr, state.d_col);
#        EncVarIntoBuffer_(dPtr, state.d_row);
#        EncVarIntoBuffer_(dPtr, state.d_assignId);
#        EncVarIntoBuffer_(dPtr, state.d_stateId);
#        EncVarIntoBuffer_(dPtr, state.d_stateTm.tv_sec);
#        EncVarIntoBuffer_(dPtr, state.d_stateTm.tv_nsec);
#    }
#    return retVal;
#}




if __name__ == "__main__":
    tfs = TableFileStore(sys.argv[1], bkupSuffix=".bak", writable=False, useCheckSum=False)
    print "TFS: ", tfs

    kvData = {}
    assignments = []
    states = []
    tfs.Load(kvData, assignments, states)
    for key, val in kvData.iteritems():
        print "%s = %s" % (key,val)

    secRows = int(kvData.get('SECTION_ROWS', -1))
    secCols = int(kvData.get('SECTION_COLS', -1))

    
    print "AIDS(%s):" % len(assignments)
    for aid in assignments:
        print aid
        
    print "STATES(%s):" % len(states)
    curStates = { }
    stateGrid = ["**"] * (secCols * secRows)
    for sr in states:
        print sr
        key = "%02d:%02d:(%02d,%02d)" % (sr._assignId, sr._phase, sr._col, sr._row)
        curStateName = AssignmentStateID.ToStr(sr._stateId)
        curStates[key] = curStateName
        gridIndex = sr._row * secCols + sr._col
        gridIcon = stateGrid[gridIndex]
        if sr._phase == 0:
            gridIcon = curStateName[0:1] + gridIcon[1:2]
        else:
            gridIcon = gridIcon[0:1] + curStateName[0:1]
        stateGrid[gridIndex] = gridIcon
            
    print "CURRENT STATES:"
    print curStates
    print stateGrid

    print "GRID %dx%d" % (secRows, secCols)
    gridLine = "     "
    for col in range(secCols):
        gridLine += " %02d  " % col
    print gridLine
    gridHSep ="    +" + "----+" * secCols
    print gridHSep
    for row in range(secRows):
        gridRow = " %02d |" % row
        for col in range(secCols):
            gridIndex = row * secCols + col
            gridRow += " %s |" % stateGrid[gridIndex]
        print gridRow
        print gridHSep

    input = raw_input("FOO:")
    tfs.Rewind()
    kvData = {}
    assignments = []
    states = []
    tfs.Load(kvData, assignments, states)
    for key, val in kvData.iteritems():
        print "%s = %s" % (key,val)

    if len(sys.argv) >= 3:
        buf = ""
        for aid in assignments:
            rec = struct.pack('B', RECAIDTYPE) + aid.encode()
            print "AIDENCODE: %s %r" % (len(rec), rec)
            buf += struct.pack('B', RECAIDTYPE) + aid.encode()
        for x, sr in enumerate(states):
            rec = struct.pack('B', RECSTATTYPE) + sr.encode() 
            print "SRENCODE(%s): %s %r" % (x, len(rec), rec)
            buf += struct.pack('B', RECSTATTYPE) + sr.encode()
        print "LEN(BUF) = %s" % len(buf)
        hash = MurmurHash3F()
        hash.init()
        hash.update(buf)
        hash.finish()

        dstPath = sys.argv[2]
        dstFP = open(dstPath, "wb")
        dstFP.write(buf)
        print "HASH" , repr(hash.hash())
        dstFP.write(hash.hashbytes())
        dstFP.close()
