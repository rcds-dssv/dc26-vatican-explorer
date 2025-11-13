# Module with tests for search_biblical_citation.py

import pytest
from src.search.search_biblical_citation import search_biblical_citations

# TODO: go through the Vatican's website to find more complex examples to test--e.g.: https://www.vatican.va/content/francesco/en/angelus/2025/documents/20250302-angelus.html

#########################################
# SINGLE-CITATION TESTS
#########################################

@pytest.mark.parametrize(
    "text,expected",
    [
        (
            'It was her interpretation of the supreme statement of the New Testament: “God is love” (1 Jn 4:8.16).',
            ['1 Jn 4:8.16']
        ),
        (
            "There, from his open side, he gave birth to the Church, his beloved bride, for which he gave his life (cf. Eph 5:25).",
            ['Eph 5:25']
        ),
        (
            "She felt herself a sister to atheists, seated with them at table, like Jesus who sat with sinners (cf. Mt 9:10-13).",
            ['Mt 9:10-13']
        ),
        (
            "Therese was conscious of the tragic reality of sin, yet she remained constantly immersed in the mystery of Christ, certain that “where sin increased, grace abounded all the more” ( Rom 5:20).",
            ['Rom 5:20']
        ),
        (
            'As “greater” than faith and hope, charity will never pass away (cf. 1 Cor 13:8-13). It is the supreme gift of the Holy Spirit and “the mother and the root of all the virtues”.',
            ['1 Cor 13:8-13']
        ),
    ]
)
def test_single_citations(text, expected):
    """Test detection of individual biblical citations in single-citation examples."""
    result = search_biblical_citations(text)
    citations = [c[0] for c in result]
    assert citations == expected


#########################################
# MULTIPLE-CITATION TEST
#########################################

def test_multiple_citations():
    """Test detection of multiple biblical citations within a long passage."""
    text = """Charity in truth, to which Jesus Christ bore witness by his earthly life and especially by his death and resurrection, is the principal driving force behind the authentic development of every person and of all humanity. Love — caritas — is an extraordinary force which leads people to opt for courageous and generous engagement in the field of justice and peace. It is a force that has its origin in God, Eternal Love and Absolute Truth. Each person finds his good by adherence to God's plan for him, in order to realize it fully: in this plan, he finds his truth, and through adherence to this truth he becomes free (cf. Jn 8:32). To defend the truth, to articulate it with humility and conviction, and to bear witness to it in life are therefore exacting and indispensable forms of charity. Charity, in fact, “rejoices in the truth” (1 Cor 13:6). All people feel the interior impulse to love authentically: love and truth never abandon them completely, because these are the vocation planted by God in the heart and mind of every human person. The search for love and truth is purified and liberated by Jesus Christ from the impoverishment that our humanity brings to it, and he reveals to us in all its fullness the initiative of love and the plan for true life that God has prepared for us. In Christ, charity in truth becomes the Face of his Person, a vocation for us to love our brothers and sisters in the truth of his plan. Indeed, he himself is the Truth (cf. Jn 14:6)."""
    expected = ['Jn 8:32', '1 Cor 13:6', 'Jn 14:6']
    result = search_biblical_citations(text)
    citations = [c[0] for c in result]
    assert citations == expected


#########################################
# NO-CITATION TEST
#########################################

def test_no_citations():
    """Test that function returns empty list when no biblical citations are present."""
    text = "No citations here."
    expected = []
    result = search_biblical_citations(text)
    assert result == expected

#########################################
# TESTS WITH PATTERN AND CONTEXT
#########################################

def test_custom_pattern_and_context():
    """Test detection with a custom regex pattern and context length."""
    text = "This doesn't need to be a biblical citation 123."
    pattern = r'\d{3}'
    context = 5
    expected = [('123', 'tion 123.')]
    result = search_biblical_citations(text, context=context, pattern=pattern)
    assert result == expected