#include "funidub_builder.h"
#include "psx_sha256.h"
#include "toml.hpp"
#include <algorithm>
#include <array>
#include <cstring>
#include <fstream>
#include <sstream>
#include <stdexcept>

namespace finalbout::funidub {
namespace {
namespace fs=std::filesystem;
constexpr uint64_t maximum_pack=128ull*1024*1024;
void need(bool yes,const char* reason){if(!yes)throw std::runtime_error(reason);}
void report(const Progress& callback,float fraction,const std::string& message) {
    if(callback && !callback(fraction,message))throw std::runtime_error("Preparation canceled.");
}
std::string digest(const Bytes& bytes) {
    uint8_t hash[32];psx_sha256_compute(bytes.data(),bytes.size(),hash);
    static constexpr char hex[]="0123456789abcdef";std::string result(64,'0');
    for(unsigned i=0;i<32;++i){result[i*2]=hex[hash[i]>>4];result[i*2+1]=hex[hash[i]&15];}
    return result;
}
uint32_t le32(const Bytes& p,size_t at) {
    need(at<=p.size() && p.size()-at>=4,"Truncated archive integer");
    return uint32_t(p[at])|uint32_t(p[at+1])<<8|uint32_t(p[at+2])<<16|uint32_t(p[at+3])<<24;
}
Bytes read(std::ifstream& file,uint64_t offset,uint64_t size) {
    need(size<=maximum_pack,"Audio resource exceeds its preparation bound");
    file.clear();file.seekg(0,std::ios::end);const auto length=file.tellg();
    need(length>=0 && offset<=uint64_t(length) && size<=uint64_t(length)-offset,"Audio source extent is outside the image");
    file.seekg(std::streamoff(offset));Bytes bytes(size);
    if(size)file.read(reinterpret_cast<char*>(bytes.data()),std::streamsize(size));
    need(bool(file),"Cannot read audio source");return bytes;
}
Bytes slice(const Bytes& data,uint64_t offset,uint64_t size) {
    need(offset<=data.size() && size<=data.size()-offset,"Audio sample is outside its bank");
    return Bytes(data.begin()+size_t(offset),data.begin()+size_t(offset+size));
}
uint64_t number(const toml::value& v,const char* name) {
    const auto n=toml::find<int64_t>(v,name);need(n>=0,"Negative audio recipe extent");return uint64_t(n);
}
struct Archive {uint32_t lba,count;uint64_t bytes;const char* table_hash;};
constexpr Archive archives[]={
    {1990,3399,1462016000,"c2e142912b88c1f6ca58d0498fd86fba3b86766d932250361970d096cc847565"},
    {715866,65201,1220337664,"d4725b21070997b5ccae51039de818dbe01a21d0c56915e0c4e2220cc41f046e"}
};
}

static BuildResult build_impl(const fs::path& target_path,const fs::path& donor_path,const fs::path& recipe_path,
                             const Progress& progress,bool validate_only) {
    report(progress,0,"Checking supported game images");
    std::ifstream target(target_path,std::ios::binary),donor(donor_path,std::ios::binary),recipe_file(recipe_path,std::ios::binary);
    need(bool(target) && bool(donor),"Select the original Final Bout disc and a supported BT3 USA ISO");
    need(bool(recipe_file),"FuniDub recipe is missing; reinstall the mod");
    need(fs::file_size(recipe_path)<=1024*1024,"FuniDub recipe exceeds its preparation bound");
    const auto recipe_bytes=read(recipe_file,0,fs::file_size(recipe_path));
    BuildResult result;result.recipe_sha256=digest(recipe_bytes);
    std::istringstream recipe_stream(std::string(recipe_bytes.begin(),recipe_bytes.end()));
    const auto recipe=toml::parse(recipe_stream,recipe_path.u8string());
    need(number(recipe,"format_version")==1 && toml::find<std::string>(recipe,"codec")==codec_version,"Unsupported FuniDub recipe version");
    need(fs::file_size(target_path)==158811744 && fs::file_size(donor_path)==3020816384,"Unsupported game image size");
    need(digest(read(donor,16*2048,2048))=="ff7f5b8c457ed31bcca4c29be44e606e52fc79bc1cfe05d9c48db09560aa4c6c","Unsupported BT3 USA content; image label alone is insufficient");
    std::array<Bytes,2> tables;
    for(unsigned i=0;i<2;++i) {
        tables[i]=read(donor,uint64_t(archives[i].lba)*2048,8+uint64_t(archives[i].count)*8+8);
        need(digest(tables[i])==archives[i].table_hash,"BT3 archive table fingerprint does not match the supported release");
    }
    const auto& files=toml::find(recipe,"file").as_array();
    need(!files.empty() && files.size()<=8,"Unsupported FuniDub resource count");
    std::map<std::string,size_t> file_starts;
    for(const auto& file:files) {
        report(progress,0.05f,"Reading original audio resources");
        const auto id=toml::find<std::string>(file,"id");
        const auto lba=number(file,"lba"),size=number(file,"size");
        need(lba<158811744/2352 && (size+2047)/2048<=158811744/2352-lba,"Original resource exceeds disc geometry");
        need(size && size<=maximum_pack-result.bytes.size() && !file_starts.count(id),"Invalid target file layout");
        Bytes data;data.reserve(size);
        for(uint64_t at=0;at<size;at+=2048) {
            auto sector=read(target,(lba+at/2048)*2352,2352);
            need(sector[15]==2 && !(sector[18]&0x20),"Expected original Form1 resource sector");
            const auto n=std::min<uint64_t>(2048,size-at);data.insert(data.end(),sector.begin()+24,sector.begin()+24+n);
        }
        need(digest(data)==toml::find<std::string>(file,"sha256"),"Original Final Bout resource checksum failed");
        file_starts.emplace(id,result.bytes.size());result.bytes.insert(result.bytes.end(),data.begin(),data.end());
    }
    const auto& cues=toml::find(recipe,"cue").as_array();
    need(!cues.empty() && cues.size()<=1024,"Unsupported FuniDub cue count");
    std::map<std::pair<unsigned,unsigned>,Bytes> source_entries;
    std::vector<std::pair<uint64_t,uint64_t>> claimed;
    for(size_t i=0;i<cues.size();++i) {
        const auto& cue=cues[i];const auto id=toml::find<std::string>(cue,"id");
        report(progress,0.1f+0.85f*float(i)/float(std::max<size_t>(1,cues.size())),
               std::string(validate_only?"Checking ":"Preparing ")+toml::find_or<std::string>(cue,"target_character","character")+" voices");
        const auto file_id=toml::find<std::string>(cue,"target_file");
        need(file_starts.count(file_id),"Unknown target audio file");
        const auto local=number(cue,"target_offset"),size=number(cue,"target_size");
        const auto file=std::find_if(files.begin(),files.end(),[&](const auto& f){return toml::find<std::string>(f,"id")==file_id;});
        need(local<=number(*file,"size") && size<=number(*file,"size")-local,"Target audio sample exceeds its file");
        const uint64_t offset=file_starts.at(file_id)+local;
        need(size && size%16==0,"Invalid original ADPCM sample length");
        for(const auto& span:claimed)need(offset+size<=span.first || offset>=span.second,"Two FuniDub cues overlap");
        claimed.emplace_back(offset,offset+size);
        auto original=slice(result.bytes,offset,size);
        need(digest(original)==toml::find<std::string>(cue,"target_sha256"),"Original voice cue checksum failed");
        const auto archive_number=number(cue,"archive"),entry_number=number(cue,"entry");
        need(archive_number>=1 && archive_number<=2 && entry_number<archives[archive_number-1].count,"Unknown donor archive entry");
        const unsigned archive=unsigned(archive_number),index=unsigned(entry_number);
        const auto key=std::make_pair(archive,index);
        if(!source_entries.count(key)) {
            const auto& info=archives[archive-1];const auto& table=tables[archive-1];
            const uint64_t start=le32(table,8+index*8),length=le32(table,12+index*8);
            need(start<=info.bytes && length<=info.bytes-start,"Donor archive entry exceeds its archive");
            source_entries.emplace(key,read(donor,uint64_t(info.lba)*2048+start,length));
        }
        const auto& entry=source_entries.at(key);
        need(digest(entry)==toml::find<std::string>(cue,"entry_sha256"),"Donor voice entry checksum failed");
        Sound source;
        const auto codec=toml::find<std::string>(cue,"source_codec");
        if(codec=="adx")source=decode_adx(entry);
        else {
            need(codec=="spu","Unsupported donor codec");
            const auto bytes=slice(entry,number(cue,"source_offset"),number(cue,"source_size"));
            need(digest(bytes)==toml::find<std::string>(cue,"source_sha256"),"Donor short-sample checksum failed");
            source=decode_spu(bytes,uint32_t(number(cue,"source_rate")));
        }
        const size_t capacity=number(cue,"target_samples");
        need(capacity<=size/16*28,"Audible voice capacity exceeds original extent");
        const auto rate=number(cue,"target_rate_numerator"),denominator=number(cue,"target_rate_denominator");
        need(rate<=UINT32_MAX && denominator<=65536,"Unsupported target voice pitch");
        const auto destination_rate=uint32_t(rate);
        const auto first=number(cue,"first_sample"),end=number(cue,"end_sample");
        const auto gain=number(cue,"gain_q16"),fade=number(cue,"fade_ms");
        need(first<end && end<=source.pcm.size() && gain<=4*65536 && fade<=1000,"Invalid FuniDub edit bounds");
        auto prepared=edit(source,size_t(first),size_t(end),destination_rate,
                           capacity,int32_t(gain),unsigned(fade),uint32_t(denominator));
        if(validate_only){++result.replaced;continue;}
        prepared.pcm.resize(size/16*28,0);
        const auto replacement=encode_spu(prepared,original);
        std::copy(replacement.begin(),replacement.end(),result.bytes.begin()+offset);++result.replaced;
    }
    report(progress,1,validate_only?"Voice sources verified":"Voice pack prepared");return result;
}
BuildResult build(const fs::path& target,const fs::path& donor,const fs::path& recipe,const Progress& progress) {
    return build_impl(target,donor,recipe,progress,false);
}
std::string validate_sources(const fs::path& target,const fs::path& donor,const fs::path& recipe,const Progress& progress) {
    return build_impl(target,donor,recipe,progress,true).recipe_sha256;
}
}
