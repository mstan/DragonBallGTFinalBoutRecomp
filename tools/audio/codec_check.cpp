// Small standalone developer driver; all media inputs/outputs stay local.
#include "../../src/audio/funidub_codecs.h"
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
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
        if(argc!=4)throw std::runtime_error("Usage: codec_check adx|spu INPUT OUTPUT.pcm");
        const auto data=read(argv[2]);
        const auto sound=std::string(argv[1])=="adx"?decode_adx(data):decode_spu(data,16000);
        // Explicit wire order, not the host's int16 representation.
        Bytes pcm;pcm.reserve(sound.pcm.size()*2);
        for(int16_t s:sound.pcm){pcm.push_back(uint8_t(s));pcm.push_back(uint8_t(uint16_t(s)>>8));}
        write(argv[3],pcm.data(),pcm.size());
        std::cout<<sound.rate<<" Hz, "<<sound.pcm.size()<<" samples\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}
