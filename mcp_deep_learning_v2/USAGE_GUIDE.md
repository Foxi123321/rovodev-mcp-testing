# Quick Start Guide - Deep Learning Intelligence v2

## ✅ System Status: OPERATIONAL

Your system is ready to rock! Both DeepSeek and Qwen models are available.

## How It Works

```
YOU → Ask Rex about code
  ↓
REX → Calls MCP tools to research
  ↓
MCP → DeepSeek + Qwen analyze in parallel
  ↓
MCP → Stores results in database
  ↓
REX → Reads analysis and makes smart decisions
  ↓
REX → Does what you asked with full knowledge
```

## Example Conversations

### Scenario 1: Understand Existing Code

**You:** "Rex, what does the login function in auth.py do?"

**Rex (internal):**
```javascript
// Calls MCP tool
analyze_function({
  function_name: "login",
  file_path: "auth.py"
})
```

**Rex (to you):** "Boss, analyzed the login function. Here's what it does:
- Validates username/password against DB
- Creates JWT token on success
- Handles rate limiting (5 attempts per minute)
- Logs all authentication attempts

Both AIs agree (95% confidence). Want me to optimize it?"

### Scenario 2: Code Modification

**You:** "Rex, make the authentication faster"

**Rex (internal):**
```javascript
// Step 1: Index the codebase
index_codebase({ path: "./auth" })

// Step 2: Query for auth code
query_codebase({ 
  question: "what handles authentication and database queries?" 
})

// Step 3: Analyze specific functions
analyze_function({ function_name: "validate_credentials" })

// Step 4: Check dependencies
get_dependencies({ 
  entity_name: "validate_credentials",
  direction: "both" 
})
```

**Rex (to you):** "Boss, I analyzed the auth system. Found the bottleneck - it's hitting the DB on every request. Here's what I'm doing:

1. Adding Redis cache for validated sessions
2. Caching user objects for 5 minutes
3. Reducing DB queries from ~1000/min to ~50/min

This won't break anything - checked all 15 dependent functions. Making changes now..."

*Rex then modifies code with confidence*

### Scenario 3: Finding Similar Code

**You:** "Rex, are there any duplicate functions in this codebase?"

**Rex (internal):**
```javascript
// Index everything
index_codebase({ path: "./src", recursive: true })

// For each function, find similar
find_similar_code({ 
  code: "function code here...",
  top_k: 10 
})
```

**Rex (to you):** "Boss, found 3 sets of duplicates:
1. `validateEmail()` appears in auth.js and utils.js (98% similar)
2. `formatDate()` duplicated across 4 files
3. `calculateTotal()` has 2 nearly identical versions

Want me to consolidate them?"

## Tools Available to Rex

| Tool | What Rex Uses It For |
|------|---------------------|
| `index_codebase` | Understand a new project or directory |
| `analyze_function` | Deep dive on specific functions before changing |
| `analyze_code` | Quick analysis of any code snippet |
| `query_codebase` | Natural language search ("find auth code") |
| `get_dependencies` | Check what will break if he changes something |
| `find_similar_code` | Find duplicates or related functionality |
| `get_system_stats` | Check what's been indexed |

## What Makes This Special

### 🧠 Dual-AI Validation
- **DeepSeek**: Technical expert (algorithms, performance, bugs)
- **Qwen**: Design expert (purpose, patterns, maintainability)
- **Consensus**: They validate each other's findings

### 💾 Smart Memory
- Analysis cached forever
- Never re-analyzes the same code
- Gets smarter over time

### 🎯 Relationship Tracking
- Knows what calls what
- Understands import chains
- Won't break dependencies

### 🚀 Fast Queries
- First analysis: 5-10 seconds (dual-AI)
- Cached queries: <1ms
- Vector search: 10-50ms

## Real Usage Example

Let's say you're working on an e-commerce app:

**You:** "Rex, optimize the checkout process"

**Rex does:**
1. `index_codebase({ path: "./checkout" })` - Understand the checkout code
2. `query_codebase({ question: "what are the performance bottlenecks in checkout?" })` - Find issues
3. `analyze_function({ function_name: "processPayment" })` - Deep dive on payment processing
4. `get_dependencies({ entity_name: "processPayment" })` - See what depends on it
5. Reads all the analysis from the database
6. Makes informed optimizations

**Rex reports:**
"Boss, optimized checkout flow:
- Moved inventory check before payment (saves failed transactions)
- Added parallel processing for tax + shipping calculations
- Cached product data (was fetching on every page load)
- Result: Checkout time reduced from 3.2s to 0.8s
- Tested against all 23 dependent functions - no breaks"

## Confidence Levels

When Rex reads analysis, he sees:

```javascript
{
  "consensus_confidence": 0.95,  // How sure the AIs are
  "agreement_score": 0.89,       // How much they agree
  "needs_review": false          // Should human check it?
}
```

- **High Confidence (>90%)**: Trust it completely
- **Good Confidence (75-90%)**: Reliable analysis
- **Low Confidence (<75%)**: Both AIs unsure, flagged for review
- **Disagreement**: AIs gave different answers, human should check

## Database Structure

All analysis is stored at: `~/.rovodev/deep_learning_v2/`

```
knowledge.db          ← All code + analysis (SQLite)
vectors.faiss         ← Semantic search index
vectors.faiss_metadata.pkl ← Vector metadata
```

**Rex can query this directly if he wants!**

Example: Rex could run SQL queries like:
```sql
SELECT * FROM code_entities WHERE entity_type = 'function' AND name LIKE '%auth%'
```

## Performance Expectations

**First Index (100 files):**
- Time: ~2-3 minutes
- Creates: ~500-1000 entity records
- Embeddings: ~500-1000 vectors

**After Indexing:**
- Questions: 5-10 seconds (includes AI analysis)
- Cached queries: Instant
- Vector search: <100ms

**Memory:**
- Database: ~5-10MB per 1000 entities
- Vector index: ~3MB per 1000 embeddings
- Total for 10k files: ~100-200MB

## Tips for Best Results

1. **Index once, query many**: Index your codebase once, then ask unlimited questions
2. **Be specific**: "optimize login" is better than "make it better"
3. **Trust the consensus**: When both AIs agree (>80%), it's solid
4. **Use dependencies**: Always check dependencies before major changes
5. **Let it cache**: Repeated queries get faster over time

## What's Next?

Now that it's working, you can:

1. **Start using it naturally**: Just ask Rex about code - he'll use these tools automatically
2. **Index your projects**: Rex can index any codebase you point him at
3. **Watch him get smarter**: As he analyzes more, the database fills with knowledge

---

**Boss, this system makes me 10x smarter at handling your code. Let's build some shit! 🔥**
