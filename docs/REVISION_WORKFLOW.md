# Revision Workflow Feature

> **Status**: ✅ Merged to `main` branch

## Overview

This feature implements an intelligent revision workflow that ensures the Critic agent's feedback is actually applied to improve deliverables before they reach the Project Manager.

## The Problem

**Before this feature:**
```
Strategist → Copywriter → Designer → Critic → PM
                                        ↓
                            "Posts need improvement"
                            "Tone too casual"
                                        ↓
                                  (Ignored! ❌)
                                        ↓
                                    PM gets
                                  flawed posts
```

The Critic would identify issues, but the orchestrator would proceed directly to the Project Manager with the unrevised deliverables.

## The Solution

**With this feature:**
```
Strategist → Copywriter → Designer → Critic
                            ↓           ↓
                            ↓    Analyzes feedback
                            ↓    "Posts: NEEDS_REVISION"
                            ↓    "Visuals: APPROVED"
                            ↓           ↓
                            ← ← ← Orchestrator
                            ↓     decides to revise
                        Copywriter
                       (with feedback)
                            ↓
                     Revised posts
                            ↓
                           PM
                    (gets quality work)
```

## How It Works

### 1. Critic Provides Structured Feedback

The Critic now outputs feedback in a standardized format:

```
**POSTS REVIEW:**
- Score: 6/10
- Status: NEEDS_REVISION
- What Works: Engaging content, good hashtags
- Issues: Tone too casual, weak CTAs
- Suggestions: Elevate language to be more professional.
  Strengthen CTAs - use "Discover" instead of "Check out"

**VISUALS REVIEW:**
- Score: 8/10
- Status: APPROVED
- What Works: On-brand, visually compelling
- Issues: None major
- Suggestions: N/A

**OVERALL ASSESSMENT:**
- All Approved: NO
- Priority Revisions: Posts need professional tone and stronger CTAs
- Overall Score: 7/10
```

### 2. Orchestrator Parses Feedback

The orchestrator:
1. Reads the Critic's structured response
2. Checks for "Status: NEEDS_REVISION"
3. Identifies which agents need to be called for revisions
4. Coordinates the revision process

**Agent Mapping:**
- `Posts: NEEDS_REVISION` → Call **copywriter** for revision
- `Visuals: NEEDS_REVISION` → Call **designer** for revision
- Both → Call both agents sequentially

### 3. Revision Execution

**When revision is needed:**

```
Orchestrator announces to user:
"The Critic identified improvements needed:
- Posts: 6/10 - NEEDS_REVISION (tone too casual)
- Visuals: 8/10 - APPROVED ✓

I'll work with the Copywriter to revise the posts..."

Orchestrator calls copywriter with context:
"I need you to revise the Instagram posts based on critic feedback.

ORIGINAL BRIEF:
[user's request]

YOUR FIRST VERSION:
[the posts you created]

CRITIC FEEDBACK (Score: 6/10 - NEEDS_REVISION):
Tone is too casual. Elevate language while maintaining warmth.
Strengthen CTAs - use 'Discover how...' instead of 'Check it out'

Please revise addressing this feedback."

Copywriter creates revised version

Orchestrator confirms:
"✓ Copywriter completed revisions based on critic feedback"

Orchestrator proceeds to PM with REVISED posts
```

**When all approved:**

```
Orchestrator announces:
"✓ Critic approved all deliverables!
- Posts: 9/10 - APPROVED ✓
- Visuals: 8/10 - APPROVED ✓

Proceeding to Project Manager..."

Orchestrator proceeds directly to PM (no revision needed)
```

### 4. Revision Limits

**Critical safeguard against infinite loops:**
- Maximum **1 revision round** per deliverable
- After 1 revision, proceed to PM regardless of score
- Prevents cost explosion from endless revision cycles

## Benefits

### ✅ Quality Assurance
- Deliverables actually get improved based on expert feedback
- Project Manager receives polished, approved materials
- Final campaign quality is higher

### ✅ Cost Efficient
- Only revises what needs improvement
- Approved deliverables skip revision entirely
- 1 revision max prevents runaway costs

### ✅ Transparent Process
- User sees quality control in action
- Clear communication about what's being revised and why
- Builds trust in the system

### ✅ Realistic Workflow
- Mirrors real creative agency processes
- Feedback → Revision → Approval cycle
- Professional quality standards

## Changes Made

### File: `agents/critic/agent.py`

**Changed:**
- Updated `SYSTEM_INSTRUCTION` with structured feedback format
- Added clear `APPROVED | NEEDS_REVISION` status markers
- Included scoring guide (7+ = approved, <7 = needs revision)
- Provided example review showing the format

**Key sections:**
```python
**POSTS REVIEW:**
- Score: [X/10]
- Status: [APPROVED | NEEDS_REVISION]
- What Works: [...]
- Issues: [...]
- Suggestions: [...]
```

### File: `agents/creative_director/agent.py`

**Changed:**
- Added comprehensive "REVISION WORKFLOW" section to `SYSTEM_INSTRUCTION_TEMPLATE`
- Detailed instructions for parsing critic feedback
- Step-by-step revision coordination process
- Two complete workflow examples (with/without revisions)
- Revision limits to prevent infinite loops

**Key sections:**
1. Parsing Critic's Structured Feedback
2. Identifying What Needs Revision
3. Executing Revision Workflow
4. Revision Limits (max 1 round)
5. Complete Workflow Examples

