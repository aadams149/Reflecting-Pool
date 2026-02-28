#!/usr/bin/env python3
"""
Journal RAG System
Semantic search and Q&A over journal entries using local embeddings and LLM
"""

import json
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class JournalRAG:
    """RAG system for semantic search over journal entries"""
    
    def __init__(self, db_path: str = "./vector_db", 
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG system
        
        Args:
            db_path: Path to ChromaDB storage
            embedding_model: sentence-transformers model to use
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True, parents=True)
        
        print(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="journal_entries",
            metadata={"description": "Personal journal entries"}
        )
        
        print("RAG system initialized")
        print(f"  Database: {self.db_path}")
        print(f"  Entries in database: {self.collection.count()}")
    
    def ingest_from_ocr(self, ocr_output_dir: str, chunk_size: int = 500,
                       overlap: int = 50) -> int:
        """
        Ingest OCR'd journal entries into vector database
        
        Args:
            ocr_output_dir: Path to OCR output directory
            chunk_size: Characters per chunk (for long entries)
            overlap: Character overlap between chunks
            
        Returns:
            Number of entries ingested
        """
        ocr_path = Path(ocr_output_dir)
        text_dir = ocr_path / "text"
        metadata_dir = ocr_path / "metadata"
        
        if not text_dir.exists() or not metadata_dir.exists():
            raise FileNotFoundError(
                f"OCR output directory not found or incomplete: {ocr_output_dir}"
            )
        
        print(f"\nIngesting journal entries from {ocr_output_dir}")
        
        text_files = sorted(text_dir.glob("*.txt"))
        if not text_files:
            print("No text files found to ingest")
            return 0
        
        ingested = 0
        for text_file in text_files:
            metadata_file = metadata_dir / f"{text_file.stem}.json"
            
            if not metadata_file.exists():
                print(f"  Skipping {text_file.name} - no metadata found")
                continue
            
            # Load text and metadata
            with open(text_file, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            if not text:
                print(f"  Skipping {text_file.name} - empty text")
                continue
            
            # Chunk text if it's long
            chunks = self._chunk_text(text, chunk_size, overlap)
            
            # Add each chunk to database
            for i, chunk in enumerate(chunks):
                doc_id = f"{metadata['entry_date']}_chunk_{i}"
                
                # Check if already exists
                existing = self.collection.get(ids=[doc_id])
                if existing['ids']:
                    continue  # Skip duplicates
                
                # Create metadata for this chunk
                chunk_metadata = {
                    "date": metadata['entry_date'],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "word_count": metadata['word_count'],
                    "source_file": str(text_file.absolute())
                }
                
                # Add to collection
                self.collection.add(
                    ids=[doc_id],
                    documents=[chunk],
                    metadatas=[chunk_metadata]
                )
            
            ingested += 1
            print(f"  {text_file.name} ({len(chunks)} chunks)")
        
        print(f"\nIngested {ingested} entries")
        print(f"  Total documents in database: {self.collection.count()}")
        
        return ingested
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Character overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending (., !, ?) near the chunk boundary
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?' and i + 1 < len(text) and text[i + 1].isspace():
                        end = i + 1
                        break
            
            chunks.append(text[start:end].strip())
            start = end - overlap
        
        return chunks
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Semantic search over journal entries
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of search results with text and metadata
        """
        if self.collection.count() == 0:
            print("Database is empty. Ingest entries first with --ingest")
            return []
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'date': results['metadatas'][0][i]['date'],
                'text': results['documents'][0][i],
                'chunk_index': results['metadatas'][0][i]['chunk_index'],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
    
    def search_by_date_range(self, start_date: str, end_date: str,
                            query: Optional[str] = None, n_results: int = 10) -> List[Dict]:
        """
        Search entries within a date range, optionally with semantic query
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            query: Optional semantic search query
            n_results: Number of results
            
        Returns:
            List of matching entries
        """
        where_filter = {
            "$and": [
                {"date": {"$gte": start_date}},
                {"date": {"$lte": end_date}}
            ]
        }
        
        if query:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
        else:
            results = self.collection.get(
                where=where_filter,
                limit=n_results
            )
        
        # Format results
        formatted_results = []
        ids_list = results['ids'][0] if query else results['ids']
        docs_list = results['documents'][0] if query else results['documents']
        meta_list = results['metadatas'][0] if query else results['metadatas']
        
        for i in range(len(ids_list)):
            formatted_results.append({
                'date': meta_list[i]['date'],
                'text': docs_list[i],
                'chunk_index': meta_list[i]['chunk_index']
            })
        
        return formatted_results
    
    def get_all_dates(self) -> List[str]:
        """Get all unique dates in the database"""
        all_entries = self.collection.get()
        dates = set()
        for metadata in all_entries['metadatas']:
            dates.add(metadata['date'])
        return sorted(list(dates))
    
    def backup(self, reason: str = "manual") -> Path:
        """Create a timestamped backup of the vector database.

        Args:
            reason: Label for the backup (e.g., 'pre-delete', 'pre-clear')

        Returns:
            Path to the backup directory
        """
        backup_dir = self.db_path.parent / "vector_db_backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}_{reason}"

        shutil.copytree(self.db_path, backup_path)
        print(f"Backup created: {backup_path}")

        # Keep only the 5 most recent backups
        all_backups = sorted(
            [p for p in backup_dir.iterdir() if p.is_dir()],
            key=lambda p: p.stat().st_mtime,
        )
        while len(all_backups) > 5:
            oldest = all_backups.pop(0)
            shutil.rmtree(oldest)
            print(f"  Removed old backup: {oldest.name}")

        return backup_path

    def list_backups(self) -> list:
        """List available backups with metadata."""
        backup_dir = self.db_path.parent / "vector_db_backups"
        if not backup_dir.exists():
            return []

        backups = []
        for p in sorted(backup_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if p.is_dir() and p.name.startswith("backup_"):
                size_bytes = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
                backups.append({
                    "path": str(p),
                    "name": p.name,
                    "size_mb": round(size_bytes / (1024 * 1024), 1),
                    "created": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                })
        return backups

    def restore(self, backup_path: str) -> bool:
        """Restore the vector database from a backup.

        Args:
            backup_path: Path to the backup directory

        Returns:
            True if restored successfully
        """
        backup = Path(backup_path)
        if not backup.is_dir():
            print(f"Backup not found: {backup_path}")
            return False

        # Remove current DB
        if self.db_path.exists():
            shutil.rmtree(self.db_path)

        # Copy backup to DB path
        shutil.copytree(backup, self.db_path)

        # Reinitialize client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="journal_entries",
            metadata={"description": "Personal journal entries"}
        )

        print(f"Restored from backup: {backup_path}")
        print(f"  Entries in database: {self.collection.count()}")
        return True

    def delete_entry_by_date(self, date: str) -> int:
        """
        Delete all chunks from a specific date

        Args:
            date: Date to delete (YYYY-MM-DD format)

        Returns:
            Number of chunks deleted
        """
        self.backup(reason="pre-delete")
        # Get all IDs for this date
        results = self.collection.get(
            where={"date": date}
        )
        
        if not results['ids']:
            print(f"No entries found for date: {date}")
            return 0
        
        # Delete all chunks for this date
        self.collection.delete(ids=results['ids'])
        
        deleted_count = len(results['ids'])
        print(f"Deleted {deleted_count} chunks from {date}")
        
        return deleted_count
    
    def delete_entry_by_id(self, entry_id: str) -> bool:
        """
        Delete a specific entry by ID (deletes all its chunks)

        Args:
            entry_id: Entry ID prefix (e.g., "2026-01-31")

        Returns:
            True if deleted, False if not found
        """
        self.backup(reason="pre-delete")
        # Get all chunks that start with this ID
        all_entries = self.collection.get()
        matching_ids = [id for id in all_entries['ids'] if id.startswith(entry_id)]
        
        if not matching_ids:
            print(f"No entry found with ID: {entry_id}")
            return False
        
        # Delete all matching chunks
        self.collection.delete(ids=matching_ids)
        
        print(f"Deleted {len(matching_ids)} chunks for entry: {entry_id}")
        return True
    
    def clear_all_entries(self) -> int:
        """
        Delete ALL entries from the database
        WARNING: This cannot be undone!
        
        Returns:
            Number of entries deleted
        """
        # Get all IDs
        all_entries = self.collection.get()
        total = len(all_entries['ids'])
        
        if total == 0:
            print("Database is already empty")
            return 0

        self.backup(reason="pre-clear")

        # Delete everything
        self.collection.delete(ids=all_entries['ids'])
        
        print(f"Deleted all {total} entries from database")
        return total
    
    def list_all_entries(self) -> List[Dict]:
        """
        List all entries in the database
        
        Returns:
            List of entries with dates and IDs
        """
        all_entries = self.collection.get()
        
        # Group by date
        entries_by_date = {}
        for i, entry_id in enumerate(all_entries['ids']):
            date = all_entries['metadatas'][i]['date']
            if date not in entries_by_date:
                entries_by_date[date] = {
                    'date': date,
                    'chunks': 0,
                    'word_count': all_entries['metadatas'][i].get('word_count', 0)
                }
            entries_by_date[date]['chunks'] += 1
        
        return sorted(entries_by_date.values(), key=lambda x: x['date'])
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        all_entries = self.collection.get()
        
        dates = []
        total_words = 0
        
        for metadata in all_entries['metadatas']:
            dates.append(metadata['date'])
            if 'word_count' in metadata:
                total_words += metadata['word_count']
        
        unique_dates = sorted(set(dates))
        
        return {
            'total_entries': len(unique_dates),
            'total_chunks': len(all_entries['ids']),
            'total_words': total_words,
            'date_range': {
                'first': unique_dates[0] if unique_dates else None,
                'last': unique_dates[-1] if unique_dates else None
            }
        }


class OllamaLLM:
    """Interface to local Ollama LLM for Q&A"""
    
    def __init__(self, model: str = "llama3.3"):
        """
        Initialize Ollama LLM
        
        Args:
            model: Ollama model name (e.g., 'llama3.3', 'mistral')
        """
        self.model = model
        
        # Check if Ollama is available
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                raise ConnectionError("Ollama not responding")
            
            # Check if model is available
            models = response.json().get('models', [])
            model_names = [m['name'].split(':')[0] for m in models]
            
            if model not in model_names:
                available = ', '.join(model_names) if model_names else 'none'
                raise ValueError(
                    f"Model '{model}' not found. Available: {available}. "
                    f"Install with: ollama pull {model}"
                )

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Could not connect to Ollama. "
                "Make sure it is installed (https://ollama.ai) and running (ollama serve)."
            )
    
    def generate(self, prompt: str, context: List[str]) -> str:
        """
        Generate answer using context from journal entries
        
        Args:
            prompt: User's question
            context: Relevant journal excerpts
            
        Returns:
            Generated answer
        """
        import requests
        
        # Build prompt with context
        context_str = "\n\n".join([f"Journal Entry:\n{c}" for c in context])
        
        full_prompt = f"""Based on the following journal entries, please answer the question.

{context_str}

Question: {prompt}

Answer based only on the journal entries provided above. If the entries don't contain enough information to answer, say so."""
        
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
        
        return response.json()['response']


def interactive_search(rag: JournalRAG, use_llm: bool = False, llm_model: str = "llama3.3"):
    """
    Interactive search interface
    
    Args:
        rag: JournalRAG instance
        use_llm: Whether to use LLM for Q&A
        llm_model: Ollama model to use
    """
    llm = None
    if use_llm:
        try:
            llm = OllamaLLM(model=llm_model)
        except Exception:
            print("Continuing without LLM Q&A...")
            use_llm = False
    
    print("\n" + "="*60)
    print("Journal Search Interface")
    print("="*60)
    
    stats = rag.get_stats()
    print(f"\nDatabase Stats:")
    print(f"  Entries: {stats['total_entries']}")
    print(f"  Date Range: {stats['date_range']['first']} to {stats['date_range']['last']}")
    print(f"  Total Words: {stats['total_words']:,}")
    
    print("\nCommands:")
    print("  search <query>        - Semantic search")
    print("  dates                 - List all entry dates")
    print("  list                  - List all entries")
    print("  stats                 - Show database statistics")
    print("  range <start> <end>   - Search date range (YYYY-MM-DD)")
    print("  delete <date>         - Delete entry by date (YYYY-MM-DD)")
    print("  clear                 - Delete ALL entries (use with caution!)")
    print("  quit / exit           - Exit")
    
    if use_llm:
        print("  ask <question>        - Ask a question (uses LLM)")
    
    print()
    
    while True:
        try:
            user_input = input("🔍 > ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            
            if command == 'search' and len(parts) > 1:
                query = parts[1]
                results = rag.search(query, n_results=5)
                
                if not results:
                    print("No results found")
                    continue
                
                print(f"\nFound {len(results)} results:\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. [{result['date']}]")
                    print(f"   {result['text'][:200]}...")
                    print()
            
            elif command == 'ask' and len(parts) > 1 and use_llm:
                question = parts[1]
                # Get relevant context
                results = rag.search(question, n_results=3)
                context = [r['text'] for r in results]
                
                print("\nThinking...\n")
                answer = llm.generate(question, context)
                print(f"{answer}\n")
            
            elif command == 'dates':
                dates = rag.get_all_dates()
                print(f"\n{len(dates)} entry dates:")
                for date in dates:
                    print(f"  - {date}")
                print()
            
            elif command == 'list':
                entries = rag.list_all_entries()
                print(f"\nAll entries in database:\n")
                for entry in entries:
                    print(f"  {entry['date']} - {entry['chunks']} chunks, ~{entry['word_count']} words")
                print()
            
            elif command == 'delete' and len(parts) > 1:
                date_to_delete = parts[1]
                confirm = input(f"Delete all entries from {date_to_delete}? (yes/no): ")
                if confirm.lower() in ['yes', 'y']:
                    rag.delete_entry_by_date(date_to_delete)
                else:
                    print("Cancelled")
                print()
            
            elif command == 'clear':
                confirm = input("WARNING: Delete ALL entries? This cannot be undone! (type 'DELETE ALL' to confirm): ")
                if confirm == 'DELETE ALL':
                    rag.clear_all_entries()
                else:
                    print("Cancelled")
                print()
            
            elif command == 'stats':
                stats = rag.get_stats()
                print(f"\nDatabase Statistics:")
                print(f"  Total Entries: {stats['total_entries']}")
                print(f"  Total Chunks: {stats['total_chunks']}")
                print(f"  Total Words: {stats['total_words']:,}")
                print(f"  First Entry: {stats['date_range']['first']}")
                print(f"  Last Entry: {stats['date_range']['last']}")
                print()
            
            elif command == 'range' and len(parts) > 1:
                dates = parts[1].split()
                if len(dates) < 2:
                    print("Usage: range <start_date> <end_date>")
                    continue
                
                results = rag.search_by_date_range(dates[0], dates[1], n_results=10)
                print(f"\nFound {len(results)} entries in date range:\n")
                for result in results:
                    print(f"[{result['date']}]")
                    print(f"{result['text'][:200]}...")
                    print()
            
            else:
                print("Unknown command. Type 'quit' to exit.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="RAG system for semantic search over journal entries"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest OCR output into database')
    ingest_parser.add_argument('ocr_output', help='Path to OCR output directory')
    ingest_parser.add_argument('--db', default='./vector_db', help='Database path')
    ingest_parser.add_argument('--chunk-size', type=int, default=500, help='Chunk size')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search journal entries')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--db', default='./vector_db', help='Database path')
    search_parser.add_argument('-n', type=int, default=5, help='Number of results')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Interactive search interface')
    interactive_parser.add_argument('--db', default='./vector_db', help='Database path')
    interactive_parser.add_argument('--llm', action='store_true', help='Enable LLM Q&A')
    interactive_parser.add_argument('--model', default='llama3.3', help='Ollama model')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    stats_parser.add_argument('--db', default='./vector_db', help='Database path')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all entries in database')
    list_parser.add_argument('--db', default='./vector_db', help='Database path')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete entry by date')
    delete_parser.add_argument('date', help='Date to delete (YYYY-MM-DD)')
    delete_parser.add_argument('--db', default='./vector_db', help='Database path')
    delete_parser.add_argument('--yes', action='store_true', help='Skip confirmation')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Delete ALL entries (use with caution!)')
    clear_parser.add_argument('--db', default='./vector_db', help='Database path')
    clear_parser.add_argument('--yes', action='store_true', help='Skip confirmation')

    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a manual backup')
    backup_parser.add_argument('--db', default='./vector_db', help='Database path')

    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from a backup')
    restore_parser.add_argument('backup_path', help='Path to backup directory')
    restore_parser.add_argument('--db', default='./vector_db', help='Database path')

    # List backups command
    backups_parser = subparsers.add_parser('backups', help='List available backups')
    backups_parser.add_argument('--db', default='./vector_db', help='Database path')

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize RAG system
    rag = JournalRAG(db_path=args.db)
    
    if args.command == 'ingest':
        rag.ingest_from_ocr(args.ocr_output, chunk_size=args.chunk_size)
    
    elif args.command == 'search':
        results = rag.search(args.query, n_results=args.n)
        
        if not results:
            print("No results found")
            return 0
        
        print(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result['date']}]")
            print(f"   {result['text'][:300]}...")
            print()
    
    elif args.command == 'interactive':
        interactive_search(rag, use_llm=args.llm, llm_model=args.model)
    
    elif args.command == 'stats':
        stats = rag.get_stats()
        print("\nDatabase Statistics:")
        print(f"  Total Entries: {stats['total_entries']}")
        print(f"  Total Chunks: {stats['total_chunks']}")
        print(f"  Total Words: {stats['total_words']:,}")
        if stats['date_range']['first']:
            print(f"  Date Range: {stats['date_range']['first']} to {stats['date_range']['last']}")
        print()
    
    elif args.command == 'list':
        entries = rag.list_all_entries()
        print(f"\nAll entries in database:\n")
        for entry in entries:
            print(f"  {entry['date']} - {entry['chunks']} chunks, ~{entry['word_count']} words")
        print(f"\nTotal: {len(entries)} entries\n")
    
    elif args.command == 'delete':
        if not args.yes:
            confirm = input(f"Delete all entries from {args.date}? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                print("Cancelled")
                return 0
        
        rag.delete_entry_by_date(args.date)
    
    elif args.command == 'clear':
        if not args.yes:
            confirm = input("WARNING: Delete ALL entries? This cannot be undone! (type 'DELETE ALL' to confirm): ")
            if confirm != 'DELETE ALL':
                print("Cancelled")
                return 0
        
        rag.clear_all_entries()

    elif args.command == 'backup':
        backup_path = rag.backup(reason="manual")
        print(f"\nBackup saved to: {backup_path}")

    elif args.command == 'restore':
        if rag.restore(args.backup_path):
            print("\nDatabase restored successfully")
        else:
            print("\nRestore failed")
            return 1

    elif args.command == 'backups':
        backups = rag.list_backups()
        if not backups:
            print("\nNo backups found")
        else:
            print(f"\nAvailable backups ({len(backups)}):\n")
            for b in backups:
                print(f"  {b['name']}  ({b['size_mb']} MB)  {b['created']}")
                print(f"    {b['path']}")
            print()

    return 0


if __name__ == "__main__":
    exit(main())
