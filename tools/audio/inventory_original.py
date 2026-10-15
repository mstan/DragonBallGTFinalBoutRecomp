"""Inventory verified Final Bout sample slots without captured RAM or media output."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
from probe_sources import TARGET_SHA1, require, sha, target_inventory

BOOT_SHA256 = "507f132cdcbb635bbbf7a75e15c62a9d0d51e22ce4432828da784ec03b67cbcc"
STEP1_SHA256 = "a65555d55ed6a9bb10111469b3d9a2d1e08906e1c8c6b895185f50c7c69a969c"
STEP40_SHA256 = "001adcdc2e129d3bd715c29b64e393fa8c2901a7ef39c2347874b321aae6b9dd"
NAMES = ["Goku", "Pan", "Little Goku", "Trunks", "Super Vegeta",
         "Super Saiyan Goku", "Gohan", "Cell", "Majin Boo", "Frieza",
         "Piccolo", "Super Goku", "Super Saiyan Trunks", "Super Vegetto",
         "Super Saiyan 4 Goku", "Super Little Goku", "Super Trunks", "Super Baby"]

def sample_info(data):
    require(data and len(data)%16==0,"Unaligned sample")
    require(all(data[i]>>4<=4 and data[i]&15<=12 and data[i+1]<=7
                for i in range(0,len(data),16)),"Invalid ADPCM frame")
    terminal=next((i for i in range(0,len(data),16) if data[i+1]&1),None)
    require(terminal is not None,"Sample has no terminal frame")
    flag=data[terminal+1]
    return dict(size=len(data),sha256=sha(data),first_terminal=terminal,
                first_terminal_flag=flag,loops=bool(flag&2),
                first_pass_samples=(terminal//16+1)*28,
                flags=dict(Counter(data[1::16])))

def inventory(path):
    original,_=target_inventory(path)
    raw=path.read_bytes()
    require(hashlib.sha1(raw).hexdigest()==TARGET_SHA1,"Source changed during inventory")
    files={r['path']:r for r in original['files']}
    def read(name):
        entry=files['/'+name+';1'];start=entry['lba'];size=entry['size']
        return b''.join(raw[i*2352+24:i*2352+2072]
                        for i in range(start,start+(size+2047)//2048))[:size]
    boot=read('SLUS_004.93');step1=read('MENU/STEP01.BIN');step40=read('MENU/STEP40.BIN')
    require(sha(boot)==BOOT_SHA256 and sha(step1)==STEP1_SHA256 and sha(step40)==STEP40_SHA256,
            "Unsupported executable/overlay tables")
    text=boot[2048:];base=struct.unpack_from('<I',boot,24)[0]
    def pitch(note):
        fine=((0x3c00&255)+(note&255))//8
        semitone=60+60-(note>>8)+fine//16
        index=semitone%12*16+fine%16
        value=struct.unpack_from('<H',text,0x8002c66c-base+index*2)[0]
        octave=semitone//12-5
        return value<<octave if octave>=0 else value>>-octave
    overlay_base=0x8003dfa0
    def table(data,addr,count):return struct.unpack_from('<'+'I'*count,data,addr-overlay_base)
    charsel=read('TITLE/CHARSEL.BIN');combat=read('TITLE/BTCHARA.DAT');victory=read('BATTLE/BTWINV.DAT')
    banks=[];menu=[];wins=[]
    for char in range(18):
        bounds=table(step1,0x80053bec+char*15*4,16)
        require(all(a<=b for a,b in zip(bounds,bounds[1:])) and bounds[-1]*2048<=len(combat),"Combat resource bounds")
        body=bounds[5]*2048;header=bounds[10]*2048+0x200
        require(combat[header:header+4]==b'SNTp',"Missing sample bank header")
        length,count=struct.unpack_from('<IH',combat,header+4);waves=combat[header+10]
        require(body+length<=bounds[6]*2048 and count<=32 and waves<=32,"Invalid sample bank bounds")
        starts=[v*8 for v in struct.unpack_from('<'+'H'*waves,combat,header+16+count*16)]+[length]
        require(starts[0]==0 and all(a<b for a,b in zip(starts,starts[1:])),'Sample table order')
        instruments=[]
        for i in range(count):
            at=header+16+i*16;wave=combat[at+1];note=struct.unpack_from('<H',combat,at+4)[0]
            require(wave<waves,'Instrument references absent sample')
            instruments.append(dict(index=i,wave=wave,base_note=note,spu_pitch=pitch(note)))
        records=[]
        for i,(start,end) in enumerate(zip(starts,starts[1:])):
            records.append(dict(id=f'btchara/c{char:02}/wave{i:02}',offset=body+start,
                                **sample_info(combat[body+start:body+end])))
        banks.append(dict(character_id=char,name=NAMES[char],body_offset=body,
                          header_offset=header,body_size=length,instruments=instruments,waves=records))
        for variant in range(8):
            index=char*12+4+variant
            if index+1>=213:continue
            start,end=table(step1,0x80053888+index*4,2)
            if start==end:continue
            require(0<=start<end<=len(charsel)//2048,'Menu voice extent')
            data=charsel[start*2048:end*2048]
            last=next((p+32 for p in range(0,len(data)-16,16)
                       if data[p+1]==1 and data[p+17]==7),None)
            if last is None:continue
            try:info=sample_info(data[:last])
            except ValueError:continue
            require(not any(data[last:]),'Unexpected menu allocation tail')
            menu.append(dict(id=f'charsel/c{char:02}/variant{variant}',character_id=char,
                             variant=variant,offset=start*2048,allocation=(end-start)*2048,spu_pitch=1485,**info))
    bounds=table(step40,0x80071798,55)
    require(bounds[0]==0 and bounds[-1]*2048==len(victory),'Victory table extent')
    for i,(start,end) in enumerate(zip(bounds,bounds[1:])):
        data=victory[start*2048:end*2048]
        last=next((p+32 for p in range(0,len(data)-16,16) if data[p+1]==1 and data[p+17]==7),None)
        require(last is not None and not any(data[last:]),'Victory terminal/tail')
        wins.append(dict(id=f'btwinv/c{i//3:02}/condition{i%3}',character_id=i//3,
                         condition=i%3,offset=start*2048,allocation=len(data),spu_pitch=2048,
                         **sample_info(data[:last])))
    require(sum(len(b['waves']) for b in banks)==227 and len(menu)==110 and len(wins)==54,'Unexpected cue inventory')
    identities={name:dict(lba=files['/'+name+';1']['lba'],size=len(data),sha256=sha(data))
                for name,data in [('TITLE/BTCHARA.DAT',combat),('TITLE/CHARSEL.BIN',charsel),('BATTLE/BTWINV.DAT',victory)]}
    return dict(schema=1,disc_sha256=sha(raw),boot_sha256=BOOT_SHA256,files=identities,
                banks=banks,menu=menu,victory=wins,xa=original['xa_streams'],
                classification='Names read from original portrait/name TIM resources; event semantics require separate evidence')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target-bin',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=inventory(args.target_bin)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f"18 combat banks, 227 samples, {len(result['menu'])} menu, {len(result['victory'])} victory slots")
