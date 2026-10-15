// Small standalone developer driver; all media inputs/outputs stay local.
#include "../../src/audio/funidub_codecs.h"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <stdexcept>
using namespace finalbout::funidub;
static Bytes read(const char* path) {
    std::ifstream file(path,std::ios::binary);
    if(!file)throw std::runtime_error("Cannot open input");
    return Bytes(std::istreambuf_iterator<char>(file),{});
}
static void write(const char* path,const void* data,size_t n) {
    std::ofstream file(path,std::ios::binary);
    file.write(static_cast<const char*>(data),n);
    if(!file)throw std::runtime_error("Cannot write output");
}
int main(int argc,char** argv) {
    try {
        if(argc!=4)throw std::runtime_error("Usage: codec_check adx|spu|xa INPUT OUTPUT.pcm (xa: complete raw sectors from one channel)");
        const auto data=read(argv[2]);
        const std::string codec=argv[1];Sound sound;
        if(codec=="adx")sound=decode_adx(data);
        else if(codec=="spu")sound=decode_spu(data,16000);
        else if(codec=="xa") {
            if(data.empty() || data.size()%2352!=0)
                throw std::runtime_error("XA input must contain complete 2352-byte sectors");
            const size_t sectors=data.size()/2352;
            if(sectors>sound.pcm.max_size()/4032)
                throw std::runtime_error("XA input exceeds PCM capacity");
            sound.pcm.reserve(sectors*4032);History history;
            for(size_t at=0;at<data.size();at+=2352) {
                std::array<uint8_t,2352> sector;
                std::copy_n(data.begin()+at,sector.size(),sector.begin());
                if(at && (sector[16]!=data[16] || sector[17]!=data[17]))
                    throw std::runtime_error("XA input must contain one selected file/channel in original order");
                const auto decoded=decode_xa_mono(sector,history);
                if(sound.rate && sound.rate!=decoded.rate)
                    throw std::runtime_error("XA input changes native sample rate");
                sound.rate=decoded.rate;
                sound.pcm.insert(sound.pcm.end(),decoded.pcm.begin(),decoded.pcm.end());
            }
        } else throw std::runtime_error("Unsupported input codec");
        // Explicit wire order, not the host's int16 representation.
        Bytes pcm;pcm.reserve(sound.pcm.size()*2);
        for(int16_t s:sound.pcm){pcm.push_back(uint8_t(s));pcm.push_back(uint8_t(uint16_t(s)>>8));}
        write(argv[3],pcm.data(),pcm.size());
        std::cout<<sound.rate<<" Hz, "<<sound.pcm.size()<<" samples\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}
