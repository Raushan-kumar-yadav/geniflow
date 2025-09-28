from openai import OpenAI

client = OpenAI(
  api_key="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"
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message);
