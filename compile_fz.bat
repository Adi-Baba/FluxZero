@echo off
echo --- Building FluxZero (TC+RL) ---

echo [1/4] Compiling Fortran Graph Kernels...
gfortran -c src/fortran/fz_graph.f90 -o src/fortran/fz_graph.o
if %errorlevel% neq 0 exit /b %errorlevel%

echo [2/4] Compiling C++ Tree Engine...
g++ -c src/cpp/fz_engine.cpp -o src/cpp/fz_engine.o -I src/cpp -I src/fortran
if %errorlevel% neq 0 exit /b %errorlevel%

echo [3/4] Compiling C Bridge...
g++ -c src/c_api/fz_bridge.cpp -o src/c_api/fz_bridge.o -I src/cpp
if %errorlevel% neq 0 exit /b %errorlevel%

echo [4/4] Linking FluxZero DLL...
gfortran -shared -o fluxzero.dll src/fortran/fz_graph.o src/cpp/fz_engine.o src/c_api/fz_bridge.o -lstdc++ -lquadmath
if %errorlevel% neq 0 exit /b %errorlevel%

echo --- Build Success! Created fluxzero.dll ---
