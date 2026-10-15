#include "../../src/audio/funidub_codecs.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>
using namespace finalbout::funidub;
static void check(bool yes,const char* message) {if(!yes)throw std::runtime_error(message);}
template<class F> static void rejects(F f) {
    try {f();} catch(const std::runtime_error&) {return;}
    throw std::runtime_error("Malformed input accepted");
}
static std::array<uint8_t,2352> xa_sector(uint8_t header=12) {
    std::array<uint8_t,2352> sector{};sector[15]=2;
    sector[16]=sector[20]=1;sector[18]=sector[22]=0x64;
    for(size_t at=24;at<2328;at+=128)
        std::fill(sector.begin()+at,sector.begin()+at+16,header);
    return sector;
}
static void test_xa_decode() {
    auto sector=xa_sector();
    for(size_t at=24;at<2328;at+=128) for(unsigned i=0;i<28;++i)
        for(unsigned block=0;block<4;++block)
            sector[at+16+block+i*4]=uint8_t((block+1)|((15-block)<<4));
    History history;const auto ordered=decode_xa_mono(sector,history);
    check(ordered.rate==37800 && ordered.pcm.size()==4032,"XA native geometry changed");
    for(size_t i=0;i<ordered.pcm.size();++i) {
        const unsigned unit=unsigned(i/28%8);
        check(ordered.pcm[i]==(unit%2 ? -int(unit/2+1) : int(unit/2+1)),
              "XA mono nibble/block/group order changed");
    }
    check(history.previous==-4 && history.older==-4,"XA final history was not returned");
    sector=xa_sector(0);sector[19]=sector[23]=4;
    for(size_t at=24;at<2328;at+=128)
        std::fill(sector.begin()+at+16,sector.begin()+at+128,0x78);
    history={};const auto scaled=decode_xa_mono(sector,history);
    check(scaled.rate==18900 && scaled.pcm[0]==-32768 && scaled.pcm[28]==28672,
          "XA signed nibble scaling/rate changed");
    sector=xa_sector(0x1c);history={64,-64};
    const auto predicted=decode_xa_mono(sector,history);
    check(predicted.pcm[0]==60 && predicted.pcm[1]==56 && predicted.pcm[2]==53,
          "XA predictor rounding changed");
    const auto continued=decode_xa_mono(sector,history);
    History fresh;const auto reset=decode_xa_mono(sector,fresh);
    check(continued.pcm[0]==8 && reset.pcm[0]==0,"XA history did not span sectors");
    history={-64,64};
    const auto negative=decode_xa_mono(sector,history);
    check(negative.pcm[0]==-60 && negative.pcm[1]==-56,"XA negative predictor rounding changed");
    sector=xa_sector(0x2c);history={100,-100};
    const auto two_tap=decode_xa_mono(sector,history);
    check(two_tap.pcm[0]==261 && two_tap.pcm[1]==388,"XA second predictor tap changed");
    sector=xa_sector(0x3c);history={32767,-32768};
    check(decode_xa_mono(sector,history).pcm[0]==32767,"XA predictor clipping changed");
    const auto bad=[&](std::array<uint8_t,2352> malformed) {
        History unchanged{123,-456};rejects([&]{decode_xa_mono(malformed,unchanged);});
        check(unchanged.previous==123 && unchanged.older==-456,"Rejected XA sector changed history");
    };
    sector=xa_sector();sector[15]=1;bad(sector);
    sector=xa_sector();sector[18]=sector[22]=0x60;bad(sector);
    sector=xa_sector();sector[18]=sector[22]=0x44;bad(sector);
    sector=xa_sector();sector[20]=2;bad(sector);
    for(uint8_t coding:{uint8_t(1),uint8_t(8),uint8_t(16),uint8_t(0x80)}) {
        sector=xa_sector();sector[19]=sector[23]=coding;bad(sector);
    }
    sector=xa_sector();sector[24]=0;bad(sector);
    // A malformed final group must also leave the input history untouched.
    sector=xa_sector(0x4c);bad(sector);
    sector=xa_sector(13);bad(sector);
    sector=xa_sector();
    std::fill(sector.begin()+24+17*128,sector.begin()+24+17*128+16,0x3d);bad(sector);
}
int main() {
    try {
        test_xa_decode();
        rejects([]{decode_adx(Bytes(39));});
        rejects([]{decode_spu(Bytes(15),16000);});
        Bytes original(160,0); original[1]=4;original[145]=1;
        Sound source{16000,std::vector<int16_t>(280)};
        for(size_t i=0;i<source.pcm.size();++i)source.pcm[i]=int16_t((int(i%64)-32)*500);
        const auto encoded=encode_spu(source,original);
        check(encoded.size()==original.size(),"SPU extent changed");
        for(size_t i=1;i<original.size();i+=16)check(encoded[i]==original[i],"SPU flag changed");
        check(encoded==encode_spu(source,original),"Encoder is not reproducible");
        const auto decoded=decode_spu(encoded,source.rate);
        check(decoded.pcm.size()==source.pcm.size(),"SPU sample count changed");
        int64_t error=0;for(size_t i=0;i<source.pcm.size();++i){int64_t d=source.pcm[i]-decoded.pcm[i];error+=d*d;}
        check(error/source.pcm.size()<300000,"SPU quantization error exceeded bound");
        const auto padded=edit(source,0,140,32000,300,65536,0);
        check(padded.pcm.size()==300 && padded.pcm[0]==source.pcm[0] && padded.pcm[2]==source.pcm[1],"Resampling position changed");
        check(std::all_of(padded.pcm.begin()+280,padded.pcm.end(),[](int16_t n){return n==0;}),"Padding is not silence");
        rejects([&]{edit(source,0,280,32000,559);});
        rejects([&]{edit(source,1,281,32000,600);});
        rejects([&]{encode_spu(padded,original);});
        std::array<uint8_t,2352> sector{};sector[15]=2;
        sector[16]=sector[20]=1;sector[18]=sector[22]=0x64;
        std::array<int16_t,4032> pcm{};for(size_t i=0;i<pcm.size();++i)pcm[i]=source.pcm[i%280];
        History h;const auto xa=encode_xa_mono(sector,pcm.data(),pcm.size(),h);
        check(std::equal(xa.begin(),xa.begin()+24,sector.begin()),"XA control header changed");
        check(std::equal(xa.begin()+2328,xa.end(),sector.begin()+2328),"XA trailer changed");
        check(xa!=sector,"XA payload is still silence");
        History replay;check(xa==encode_xa_mono(sector,pcm.data(),pcm.size(),replay),"XA encoder is not reproducible");
        sector[2348]=1;
        History checksummed;
        const auto with_edc=encode_xa_mono(sector,pcm.data(),pcm.size(),checksummed);
        check(std::equal(with_edc.begin()+2328,with_edc.begin()+2348,sector.begin()+2328),"XA reserved tail changed");
        check(!std::equal(with_edc.begin()+2348,with_edc.end(),sector.begin()+2348),"XA EDC was not updated");
        for(size_t at=24;at<2328;at+=128){
            check(std::equal(xa.begin()+at,xa.begin()+at+4,xa.begin()+at+4),"XA first redundant header mismatch");
            check(std::equal(xa.begin()+at+8,xa.begin()+at+12,xa.begin()+at+12),"XA last redundant header mismatch");
        }
        History decoded_history;const auto xa_pcm=decode_xa_mono(xa,decoded_history);
        int64_t xa_error=0;
        for(size_t i=0;i<pcm.size();++i){const int64_t d=int64_t(pcm[i])-xa_pcm.pcm[i];xa_error+=d*d;}
        check(xa_error/int64_t(pcm.size())<300000,"XA roundtrip quantization error exceeded bound");
        check(decoded_history.previous==h.previous && decoded_history.older==h.older,
              "XA decoded history differs from encoder reconstruction");
        const auto xa_next=encode_xa_mono(sector,pcm.data(),pcm.size(),h);
        const auto next_pcm=decode_xa_mono(xa_next,decoded_history);
        check(next_pcm.pcm.size()==4032 && decoded_history.previous==h.previous && decoded_history.older==h.older,
              "XA roundtrip lost history between sectors");
        sector[19]=sector[23]=1;
        rejects([&]{encode_xa_mono(sector,pcm.data(),pcm.size(),h);});
        std::cout<<"Audio codec bounds, timing and reproducibility checks passed\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}
