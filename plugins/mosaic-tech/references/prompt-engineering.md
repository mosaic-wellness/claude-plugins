# Prompt Engineering Reference

## System Prompt Design

### Structure
A good system prompt has these sections (in order):

1. **Identity** — Who the AI is
2. **Capabilities** — What it can and cannot do
3. **Rules** — Hard constraints (must/must not)
4. **Output format** — How to structure responses
5. **Examples** — Few-shot demonstrations (optional)

```
You are a customer support agent for [Brand].

## Capabilities
- Answer questions about products, orders, and shipping
- Look up order status using the get_order tool
- Escalate complex issues to human support

## Rules
- Never make up order information — always use the get_order tool
- Never share customer data from one customer with another
- If unsure, say "Let me connect you with a team member"
- Always be polite and professional

## Output Format
- Keep responses under 3 sentences unless the customer asks for detail
- Use bullet points for lists
- Include order numbers when referencing orders
```

### Anti-Patterns
- **Too vague:** "Be helpful" — doesn't guide behavior
- **Too restrictive:** 50 rules that conflict — model gets confused
- **Contradictory:** "Be concise" + "Always explain your reasoning in detail"
- **Dynamic content in system prompt:** User input interpolated here = injection risk

## Few-Shot Examples

For consistent output format, include 2-3 examples:

```
## Examples

User: What's the status of order #12345?
Assistant: Let me check that for you. [Uses get_order tool] Your order #12345 shipped on March 15 and is expected to arrive by March 20. The tracking number is ABC123.

User: Can I return my hair oil?
Assistant: Yes, we accept returns within 30 days of delivery. Would you like me to start a return for you? I'll need your order number.
```

**Tips:**
- Use realistic examples, not toy cases
- Show the exact format you want
- Include edge cases (errors, "I don't know" scenarios)
- 2-3 examples is usually enough; more can be counterproductive

## Structured Output

### JSON via System Prompt
```
Always respond with valid JSON matching this schema:
{
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": 0.0-1.0,
  "key_phrases": ["phrase1", "phrase2"]
}
```

### JSON via Tool Use (More Reliable)
Define a "respond" tool with strict schema — model will conform:

```typescript
const tools = [{
  name: "respond",
  description: "Provide your analysis in structured format",
  input_schema: {
    type: "object",
    properties: {
      sentiment: { type: "string", enum: ["positive", "negative", "neutral"] },
      confidence: { type: "number", minimum: 0, maximum: 1 },
      key_phrases: { type: "array", items: { type: "string" } }
    },
    required: ["sentiment", "confidence", "key_phrases"]
  }
}];
```

## Chain-of-Thought

For complex reasoning, ask the model to think step-by-step:

```
Analyze this code for security issues. Think through each potential vulnerability step by step before giving your final assessment.
```

Or use extended thinking (built into the API):
```typescript
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 16000,
  thinking: { type: "enabled", budget_tokens: 10000 },
  messages: [{ role: "user", content: "Complex reasoning task..." }],
});
```

## Task-Specific Patterns

### Classification
```
Classify the following customer message into exactly one category:
- ORDER_STATUS — asking about order tracking or delivery
- RETURN — wanting to return or exchange a product
- PRODUCT_QUESTION — asking about a product's features, ingredients, etc.
- COMPLAINT — expressing dissatisfaction
- OTHER — doesn't fit above categories

Respond with only the category name, nothing else.

Message: "{input}"
```

### Extraction
```
Extract the following fields from the text below. If a field is not present, use null.

Fields: name, email, phone, company

Text: "{input}"

Respond as JSON: {"name": "...", "email": "...", "phone": "...", "company": "..."}
```

### Summarization
```
Summarize the following text in 2-3 sentences. Focus on:
1. The main point or conclusion
2. Key supporting evidence
3. Any action items mentioned

Text: "{input}"
```

### Code Generation
```
Write a TypeScript function that {description}.

Requirements:
- Use named exports (no default exports)
- Include JSDoc comment
- Handle edge cases (null input, empty arrays, etc.)
- Return type should be explicit

Do not include tests or example usage — just the function.
```

## Prompt Optimization Tips

1. **Be specific about format** — "Respond in 2-3 sentences" beats "Be concise"
2. **Use XML tags for structure** — `<context>...</context>` helps separate sections
3. **Put instructions before content** — Model pays more attention to instructions at the top
4. **Use positive instructions** — "Always respond in English" beats "Don't respond in other languages"
5. **Test with edge cases** — Adversarial inputs, empty inputs, very long inputs
6. **Iterate on real failures** — When output is wrong, fix the prompt for that case, then re-test all cases
