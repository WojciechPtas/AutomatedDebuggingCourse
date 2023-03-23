from exercise_1 import convert_to_rgb

hex_str_assertion_error = 'gggggg' # Should't be accepted
hex_str_functional_error = 'aaab00' # should equal 170,171,0 

if __name__ == '__main__':
    try:
        convert_to_rgb(hex_str_assertion_error)
    except AssertionError:
        print(f'{hex_str_assertion_error} triggered an AssertionError. Is this intended?')
    else:
        print(f'{hex_str_assertion_error} did not trigger an AssertionError. Is this intended?')
        
    print(f'{hex_str_functional_error} has the following rgb values: {convert_to_rgb(hex_str_functional_error)}. Is this correct?')
    