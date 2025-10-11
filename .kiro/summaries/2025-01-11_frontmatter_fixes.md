# Frontmatter YAML Syntax Fixes

**Date:** 2025-01-11  
**Task:** Fix YAML syntax errors in episode frontmatter files

## Summary

Fixed YAML syntax errors in 13 episode files caused by unescaped apostrophes in Italian quote strings. All 98 episode files now pass validation.

## Files Fixed

1. **_episodes/7.md** - Fixed `quote_deepseek` apostrophe in "l'illusione"
2. **_episodes/19.md** - Fixed `quote_claude` and `quote_deepseek` apostrophes
3. **_episodes/20.md** - Fixed `quote_deepseek` apostrophe in "l'anima"
4. **_episodes/23.md** - Fixed `quote_openai` apostrophe in "l'Europa"
5. **_episodes/25.md** - Fixed `quote_openai` and `quote_llama` apostrophes
6. **_episodes/26.md** - Fixed `quote_deepseek` apostrophe in "l'AI"
7. **_episodes/28.md** - Fixed `quote_llama` apostrophe in "d'uscita"
8. **_episodes/31.md** - Fixed `quote_llama` apostrophe in "l'hardware"
9. **_episodes/37.md** - Fixed `quote_openai` apostrophe in "Nell'era"
10. **_episodes/50.md** - Fixed `quote_openai` apostrophe in "Nell'era"
11. **_episodes/64.md** - Fixed `quote_openai` apostrophe in "sull'orlo"
12. **_episodes/77.md** - Fixed `quote_deepseek` apostrophe in "l'IA"
13. **_episodes/78.md** - Fixed `quote_deepseek` apostrophe in "L'arte"

## Issue Type

All errors were caused by single apostrophes (') in Italian contractions within YAML quoted strings. In YAML, apostrophes inside single-quoted strings must be escaped by doubling them ('').

## Solution Applied

Changed all instances of `l'` to `l''` and `d'` to `d''` within YAML quote fields to properly escape apostrophes according to YAML syntax rules.

## Validation Results

- **Before:** 89 passed, 9 failed
- **After:** 98 passed, 0 failed ✓

All episode frontmatter files now have valid YAML syntax and can be properly parsed by Jekyll.
