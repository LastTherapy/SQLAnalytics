import re

def tokenize_ddl(ddl_string):
    """
    Tokenizes a DDL string into logical parts.

    Args:
        ddl_string (str): The DDL string to tokenize.

    Returns:
        list: A list of tokens.
    """
    # Define a regular expression for matching tokens
    token_pattern = re.compile(r"""
        \s*(               # Allow leading spaces
            (".*?"|'.*?')    # Match quoted strings (single or double quotes)
            |\b\w+\b        # Match keywords or identifiers
            |\(              # Match opening parenthesis
            |\)              # Match closing parenthesis
            |,               # Match commas
            |=               # Match equal signs
            |\*              # Match asterisks
            |\;              # Match semicolons
            |\.              # Match dots
        )
    """, re.VERBOSE | re.IGNORECASE)

    # Find all matches in the DDL string
    tokens = token_pattern.findall(ddl_string)

    # Extract the matched groups and strip spaces
    return [token.strip() for token, *_ in tokens if token.strip()]

# Example usage
ddl_example = """
CREATE FUNCTION my_function(a INT, b VARCHAR)
RETURNS INT AS $$
BEGIN
  RETURN a + b;
END;
$$ LANGUAGE plpgsql;
"""

tokens = tokenize_ddl(ddl_example)
print(tokens)
