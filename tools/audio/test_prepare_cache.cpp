// Exercise the real media provider with a source-builder double. Warm imports
// must never resolve/read source media; corrupt cached bytes must not pass.
#include "../../src/mods/final_bout_funidub_prepare.cpp"
#include <iostream>

namespace {
unsigned source_resolves=0,build_calls=0;
bool source_available=true;
const finalbout::funidub::Bytes fixture_pack{1,3,5,7,9,11,13,15};
void check(bool value,const char* message) {
    if(!value)throw std::runtime_error(message);
}
void write(const fs::path& path,const std::string& text) {
    std::ofstream stream(path,std::ios::binary);stream<<text;
    check(bool(stream),"Cannot write cache fixture");
}
}
namespace PSXRecompV4 {
bool mod_register_media_preparer(const std::string&,ModMediaPreparer,ModMediaPreparer) {return true;}
DiscPathResolution resolve_disc_path(const fs::path& path) {
    ++source_resolves;return {path,path,path};
}
}
namespace finalbout::funidub {
BuildResult build(const fs::path&,const fs::path&,const fs::path& recipe,const Progress&) {
    ++build_calls;
    if(!source_available)throw std::runtime_error("Fixture source media is offline");
    return {fixture_pack,hash_file(recipe),1};
}
}
int main() {
    const auto parent=fs::canonical(fs::temp_directory_path());
    const auto root=parent/("finalbout-cache-test-"+
        std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
    if(!fs::create_directory(root))return 1;
    struct Cleanup {
        fs::path root,parent;
        ~Cleanup() {
            std::error_code ec;
            if(fs::weakly_canonical(root,ec).parent_path()==parent && !ec)fs::remove_all(root,ec);
        }
    } cleanup{root,parent};
    try {
        ModPackage package;package.root=root;
        write(root/"recipe.toml","fixture recipe revision 1\n");
        write(root/"source.bin","original game fixture");
        write(root/"donor.iso","donor fixture");
        ModResource resource;resource.feature_id="funidub";resource.id="pack";
        resource.size=fixture_pack.size();
        write(root/"expected.pack",std::string(fixture_pack.begin(),fixture_pack.end()));
        resource.sha256=hash_file(root/"expected.pack");package.resources.push_back(resource);
        ModPrepareContext context{package,"funidub",root/"source.bin",root/"cache",root,
                                  {{"bt3",root/"donor.iso"}}, {}};
        std::map<std::string,fs::path> output;std::string reason;
        check(prepare(context,output,reason),"First preparation failed");
        check(build_calls==1 && source_resolves==1,"First preparation did not use sources");
        const auto pack=output.at("pack");
        source_available=false;fs::remove(root/"source.bin");fs::remove(root/"donor.iso");
        output.clear();check(probe(context,output,reason),"Offline cached probe failed");
        output.clear();check(prepare(context,output,reason),"Offline cached preparation failed");
        check(output.at("pack")==pack && build_calls==1 && source_resolves==1,
              "Warm cache accessed sources or rebuilt audio");
        // Same-size corruption with a restored write time must still fail.
        const auto time=fs::last_write_time(pack);
        write(pack,std::string(fixture_pack.size(),'x'));fs::last_write_time(pack,time);
        output.clear();check(!probe(context,output,reason) && output.empty(),"Corrupt cache passed probe");
        check(!prepare(context,output,reason) && output.empty(),"Offline corrupt cache was published");
        source_available=true;
        check(prepare(context,output,reason),"Cache repair failed");
        check(build_calls==3 && source_resolves==3 && hash_file(pack)==resource.sha256,
              "Repair did not restore the verified pack");
        // A new recipe cannot reuse a previously prepared pack/receipt.
        write(root/"recipe.toml","fixture recipe revision 2\n");
        output.clear();check(!probe(context,output,reason) && output.empty(),"Old recipe cache accepted");
        source_available=false;
        check(!prepare(context,output,reason) && output.empty(),"Missing new-recipe source accepted");
        std::cout<<"FuniDub cache: first build, offline warm reuse, corruption, repair and recipe invalidation pass\n";
        return 0;
    }catch(const std::exception& error) {std::cerr<<error.what()<<"\n";return 1;}
}
