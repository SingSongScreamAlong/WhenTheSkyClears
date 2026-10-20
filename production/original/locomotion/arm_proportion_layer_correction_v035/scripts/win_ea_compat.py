"""Task-scoped Windows implementation of missing Python xattr calls.

Real NTFS extended attributes via the native Windows EA interfaces; no sidecar
substitution and no changes to the official Library transfer helper. All paths
are restricted to this task directory. Missing metadata/errors remain errors.
"""
import os,sys,ctypes,struct,errno
from pathlib import Path
from ctypes import wintypes as w
ROOT=Path(__file__).resolve().parents[1]
if sys.platform!='win32':raise RuntimeError('Windows adapter used outside Windows')
class IOSB(ctypes.Structure):
 _fields_=[('StatusOrPointer',ctypes.c_void_p),('Information',ctypes.c_size_t)]
k=ctypes.WinDLL('kernel32',use_last_error=True);n=ctypes.WinDLL('ntdll')
k.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,ctypes.c_void_p,w.DWORD,w.DWORD,w.HANDLE];k.CreateFileW.restype=w.HANDLE
k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle.restype=w.BOOL
n.NtSetEaFile.argtypes=[w.HANDLE,ctypes.POINTER(IOSB),ctypes.c_void_p,w.ULONG];n.NtSetEaFile.restype=ctypes.c_long
n.NtQueryEaFile.argtypes=[w.HANDLE,ctypes.POINTER(IOSB),ctypes.c_void_p,w.ULONG,ctypes.c_ubyte,ctypes.c_void_p,w.ULONG,ctypes.c_void_p,ctypes.c_ubyte];n.NtQueryEaFile.restype=ctypes.c_long
n.RtlNtStatusToDosError.argtypes=[ctypes.c_long];n.RtlNtStatusToDosError.restype=w.ULONG
def path_checked(path,follow_symlinks=True):
 if not follow_symlinks:raise NotImplementedError('No symlink metadata operation in this adapter')
 p=Path(os.fsdecode(path)).resolve(strict=True)
 if not p.is_relative_to(ROOT):raise PermissionError('EA operation outside task scope')
 return p
def ea_name(name):
 b=name if isinstance(name,bytes) else str(name).encode('ascii')
 if not b or len(b)>=255 or any(x<32 or x in b'\\/:*?"<>|,+=[];' for x in b):raise ValueError('Invalid Windows EA name')
 return b
def handle(path,write=False):
 h=k.CreateFileW(str(path),0x0008|(0x0010 if write else 0),0x7,None,3,0x02000000,None)
 if h==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
 return h
def check(status,path):
 if status<0:
  code=n.RtlNtStatusToDosError(status)
  if (status&0xffffffff) in [0xc0000051,0xc0000052]:raise OSError(getattr(errno,'ENODATA',61),'Extended attribute not found',str(path))
  raise OSError(code,ctypes.FormatError(code),str(path))
def getxattr(path,attribute,*,follow_symlinks=True):
 p=path_checked(path,follow_symlinks);name=ea_name(attribute);query=struct.pack('<IB',0,len(name))+name+b'\0';qb=ctypes.create_string_buffer(query);out=ctypes.create_string_buffer(65536);ios=IOSB();h=handle(p)
 try:check(n.NtQueryEaFile(h,ctypes.byref(ios),out,len(out),1,qb,len(query),None,1),p)
 finally:k.CloseHandle(h)
 raw=out.raw[:ios.Information]
 if len(raw)<8:raise OSError(getattr(errno,'ENODATA',61),'Extended attribute not found',str(p))
 _,_,nl,vl=struct.unpack_from('<IBBH',raw)
 if raw[8:8+nl].upper()!=name.upper() or vl==0:raise OSError(getattr(errno,'ENODATA',61),'Extended attribute not found',str(p))
 result=raw[9+nl:9+nl+vl]
 if len(result)!=vl:raise RuntimeError('Truncated EA response')
 return result
def setxattr(path,attribute,value,flags=0,*,follow_symlinks=True):
 p=path_checked(path,follow_symlinks);name=ea_name(attribute);data=bytes(value)
 if not data or len(data)>65535:raise ValueError('Library metadata must be1..65535bytes')
 if flags not in [0,1,2]:raise ValueError('Unknown xattr flags')
 if flags:
  try:getxattr(p,name);exists=True
  except OSError as e:
   if e.errno!=getattr(errno,'ENODATA',61):raise
   exists=False
  if flags==1 and exists:raise FileExistsError(errno.EEXIST,'EA already exists',str(p))
  if flags==2 and not exists:raise OSError(getattr(errno,'ENODATA',61),'EA does not exist',str(p))
 data_bytes=struct.pack('<IBBH',0,0,len(name),len(data))+name+b'\0'+data;buf=ctypes.create_string_buffer(data_bytes);ios=IOSB();h=handle(p,write=True)
 try:check(n.NtSetEaFile(h,ctypes.byref(ios),buf,len(data_bytes)),p)
 finally:k.CloseHandle(h)
 if getxattr(p,name)!=data:raise RuntimeError('Windows EA readback did not match')
def install():
 if hasattr(os,'setxattr') or hasattr(os,'getxattr'):raise RuntimeError('Native Python xattr methods already exist; do not override')
 os.setxattr=setxattr;os.getxattr=getxattr
