cmake_minimum_required(VERSION 3.10)
project(VelocityLizard)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ============================================================================
# VCPKG INTEGRATION (For C++ Dependencies)
# ============================================================================
if(DEFINED ENV{VCPKG_ROOT})
    set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" CACHE STRING "")
endif()

include(FetchContent)

# Fetch nlohmann_json (For JSON parsing)
FetchContent_Declare(json
    URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz
)
FetchContent_MakeAvailable(json)

# SHARED LIBRARY FOR PYTHON CTYPES
set(LIZARD_LIB_SOURCES
    src/lizard_api.cpp
    src/lizard_mouse.cpp
    src/lizard_keyboard.cpp
    src/bezier.cpp
    src/platform_utils.cpp
    src/reflex_dispatcher.cpp
)

add_library(lizard SHARED ${LIZARD_LIB_SOURCES})
target_include_directories(lizard PRIVATE ${CMAKE_SOURCE_DIR}/src)

if(WIN32)
    target_link_libraries(lizard user32 gdi32)
else()
    target_link_libraries(lizard X11 Xtst)
endif()

set_target_properties(lizard PROPERTIES 
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../brain/core_bin"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../brain/core_bin"
)

# STANDALONE EXECUTABLE (STDIN MODE)
set(LIZARD_EXE_SOURCES
    src/main.cpp
    src/lizard_mouse.cpp
    src/lizard_keyboard.cpp
    src/bezier.cpp
    src/platform_utils.cpp
)

add_executable(lizard_exe ${LIZARD_EXE_SOURCES})
target_include_directories(lizard_exe PRIVATE ${CMAKE_SOURCE_DIR}/src)

if(WIN32)
    target_link_libraries(lizard_exe user32 gdi32)
else()
    target_link_libraries(lizard_exe X11)
endif()

set_target_properties(lizard_exe PROPERTIES OUTPUT_NAME "lizard_standalone")
# ============================================================================
# C++ HYBRID BRAIN (NEW - THE CORTEX)
# ============================================================================

set(CORTEX_SOURCES
    src/hybrid_brain.h
    src/hybrid_brain.cpp
    src/cortex_main.cpp
    src/lizard_mouse.cpp
    src/lizard_keyboard.cpp
    src/bezier.cpp
    src/platform_utils.cpp
)

add_executable(velocity_cortex ${CORTEX_SOURCES})
target_include_directories(velocity_cortex PRIVATE ${CMAKE_SOURCE_DIR}/src)
target_link_libraries(velocity_cortex nlohmann_json::nlohmann_json)

if(WIN32)
    target_link_libraries(velocity_cortex user32 gdi32)
else()
    target_link_libraries(velocity_cortex X11 pthread)
endif()

set_target_properties(velocity_cortex PROPERTIES 
    OUTPUT_NAME "velocity"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../brain/core_bin"
)

# Future: Link llama.cpp when available
# target_link_libraries(velocity_cortex llama)
# target_link_libraries(velocity_cortex whisper)
# target_link_libraries(velocity_cortex opencv_core opencv_imgproc)