## Testing

### Test Case 1: Posts Need Revision

**Setup:**
```
User: "Create campaign for eco-friendly water bottles targeting professionals aged 30-45"
```

**Expected Flow:**
1. Brand Strategist completes research
2. Copywriter creates posts (casual tone)
3. Designer creates visual concepts
4. Critic reviews:
   - Posts: 6/10 - NEEDS_REVISION (too casual for target audience)
   - Visuals: 8/10 - APPROVED
5. **Orchestrator calls Copywriter for revision** with critic feedback
6. Copywriter creates professional-toned posts
7. Orchestrator proceeds to PM with revised posts

**Verify:**
- [ ] Orchestrator announces revision plan
- [ ] Copywriter is called with full context (brief + first version + feedback)
- [ ] Revised posts have more professional tone
- [ ] PM receives revised posts, not original

### Test Case 2: All Approved

**Setup:**
```
User: "Create campaign for luxury watches"
```

**Expected Flow:**
1. Brand Strategist completes research
2. Copywriter creates posts (high quality)
3. Designer creates visual concepts (high quality)
4. Critic reviews:
   - Posts: 9/10 - APPROVED
   - Visuals: 8/10 - APPROVED
5. **Orchestrator proceeds directly to PM** (no revision)

**Verify:**
- [ ] Orchestrator announces all approved
- [ ] No revision calls made
- [ ] PM receives original versions
- [ ] Workflow is faster (no extra LLM calls)

### Test Case 3: Both Need Revision

**Setup:**
```
User: "Create campaign for budget smartphones"
```

**Expected Flow:**
1. Research, posts, visuals created
2. Critic reviews:
   - Posts: 5/10 - NEEDS_REVISION
   - Visuals: 6/10 - NEEDS_REVISION
3. **Orchestrator calls both Copywriter and Designer**
4. Both create revised versions
5. Orchestrator proceeds to PM

**Verify:**
- [ ] Orchestrator announces both need revision
- [ ] Copywriter called first
- [ ] Designer called second
- [ ] PM receives both revised versions

### Test Case 4: Revision Limit

**Manual test** - Force critic to keep suggesting revisions:

**Expected:**
- After 1 revision, orchestrator proceeds to PM
- No second revision even if critic still suggests changes
- Prevents infinite loop

## Deployment

### Local Testing

```bash
# Switch to feature branch
git checkout feature/critic-revision-workflow

# Test critic agent
cd agents/critic
python agent.py

# Test orchestrator (make sure all agent URLs are set)
cd ../creative_director
python agent.py
```

### Deploy to Cloud

```bash
# Deploy updated critic
cd agents/common
python deploy_all_specialists.py  # Deploys all including critic

# Deploy updated orchestrator
cd ../deploy
python deploy_orchestrator_two_stage.py --action deploy
```

### Merge to Main

After testing:

```bash
git checkout feature/critic-revision-workflow
git add agents/critic/agent.py agents/creative_director/agent.py docs/REVISION_WORKFLOW.md
git commit -m "feat: Add revision workflow - critic feedback now triggers agent revisions"
git checkout main
git merge feature/critic-revision-workflow
git push origin main
```

## Configuration

No environment variables needed - this feature works with existing configuration.

## Performance Impact

**With revisions:**
- Additional 1-2 LLM calls (copywriter and/or designer revision)
- Adds ~10-20 seconds to workflow (when revisions needed)
- Cost: ~$0.002-0.004 per revision (Gemini 2.5 Flash)

**Without revisions:**
- No impact - proceeds directly to PM as before
- Same speed and cost as original workflow

**Overall:**
- ~30-40% of campaigns may need revisions
- Quality improvement outweighs minimal cost increase
- User receives better deliverables

## Future Enhancements

### Potential Improvements

1. **Multi-round revisions** (with user approval)
   - After 1 auto-revision, ask user if they want another round
   - Configurable max revision count

2. **Revision quality tracking**
   - Track score improvements (6/10 → 8/10)
   - Log revision effectiveness metrics

3. **Selective revision scope**
   - "Revise only the first 2 posts, others are fine"
   - Granular feedback per deliverable item

4. **Critic re-review**
   - After revision, optionally call critic again
   - Verify revisions addressed the issues

5. **User override**
   - Let user decide: "Proceed without revision" or "Revise"
   - User-in-the-loop approval

## FAQs

**Q: Will this make every workflow slower?**
A: No - only when revisions are actually needed. If critic approves everything (score 7+), workflow proceeds directly to PM with no slowdown.

**Q: What if revisions don't improve the score?**
A: The 1-revision limit ensures we don't get stuck. After 1 revision, we proceed regardless.

**Q: Can users disable this feature?**
A: Currently no, but you could add a flag in the orchestrator instruction or environment variable.

**Q: Does this work with context compaction?**
A: Yes - compaction still triggers after every 3 agents. Revision calls count as agent calls.

**Q: What if only part of the posts need revision?**
A: Currently, the entire deliverable (all posts or all visuals) gets revised. Future enhancement could support granular revisions.

## Conclusion

This revision workflow bridges the gap between feedback and action, ensuring the Critic agent's insights actually improve campaign quality before reaching the Project Manager.

**Key takeaway:** Quality control that actually controls quality! ✨

---

**Branch**: `feature/critic-revision-workflow`
**Status**: Ready for testing
**Last Updated**: December 2024
