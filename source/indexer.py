import os
import glob
from pathlib import Path
import hashlib
from typing import List, Dict, Any
import frontmatter
import markdown
from bs4 import BeautifulSoup

class NoteIndexer:
    def __init__(self, notes_directory: str = "."):
        self.notes_directory = notes_directory

    def find_markdown_files(self) -> List[str]:
        """Find all markdown files"""
        pattern = os.path.join(self.notes_directory, "**/*.md")
        return glob.glob(pattern, recursive=True)

    def extract_content(self, filepath: str) -> Dict[str, Any]:
        """Extract content from markdown file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter
        post = frontmatter.loads(content)
        metadata = post.metadata
        body = post.content

        # Extract plain text (remove markdown tags)
        html = markdown.markdown(body)
        soup = BeautifulSoup(html, 'html.parser')
        plain_text = soup.get_text()

        # Generate document ID
        file_hash = hashlib.md5(filepath.encode()).hexdigest()[:16]

        return {
            "id": f"{Path(filepath).stem}_{file_hash}",
            "filepath": filepath,
            "filename": Path(filepath).name,
            "title": metadata.get('title', Path(filepath).stem),
            "content": plain_text,
            "metadata": metadata,
            "full_content": content[:1000]  # Save partial original content for display
        }

    def chunk_document(self, document: Dict[str, Any], chunk_size: int = 500) -> List[Dict[str, Any]]:
        """Chunk the document"""
        content = document["content"]
        words = content.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)

            chunk_id = f"{document['id']}_chunk_{i//chunk_size}"

            chunks.append({
                "id": chunk_id,
                "document_id": document["id"],
                "content": chunk_text,
                "metadata": {
                    **document["metadata"],
                    "source": document["filepath"],
                    "title": document["title"],
                    "chunk_index": i // chunk_size
                }
            })

        return chunks

    def index_all_notes(self) -> List[Dict[str, Any]]:
        """Index all notes"""
        md_files = self.find_markdown_files()
        all_chunks = []

        print(f"Found {len(md_files)} markdown files")

        for filepath in md_files:
            try:
                document = self.extract_content(filepath)
                chunks = self.chunk_document(document)
                all_chunks.extend(chunks)
                print(f"✓ Processed: {document['title']} ({len(chunks)} chunks)")
            except Exception as e:
                print(f"✗ Failed to process {filepath}: {e}")

        return all_chunks
