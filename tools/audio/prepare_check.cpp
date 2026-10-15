// Exercise the actual launcher media provider without booting the game.
#include "mod_packages.h"
#include <algorithm>
#include <iostream>
#include <stdexcept>
int main(int argc,char** argv) {
    try {
        if(argc!=6)throw std::runtime_error("Usage: prepare_check MODS DISC BT3 CACHE prepare|probe|cancel");
        PSXRecompV4::ModPackageManager manager(argv[1]);std::string reason;
        if(!manager.scan(&reason) || !manager.scan_errors().empty())throw std::runtime_error("Catalog did not parse: "+reason);
        const auto& package=manager.packages().at("finalbout.audio.funidub").rbegin()->second;
        const auto overlay_count=std::count_if(package.overlays.begin(),package.overlays.end(),
            [](const auto& overlay){return overlay.feature_id=="funidub";});
        if(!manager.set_feature_enabled("finalbout.audio.funidub","funidub",true,&reason) ||
           !manager.set_feature_resource_path("finalbout.audio.funidub","funidub","bt3",argv[3],&reason))
            throw std::runtime_error(reason);
        const std::string operation=argv[5];
        bool canceled=false;
        const auto progress=[&](float fraction,const std::string& text) {
            if(operation=="cancel" && fraction>=0.3f){canceled=true;return false;}
            std::cout<<int(fraction*100)<<"% "<<text<<"\n";return true;
        };
        const bool ok=manager.prepare_resources("SLUS-00493",argv[2],argv[4],&reason,operation=="probe",progress);
        if(operation=="cancel") {
            if(ok || !canceled)throw std::runtime_error("Expected cooperative cancellation");
            std::cout<<"Cancellation observed; no derived binding published\n";return 0;
        }
        if(!ok)throw std::runtime_error(reason.empty()?"Verified cache unavailable":reason);
        const auto plan=manager.resolve("SLUS-00493",{},"2f9d475fa089bed3f77a3344ea23af0663b30ffe9a2bc0b803bcae389480a15b");
        if(!plan.ok || plan.resources.size()!=1 || plan.overlays.size()!=size_t(overlay_count))
            throw std::runtime_error(plan.errors.empty()?"Prepared plan is incomplete":plan.errors.front());
        std::cout<<"Verified "<<overlay_count<<" overlays; fingerprint "<<plan.fingerprint<<"\n";
        std::cout<<"Pack "<<manager.feature_resource_path("finalbout.audio.funidub","funidub","pack").u8string()<<"\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}
