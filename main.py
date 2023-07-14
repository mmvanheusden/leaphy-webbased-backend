from typing import Union
import asyncio
import tempfile
import aiofiles

from time import sleep

from fastapi import FastAPI


app = FastAPI()



@app.post("/compile/c++")
async def compile(fileContent: str, board: str, libraries: list[str] = []):
    dir = tempfile.TemporaryDirectory()
    print("Created temporary directory: ", dir.name)
    async with aiofiles.open(f"/{dir.name}/{dir.name.removeprefix('/tmp/')}.ino", "w") as f:
        await f.write(fileContent)

    if libraries:
        for lib in libraries:
            print("Adding libraries: ", lib)

            await asyncio.create_subprocess_exec("/home/koen/Documents/GitHub/leaphy-webbased-backend/arduino-cli", "lib", "install", lib)

    a = await asyncio.create_subprocess_exec("/home/koen/Documents/GitHub/leaphy-webbased-backend/arduino-cli", "compile", "--fqbn", board, f"/{dir.name}/{dir.name.removeprefix('/tmp/')}.ino", "--output-dir", f"/{dir.name}/", stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await a.communicate()
    if a.returncode != 0:
        return stderr.decode() + stdout.decode()


    try:
        async with aiofiles.open(f"/{dir.name}/{dir.name.removeprefix('/tmp/')}.ino.hex", "rb") as f:
            return await f.read()
    except Exception as e:
        return str(e)