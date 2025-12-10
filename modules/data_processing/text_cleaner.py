import re

class VietnameseTextCleaner:
    def clean(self, text: str) -> str:
        """Clean Vietnamese text for embedding"""
        if not text:
            return ""

        # Remove citations [1], [2], [abc]
        text = re.sub(r'\[\w+\]', '', text)
        
        # Remove edit markers [sửa | sửa mã nguồn] (if any slipped through)
        text = re.sub(r'\[\s*sửa\s*\|\s*sửa mã nguồn\s*\]', '', text)

        # Normalize whitespace (replace multiple spaces/newlines with single space)
        # We might want to keep paragraph breaks, but for embedding chunks, 
        # usually single stream of text is easier unless we chunk by paragraph.
        # Let's keep paragraph breaks as single newlines for now, and multi-spaces as single.
        
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                # Remove extra spaces inside line
                line = re.sub(r'\s+', ' ', line)
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
