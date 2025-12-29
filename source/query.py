from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

class QueryProcessor:
    def __init__(self, chroma_db):
        self.chroma_db = chroma_db

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        results = self.chroma_db.query(query, n_results=n_results)

        formatted_results = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None
                })

        return formatted_results

    def display_results(self, results: List[Dict[str, Any]], query: str = None):
        """Display search results"""
        if query:
            console.print(Panel(f"[bold blue]Query:[/bold blue] {query}", border_style="blue"))

        if not results:
            console.print("[yellow]No relevant results found[/yellow]")
            return

        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            source = metadata.get("source", "Unknown")
            title = metadata.get("title", "Untitled")

            console.print(f"\n[bold cyan]{i}. {title}[/bold cyan]")
            console.print(f"[dim]Source: {source}[/dim]")

            if "distance" in result and result["distance"] is not None:
                console.print(f"[dim]Similarity: {1 - result['distance']:.3f}[/dim]")

            # Display content preview
            content = result["content"]
            if len(content) > 300:
                content = content[:300] + "..."

            console.print(Panel(content, border_style="green"))
