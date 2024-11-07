# First, build the rust library
# Run maturin develop
import subprocess
import os
import platform

env = os.environ.copy()

# only for macos
if platform.system() == 'Darwin':
    env["DYLD_FALLBACK_LIBRARY_PATH"] = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/"

# subprocess.run(['maturin', 'develop'], env=env).check_returncode()

import asyncio
from python.app import App

app = App()

asyncio.run(app.run())
app.close()
