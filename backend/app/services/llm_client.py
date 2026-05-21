import os

from openai import OpenAI


DEEPSEEK_BASE_URL = "https://api.deepseek.com"


# call_deepseek 调用 DeepSeek API，发送构建好的提示词并获取生成结果
def call_deepseek(prompt: str) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not configured")

    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a travel planning assistant. "
                    "Return valid JSON only. Do not return Markdown."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("DeepSeek returned empty content")

    return content
