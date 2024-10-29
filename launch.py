# First, build the rust library
# Run maturin develop
import subprocess
import os
env = os.environ.copy()
env["DYLD_FALLBACK_LIBRARY_PATH"] = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/"
subprocess.run(['maturin', 'develop'], env=env).check_returncode()

import asyncio
from python.app import App
asyncio.run(App().run())
