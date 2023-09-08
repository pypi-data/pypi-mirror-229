import unicodedata
import re
from pathlib import Path
import string

MAX_FILENAME_LENGTH: int = 255
MAX_EXTENSION_LENGTH: int = 254
MIN_ASCII_VALUE: int = 32

def sanitize(filename:str, strict: bool = True) -> str:
    """Return a fairly safe version of the filename.
    """
    if not strict:
        filepath: Path = Path(filename)
        filedir: Path = filepath.parent
        filename = filepath.name
    else:
        filedir: Path = Path()
    
    filename = _remove_blacklisted_characters(filename)
    filename = _remove_chars_below_code_point(filename, MIN_ASCII_VALUE)
    filename = _normalize_filename(filename)
    filename, ext = _handle_extension(filename)
    filename = _handle_reserved(filename)
    filename = _handle_max_length(filename, ext, 
                                    MAX_FILENAME_LENGTH, MAX_EXTENSION_LENGTH)

    return str(filedir / filename)


def _remove_blacklisted_characters(filename: str) -> str:
    """Remove blacklisted characters from the filename."""
    blacklist = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|", "\0"]
    return "".join(c for c in filename if c not in blacklist)

def _remove_chars_below_code_point(filename: str, code_point: int) -> str:
    """Remove characters from the filename below a certain ASCII code point."""
    return "".join(c for c in filename if ord(c) > code_point)

def _normalize_filename(filename: str) -> str:
    """Normalize the filename and remove trailing/leading spaces and periods."""
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.rstrip(". ").strip()
    return "__" + filename if all([x == "." for x in filename]) else filename

def _handle_extension(filename: str) -> tuple[str, str]:
    """Handle the extension of the filename."""
    parts = re.split(r"/|\\", filename)[-1].split(".")
    ext = "." + parts.pop() if len(parts) > 1 else ""
    filename = filename[:-len(ext)] if ext else filename
    return filename, ext

def _handle_reserved(filename: str) -> str:
    """Handle reserved filenames."""
    
    # Reserved words on Windows
    reserved = [
        "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
        "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
        "LPT6", "LPT7", "LPT8", "LPT9",
    ]  
    return "__" + filename if filename in reserved else filename

def _handle_max_length(filename: str, ext: str, max_filename_length: int, 
                        max_extension_length: int) -> str:
    """Handle filenames that exceed the maximum length."""
    if len(filename) > max_filename_length:
        if len(ext) > max_extension_length:
            ext = ext[max_extension_length:]
        maxl = max_filename_length - len(ext)
        filename = filename[:maxl] + ext
        filename = filename.rstrip(". ")
        filename = "__" if len(filename) == 0 else filename
    return filename

def _stringshift(stringlist: str, shift: int) -> str:
    return stringlist[shift:] + stringlist[:shift]
    
def obfuscate(text: str, shift_val: int = 17) -> str:
    stringlist: str = f"{string.ascii_letters}0123456789. "
    
    replacement_dict: dict[str, str] = {}
    for original, replaced in zip(stringlist, _stringshift(stringlist, shift_val)):
        replacement_dict[original] = replaced
    
    new_text: str = ""
    for char in text:
        new_char = replacement_dict.get(char)
        if new_char is None:
            new_text += char
        else:
            new_text += new_char
    return new_text

def unobfuscate(text: str, shift_val: int = 17) -> str:
    stringlist: str = f"{string.ascii_letters}0123456789. "
    
    replacement_dict: dict[str, str] = {}
    for original, replaced in zip(stringlist, _stringshift(stringlist, shift_val)):
        replacement_dict[replaced] = original
    
    new_text: str = ""
    for char in text:
        new_char = replacement_dict.get(char)
        if new_char is None:
            new_text += char
        else:
            new_text += new_char
    return new_text