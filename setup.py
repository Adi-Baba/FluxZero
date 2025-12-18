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
                # Move dll to package dir
                src_dll = os.path.join(cwd, "fluxzero.dll")
                dst_dll = os.path.join(cwd, "fluxzero", "fluxzero.dll")
                if os.path.exists(src_dll):
                    if os.path.exists(dst_dll): os.remove(dst_dll)
                    os.rename(src_dll, dst_dll)
                    
            else:
                # Linux/Mac -> Run Make
                print(f"Detected {system}. Running make...")
                subprocess.check_call(["make"], cwd=cwd)
                
        except Exception as e:
            print(f"[ERROR] Compilation failed: {e}")
            print("FluxZero requires 'g++' and 'gfortran' to be installed.")
            
            # Robustness Check: Do we have a fallback binary?
            expected_bin = "fluxzero.dll" if system == "Windows" else ("libfluxzero.dylib" if system == "Darwin" else "libfluxzero.so")
            bin_path = os.path.join(cwd, "fluxzero", expected_bin)
            
            if os.path.exists(bin_path):
                print(f"[WARNING] Compilation failed, but found existing binary '{expected_bin}'. Using it.")
            else:
                print(f"[FATAL] Compilation failed and no pre-existing binary found at {bin_path}.")
                raise RuntimeError("FluxZero installation failed due to missing native library.") from e

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
