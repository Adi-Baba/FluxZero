from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.build_py import build_py
import sys
import os
import subprocess
import platform

class BuildFluxZero(install):
    def run(self):
        # 1. Attempt Compilation
        print("--- Building FluxZero Core ---")
        cwd = os.path.dirname(os.path.abspath(__file__))
        
        system = platform.system()
        try:
            if system == "Windows":
                # Run batch file
                print("Detected Windows. Running compile_fz.bat...")
                subprocess.check_call(["compile_fz.bat"], cwd=cwd, shell=True)
                # Move dll to package dir if not already there (compile_fz.bat outputs to root usually)
                if os.path.exists(os.path.join(cwd, "fluxzero.dll")):
                    dst = os.path.join(cwd, "fluxzero", "fluxzero.dll")
                    os.replace(os.path.join(cwd, "fluxzero.dll"), dst)
                    
            else:
                # Linux/Mac -> Run Make
                print(f"Detected {system}. Running make...")
                subprocess.check_call(["make"], cwd=cwd)
                # Makefile outputs to fluxzero/libfluxzero.so directly now
                
        except Exception as e:
            print(f"[WARNING] Compilation failed: {e}")
            print("FluxZero requires 'g++' and 'gfortran'. Please install them.")
            print("Falling back to pre-compiled binaries if present...")

        # 2. Run standard install
        install.run(self)

setup(
    name="fluxzero",
    version="1.2.0",
    description="The Thermodynamic Neural Engine (Fluid Dynamics AI)",
    author="Aditya (Adi-Baba)",
    url="https://github.com/Adi-Baba/FluxZero",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'fluxzero': ['*.dll', '*.so', '*.dylib']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.6',
    cmdclass={
        'install': BuildFluxZero
    }
)
