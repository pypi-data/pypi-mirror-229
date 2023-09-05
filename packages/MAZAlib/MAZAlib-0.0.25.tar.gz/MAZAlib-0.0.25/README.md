# MAZAlib

Cross-platform 2d/3d image segmentation C++ library

Compliles with: MSVC 14.0 and later, GCC 9.2. Other GCC: not tested yet.
Compatible with C++14, C++11 - not tested

Authors: Roman V. Vasilyev, Timofey Sizonenko, Kirill M. Gerke, Marina V. Karsanina
Moscow, 2017-2021

## Prerequisites

1. Install CMake 3.13 or later. (Or you may lower version requirements by hand to your actual version in all CMakeFiles.txt and hopefully it would work, just not tested yet).
Linux (Ubuntu): sudo apt-get install cmake
Windows: https://cmake.org/download/, add cmake into PATH system variable during installation
2. Install a modern C++ compiler.
Linux (Ubuntu): sudo apt-get install g++
Windows: Visual Studio 2015 or later with C++ tools installed
3. Optionally, for hardware support of non-local means denoising, CUDA-enabled GPU and CUDA toolkit installed


## Building

1. (Optionally) make a build subdirectory and move there, for example "build_release"
2. run cmake <relative path to project>, for example "cmake .." inside build directory. If you're building project with CUDA support, you can specify compute capability of your GPU (to define the one, go to NVIDIA web site). For example, GeForce GTX 1080Ti has compute capability 6.1, then use following command: "cmake DCMAKE_CUDA_FLAGS="-arch=sm61" .."
3. If you have CUDA compiler and NVIDIA GPU, the project automatically configures itself to use GPU for NLM denoising. Otherwise, CPU host code will be used
4. Then under Linux just run "make", under Windows open a generated solution file using Visual Studio and build "segmentation_test_exe" project. A library and "segmentation_probny_loshar.exe" will be compiled and built
5. Run segmentation_probny_loshar under console to check that all is OK


## Config file structure

width height depth
radius VarMethod CorMethod OutFormat
LowThreshold HighThreshold
binary_input_file_name
