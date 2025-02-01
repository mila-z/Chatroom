HEADER_LENGTH = 10

def generate_header(message):
    """Generates a fixed-length header for a message."""
    return f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
