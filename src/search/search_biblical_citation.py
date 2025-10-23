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

    # Test 6
    print(f"Running test 6...")
    test_string_6 = """Charity in truth, to which Jesus Christ bore witness by his earthly life and especially by his death and resurrection, is the principal driving force behind the authentic development of every person and of all humanity. Love — caritas — is an extraordinary force which leads people to opt for courageous and generous engagement in the field of justice and peace. It is a force that has its origin in God, Eternal Love and Absolute Truth. Each person finds his good by adherence to God's plan for him, in order to realize it fully: in this plan, he finds his truth, and through adherence to this truth he becomes free (cf. Jn 8:32). To defend the truth, to articulate it with humility and conviction, and to bear witness to it in life are therefore exacting and indispensable forms of charity. Charity, in fact, “rejoices in the truth” (1 Cor 13:6). All people feel the interior impulse to love authentically: love and truth never abandon them completely, because these are the vocation planted by God in the heart and mind of every human person. The search for love and truth is purified and liberated by Jesus Christ from the impoverishment that our humanity brings to it, and he reveals to us in all its fullness the initiative of love and the plan for true life that God has prepared for us. In Christ, charity in truth becomes the Face of his Person, a vocation for us to love our brothers and sisters in the truth of his plan. Indeed, he himself is the Truth (cf. Jn 14:6)."""
    test_result_6 = search_biblical_citations(test_string_6)
    print(f"Test 6 Result: {test_result_6}")
    assert test_result_6[0][0] == 'Jn 8:32', "Test 6 a Failed"
    assert test_result_6[1][0] == '1 Cor 13:6', "Test 6 b Failed"
    assert test_result_6[2][0] == 'Jn 14:6', "Test 6 c Failed"

    # Test 7
    print(f"Running test 7...")
    test_string_7 = "No citations here."
    test_result_7 = search_biblical_citations(test_string_7)
    print(f"Test 7 Result: {test_result_7}")
    assert test_result_7 == [], "Test 7 Failed"

    # TODO: go through the Vatican's website to find more complex examples to test

    print("All tests passed successfully!")