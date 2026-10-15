"""Extend the curated SPU recipe with tournament and streamed attack voices.

Development-only curation. Uses supplied images and an explicit metadata mapping;
no speech recognition, audio download or runtime matching is involved. Output
contains source coordinates, hashes and edits, never audio or transcripts.
"""
from __future__ import annotations
import argparse
import array
import copy
import json
import math
from pathlib import Path
import struct
import subprocess
import tomllib
from curate_recipe import DONORS, FORM_NOTES, adx, spu, trimmed
from probe_sources import ARCHIVES, PVD_SHA256, adx_info, require, sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('base-recipe','original-inventory','donor-inventory','xa-inventory','mappings','target-bin','donor-iso','codec-check','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    recipe=tomllib.loads(args.base_recipe.read_text(encoding='utf-8'))
    for file in recipe['file']:file.setdefault('layout','disc_user')
    original=json.loads(args.original_inventory.read_text(encoding='utf-8'))
    donor=json.loads(args.donor_inventory.read_text(encoding='utf-8'))
    xa=json.loads(args.xa_inventory.read_text(encoding='utf-8'))
    mappings=json.loads(args.mappings.read_text(encoding='utf-8'))
    raw=args.target_bin.read_bytes();require(sha(raw)==original['disc_sha256'],'Changed original disc')
    require(args.donor_iso.stat().st_size==3020816384,'Unsupported donor size')
    recipe['format_version']=2
    banks={b['index']:b for b in donor['banks']}
    image=args.donor_iso.open('rb');tables={};entry_cache={};source_cache={}
    def read(at,size):
        image.seek(at);data=image.read(size);require(len(data)==size,'Short donor read');return data
    require(sha(read(16*2048,2048))==PVD_SHA256,'Unsupported donor PVD')
    for index,(name,(lba,size,count,digest,_)) in enumerate(ARCHIVES.items(),1):
        table=read(lba*2048,8+count*8+8);require(sha(table)==digest,'Unsupported donor archive')
        tables[index]=(lba*2048,list(struct.iter_unpack('<II',table[8:-8])))
    def entry(archive,index):
        key=archive,index
        if key not in entry_cache:
            base,table=tables[archive];offset,size=table[index];entry_cache[key]=read(base+offset,size)
        return entry_cache[key]
    def source(selector):
        bank=selector['bank'];kind=selector['codec'];slot=selector['slot'];key=kind,bank,slot
        if key not in source_cache:
            if kind=='adx':
                index=48874+(bank-3194)*100+slot;data=entry(2,index);info=adx_info(data);pcm=adx(data)
                metadata=dict(archive=2,entry=index,entry_sha256=sha(data),source_codec=kind,source_rate=info['sample_rate'],source_line=slot,
                              source_label=f'English character {bank-3194}, line {slot}')
            else:
                require(kind=='spu','Unknown donor codec');info=banks[bank];wave=info['waves'][slot];data=entry(1,bank)
                require(sha(data)==info['pak_sha256'],'Changed donor PAK')
                offset=info['members'][0][0]+wave['offset'];encoded=data[offset:offset+wave['size']]
                require(sha(encoded)==wave['adpcm_sha256'],'Changed donor short sample')
                pcm=spu(encoded)[:wave['first_end_decoded_samples']]
                metadata=dict(archive=1,entry=bank,entry_sha256=info['pak_sha256'],source_codec=kind,source_rate=wave['sample_rate'],
                              source_offset=offset,source_size=wave['size'],source_sha256=sha(encoded),source_wave=slot,source_label=info['label'])
            source_cache[key]=metadata,pcm,trimmed(pcm,metadata['source_rate'])
        return source_cache[key]
    files={f['id']:f for f in recipe['file']};file_data={}
    def add_file(name,info,layout='disc_user'):
        row=dict(id=name,**info,layout=layout)
        if layout=='disc_raw':data=raw[row['lba']*2352:row['lba']*2352+row['size']]
        else:data=b''.join(raw[lba*2352+24:lba*2352+2072] for lba in range(row['lba'],row['lba']+(row['size']+2047)//2048))[:row['size']]
        require(sha(data)==row['sha256'],'Changed original resource')
        if name not in files:recipe['file'].append(row);files[name]=row
        file_data[name]=data
    for name,info in original['files'].items():add_file(name,info)
    raw_files={}
    for stream in xa['streams']:
        name=stream['file'].lstrip('/').split(';')[0]
        if name in raw_files:continue
        # The original ISO directory reports logical 2048-byte allocation units;
        # retain every physical sector, including interleaved filler channels.
        require(name in mappings['raw_files'],'Unknown streamed resource')
        info=mappings['raw_files'][name];start=info['lba']*2352;size=info['size']
        info=dict(info,sha256=sha(raw[start:start+size]));add_file(name,info,'disc_raw');raw_files[name]=info
    def append(target,selectors,note):
        capacity=target['target_samples'];rate=target['target_rate_numerator'];den=target['target_rate_denominator']
        candidates=[]
        for selector in selectors:
            metadata,pcm,bounds=source(selector)
            if bounds is None:continue
            first,end=bounds;divisor=metadata['source_rate']*den
            needed=((end-first)*rate+divisor-1)//divisor
            if needed<=capacity:candidates.append((capacity-needed,metadata,pcm,first,end,selector.get('note',note)))
        if not candidates:
            recipe.setdefault('gap',[]).append(dict(id=target['id'],reason='No intact selected donor fits original active playback window'))
            return
        _,metadata,pcm,first,end,note=min(candidates,key=lambda row:row[0])
        samples=pcm[first:end];peak=max(abs(n) for n in samples)
        rms=math.sqrt(sum(n*n for n in samples)/len(samples))
        # Conservative fixed target RMS; peak cap prevents gain clipping.
        gain=min(1.5,max(.5,5500/max(1,rms)),26000/max(1,peak))
        target.update(metadata,first_sample=first,end_sample=end,gain_q16=round(gain*65536),fade_ms=5,excerpt=False,
                      semantic_fit='generic-context substitution',source_form_note=note,
                      edit_policy='intact performance; silence trim only; no time stretch',
                      transcript_status='words not shipped; donor context and source coordinates recorded',
                      review_status='candidate for short owner audition')
        if metadata['source_codec']=='spu' and 16<=metadata['source_wave']<=25:
            wave=metadata['source_wave']
            target['source_native_event_category']='attack-record-voice-'+str(1 if wave<19 else 2 if wave<22 else 3)
            target['source_context_note']='Complete physical attack recording reused for '+target['category']+'; words and emotional delivery not independently accepted'
        recipe['cue'].append(target)
    names={b['character_id']:b['name'] for b in original['banks']}
    for sample in original['tournament']:
        if not sample['replacement_candidate']:continue
        char=sample['character_id'];bank=DONORS[char]
        selectors=[dict(codec='adx',bank=bank,slot=n) for n in (3,4)]
        if char==15:selectors+=[dict(codec='adx',bank=3201,slot=n) for n in (3,4)]
        if char==8:selectors=[dict(codec='spu',bank=bank,slot=n) for n in (16,17,18,21,22,23,24,25)]
        # Already curated intact victory alternatives retain their precise
        # form/context notes; never silently label an alternate as matching.
        for existing in recipe['cue']:
            if not existing['id'].startswith(f'btwinv/c{char:02}/'):continue
            if existing['source_codec']=='spu':
                selector=dict(codec='spu',bank=existing['entry'],slot=existing['source_wave'])
            else:
                ordinal=existing['entry']-48874
                selector=dict(codec='adx',bank=3194+ordinal//100,slot=ordinal%100)
            selector['note']=existing['source_form_note']+'; generic tournament victory substitution'
            selectors.append(selector)
        append(dict(id=sample['id'],target_file='TITLE/TENKAWIN.BIN',target_character=names[char],category='tournament-victory',
                    target_offset=sample['offset'],target_size=sample['size'],target_sha256=sample['sha256'],
                    target_samples=sample['first_pass_samples'],target_spu_pitch=sample['spu_pitch'],
                    target_rate_numerator=44100*sample['spu_pitch'],target_rate_denominator=4096),
               selectors,FORM_NOTES.get(char,'Matching donor character/form')+'; generic tournament victory context')
    for mapping in mappings['extra_spu']:
        char=mapping['character_id'];bank=original['banks'][char];sample=bank['waves'][mapping['wave']]
        instrument=next(i for i in bank['instruments'] if i['index']==mapping['instrument'])
        require(instrument['wave']==mapping['wave'] and not sample['loops'],'Changed extra attack caller')
        append(dict(id=sample['id'],target_file='TITLE/BTCHARA.DAT',target_character=names[char],category='named-attack',
                    target_offset=sample['offset'],target_size=sample['size'],target_sha256=sample['sha256'],
                    target_samples=sample['first_pass_samples'],target_spu_pitch=instrument['spu_pitch'],
                    target_rate_numerator=44100*instrument['spu_pitch'],target_rate_denominator=4096),
               mapping['sources'],mapping['note'])
    work=args.out.parent/'xa-curation';work.mkdir(parents=True,exist_ok=True)
    selected={(m['file'],m['channel']) for m in mappings['xa']}
    expected={(s['file'].lstrip('/').split(';')[0],s['channel']) for s in xa['streams'] if s['script_referenced']}
    retained={(m['file'],m['channel']) for m in mappings.get('retained_xa',[])}
    require(not (selected&retained) and (selected|retained)==expected and len(selected)==len(mappings['xa']),
            'Mapping must replace or explicitly retain each script-associated XA channel once')
    for row in mappings.get('retained_xa',[]):
        recipe.setdefault('gap',[]).append(dict(id=f'xa/{Path(row["file"]).stem.lower()}/ch{row["channel"]:02}',reason=row['reason']))
    for mapping in mappings['xa']:
        stream=next(s for s in xa['streams'] if s['file'].lstrip('/').split(';')[0]==mapping['file'] and s['channel']==mapping['channel'])
        data=file_data[mapping['file']];sectors=[]
        for at in range(0,len(data),2352):
            sector=data[at:at+2352]
            if sector[15]==2 and sector[18]&4 and sector[16]==stream['xa_file'] and sector[17]==stream['channel']:sectors.append(sector)
        encoded=b''.join(sectors);require(sha(encoded)==stream['raw_sector_sha256'],'Changed original XA channel')
        raw_path=work/'channel.raw';pcm_path=work/'channel.pcm';raw_path.write_bytes(encoded)
        subprocess.run([str(args.codec_check),'xa',str(raw_path),str(pcm_path)],check=True,capture_output=True)
        pcm=array.array('h');pcm.frombytes(pcm_path.read_bytes())
        # CLI writes little endian even when curation runs on a big-endian host.
        import sys
        if sys.byteorder!='little':pcm.byteswap()
        require(len(pcm)==len(sectors)*4032,'XA decoder sample count changed')
        nonzero=[i for i,n in enumerate(pcm) if n]
        require(nonzero,'Selected XA channel is silent')
        end=nonzero[-1]+1;char=mapping['character_id']
        if 'FINISH' in mapping['file']:
            require(char==stream['channel'],'FINISH channel is not the acting character')
        else:
            event=0x32+(int(Path(mapping['file']).stem[-2:])-1)*16+stream['channel']
            require(any(e['event_id']==event for s in xa['characters'][char]['scripts'] for e in s['events']),
                    'DEMOXA channel has no declared character script association')
        append(dict(id=f'xa/{Path(mapping["file"]).stem.lower()}/ch{stream["channel"]:02}',target_kind='xa_mono',
                    target_file=mapping['file'],target_character=names[char],category=mapping['category'],
                    target_xa_file=stream['xa_file'],target_channel=stream['channel'],target_coding=stream['coding'],
                    target_sector_count=len(sectors),target_sha256=sha(encoded),target_samples=end,
                    target_rate_numerator=stream['rate'],target_rate_denominator=1,target_replace_first_sample=0,
                    target_replace_end_sample=end,target_insert_offset_samples=0,original_pcm_sha256=sha(pcm_path.read_bytes()),
                    original_active_end_sample=end,placement_note='Start aligned; native stream stop/cancel unchanged; exact zero tail excluded from capacity'),
               mapping['sources'],mapping['note'])
    recipe['preserved']=[dict(id=f'xa/{Path(s["file"].split(";")[0]).stem.lower()}/ch{s["channel"]:02}',
                              reason='No original character attack-script association; speaker/usage unqualified')
                         for s in xa['streams'] if not s['script_referenced']]
    require(len({c['id'] for c in recipe['cue']})==len(recipe['cue']),'Duplicate curated target')
    lines=[]
    for key,value in recipe.items():
        if isinstance(value,list):
            for row in value:
                lines+=['',f'[[{key}]]']+[f'{k} = {json.dumps(v,ensure_ascii=False)}' for k,v in row.items()]
        else:lines.append(f'{key} = {json.dumps(value,ensure_ascii=False)}')
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_bytes(('\n'.join(lines)+'\n').encode('utf-8'))
    print(json.dumps(dict(cues=len(recipe['cue']),gaps=len(recipe.get('gap',[])),files=len(recipe['file']),sha256=sha(args.out.read_bytes()))))


if __name__=='__main__':main()
