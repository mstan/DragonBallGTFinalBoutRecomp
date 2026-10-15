cmake_minimum_required(VERSION 3.20)
project(DragonBallGTFinalBoutRecomp LANGUAGES C CXX)

set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp" CACHE PATH
    "Path to the pinned psxrecomp framework")
if(NOT EXISTS "${PSXRECOMP_ROOT}/runtime/runtime.cmake")
    message(FATAL_ERROR
        "Missing psxrecomp framework. Run: git submodule update --init --recursive")
endif()
if(NOT EXISTS "${PSXRECOMP_ROOT}/lib/recomp-net/CMakeLists.txt")
    message(FATAL_ERROR
        "Missing recomp-net dependency. Run: git submodule update --init --recursive")
endif()
if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/recomp-ui/recomp_ui.cmake")
    message(FATAL_ERROR
        "Missing recomp-ui launcher. Run: git submodule update --init --recursive")
endif()

set(PSX_NETPLAY ON CACHE BOOL "Enable two-player recomp-net" FORCE)
set(PSX_SETUP_WIZARD ON CACHE BOOL "Enable legal-disc setup and rebuild wizard" FORCE)
set(PSX_LAUNCHER_MOD_COMMIT_WORKER_SAFE ON CACHE BOOL
    "Prepare verified FuniDub resources on the owned launcher worker" FORCE)
include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")

# Generated game C and the legally supplied disc stay local. The same sources
# can build a first-run setup host before game C has been generated.
psxrecomp_add_game_runtime(psx-runtime
    PRELOADED_MODS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/mods/preloaded"
    ENABLE_NETPLAY_IF_PRESENT
    NETPLAY_LOBBY_URL "ws://netplay.retcomm.net:8765"
    ENABLE_SETUP_WIZARD
    WINDOW_TITLE "Dragon Ball GT: Final Bout Recompiled"
    EXE_NAME "DragonBallGTFinalBout_Recompiled"
    DEFAULT_GAME_CONFIG_PATH "game.toml"
    MAX_PLAYERS 2
    APP_ICON "${CMAKE_CURRENT_SOURCE_DIR}/assets/psxrecomp.ico"
    GEN_MARKER "generated/SLUS_004.93_dispatch.c"
    GEN_FULL_GLOB "generated/SLUS_004.93_full_*.c"
    CODEGEN_SETUP_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/codegen_setup.c"
)

foreach(_FINAL_BOUT_RUNTIME psx-runtime psx-runtime-pgxp)
    if(TARGET ${_FINAL_BOUT_RUNTIME})
        target_sources(${_FINAL_BOUT_RUNTIME} PRIVATE
            src/mods/final_bout_widescreen.c
            src/mods/final_bout_funidub_prepare.cpp
            src/audio/funidub_builder.cpp
            src/audio/funidub_codecs.cpp)
    endif()
endforeach()

foreach(_PSX_RUNTIME_CONFIG game.toml game_options.toml)
    add_custom_command(TARGET psx-runtime POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_CURRENT_SOURCE_DIR}/${_PSX_RUNTIME_CONFIG}"
            "$<TARGET_FILE_DIR:psx-runtime>/${_PSX_RUNTIME_CONFIG}"
        COMMENT "Staging ${_PSX_RUNTIME_CONFIG}"
        VERBATIM)
endforeach()
