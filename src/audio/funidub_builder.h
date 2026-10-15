#pragma once
#include "funidub_codecs.h"
#include <filesystem>
#include <functional>
#include <map>
#include <string>

namespace finalbout::funidub {
using Progress = std::function<bool(float,const std::string&)>;
// Only file paths and recipes enter preparation. Returned bytes are complete,
// deterministic disc overlays; no guest/SDL/network API is called here.
struct BuildResult {Bytes bytes;std::string recipe_sha256;unsigned replaced=0;};
BuildResult build(const std::filesystem::path& target_raw,
                  const std::filesystem::path& donor_iso,
                  const std::filesystem::path& recipe,
                  const Progress& progress = {});
// Recheck all recipe/source hashes and edit bounds without encoding again.
std::string validate_sources(const std::filesystem::path& target_raw,
                      const std::filesystem::path& donor_iso,
                      const std::filesystem::path& recipe,
                      const Progress& progress = {});
}
