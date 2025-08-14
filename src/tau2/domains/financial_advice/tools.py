"""Toolkit for the airline reservation system."""

import os
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool
from tau2.domains.financial_advice.utils import PRODUCT_FILES, KNOWLEDGE_BASE_PATH, load_product_file_contents
from openai import OpenAI

def product_files_as_str(product_file_contents: list[str]) -> str:
    s = ""
    for i, file_content in enumerate(product_file_contents):
        s += f"""
Document {i+1}:
```markdown
{file_content}
```
"""
    return s


product_file_contents = load_product_file_contents(KNOWLEDGE_BASE_PATH, PRODUCT_FILES)
product_files_str = product_files_as_str(product_file_contents)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class FinancialAdviceTools(ToolKitBase):  # Tools
    """All the tools for the financial advice domain."""

    def __init__(self) -> None:
        super().__init__()

    def _get_product(self, query: str) -> str:
        """
        Lookup product information from the Lloyds Bank website on the topic of the query.

        Args:
            query: The query to get the product details.

        Returns:
            A string that contains the product details.
        """

        documents = f"""
Here is the set of documents that you can use to provide your guidance:
{product_files_str}
        """
        instructions = f"""
You are an assistant to a finaicial advisor for Lloyds Bank customers.
Your goal is to retrieve guidance i.e. accurate and cited information about financial products and related topics for Lloyds bank, that is:
- relevant to the advisor's query
- fair, clear, not-misleading in order to be compliant with FCA regulations (COBS)
- sourced ONLY from the set of documents provided to you below.

Process to follow:
- In order to retrieve any and all of the relevant information accurately, go through each of the documents provided below, understanding their topic and content and then carefully retrieve all the information that may be useful to respond to the advisor.
- You should only provide fair, clear and not-misleading factual information, making sure that any key details are verbatim from the source documents.
- You must always cite the URL from the source documents you use in your response.
- Always provide your best guess of cited relevant information in your response, don't respond back with a question or a comment.
        """
        messages = [
            {"role": "system", "content": instructions},
            {"role": "developer", "content": documents},
            {"role": "user", "content": query},
        ]
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(model="gpt-4o", input=messages)
        return response.output[0].content[-1].text

    @is_tool(ToolType.READ)
    def get_product_details(self, query: str) -> str:
        """
        Lookup product information from the Lloyds Bank website on the topic of the query.

        Args:
            query: The query to get the product details.

        Returns:
            A string that contains the product details.
        """
        return self._get_product(query)


if __name__ == "__main__":
    financial_advice = FinancialAdviceTools()
    print(financial_advice.get_statistics())
