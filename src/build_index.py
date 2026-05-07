"""
build_index.py

This file builds the searchable Wikipedia index for the CSC 483 Watson-style
Jeopardy question answering project.

The Wikipedia collection is stored as large text files, where each file contains
many Wikipedia pages. Each page begins with a title line formatted like:

    [[British Standards]]

This program:
    1. Reads each valid Wikipedia data file from data/wiki/
    2. Splits the file into individual Wikipedia pages using the [[Title]] marker
    3. Creates a Whoosh search index
    4. Adds each Wikipedia page as a separate document in the index
    5. Stores the page title so it can be returned as the predicted answer

The final index is written to the index/ directory and is later used by the
evaluation program to retrieve the most likely Wikipedia page for each Jeopardy clue.
"""

import os
import shutil
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from whoosh.analysis import StemmingAnalyzer


# Folder containing the extracted Wikipedia files
WIKI_DIR = "data/wiki"

# Folder where Whoosh will store the search index
INDEX_DIR = "index"


def is_valid_wiki_file(filename):
    """
    Returns True if this is a real Wikipedia data file.

    Real files look like:
        enwiki-20140602-pages-articles.xml-0052

    Junk files may look like:
        ._enwiki-20140602-pages-articles.xml-0052
        .DS_Store
    """

    # Skip hidden files and macOS metadata files
    if filename.startswith("."):
        return False

    # Only use the actual Wikipedia subset files
    if not filename.startswith("enwiki-"):
        return False

    return True


def is_title_line(line):
    """
    A Wikipedia page starts with a title line like:
        [[British Standards]]
    """
    return line.startswith("[[") and line.endswith("]]")


def clean_title(line):
    """
    Converts:
        [[British Standards]]

    into:
        British Standards
    """
    return line[2:-2].strip()


def parse_wiki_file(filepath):
    """
    Reads one Wikipedia file and separates it into individual pages.

    Returns:
        A list of (title, text) tuples.
    """

    pages = []
    current_title = None
    current_text = []

    with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            line = line.strip()

            # A title line means a new Wikipedia page is starting
            if is_title_line(line):

                # Save the previous page before starting a new one
                if current_title is not None:
                    page_text = " ".join(current_text)
                    pages.append((current_title, page_text))

                current_title = clean_title(line)
                current_text = []

            else:
                # Only save text if we are currently inside a page
                if current_title is not None:
                    current_text.append(line)

    # Save the final page in the file
    if current_title is not None:
        page_text = " ".join(current_text)
        pages.append((current_title, page_text))

    return pages


def create_index_schema():
    """
    Defines what each document in the search index contains.

    title:
        Stored because this is what we return as the answer.

    content:
        Indexed for searching. It includes both the title and page text.
    """

    return Schema(
        title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        content=TEXT(stored=False, analyzer=StemmingAnalyzer())
    )


def reset_index_folder(index_dir):
    """
    Deletes any old index and creates a fresh index folder.
    """

    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)

    os.mkdir(index_dir)


def build_index(wiki_dir, index_dir):
    """
    Builds a Whoosh index over the Wikipedia collection.

    Each Wikipedia page becomes one separate document.
    """

    reset_index_folder(index_dir)

    schema = create_index_schema()
    index = create_in(index_dir, schema)
    writer = index.writer()

    total_files = 0
    total_pages = 0

    for filename in sorted(os.listdir(wiki_dir)):

        if not is_valid_wiki_file(filename):
            continue

        filepath = os.path.join(wiki_dir, filename)

        if not os.path.isfile(filepath):
            continue

        pages = parse_wiki_file(filepath)

        for title, text in pages:
            writer.add_document(
                title=title,

                # Add title into content too so title words can help retrieval
                content=title + " " + text
            )

        total_files += 1
        total_pages += len(pages)

        print(f"Indexed {filename}: {len(pages)} pages")

    writer.commit()

    print()
    print("Finished building index.")
    print(f"Files indexed: {total_files}")
    print(f"Total Wikipedia pages indexed: {total_pages}")


if __name__ == "__main__":
    build_index(WIKI_DIR, INDEX_DIR)