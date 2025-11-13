# Module to implement biblical citation search

######################################### IMPORT LIBRARIES #########################################
import re
from typing import List, Tuple, Optional

######################################### DEFINE FUNCTIONS #########################################

def search_biblical_citations(text: str, context: int=100, pattern: Optional[str] = None) -> List[Tuple[str, str]]:
    """Function to search for biblical citations in a given text.

    Args:
        text: The input text to search for biblical citations.
        context: The number of characters to include before and after the citation for context.
        pattern: The regex pattern to use for searching. If None, a default pattern is used.    
    
    Returns:
        list of tuples: Each tuple contains the found citation and its surrounding context.
    """
    # Check that the input text is a string
    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")
    
    # Check that context is an integer
    if not isinstance(context, int):
        raise ValueError("Context must be an integer.")
    
    # Check that pattern is a string if provided
    if pattern is not None and not isinstance(pattern, str):
        raise ValueError("Pattern must be a string.")
    
    # Default regex pattern for biblical citations if none provided
    if pattern is None:
        pattern = r'\b(?:[1-3]\s+)?[A-Za-z]{2,4}\s+\d{1,3}:\d{1,3}(?:[-.]\d{1,3})?\b'
    
    # Search for citations using regex
    matches = re.finditer(pattern, text)

    # Initialize results list
    results = []

    # Iterate over matches
    for match in matches:

        # Extract citation
        citation = match.group()

        # Get start and end indices of the match
        start, end = match.span()
        
        # Calculate context boundaries
        context_start = max(0, start - context)
        context_end = min(len(text), end + context)

        # Extract context
        surrounding_text = text[context_start:context_end]
        
        # Append citation and context to results
        results.append((citation, surrounding_text))

    # Return results
    return results