cmake_minimum_required(VERSION 3.25 FATAL_ERROR)

project("_pymgl" VERSION "")

# Only use the active virtual environment of Python
set(Python_FIND_VIRTUALENV ONLY)
set(Python_FIND_FRAMEWORK NEVER)
set(Python_ROOT_DIR ${CMAKE_PYTHON_PATH})
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

message("Found python version: " ${Python_VERSION}", include dirs: "${Python_INCLUDE_DIRS})

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(MLN_SOURCE_DIR ${PROJECT_SOURCE_DIR}/vendor/maplibre-native)

# Match MapLibre Native's compiler requirements.
cmake_policy(SET CMP0063 NEW)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_VISIBILITY_PRESET hidden)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_VISIBILITY_INLINES_HIDDEN 1)
set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set_property(GLOBAL PROPERTY PREDEFINED_TARGETS_FOLDER Core)

if(NOT("${CMAKE_BUILD_TYPE}" STREQUAL "Debug"))
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_MINSIZEREL ON)
endif()

# Hide warnings about no symbols
SET(CMAKE_C_ARCHIVE_CREATE "<CMAKE_AR> Scr <TARGET> <LINK_FLAGS> <OBJECTS>")
SET(CMAKE_CXX_ARCHIVE_CREATE "<CMAKE_AR> Scr <TARGET> <LINK_FLAGS> <OBJECTS>")
SET(CMAKE_C_ARCHIVE_FINISH "<CMAKE_RANLIB> -no_warning_for_no_symbols -c <TARGET>")
SET(CMAKE_CXX_ARCHIVE_FINISH "<CMAKE_RANLIB> -no_warning_for_no_symbols -c <TARGET>")

# Build MapLibre Native through its supported CMake entry point.  The previous
# pymgl build copied MapLibre's source list into this repository, which made
# new core components (including PMTiles/MLT) silently disappear on upgrades.
set(BUILD_TESTING OFF CACHE BOOL "Disable MapLibre Native's test suite" FORCE)
set(MLN_WITH_CORE_ONLY OFF CACHE BOOL "Include default platform file sources" FORCE)
set(MLN_WITH_GLFW OFF CACHE BOOL "Do not build the GLFW application" FORCE)
set(MLN_WITH_NODE OFF CACHE BOOL "Do not build Node bindings" FORCE)
set(MLN_WITH_PMTILES ON CACHE BOOL "Enable PMTiles, including MLT tiles" FORCE)
set(MLN_WITH_WERROR OFF CACHE BOOL "Do not promote dependency warnings" FORCE)

if(APPLE)
    set(MLN_WITH_OPENGL OFF CACHE BOOL "Disable OpenGL on Apple platforms" FORCE)
    set(MLN_WITH_METAL ON CACHE BOOL "Use Metal for headless rendering" FORCE)
elseif(UNIX)
    set(MLN_WITH_OPENGL ON CACHE BOOL "Use OpenGL for headless rendering" FORCE)
endif()

add_subdirectory(${MLN_SOURCE_DIR} maplibre-native EXCLUDE_FROM_ALL)

# Include headers for pymgl and build the wrapper
include_directories(${PROJECT_SOURCE_DIR}/include)

add_library(
    mgl_wrapper STATIC
    ${PROJECT_SOURCE_DIR}/src/map.cpp
    ${PROJECT_SOURCE_DIR}/src/spng.c
)

# The wrapper exposes style mutation helpers that MapLibre currently keeps in
# its internal conversion API.
target_include_directories(mgl_wrapper PRIVATE ${MLN_SOURCE_DIR}/src)

# link against mln-core
target_link_libraries(
    mgl_wrapper PUBLIC
    mbgl-core
)

# Build Python module
add_subdirectory(vendor/nanobind)

nanobind_add_module(
    _pymgl
    NB_STATIC LTO
    ${PROJECT_SOURCE_DIR}/src/_pymgl.cpp
)

target_link_libraries(
    _pymgl
    PRIVATE
    mgl_wrapper
)

set_target_properties(_pymgl PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
target_compile_definitions(_pymgl PRIVATE VERSION_INFO=${VERSION_INFO})

# C++ tests are optional because MapLibre Native intentionally owns the
# top-level BUILD_TESTING switch in an embedded build.
option(PYMGL_BUILD_CPP_TESTS "Build pymgl's C++ tests" OFF)
if(PYMGL_BUILD_CPP_TESTS)
    include(CTest)
    add_subdirectory(${PROJECT_SOURCE_DIR}/tests)
endif()
