def in_ascii_bounds( char ):
    char = ord(char)

    if   (char >= ord('0') and char <= ord('9')):
        return True
    elif (char >= ord('A') and char <= ord('Z')):
        return True
    elif (char >= ord('a') and char <= ord('z')):
        return True
        
    return False

def urlify( string, replacement=True):
    new_string = ""
    
    for char in string:

        if in_ascii_bounds(char):
            new_string += char
        else:
            char_num = '{:02x}'.format(ord(char)).upper()
            if replacement:
                new_string += f"%%{char_num}"
            else:
                new_string += f"%{char_num}"
                

    return new_string