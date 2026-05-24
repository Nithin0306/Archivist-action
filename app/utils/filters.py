import re

def filter_junk_files(diff_text: str) -> str:
    # Removes changes to lockfiles, images, and other noisy files from the diff
    
    junk_patterns = [
        r'\.lock$', r'-lock\.json$', r'\.svg$', r'\.png$', r'\.css$', r'\.min\.js$'
    ]
    
    filtered_diff = []
    skip_current_file = False
    
    for line in diff_text.split('\n'):

        if line.startswith('diff --git'):
            skip_current_file = False

            if any(re.search(pattern, line) for pattern in junk_patterns):
                skip_current_file = True
                
        if not skip_current_file:
            filtered_diff.append(line)
            
    return '\n'.join(filtered_diff)