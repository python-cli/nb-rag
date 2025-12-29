import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import os
from pathlib import Path

from .chroma_db import ChromaDBManager
from .indexer import NoteIndexer
from .query import QueryProcessor

console = Console()

@click.group()
@click.option('--notes-dir', default='.', help='Path to notes directory')
@click.option('--db-dir', default='./chroma_db', help='ChromaDB storage directory')
@click.pass_context
def cli(ctx, notes_dir, db_dir):
    """NB RAG System - Local Knowledge Base Retrieval"""
    ctx.ensure_object(dict)

    # test
    notes_dir = '~/Documents/nb'
    db_dir = '~/Documents/nb/.rag'

    ctx.obj['NOTES_DIR'] = os.path.expanduser(notes_dir)
    ctx.obj['DB_DIR'] = os.path.expanduser(db_dir)

    # Ensure directories exist
    os.makedirs(ctx.obj['NOTES_DIR'], exist_ok=True)
    os.makedirs(ctx.obj['DB_DIR'], exist_ok=True)

@cli.command()
@click.pass_context
def init(ctx):
    """Initialize the RAG system"""
    console.print("[bold green]Initializing NB RAG system...[/bold green]")

    db_manager = ChromaDBManager(ctx.obj['DB_DIR'])
    indexer = NoteIndexer(ctx.obj['NOTES_DIR'])

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Indexing notes...", total=None)

        # Index all notes
        chunks = indexer.index_all_notes()

        if not chunks:
            console.print("[yellow]No markdown notes found[/yellow]")
            return

        # Add to database
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [chunk["id"] for chunk in chunks]

        db_manager.add_documents(documents, metadatas, ids)

        progress.update(task, completed=True)

    console.print(f"[bold green]✓ Initialization complete! Indexed {len(chunks)} document chunks[/bold green]")
    console.print(f"[dim]Database location: {ctx.obj['DB_DIR']}[/dim]")

@cli.command()
@click.pass_context
def update(ctx):
    """Update index (incremental update)"""
    console.print("[bold green]Updating note index...[/bold green]")

    # Incremental update logic can be implemented here
    # For now, re-index all notes
    init.callback(ctx)

@cli.command()
@click.argument('query', nargs=-1, required=True)
@click.option('--limit', default=5, help='Number of results to return')
@click.pass_context
def query(ctx, query, limit):
    """Query notes"""
    query_text = " ".join(query)

    db_manager = ChromaDBManager(ctx.obj['DB_DIR'])
    processor = QueryProcessor(db_manager)

    console.print(f"[bold]Searching:[/bold] {query_text}\n")

    results = processor.search(query_text, n_results=limit)
    processor.display_results(results, query_text)

@cli.command()
@click.pass_context
def stats(ctx):
    """Display statistics"""
    db_manager = ChromaDBManager(ctx.obj['DB_DIR'])

    try:
        count = db_manager.get_stats()
        console.print(f"[bold green]Database statistics:[/bold green]")
        console.print(f"Document count: {count}")
        console.print(f"Database location: {ctx.obj['DB_DIR']}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please run 'nb rag init' to initialize the database first[/yellow]")

@cli.command()
@click.confirmation_option(prompt='Are you sure you want to reset the database?')
@click.pass_context
def reset(ctx):
    """Reset the database"""
    db_manager = ChromaDBManager(ctx.obj['DB_DIR'])
    db_manager.reset()
    console.print("[bold green]✓ Database has been reset[/bold green]")

def main():
    cli(obj={})

if __name__ == "__main__":
    main()
