import asyncio
import shutil

from lmk.utils.asyncio import check_output


async def check_lldb() -> None:
    exec_path = shutil.which("lldb")
    if exec_path is None:
        raise LLDBNotFound

    process = await asyncio.create_subprocess_shell(
        "lldb --batch -o r -- echo 1",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    exit_code = await process.wait()

    if exit_code != 0:
        raise LLDBNotUsable


class LLDBNotFound(Exception):
    """
    """
    def __init__(self) -> None:
        super().__init__(f"No `lldb` executable found")


class LLDBNotUsable(Exception):
    """
    """
    def __init__(self) -> None:
        super().__init__(f"`lldb` cannot attach to processes")



async def main():
    await check_lldb()
    print("BEFORE")
    interpreter_info_str = await check_output(
        ["lldb", "--print-script-interpreter-info"]
    )
    print("INFO", interpreter_info_str)

if __name__ == "__main__":
    asyncio.run(main())
