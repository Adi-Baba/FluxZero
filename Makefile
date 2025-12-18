# Makefile for FluxZero (Linux/macOS)
# Requires: gfortran, g++

CXX = g++
FC = gfortran
CXXFLAGS = -O3 -fPIC -std=c++17 -shared -I src/cpp -I src/fortran
FCFLAGS = -O3 -fPIC -shared
LDFLAGS = -shared

# Output
TARGET = fluxzero/libfluxzero.so
ifeq ($(shell uname), Darwin)
    TARGET = fluxzero/libfluxzero.dylib
endif

# Sources
SRC_DIR = src
CPP_SRC = $(SRC_DIR)/cpp/fz_engine.cpp $(SRC_DIR)/c_api/fz_bridge.cpp
FOR_SRC = $(SRC_DIR)/fortran/fz_graph.f90

# Objects
CPP_OBJ = $(CPP_SRC:.cpp=.o)
FOR_OBJ = $(FOR_SRC:.f90=.o)

all: $(TARGET)

$(TARGET): $(FOR_OBJ) $(CPP_OBJ)
	$(CXX) $(LDFLAGS) -o $@ $^ -lgfortran -lquadmath

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

%.o: %.f90
	$(FC) $(FCFLAGS) -c $< -o $@

clean:
	rm -f $(CPP_OBJ) $(FOR_OBJ) $(TARGET) *.mod
