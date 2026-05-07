# CSC 483 – Building Part of Watson

This project implements a simplified Watson-style Jeopardy question answering system using Python and the Whoosh IR library.

The system indexes approximately 280,000 Wikipedia pages and attempts to answer Jeopardy clues by retrieving the most relevant Wikipedia page title.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
