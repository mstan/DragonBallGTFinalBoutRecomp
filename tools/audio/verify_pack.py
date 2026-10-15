"""Check a prepared pack against every declared original extent, without playback."""
from __future__ import annotations
import argparse
import array
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
from curate_recipe import spu
from probe_sources import require, sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('recipe','target-bin','pack','codec-check','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    require(args.out.suffix.lower()=='.json','Verification output must be JSON')
    require(all(args.out.resolve()!=p.resolve() for p in (args.recipe,args.target_bin,args.pack,args.codec_check)),
            'Verification output must not replace an input')
    recipe=tomllib.loads(args.recipe.read_text(encoding='utf-8'))
    raw=args.target_bin.read_bytes();pack=args.pack.read_bytes()
    require(sha(raw)==recipe['target_disc_sha256'],'Changed target image')
    original=bytearray();starts={}
    for file in recipe['file']:
        starts[file['id']]=len(original)
        if file.get('layout')=='disc_raw':data=raw[file['lba']*2352:file['lba']*2352+file['size']]
        else:data=b''.join(raw[lba*2352+24:lba*2352+2072] for lba in range(file['lba'],file['lba']+(file['size']+2047)//2048))[:file['size']]
        require(sha(data)==file['sha256'],'Changed original resource');original.extend(data)
    require(len(original)==len(pack),'Prepared pack has wrong size')
    expected=bytearray(original);rows=[]
    with tempfile.TemporaryDirectory(prefix='finalbout-pack-verify-') as temporary:
        path=Path(temporary)
        for cue in recipe['cue']:
            start=starts[cue['target_file']]
            if cue.get('target_kind')!='xa_mono':
                at=start+cue['target_offset'];end=at+cue['target_size'];stock=original[at:end];data=pack[at:end]
                require(sha(stock)==cue['target_sha256'],'Changed original cue')
                require(stock!=data and stock[1::16]==data[1::16],'Unchanged cue or changed SPU flags')
                pcm=spu(data)[:cue['target_samples']];expected[at:end]=data
            else:
                file=next(f for f in recipe['file'] if f['id']==cue['target_file'])
                stock_parts=[];parts=[]
                for local in range(0,file['size'],2352):
                    at=start+local;a=original[at:at+2352];b=pack[at:at+2352]
                    if a[15]!=2 or not a[18]&4 or a[16]!=cue['target_xa_file'] or a[17]!=cue['target_channel']:continue
                    require(a[:24]==b[:24] and a[2328:2348]==b[2328:2348],'XA controls or reserved tail changed')
                    if a[2348:]==b'\0'*4:require(b[2348:]==b'\0'*4,'Absent XA EDC changed')
                    else:
                        edc=0
                        for value in b[16:2348]:
                            edc^=value
                            for _ in range(8):edc=(edc>>1)^(0xD8018001 if edc&1 else 0)
                        require(b[2348:]==edc.to_bytes(4,'little'),'Invalid replacement XA EDC')
                    stock_parts.append(a);parts.append(b);expected[at:at+2352]=b
                stock=b''.join(stock_parts);data=b''.join(parts)
                require(len(parts)==cue['target_sector_count'] and sha(stock)==cue['target_sha256'] and stock!=data,
                        'XA channel unchanged or identity mismatch')
                (path/'channel.raw').write_bytes(data)
                subprocess.run([str(args.codec_check),'xa',str(path/'channel.raw'),str(path/'channel.pcm')],check=True,capture_output=True)
                decoded=array.array('h');decoded.frombytes((path/'channel.pcm').read_bytes())
                if sys.byteorder!='little':decoded.byteswap()
                end=cue['target_replace_end_sample']
                require(not any(decoded[end+4032:]),'XA zero tail contains sustained replacement audio')
                pcm=decoded[cue['target_replace_first_sample']:end]
            require(any(pcm),'Silent replacement cue')
            row=dict(id=cue['id'],peak=max(abs(n) for n in pcm),rails=sum(n in (-32768,32767) for n in pcm),encoded_sha256=sha(data))
            require(row['rails']==0,'Replacement clips at PCM rail: '+cue['id']);rows.append(row)
    require(expected==pack,'Bytes outside declared replacement extents changed')
    report=dict(cues=len(rows),gaps=len(recipe.get('gap',[])),files=len(recipe['file']),bytes=len(pack),pack_sha256=sha(pack),
                recipe_sha256=sha(args.recipe.read_bytes()),unmapped_bytes_unchanged=True,spu_flags_unchanged=True,
                xa_controls_reserved_and_edc_preserved=True,max_peak=max(r['peak'] for r in rows),rails=sum(r['rails'] for r in rows),rows=rows)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}))


if __name__=='__main__':main()
