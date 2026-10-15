cmake_minimum_required(VERSION 3.20)
project(FinalBoutAudioTools LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../psxrecomp" CACHE PATH
    "Pinned framework for SHA-256 and toml11")
set(AUDIO_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/../../src/audio")
add_library(funidub_codecs STATIC "${AUDIO_SOURCE}/funidub_codecs.cpp")
add_executable(codec_check codec_check.cpp)
target_link_libraries(codec_check PRIVATE funidub_codecs)
add_executable(build_pack build_pack.cpp "${AUDIO_SOURCE}/funidub_builder.cpp"
    "${PSXRECOMP_ROOT}/runtime/src/psx_sha256.c")
target_include_directories(build_pack PRIVATE "${PSXRECOMP_ROOT}/runtime/include"
    "${PSXRECOMP_ROOT}/recompiler/lib/toml11")
target_link_libraries(build_pack PRIVATE funidub_codecs)
include(CTest)
if(BUILD_TESTING)
    add_executable(test_codecs test_codecs.cpp)
    target_link_libraries(test_codecs PRIVATE funidub_codecs)
    add_test(NAME funidub_codecs COMMAND test_codecs)
    add_executable(test_prepare_cache test_prepare_cache.cpp
        "${PSXRECOMP_ROOT}/runtime/src/psx_sha256.c")
    target_include_directories(test_prepare_cache PRIVATE
        "${PSXRECOMP_ROOT}/runtime/include"
        "${PSXRECOMP_ROOT}/recompiler/lib/toml11")
    add_test(NAME funidub_prepare_cache COMMAND test_prepare_cache)
    # RetComM's compact SDK ships cmake/ninja without a standalone ctest.
    add_custom_target(check_audio COMMAND $<TARGET_FILE:test_codecs>
        COMMAND $<TARGET_FILE:test_prepare_cache>
        DEPENDS test_codecs test_prepare_cache VERBATIM)
endif()
