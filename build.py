#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
import subprocess
import importlib
import tempfile
from pathlib import Path

# Toolchains definition for cross-platform
TOOLCHAINS = {
    'linux': {
        'cc': 'gcc',
        'ext': ''
    },
    'windows': {
        'cc': 'x86_64-w64-mingw32-gcc',
        'ext': '.exe'
    },
    'android': {
        'cc': 'aarch64-linux-android30-clang', # Update with the NDK toolchain name available in PATH
        'ext': ''
    }
}

def compile_c(compiler, flags, c_code, output_path):
    with tempfile.NamedTemporaryFile(suffix='.c', delete=False, mode='w') as f:
        f.write(c_code)
        f_name = f.name
        
    cmd = [compiler] + flags + ['-o', output_path, f_name]
    try:
        print(f"  [+] Executing: {' '.join(cmd)}")
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        print(f"  [-] Failed to compile {output_path}")
    except FileNotFoundError:
        print(f"  [-] Compiler '{compiler}' not found in PATH.")
    finally:
        if os.path.exists(f_name):
            os.remove(f_name)

def build_all(targets, seed_suffix):
    base_dir = Path(__file__).parent.absolute() / 'challenges_src'
    if not base_dir.exists():
        print(f"  [-] Directory {base_dir} does not exist.")
        return
    levels = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and 'angr' in d and d != 'xx_angr_segfault']
    levels.append('xx_angr_segfault') # ensures it's checked if exists
    levels = [lvl for lvl in levels if os.path.exists(os.path.join(base_dir, lvl, 'generate.py'))]
    levels.sort()

    for target in targets:
        print(f"\n========== Building for {target} ==========")
        target_info = TOOLCHAINS[target]
        out_path = Path(__file__).parent.absolute() / 'dist' / target
        out_path.mkdir(parents=True, exist_ok=True)
        
        for level in levels:
            print(f"\nProcessing {level}...")
            # Import dynamically
            if level in sys.modules:
                del sys.modules[level]
                
            spec = importlib.util.spec_from_file_location(f"generate_{level}", os.path.join(base_dir, level, 'generate.py'))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            
            try:
                seed = f"{level}_user_{seed_suffix}"
                res = mod.generate(seed)
                if not res:
                    continue
                
                c_code = res.get('c_code', '')
                flags = res.get('flags', [])
                
                # Special Handle for iOS/Mac/Windows regarding PIE
                if target == 'windows':
                    flags = [f for f in flags if f not in ['-fno-pie', '-no-pie', '-fPIC', '-fpic']]
                    
                    if level in ['15_angr_arbitrary_read', '16_angr_arbitrary_write', '17_angr_arbitrary_jump']:
                        flags.append('-Wl,--image-base=0x40000000')
                
                exe_name = level + target_info['ext']
                exe_out = str(out_path / exe_name)
                
                if 'shared_c_code' in res:
                    # Special step for 14_angr_shared_library
                    shared_c = res['shared_c_code']
                    libext = '.dll' if target == 'windows' else '.so'
                    shared_out = str(out_path / f"lib{level}{libext}")
                    
                    shared_flags = ['-shared', '-fPIC'] if target != 'windows' else ['-shared']
                    print("  [+] Building shared library...")
                    compile_c(target_info['cc'], shared_flags, shared_c, shared_out)
                    
                    print("  [+] Building main executable...")
                    if target == 'linux':
                        link_flags = flags + [f'-Wl,-R,.', '-L' + str(out_path), '-l' + level]
                    elif target == 'android':
                        link_flags = flags + [f'-Wl,-rpath=.', '-L' + str(out_path), '-l' + level]
                    else: # windows
                        link_flags = flags + ['-L' + str(out_path), '-l' + level]
                    
                    compile_c(target_info['cc'], link_flags, c_code, exe_out)
                else:
                    compile_c(target_info['cc'], flags, c_code, exe_out)
                
                print(f"  [+] Done {level} -> {target}")
            
            except Exception as e:
                print(f"  [-] Error generating {level}: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cross-compile angr CTF challenges")
    parser.add_argument('--targets', nargs='+', choices=list(TOOLCHAINS.keys()), default=list(TOOLCHAINS.keys()), help="Target platforms to compile for. E.g. linux windows android")
    
    # Allow overriding CC from command line
    parser.add_argument('--linux-cc', default=TOOLCHAINS['linux']['cc'])
    parser.add_argument('--windows-cc', default=TOOLCHAINS['windows']['cc'])
    parser.add_argument('--android-cc', default=TOOLCHAINS['android']['cc'])
    
    # Custom seed to differentiate student binaries basically
    parser.add_argument('--seed', default="1337", help="Random seed for binary generation")
    
    args = parser.parse_args()
    
    TOOLCHAINS['linux']['cc'] = args.linux_cc
    TOOLCHAINS['windows']['cc'] = args.windows_cc
    TOOLCHAINS['android']['cc'] = args.android_cc
    
    build_all(args.targets, args.seed)
