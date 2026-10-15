#include "../../src/audio/funidub_builder.h"
#include "psx_sha256.h"
#include <cstdio>
#include <fstream>
#include <iostream>

int main(int argc,char** argv) {
    try {
        if(argc!=5)throw std::runtime_error("Usage: build_pack TARGET.bin BT3.iso RECIPE.toml OUTPUT.pack");
        const auto result=finalbout::funidub::build(argv[1],argv[2],argv[3],
            [](float fraction,const std::string& text) {std::cout<<int(fraction*100)<<"% "<<text<<"\n";return true;});
        std::ofstream output(argv[4],std::ios::binary);output.write(reinterpret_cast<const char*>(result.bytes.data()),result.bytes.size());
        output.close();if(!output)throw std::runtime_error("Cannot write developer pack output");
        uint8_t hash[32];psx_sha256_compute(result.bytes.data(),result.bytes.size(),hash);
        std::cout<<"Pack: "<<result.bytes.size()<<" bytes, "<<result.replaced<<" cues, SHA256 ";
        for(auto byte:hash)std::printf("%02x",byte);std::cout<<"\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}
