# Testing AI Applications

## Testing Levels

### Level 1: Unit Tests (SDK Integration)

Test that your code correctly calls the AI API and handles responses.

```typescript
// Mock the SDK client
import { vi, describe, it, expect } from "vitest";

const mockCreate = vi.fn();
vi.mock("@anthropic-ai/sdk", () => ({
  default: class {
    messages = { create: mockCreate };
  },
}));

describe("summarize", () => {
  it("sends correct prompt and returns text", async () => {
    mockCreate.mockResolvedValue({
      content: [{ type: "text", text: "Summary here" }],
      usage: { input_tokens: 100, output_tokens: 50 },
    });

    const result = await summarize("Long article text...");

    expect(mockCreate).toHaveBeenCalledWith(
      expect.objectContaining({
        model: "claude-sonnet-4-6",
        messages: expect.arrayContaining([
          expect.objectContaining({ role: "user" }),
        ]),
      })
    );
    expect(result).toBe("Summary here");
  });

  it("handles API errors gracefully", async () => {
    mockCreate.mockRejectedValue(new Error("Rate limited"));
    await expect(summarize("text")).rejects.toThrow("Rate limited");
  });
});
```

### Level 2: Integration Tests (Real API)

Test against the real API with controlled inputs. Use Haiku for speed and cost.

```typescript
describe("integration", () => {
  it("classifies sentiment correctly", async () => {
    const result = await classifySentiment("I love this product!");
    expect(["positive", "very_positive"]).toContain(result.sentiment);
  });

  it("extracts structured data", async () => {
    const result = await extractContact("John Doe, john@example.com");
    expect(result).toMatchObject({
      name: expect.stringContaining("John"),
      email: "john@example.com",
    });
  });
});
```

**Tips:**
- Use `claude-haiku-4-5-20251001` for integration tests (fast, cheap)
- Set `temperature: 0` for deterministic output
- Use `toContain` / `toMatchObject` for fuzzy matching (AI output varies slightly)
- Keep a test budget — integration tests cost real tokens

### Level 3: Eval Tests (Quality Measurement)

Measure the quality of AI outputs over a test dataset.

```typescript
interface EvalCase {
  input: string;
  expectedOutput: string;
  criteria: string[];
}

const evalCases: EvalCase[] = [
  {
    input: "Summarize: The quick brown fox jumps over the lazy dog.",
    expectedOutput: "A fox jumps over a dog.",
    criteria: ["mentions fox", "mentions dog", "is concise"],
  },
];

// Run evals and track pass rates
for (const testCase of evalCases) {
  const result = await summarize(testCase.input);
  const scores = testCase.criteria.map((criterion) =>
    checkCriterion(result, criterion)
  );
  console.log(`Pass rate: ${scores.filter(Boolean).length}/${scores.length}`);
}
```

**Eval frameworks:**
- **Braintrust** — Full eval platform with tracing
- **Promptfoo** — Open-source prompt testing
- **Custom** — Simple script with test cases and assertions

### Level 4: Regression Tests

Track output quality over time as you change prompts or models.

```typescript
// Save baseline outputs
const baseline = JSON.parse(fs.readFileSync("baseline.json", "utf-8"));

// Run current version
const current = await runAllCases(testCases);

// Compare
for (const [key, expected] of Object.entries(baseline)) {
  const actual = current[key];
  const similarity = computeSimilarity(expected, actual);
  if (similarity < 0.8) {
    console.warn(`Regression detected for ${key}: ${similarity}`);
  }
}
```

## Testing MCP Tools

```typescript
describe("search_products tool", () => {
  it("returns matching products", async () => {
    const result = await callTool("search_products", { query: "hair oil" });
    const data = JSON.parse(result.content[0].text);
    expect(data.length).toBeGreaterThan(0);
    expect(data[0]).toHaveProperty("name");
    expect(data[0]).toHaveProperty("price");
  });

  it("handles empty results", async () => {
    const result = await callTool("search_products", { query: "xyz_nonexistent_123" });
    const data = JSON.parse(result.content[0].text);
    expect(data.length).toBe(0);
  });

  it("validates input parameters", async () => {
    const result = await callTool("search_products", { limit: -1 });
    expect(result.isError).toBe(true);
  });
});
```

## Testing Prompts

### A/B Testing Prompts
Compare two prompt versions on the same test set:

```typescript
const promptA = "Summarize the following text concisely:";
const promptB = "Write a 1-2 sentence summary capturing the key point:";

const results = await Promise.all(
  testCases.map(async (tc) => ({
    a: await runWithPrompt(promptA, tc.input),
    b: await runWithPrompt(promptB, tc.input),
    expected: tc.expected,
  }))
);

const scoreA = results.reduce((sum, r) => sum + score(r.a, r.expected), 0) / results.length;
const scoreB = results.reduce((sum, r) => sum + score(r.b, r.expected), 0) / results.length;

console.log(`Prompt A: ${scoreA.toFixed(2)}, Prompt B: ${scoreB.toFixed(2)}`);
```

## Common Testing Mistakes

1. **Exact string matching** — AI output varies; use fuzzy matching, semantic similarity, or criteria checks
2. **No test budget** — Integration tests cost tokens; track spend, use Haiku
3. **Testing happy path only** — Test error handling, edge cases, malformed input
4. **Ignoring latency** — Track response time alongside correctness
5. **No baseline** — Without a baseline, you can't detect regressions
6. **Mocking everything** — Some integration tests with real API are essential
