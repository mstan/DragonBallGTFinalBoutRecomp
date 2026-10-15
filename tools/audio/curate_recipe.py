"""Build a reviewable generic-context FuniDub recipe from verified inventories.

Developer curation tool, not an end-user matching step. Recipes contain hashes
and sample edits only. No source recordings are written by this command.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import struct
from probe_sources import ARCHIVES, PVD_SHA256, adx_info, require, sha

# Final Bout IDs come from the original portrait/name TIMs. Donor forms are
# explicit; GT adult/Z-era and silent-form substitutions remain visible.
DONORS = [3197,3257,3201,3235,3229,3198,3211,3301,3311,3288,3217,3198,3236,3246,3204,3202,3237,3337]
CATEGORIES = {0:'physical-attack',1:'physical-attack',2:'physical-attack',3:'attack-finisher',
              4:'normal-damage',5:'strong-damage',6:'energy-attack',7:'energy-attack',8:'ki-charge'}
WAVES = {0:range(16,19),1:range(19,22),2:range(22,26),3:range(22,26),
         4:range(0,6),5:list(range(6,10))+[12,13],6:[33,34],7:[33,34],8:[35]}
FORM_NOTES = {
    0:'GT adult Goku uses BT3 Goku (End); costume/era substitution',
    3:'GT Trunks uses BT3 Z-era Trunks without a sword; era substitution',
    4:'GT Super Vegeta uses BT3 Vegeta (End) Super Saiyan; era substitution',
    5:'Adult Super Saiyan Goku uses BT3 Goku (End) Super Saiyan',
    11:'Alternate-costume adult Super Saiyan Goku uses BT3 Goku (End) Super Saiyan',
    15:'GT Super Saiyan ordinary short bank is silent; short cues reuse GT base Goku recordings; spoken cues may also use GT base',
}

def spu(data):
    out=[];h1=h2=0
    a=(0,60,115,98,122);b=(0,0,-52,-55,-60)
    require(data and len(data)%16==0,'Unaligned donor sample')
    for at in range(0,len(data),16):
        f,shift=data[at]>>4,data[at]&15
        require(f<=4 and shift<=12,'Invalid donor ADPCM')
        for i in range(28):
            n=(data[at+2+i//2]>>(4*(i%2)))&15
            if n>=8:n-=16
            value=max(-32768,min(32767,n*(1<<(12-shift))+((h1*a[f]+h2*b[f]+32)//64)))
            out.append(value);h2,h1=h1,value
    return out

def adx(data):
    info=adx_info(data);require(info['sample_rate']==24000 and struct.unpack_from('>H',data,16)[0]==500,'Unknown ADX predictor')
    out=[];h1=h2=0
    for at in range(info['data_offset'],info['data_offset']+math.ceil(info['samples']/32)*18,18):
        scale=struct.unpack_from('>H',data,at)[0];require(not scale&0x8000,'Premature ADX end')
        for i in range(32):
            n=(data[at+2+i//2]>>(4*(1-i%2)))&15
            if n>=8:n-=16
            value=max(-32768,min(32767,n*scale+(6688*h1-2730*h2)//4096))
            out.append(value);h2,h1=h1,value
    return out[:info['samples']]

def trimmed(pcm,rate):
    active=[i for i,n in enumerate(pcm) if abs(n)>=96]
    if not active:return None
    margin=rate//200
    return max(0,active[0]-margin),min(len(pcm),active[-1]+1+margin)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-inventory',type=Path,required=True)
    parser.add_argument('--donor-inventory',type=Path,required=True)
    parser.add_argument('--target-bin',type=Path,required=True)
    parser.add_argument('--donor-iso',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    target=json.loads(args.original_inventory.read_text(encoding='utf-8'))
    donor=json.loads(args.donor_inventory.read_text(encoding='utf-8'))
    banks={b['index']:b for b in donor['banks']}
    raw=args.target_bin.read_bytes();require(sha(raw)==target['disc_sha256'],'Changed original image')
    require(args.donor_iso.stat().st_size==3020816384,'Unsupported donor image')
    image=args.donor_iso.open('rb');entries={};entry_cache={};pcm_cache={}
    def read(at,size):
        image.seek(at);data=image.read(size);require(len(data)==size,'Short donor read');return data
    require(sha(read(16*2048,2048))==PVD_SHA256,'Unsupported donor PVD')
    for number,(name,(lba,size,count,table_hash,_)) in enumerate(ARCHIVES.items(),1):
        table=read(lba*2048,8+count*8+8);require(sha(table)==table_hash,'Unsupported donor table')
        entries[number]=(lba*2048,list(struct.iter_unpack('<II',table[8:-8])))
    def entry(archive,index):
        key=archive,index
        if key not in entry_cache:
            base,table=entries[archive];off,size=table[index];entry_cache[key]=read(base+off,size)
        return entry_cache[key]
    def short(bank,index):
        key=bank,index
        if key not in pcm_cache:
            info=banks[bank];wave=info['waves'][index];data=entry(1,bank)
            require(sha(data)==info['pak_sha256'],'Changed donor voice PAK')
            offset=info['members'][0][0]+wave['offset'];encoded=data[offset:offset+wave['size']]
            require(sha(encoded)==wave['adpcm_sha256'],'Changed donor wave')
            pcm=spu(encoded)[:wave['first_end_decoded_samples']]
            trim=trimmed(pcm,wave['sample_rate'])
            meta=dict(archive=1,entry=bank,entry_sha256=info['pak_sha256'],source_codec='spu',
                      source_offset=offset,source_size=wave['size'],source_sha256=wave['adpcm_sha256'],
                      source_rate=wave['sample_rate'],source_wave=index,source_label=info['label'])
            pcm_cache[key]=meta,pcm,trim
        return pcm_cache[key]
    def spoken(bank,line):
        index=48874+(bank-3194)*100+line;key=2,index
        if key not in pcm_cache:
            data=entry(2,index);info=adx_info(data);pcm=adx(data)
            pcm_cache[key]=(dict(archive=2,entry=index,entry_sha256=sha(data),source_codec='adx',
                                source_rate=info['sample_rate'],source_line=line,source_label=f'English character {bank-3194}, line {line}'),
                            pcm,trimmed(pcm,info['sample_rate']))
        return pcm_cache[key]
    cues=[];gaps=[];files=list(target['files']);file_data={}
    for name,info in target['files'].items():
        file_data[name]=b''.join(raw[i*2352+24:i*2352+2072] for i in range(info['lba'],info['lba']+(info['size']+2047)//2048))[:info['size']]
    def add(original,file_name,char,category,candidates,allow_excerpt=False):
        rate_num=44100*original['spu_pitch'];den=4096;capacity=original['first_pass_samples']
        choices=[]
        for source,pcm,trim in candidates:
            if trim is None:continue
            first,end=trim;required=math.ceil((end-first)*rate_num/(source['source_rate']*den))
            if required>capacity:
                if not allow_excerpt:continue
                end=first+capacity*source['source_rate']*den//rate_num
                if end<=first:continue
            choices.append((abs(capacity-required),source,pcm,first,end,required>capacity))
        if not choices:
            gaps.append(dict(id=original['id'],reason='No supported non-silent context candidate fits the original playback slot'));return
        _,source,pcm,first,end,excerpt=min(choices,key=lambda row:row[0])
        encoded=file_data[file_name][original['offset']:original['offset']+original['size']]
        require(sha(encoded)==original['sha256'],'Original cue extent changed')
        original_pcm=spu(encoded)[:capacity];original_active=trimmed(original_pcm,max(1,rate_num//den))
        if original_active is not None:original_pcm=original_pcm[slice(*original_active)]
        source_pcm=pcm[first:end]
        source_rms=math.sqrt(sum(n*n for n in source_pcm)/len(source_pcm))
        original_rms=math.sqrt(sum(n*n for n in original_pcm)/max(1,len(original_pcm)))
        peak=max(abs(n) for n in source_pcm)
        gain=min(1.5,max(.5,original_rms/max(1,source_rms)),26000/max(1,peak))
        record=dict(id=original['id'],target_file=file_name,target_character=target['banks'][char]['name'],
                    target_offset=original['offset'],target_size=original['size'],target_sha256=original['sha256'],
                    target_samples=capacity,target_spu_pitch=original['spu_pitch'],target_rate_numerator=rate_num,
                    target_rate_denominator=den,category=category,first_sample=first,end_sample=end,
                    gain_q16=round(gain*65536),fade_ms=5,semantic_fit='generic-context substitution',
                    excerpt=excerpt,transcript_status='not transcribed; donor event category verified',
                    review_status='candidate for owner in-game audition',
                    source_form_note=FORM_NOTES.get(char,'Matching donor character/form'),**source)
        if 'native_event_ids' in original:
            record['native_event_ids']=original['native_event_ids']
            record['native_event_categories']=[CATEGORIES[i] for i in original['native_event_ids']]
            if len(set(record['native_event_categories']))>1:
                record['semantic_fit']='shared nonverbal exertion; native sample aliases attack and charge; audition both uses'
        cues.append(record)
    for bank in target['banks']:
        char=bank['character_id'];source_bank=DONORS[char]
        if char==15:source_bank=3201 # GT SS bank's ordinary short sounds are verified silent.
        by_wave={}
        for instrument in bank['instruments']:
            if instrument['index']>8:continue
            if char==10 and instrument['index']==7:continue # Different pitch/shared-effect candidate.
            by_wave.setdefault(instrument['wave'],[]).append(instrument)
        for wave,instruments in by_wave.items():
            instrument=instruments[0];event=instrument['index']
            original=dict(bank['waves'][wave],spu_pitch=instrument['spu_pitch'],
                          native_event_ids=[i['index'] for i in instruments])
            require(not original['loops'],'Do not replace looping effects')
            candidates=[short(source_bank,i) for i in WAVES[event]]
            add(original,'TITLE/BTCHARA.DAT',char,CATEGORIES[event],candidates,allow_excerpt=True)
    for group,file_name,field,lines,category in [(target['menu'],'TITLE/CHARSEL.BIN','variant',(0,1),'generic-intro'),
                                               (target['victory'],'BATTLE/BTWINV.DAT','condition',(3,4),'generic-victory')]:
        for original in group:
            char=original['character_id'];bank=DONORS[char]
            candidates=[spoken(bank,i) for i in lines]
            if char==15:candidates += [spoken(3201,i) for i in lines]
            if char==13:require(bank==3246,'Super Vegetto form')
            add(original,file_name,char,category,candidates)
    output=['format_version = 1','codec = "fb-integer-audio-1"',
            'mapping_status = "generic context candidates; in-game audition pending"',
            'source_release = "BT3 USA SLUS-21678 English"',
            f'target_disc_sha256 = {json.dumps(target["disc_sha256"])}','']
    def table(name,row):
        output.append(f'[[{name}]]')
        for key,value in row.items():
            output.append(f'{key} = '+('true' if value else 'false') if isinstance(value,bool) else f'{key} = {json.dumps(value,ensure_ascii=False)}')
        output.append('')
    for name in files:table('file',dict(id=name,**target['files'][name]))
    for row in cues:table('cue',row)
    for row in gaps:table('gap',row)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text('\n'.join(output),encoding='utf-8')
    print(json.dumps(dict(replaced=len(cues),gaps=len(gaps),categories={c:sum(r['category']==c for r in cues) for c in sorted({r['category'] for r in cues})})))

if __name__=='__main__':main()
