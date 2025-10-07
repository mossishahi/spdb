from typing import Optional, Dict, List
import json
from spdb.utils._keys import OPENAI_FINDER_MODEL, OPENAI_API_BASE, OPENAI_API_KEY
from openai import OpenAI

FIND_STUDY_PROMPT = """
Task:
Open the following URL exactly as provided (do not modify it in any way):
{url}

After loading the page, extract the following sections if they exist and return them as key–value pairs in a JSON object:

Required keys:
1. **abstract**
2. **summary**
3. **highlights**
Extraction rules (read carefully — they are mandatory):
1. Your highest priority is the **Abstract** section.
   - If an Abstract exists, return it as the value of **abstract** (string).
2. If there is no Abstract, look for a **Summary** section instead.
   - If a Summary exists, return it as the value of **summary** (string).
3. If there is neither an Abstract nor a Summary, return `null`.
4. If the found Abstract or Summary section contains no actual text (empty or blocked), return `null`.
5. Do **not** add any extra text, explanation, or commentary to your output.

Output format:
Return a single JSON object. Example:
{{
  "abstract": "Text of the abstract if found, otherwise null",
  "summary": "Text of the summary if found and no abstract exists, otherwise null",
  "highlights": "Text of the highlights if found, otherwise null"
}}
"""

def _llm_dataset_abstract(url: str):
    prompt = FIND_STUDY_PROMPT.format(url=url)
    return _openai_request(OPENAI_FINDER_MODEL, prompt)


def _openai_request(model: str, prompt: str) -> str:
    """
    Minimal OpenAI Chat Completions call via raw HTTP (kept here to avoid adding non-Selenium scraping libs).
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.responses.create(
        model='gpt-5',
        tools=[{"type": "web_search"}],
        input=[
            {
                "role": "system",
                "content": "You get a url and you are responsible for a web scraping task and then taking the requested information from the webpage."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    if response['abstract'] is not None:
        return response['abstract']
    elif response['summary'] is not None:
        return response['summary']
    elif response['highlights'] is not None:
        return response['highlights']
    else:
        return None