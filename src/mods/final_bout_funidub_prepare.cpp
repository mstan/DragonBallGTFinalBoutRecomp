#include "../audio/funidub_builder.h"
#include "disc_path.h"
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include "host_file_identity.h"
#include "mod_packages.h"
#include "mod_plugins.h"
#include "psx_sha256.h"
#include "toml.hpp"
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <fstream>
#include <sstream>
#include <stdexcept>
#ifndef _WIN32
#include <unistd.h>
#endif

namespace {
namespace fs=std::filesystem;
using namespace PSXRecompV4;
constexpr const char* builder_version="fb-overlay-builder-3";
std::string finish_hash(psx_sha256_ctx& ctx) {
    uint8_t bytes[32];psx_sha256_final(&ctx,bytes);static constexpr char hex[]="0123456789abcdef";
    std::string result(64,'0');for(unsigned i=0;i<32;++i){result[i*2]=hex[bytes[i]>>4];result[i*2+1]=hex[bytes[i]&15];}
    return result;
}
std::string hash_file(const fs::path& path) {
    std::ifstream in(path,std::ios::binary);if(!in)throw std::runtime_error("Cannot read FuniDub content");
    psx_sha256_ctx ctx;psx_sha256_init(&ctx);std::array<uint8_t,65536> buffer{};
    while(in) {in.read(reinterpret_cast<char*>(buffer.data()),buffer.size());psx_sha256_update(&ctx,buffer.data(),size_t(in.gcount()));}
    if(!in.eof())throw std::runtime_error("Cannot finish reading FuniDub content");
    return finish_hash(ctx);
}
void report(const ModPrepareContext& ctx,float fraction,const std::string& text) {
    if(ctx.progress && !ctx.progress(fraction,text))throw std::runtime_error("Preparation canceled.");
}
struct Inputs {
    fs::path target,donor,recipe,pack,receipt;
    std::string target_stamp,donor_stamp,recipe_hash,pack_hash;
    uint64_t pack_size=0;
    bool qualified_stamps=false;
};
Inputs inputs(const ModPrepareContext& ctx) {
    Inputs result;
    if(ctx.feature_id!="funidub")throw std::runtime_error("Unsupported FuniDub selection");
    result.recipe=ctx.package.root/"recipe.toml";
    result.recipe_hash=hash_file(result.recipe);
    const auto resource=std::find_if(ctx.package.resources.begin(),ctx.package.resources.end(),[&](const auto& r){
        return r.feature_id==ctx.feature_id && r.id=="pack" && !r.input_only;
    });
    if(resource==ctx.package.resources.end() || resource->sha256.size()!=64 || !resource->size)
        throw std::runtime_error("FuniDub package is missing its verified output identity");
    result.pack_hash=resource->sha256;result.pack_size=resource->size;
    // Hash the complete identity into one component to stay within ordinary
    // Windows path limits even when the title/cache root is deeply nested.
    const std::string identity=std::string(builder_version)+"\n"+result.recipe_hash+"\n"+result.pack_hash;
    psx_sha256_ctx key;psx_sha256_init(&key);psx_sha256_update(&key,reinterpret_cast<const uint8_t*>(identity.data()),identity.size());
    const auto directory=ctx.cache_root/"finalbout-funidub"/finish_hash(key);
    result.pack=directory/"voices.pack";result.receipt=directory/"receipt.toml";
    return result;
}
void source_inputs(const ModPrepareContext& ctx,Inputs& in) {
    const auto selected=ctx.inputs.find("bt3");
    if(selected==ctx.inputs.end() || selected->second.empty())
        throw std::runtime_error("Select your BT3 USA ISO to prepare FuniDub");
    in.donor=selected->second;
    in.target=resolve_disc_path(ctx.disc_path).data;
    in.qualified_stamps=host_file_identity(in.target,in.target_stamp) &&
                        host_file_identity(in.donor,in.donor_stamp);
}
bool cache_matches(const Inputs& in) {
    try {
    std::error_code error;
    if(fs::file_size(in.receipt,error)>32768 || error)return false;
    std::ifstream stream(in.receipt,std::ios::binary);if(!stream)return false;
    const auto receipt=toml::parse(stream,"FuniDub receipt");
    if(toml::find<std::string>(receipt,"builder")!=builder_version ||
       toml::find<std::string>(receipt,"recipe")!=in.recipe_hash ||
       toml::find<std::string>(receipt,"pack_sha256")!=in.pack_hash)return false;
    // A prepared pack is self-contained. Its exact manifest hash, not the
    // source ISO's location or timestamps, determines what will be installed.
    // Verify the local bytes even on hosts without a qualified file identity.
    return fs::file_size(in.pack)==in.pack_size && hash_file(in.pack)==in.pack_hash;
    }catch(const std::exception&){return false;}
}
void publish(const fs::path& temporary,const fs::path& destination) {
#ifdef _WIN32
    if(!MoveFileExW(temporary.c_str(),destination.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))
        throw std::runtime_error("Cannot publish prepared FuniDub content");
#else
    fs::rename(temporary,destination);
#endif
}
struct Staging {
    fs::path path;
    ~Staging(){std::error_code error;fs::remove(path,error);}
};
fs::path temporary_path(const fs::path& destination) {
    static std::atomic<unsigned> count{0};
    auto path=destination;
    const auto process=
#ifdef _WIN32
        GetCurrentProcessId();
#else
        getpid();
#endif
    path+="."+std::to_string(process)+"."+std::to_string(std::chrono::steady_clock::now().time_since_epoch().count())+
          "."+std::to_string(count.fetch_add(1))+".tmp";
    return path;
}
bool probe(const ModPrepareContext& ctx,std::map<std::string,fs::path>& output,std::string& reason) {
    try {
        const auto in=inputs(ctx);
        if(!cache_matches(in))return false;
        output["pack"]=in.pack;return true;
    }catch(const std::exception& error){reason=error.what();return false;}
}
bool prepare(const ModPrepareContext& ctx,std::map<std::string,fs::path>& output,std::string& reason) {
    try {
        report(ctx,0,"Checking prepared FuniDub");auto in=inputs(ctx);
        if(cache_matches(in)) {
            report(ctx,1,"Using cached FuniDub");output["pack"]=in.pack;return true;
        }
        // Source media is needed only for the first build or cache repair.
        // Keep all original source hashes/guards on that path; a warm launch
        // must work when the already-imported BT3 ISO is offline.
        source_inputs(ctx,in);
        const auto built=finalbout::funidub::build(in.target,in.donor,in.recipe,
            [&](float fraction,const std::string& text){return !ctx.progress || ctx.progress(fraction*0.94f,text);});
        if(built.recipe_sha256!=in.recipe_hash || built.bytes.size()!=in.pack_size)
            throw std::runtime_error("FuniDub recipe changed; reopen the launcher");
        fs::create_directories(in.pack.parent_path());Staging staging{temporary_path(in.pack)};
        {
            std::ofstream stream(staging.path,std::ios::binary);
            stream.write(reinterpret_cast<const char*>(built.bytes.data()),std::streamsize(built.bytes.size()));
            stream.close();if(!stream)throw std::runtime_error("Cannot write prepared FuniDub content");
        }
        report(ctx,.96f,"Verifying voice pack");
        if(hash_file(staging.path)!=in.pack_hash)throw std::runtime_error("Prepared FuniDub checksum failed; original audio is available with FuniDub disabled");
        std::string target_after,donor_after;
        if(in.qualified_stamps && (!host_file_identity(in.target,target_after) || target_after!=in.target_stamp ||
            !host_file_identity(in.donor,donor_after) || donor_after!=in.donor_stamp))
            throw std::runtime_error("Source media changed during FuniDub preparation; try again");
        if(hash_file(in.recipe)!=in.recipe_hash)throw std::runtime_error("FuniDub recipe changed during preparation; try again");
        report(ctx,.98f,"Installing local voice pack");publish(staging.path,in.pack);
        std::string pack_stamp;host_file_identity(in.pack,pack_stamp);
        Staging receipt{temporary_path(in.receipt)};
        {
            std::ofstream stream(receipt.path,std::ios::binary);
            stream<<"builder = \""<<builder_version<<"\"\nrecipe = \""<<in.recipe_hash<<"\"\npack_sha256 = \""<<in.pack_hash<<"\"\n"
                  <<"target = \""<<in.target_stamp<<"\"\ndonor = \""<<in.donor_stamp<<"\"\npack = \""<<pack_stamp<<"\"\n";
            stream.close();if(!stream)throw std::runtime_error("Cannot record FuniDub preparation");
        }
        publish(receipt.path,in.receipt);report(ctx,1,"FuniDub ready");output["pack"]=in.pack;return true;
    }catch(const std::exception& error){reason=error.what();return false;}
}
}

PSX_MOD_CONSTRUCTOR(final_bout_register_funidub) {
    PSXRecompV4::mod_register_media_preparer("finalbout.funidub.prepare",prepare,probe);
}
