#include "funidub_codecs.h"
#include <algorithm>
#include <limits>
#include <stdexcept>

// Format references (independently written implementation):
// https://psx-spx.consoledev.net/soundprocessingunitspu/#spu-adpcm-samples
// https://psx-spx.consoledev.net/cdromformat/#cdrom-xa-audio-adpcm-compression
// ADX header/predictor facts cross-checked against FFmpeg n7.1 adxdec.c/adx.c.
// No FFmpeg source or decoder library is included in the application.
namespace finalbout::funidub {
namespace {
constexpr int a[] = {0,60,115,98,122}, b[] = {0,0,-52,-55,-60};
void need(bool yes, const char* message) {
    if (!yes) throw std::runtime_error(message);
}
int32_t clip(int64_t n) { return int32_t(std::clamp<int64_t>(n,-32768,32767)); }
// Explicit arithmetic shift: identical on every supported C++ target.
int64_t floor_div(int64_t n, int64_t d) { return n>=0 ? n/d : -((-n+d-1)/d); }
int64_t nearest(int64_t n, int64_t d) { return n>=0 ? (n+d/2)/d : -((-n+d/2)/d); }
uint32_t be32(const Bytes& p, size_t n) {
    need(n<=p.size() && p.size()-n>=4,"Truncated ADX integer");
    return uint32_t(p[n])<<24|uint32_t(p[n+1])<<16|uint32_t(p[n+2])<<8|p[n+3];
}
unsigned be16(const Bytes& p, size_t n) {
    need(n<=p.size() && p.size()-n>=2,"Truncated ADX integer");
    return unsigned(p[n])<<8|p[n+1];
}
int32_t reconstruct(int nibble, unsigned shift, unsigned filter, History& h) {
    const int32_t sample=clip(int64_t(nibble)*(1<<(12-shift))+
        floor_div(int64_t(h.previous)*a[filter]+int64_t(h.older)*b[filter]+32,64));
    h.older=h.previous; h.previous=sample; return sample;
}
struct Encoded {
    uint8_t header=0;
    std::array<uint8_t,28> nibble{};
    History history;
};
Encoded encode_block(const int16_t* pcm, const History initial, unsigned filters) {
    uint64_t best_error=std::numeric_limits<uint64_t>::max();
    Encoded best;
    // Closed-loop quantization includes decoded history when choosing a filter.
    // Stable iteration order resolves ties without a floating-point dependency.
    for (unsigned f=0;f<filters;++f) for (unsigned shift=0;shift<=12;++shift) {
        Encoded candidate; candidate.header=uint8_t(f*16+shift);
        candidate.history=initial; uint64_t error=0;
        const int step=1<<(12-shift);
        for (unsigned i=0;i<28;++i) {
            const auto& h=candidate.history;
            const int64_t prediction=floor_div(int64_t(h.previous)*a[f]+int64_t(h.older)*b[f]+32,64);
            const int q=int(std::clamp<int64_t>(nearest(int64_t(pcm[i])-prediction,step),-8,7));
            candidate.nibble[i]=uint8_t(q&15);
            const int64_t difference=int64_t(pcm[i])-reconstruct(q,shift,f,candidate.history);
            error+=uint64_t(difference*difference);
        }
        // The first exact candidate also wins the existing stable tie rule.
        if(error==0)return candidate;
        if (error<best_error) {best_error=error;best=candidate;}
    }
    return best;
}
}

Sound decode_spu(const Bytes& data, uint32_t rate) {
    need(!data.empty() && data.size()%16==0 && rate>0 && rate<=192000,
         "Invalid SPU sample extent/rate");
    Sound out{rate,{}}; out.pcm.reserve(data.size()/16*28); History h;
    for (size_t off=0;off<data.size();off+=16) {
        unsigned filter=data[off]>>4, shift=data[off]&15;
        need(filter<=4 && shift<=12 && data[off+1]<=7,"Invalid SPU ADPCM frame");
        for (size_t i=0;i<28;++i) {
            int n=(data[off+2+i/2]>>(4*(i%2)))&15; if(n>=8)n-=16;
            out.pcm.push_back(int16_t(reconstruct(n,shift,filter,h)));
        }
    }
    return out;
}

Sound decode_xa_mono(const std::array<uint8_t,2352>& sector, History& history) {
    need(sector[15]==2 && (sector[18]&0x24)==0x24 &&
         (sector[19]==0 || sector[19]==4) &&
         std::equal(sector.begin()+16,sector.begin()+20,sector.begin()+20),
         "Unsupported original XA sector");
    // Validate the complete sector before advancing the caller's predictor.
    for (unsigned group=0;group<18;++group) {
        const auto* data=sector.data()+24+group*128;
        need(std::equal(data,data+4,data+4) && std::equal(data+8,data+12,data+12),
             "Inconsistent XA sound group headers");
        for (unsigned block=0;block<8;++block)
            need((data[4+block]>>4)<=3 && (data[4+block]&15)<=12,
                 "Unsupported XA predictor/shift");
    }
    Sound out{sector[19]==4 ? 18900u : 37800u,{}};
    out.pcm.reserve(4032); History decoded_history=history;
    for (unsigned group=0;group<18;++group) {
        const auto* data=sector.data()+24+group*128;
        // Match the CD controller: each low-nibble block precedes its
        // high-nibble block, with one continuous mono predictor history.
        for (unsigned block=0;block<4;++block) for (unsigned half=0;half<2;++half) {
            const uint8_t header=data[4+block*2+half];
            for (unsigned i=0;i<28;++i) {
                int n=(data[16+block+i*4]>>(half*4))&15;
                if(n>=8)n-=16;
                out.pcm.push_back(int16_t(reconstruct(n,header&15,header>>4,decoded_history)));
            }
        }
    }
    history=decoded_history;
    return out;
}

Sound decode_adx(const Bytes& data) {
    need(data.size()>=40 && be16(data,0)==0x8000,"Invalid ADX header");
    const size_t offset=be16(data,2)+4;
    const uint32_t rate=be32(data,8), count=be32(data,12);
    need(data[4]==3 && data[5]==18 && data[6]==4 && data[7]==1 &&
         data[18]==4 && data[19]==0,"Unsupported ADX encoding");
    need(offset>=40 && offset<=data.size() &&
         std::equal(data.begin()+offset-6,data.begin()+offset,"(c)CRI"),"Invalid ADX copyright marker");
    need(rate==24000 && be16(data,16)==500,"Unsupported ADX predictor profile");
    const size_t blocks=(uint64_t(count)+31)/32;
    need(count>0 && blocks<=(data.size()-offset)/18,"Truncated ADX samples");
    // Quantized coefficients for the verified 24 kHz / 500 Hz profile.
    // Declared here rather than recomputed through platform libm.
    constexpr int c1=6688, c2=-2730;
    Sound out{rate,{}}; out.pcm.reserve(count); History h;
    for (size_t block=0;block<blocks;++block) {
        const size_t at=offset+block*18; const unsigned scale=be16(data,at);
        need(!(scale&0x8000),"ADX ended before its declared sample count");
        for (unsigned i=0;i<32 && out.pcm.size()<count;++i) {
            int n=(data[at+2+i/2]>>(4*(1-i%2)))&15; if(n>=8)n-=16;
            const int32_t sample=clip(int64_t(n)*scale+floor_div(int64_t(c1)*h.previous+int64_t(c2)*h.older,4096));
            h.older=h.previous;h.previous=sample;out.pcm.push_back(int16_t(sample));
        }
    }
    return out;
}

Sound edit(const Sound& source, size_t first, size_t end, uint32_t rate,
           size_t capacity, int32_t gain_q16, unsigned fade_ms, uint32_t rate_denominator) {
    need(source.rate>0 && source.rate<=192000 && rate_denominator>0 && rate_denominator<=65536 &&
         rate>0 && uint64_t(rate)<=uint64_t(192000)*rate_denominator && first<end && end<=source.pcm.size() &&
         gain_q16>=0 && gain_q16<=4*65536 && fade_ms<=1000,"Invalid audio edit recipe");
    const uint64_t source_rate=uint64_t(source.rate)*rate_denominator;
    const uint64_t available=((uint64_t(end-first)*rate)+source_rate-1)/source_rate;
    need(available<=capacity,"Donor excerpt exceeds the original playback slot");
    Sound out{rate/rate_denominator,std::vector<int16_t>(capacity,0)};
    const size_t fade=std::min<size_t>(available/2,uint64_t(rate)*fade_ms/(1000*rate_denominator));
    for (size_t i=0;i<available;++i) {
        const uint64_t position=uint64_t(i)*source_rate;
        const size_t left=first+size_t(position/rate), right=std::min(left+1,end-1);
        const int64_t fraction=position%rate;
        int64_t sample=nearest(int64_t(source.pcm[left])*(rate-fraction)+int64_t(source.pcm[right])*fraction,rate);
        sample=nearest(sample*gain_q16,65536);
        if (fade && i<fade) sample=nearest(sample*int64_t(i),fade);
        if (fade && available-1-i<fade) sample=nearest(sample*int64_t(available-1-i),fade);
        out.pcm[i]=int16_t(clip(sample));
    }
    return out;
}

Bytes encode_spu(const Sound& sound, const Bytes& original) {
    need(!original.empty() && original.size()%16==0 && sound.pcm.size()==original.size()/16*28,
         "Replacement does not match original SPU capacity");
    Bytes out(original.size()); History history;
    for (size_t at=0;at<out.size();at+=16) {
        need(original[at+1]<=7,"Invalid original SPU flags");
        const auto block=encode_block(sound.pcm.data()+at/16*28,history,5);
        history=block.history;out[at]=block.header;out[at+1]=original[at+1];
        for (unsigned i=0;i<14;++i) out[at+2+i]=uint8_t(block.nibble[i*2]|block.nibble[i*2+1]<<4);
    }
    return out;
}

std::array<uint8_t,2352> encode_xa_mono(const std::array<uint8_t,2352>& original,
    const int16_t* pcm, size_t samples, History& history) {
    need(pcm && samples==4032 && original[15]==2 && (original[18]&0x24)==0x24 &&
         (original[19]==0 || original[19]==4) &&
         std::equal(original.begin()+16,original.begin()+20,original.begin()+20),
         "Unsupported original XA sector");
    auto out=original; size_t cursor=0;
    for (unsigned group=0;group<18;++group) {
        auto* dest=out.data()+24+group*128;
        for (unsigned block=0;block<4;++block) for (unsigned half=0;half<2;++half) {
            const auto encoded=encode_block(pcm+cursor,history,4);cursor+=28;history=encoded.history;
            dest[4+block*2+half]=encoded.header;
            // The two redundant header quartets repeat the neighbouring quartet.
            if(block<2) dest[block*2+half]=encoded.header;
            else dest[12+(block-2)*2+half]=encoded.header;
            for(unsigned i=0;i<28;++i) {
                auto& packed=dest[16+block+i*4];
                packed=uint8_t((packed & (half?15:240)) | (encoded.nibble[i]<<(half*4)));
            }
        }
    }
    if (std::any_of(original.begin()+2348,original.end(),[](uint8_t n){return n!=0;})) {
        uint32_t edc=0;
        for(size_t i=16;i<2348;++i) {
            edc^=out[i];
            for(unsigned bit=0;bit<8;++bit)edc=(edc>>1)^((edc&1)?0xD8018001u:0u);
        }
        for(unsigned i=0;i<4;++i)out[2348+i]=uint8_t(edc>>(8*i));
    }
    return out;
}
}
