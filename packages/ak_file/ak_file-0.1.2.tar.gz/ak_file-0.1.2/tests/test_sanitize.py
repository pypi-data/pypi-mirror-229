from ak_file.sanitizer import (sanitize, remove_blacklisted_characters, 
                                remove_chars_below_code_point)

def test_remove_blacklisted_characters():
    assert remove_blacklisted_characters("a\\b/c:d*e?f\"g<h>i|j\0k") == "abcdefghijk"

def test_remove_chars_below_code_point():
    assert remove_chars_below_code_point("abc\x1fdef", 32) == "abcdef"
    
def test_length():
    assert len(sanitize("gradsf"*250)) == 255
    assert len(sanitize("gra:d\\sf"*250)) == 255

def test_sanitize():
    # Test input containing all characters in blacklist
    assert sanitize("\\/:*?\"<>|\0") == "__"
    
    # Test input containing only characters with ASCII code below 32
    assert sanitize("abc\x1fdef") == "abcdef"
    
    # Test input containing a reserved word
    assert sanitize("PRN") == "__PRN"
    
    # Test input containing only spaces and periods
    assert sanitize(" .  . .") == "__"
    
    # Test input containing only periods
    assert sanitize("...") == "__"
    
    # Test input with filename length greater than 255
    assert sanitize("a" * 300) == "a" * 255
    
    assert sanitize("") == '__'