from audit import *
class StandardInfo(ctypes.Structure):
    _fields_=[('allocation',ctypes.c_longlong),('eof',ctypes.c_longlong),('links',ctypes.c_ulong),('deletePending',ctypes.c_ubyte),('directory',ctypes.c_ubyte)]
k=ctypes.windll.kernel32
k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p];k.CreateFileW.restype=ctypes.c_void_p
k.GetFileInformationByHandleEx.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_ulong];k.CloseHandle.argtypes=[ctypes.c_void_p]
groups=collections.defaultdict(lambda:{'files':0,'logicalBytes':0,'allocatedBytes':0});identities={};errors=[];reparse=[]
for base,dirs,names in os.walk(ROOT):
    for d in list(dirs):
        p=Path(base)/d
        if getattr(p.stat(),'st_file_attributes',0)&1024:reparse.append(p.relative_to(ROOT).as_posix());dirs.remove(d)
    for name in names:
        p=Path(base)/name;n=p.relative_to(ROOT).as_posix();s=p.stat();h=k.CreateFileW(str(p),128,7,None,3,0,None)
        if h==ctypes.c_void_p(-1).value:errors.append(n);continue
        info=StandardInfo();ok=k.GetFileInformationByHandleEx(h,1,ctypes.byref(info),ctypes.sizeof(info));k.CloseHandle(h)
        if not ok:errors.append(n);continue
        g=groups[n.split('/')[0]];g['files']+=1;g['logicalBytes']+=s.st_size
        key=(s.st_dev,s.st_ino)
        if key not in identities:g['allocatedBytes']+=info.allocation;identities[key]=n
write('storage-final.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Windows FILE_STANDARD_INFO AllocationSize, unique st_dev/st_ino, excludes NTFS directory metadata/ADS/snapshots','groups':dict(groups),'logicalBytes':sum(g['logicalBytes'] for g in groups.values()),'allocatedBytes':sum(g['allocatedBytes'] for g in groups.values()),'errors':errors,'reparsePoints':reparse,'note':'Includes existing assets.zip, new local transfer ZIP and isolated static verification copy; these are deliberately excluded from Git.'})
print('logical',sum(g['logicalBytes'] for g in groups.values()),'allocated',sum(g['allocatedBytes'] for g in groups.values()),'errors',len(errors),flush=True)
