import asyncio
import tempfile
from os import path

import aiofiles
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from conf import Settings
from models import Sketch, Library

app = FastAPI()
settings = Settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _install_libraries(libraries: list[Library]):
    # Install required libraries
    for library in libraries:
        print(f"Installing libraries: {library}")
        installer = await asyncio.create_subprocess_exec(settings.arduino_cli_path, "lib", "install", library,
                                                         stderr=asyncio.subprocess.PIPE,
                                                         stdout=asyncio.subprocess.PIPE
                                                         )
        stdout, stderr = await installer.communicate()
        if installer.returncode != 0:
            raise HTTPException(500, f"Failed to install library: {stderr.decode() + stdout.decode()}")


async def _compile_sketch(sketch: Sketch):
    with tempfile.TemporaryDirectory() as dir_name:
        file_name = f"{path.basename(dir_name)}.ino"
        sketch_path = f"{dir_name}/{file_name}"

        # Write the sketch to a temp .ino file
        async with aiofiles.open(sketch_path, "w+") as f:
            await f.write(sketch.source_code)

        compiler = await asyncio.create_subprocess_exec(settings.arduino_cli_path, "compile", "--fqbn", sketch.board,
                                                        sketch_path,
                                                        "--output-dir",
                                                        dir_name, stderr=asyncio.subprocess.PIPE,
                                                        stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await compiler.communicate()
        if compiler.returncode != 0:
            raise HTTPException(500, stderr.decode() + stdout.decode())

        async with aiofiles.open(f"{sketch_path}.hex", "r") as f:
            return {"hex": await f.read()}


@app.post("/compile/cpp")
async def compile_cpp(sketch: Sketch):
    await _install_libraries(sketch.libraries)
    return await _compile_sketch(sketch)
