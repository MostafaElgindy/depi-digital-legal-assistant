import re



def clean_text_arabic(text):
    # Normalization
    text = re.sub(r'[أإآا]', 'ا', text)  # Normalize Arabic letters
    text = re.sub(r'[ى]', 'ي', text)
    text = re.sub(r'[ؤئ]', 'ء', text)
    text = re.sub(r'ة', 'ه', text)

    # Remove specified special characters
    special_characters = r'[!@#$%^&*()_ـ+\-={}\[\]:;"\'<>,.?/\\|`~]'
    text = re.sub(special_characters, '', text)  # Remove special characters
    
    # Remove non-Arabic characters except basic punctuation
    text = re.sub(r'[^\u0600-\u06FF0-9a-zA-Z\s]', '', text)  # Allow Arabic letters, English letters, digits, and spaces
    
    # Remove new lines and excess whitespace
    text = re.sub(r'[\r\n]+', ' ', text)  # Remove new lines
    # Replace multiple spaces with a single space and strip
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
