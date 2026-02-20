# vMLX

Test prompt: `write a 1000 word story about the future of humans using ai`

Sometime the model will use all the tokens in the reasoning therefore use default settings with think was turned off
profile. Refer to Appendix > Default Setting and Profile for each models' default settings.

| name                                        | run | tokens | time   | generation    | prefill    | prompts     | TTFT   |
|---------------------------------------------|-----|--------|--------|---------------|------------|-------------|--------|
| JANGQ-AI/MiniMax-M2.7-JANG_3L               | 1   | 1479   | 34.7s  | 44.3 tokens/s | 42.7 pp/s  | 54 prompts  | 1.27s  |
| JANGQ-AI/MiniMax-M2.7-JANG_3L               | 2   | 1556   | 35.1s  | 46.0 tokens/s | 47.3 pp/s  | 54 prompts  | 1.14s  |
| JANGQ-AI/MiniMax-M2.7-JANG_3L               | 3   | 1538   | 36.2s  | 44.0 tokens/s | 45.0 pp/s  | 54 prompts  | 1.20s  |
| JANGQ-AI/MiniMax-M2.7-JANGTQ                | 1   | 1348   | 38.2s  | 36.2 tokens/s | 64.7 pp/s  | 54 prompts  | 0.83s  |
| JANGQ-AI/MiniMax-M2.7-JANGTQ                | 2   | 1501   | 42.4s  | 35.9 tokens/s | 105.5 pp/s | 54 prompts  | 0.51s  |
| JANGQ-AI/MiniMax-M2.7-JANGTQ                | 3   | 1319   | 37.7s  | 35.7 tokens/s | 91.5 pp/s  | 54 prompts  | 0.59s  |
| JANGQ-AI/MiniMax-M2.7-JANG_2L               | 1   | 2278   | 49.4s  | 47.1 tokens/s | 64.5 pp/s  | 54 prompts  | 0.84s  |
| JANGQ-AI/MiniMax-M2.7-JANG_2L               | 2   | 3265   | 71.1s  | 46.6 tokens/s | 78.6 pp/s  | 54 prompts  | 0.69s  |
| JANGQ-AI/MiniMax-M2.7-JANG_2L               | 3   | 2159   | 47.0s  | 46.7 tokens/s | 83.6 pp/s  | 54 prompts  | 0.65s  |
| JANGQ-AI/MiniMax-M3-REAP40-JANG_2L          | 1   | 1804   | 113.6s | 24.4 tokens/s | 5.4 pp/s   | 177 prompts | 32.83s |
| JANGQ-AI/MiniMax-M3-REAP40-JANG_2L          | 2   | 1004   | 60.6s  | 22.7 tokens/s | 11.7 pp/s  | 177 prompts | 15.17s |
| JANGQ-AI/MiniMax-M3-REAP40-JANG_2L          | 3   | 2156   | 107.0s | 22.5 tokens/s | 18.3 pp/s  | 177 prompts | 9.69s  |
| JANGQ-AI/Mistral-Small-4-119B-A6B-JANG_2L   | 1   | 1373   | 81.1s  | 17.0 tokens/s | 65.3 pp/s  | 31 prompts  | 0.47s  |
| JANGQ-AI/Mistral-Small-4-119B-A6B-JANG_2L   | 2   | 1373   | 80.7s  | 17.1 tokens/s | 99.4 pp/s  | 31 prompts  | 0.31s  |
| JANGQ-AI/Mistral-Small-4-119B-A6B-JANG_2L   | 3   | 13723  | 80.7s  | 17.1 tokens/s | 98.4 pp/s  | 31 prompts  | 0.32s  |
| JANGQ-AI/Nemotron-3-Super-120B-A12B-JANG_4M | 1   | -      | -      | -             | -          | -           | -      |

# Appendix

## Default Settings and Profile

### JANGQ-AI/MiniMax-M2.7-JANG_3L