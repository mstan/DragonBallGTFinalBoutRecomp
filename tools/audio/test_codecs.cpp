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
int main() {
    try {
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
        sector[19]=sector[23]=1;
        rejects([&]{encode_xa_mono(sector,pcm.data(),pcm.size(),h);});
        std::cout<<"Audio codec bounds, timing and reproducibility checks passed\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}
