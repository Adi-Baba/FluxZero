from setuptools import setup, find_packages
from setuptools.command.install import install
import sys
import os
import shutil

# Custom install logic to warn about DLL compilation
class CustomInstall(install):
    def run(self):
        # 1. Run standard install
        install.run(self)
        
        # 2. Check for DLL
        # Note: In a real "plug and play" scenario we would compile here using subprocess.call(['compile_fz.bat'])
        # But compile_fz.bat relies on MinGW/gfortran which might not be in PATH.
        # We will try to copy pre-compiled DLL if exists in source, or warn.
        print("-------------------------------------------------------")
        print("FluxZero Installation Complete.")
        print("NOTE: FluxZero requires 'fluxzero.dll' (Windows) or 'libfluxzero.so' (Linux).")
        print("If you haven't compiled it, run 'compile_fz.bat' or use the pre-compiled binary.")
        print("-------------------------------------------------------")

setup(
    name="fluxzero",
    version="1.1.0",
    description="The Thermodynamic Neural Engine (Fluid Dynamics AI)",
    author="Aditya (Adi-Baba)",
    url="https://github.com/Adi-Baba/FluxZero",
    packages=find_packages(),
    include_package_data=True,
    # Ensure the DLL is included if present
    package_data={
        'fluxzero': ['*.dll', '*.so', '*.dylib']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.6',
    cmdclass={
        'install': CustomInstall
    }
)
