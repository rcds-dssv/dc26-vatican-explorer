# Module to implement biblical citation search

######################################### IMPORT LIBRARIES #########################################
import re

######################################### DEFINE FUNCTIONS #########################################

def search_biblical_citations(text, context=100, pattern=None):
    """
    Function to search for biblical citations in a given text.

    Inputs:
        text (str): The input text to search for biblical citations.
        context (int, optional): The number of characters to include before and after the citation for context.
        pattern (str, optional): The regex pattern to use for searching. If None, a default pattern is used.    
    Outputs:
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
        # TODO: check regex to make sure it's not overkill
        pattern = r'\b(?:[1-3]\s)?[A-Za-z]{2,4}\s\d{1,3}:\d{1,3}(?:[-.]\d{1,3})?(?:[.,;]?\d{1,3})*\b'
    
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

if __name__ == "__main__":

    ######## TESTS ########

    print("Starting biblical citation search tests...")

    # Test 1
    print(f"Running test 1...")
    test_string_1 = 'It was her interpretation of the supreme statement of the New Testament: “God is love” (1 Jn 4:8.16).'
    test_result_1 = search_biblical_citations(test_string_1)
    print(f"Test 1 Result: {test_result_1}")
    assert test_result_1[0][0] == '1 Jn 4:8.16', "Test 1 Failed"

    # Test 2
    print(f"Running test 2...")
    test_string_2 = "There, from his open side, he gave birth to the Church, his beloved bride, for which he gave his life (cf. Eph 5:25)."
    test_result_2 = search_biblical_citations(test_string_2)
    print(f"Test 2 Result: {test_result_2}")
    assert test_result_2[0][0] == 'Eph 5:25', "Test 2 Failed"

    # Test 3
    print(f"Running test 3...")
    test_string_3 = "She felt herself a sister to atheists, seated with them at table, like Jesus who sat with sinners (cf. Mt 9:10-13)."
    test_result_3 = search_biblical_citations(test_string_3)
    print(f"Test 3 Result: {test_result_3}")
    assert test_result_3[0][0] == 'Mt 9:10-13', "Test 3 Failed"

    # Test 4
    print(f"Running test 4...")
    test_string_4 = "Therese was conscious of the tragic reality of sin, yet she remained constantly immersed in the mystery of Christ, certain that “where sin increased, grace abounded all the more” ( Rom 5:20)."
    test_result_4 = search_biblical_citations(test_string_4)
    print(f"Test 4 Result: {test_result_4}")
    assert test_result_4[0][0] == 'Rom 5:20', "Test 4 Failed"
    
    # Test 5 
    print(f"Running test 5...")
    test_string_5 = 'As “greater” than faith and hope, charity will never pass away (cf. 1 Cor 13:8-13). It is the supreme gift of the Holy Spirit and “the mother and the root of all the virtues”.'
    test_result_5 = search_biblical_citations(test_string_5)
    print(f"Test 5 Result: {test_result_5}")
    assert test_result_5[0][0] == '1 Cor 13:8-13', "Test 5 Failed"

    # TODO: add tests with none citations and with more than one citation

    print("All tests passed successfully!")