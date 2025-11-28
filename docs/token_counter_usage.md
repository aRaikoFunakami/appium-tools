# Token Counter 使い方ガイド

`TiktokenCountCallback` は、LangChain エージェントの LLM 呼び出しを追跡し、トークン数とコストを計算するためのコールバックです。

## 基本的な使い方

### 1. 初期化

```python
from appium_tools.token_counter import TiktokenCountCallback

# モデル名を指定して初期化
token_counter = TiktokenCountCallback(model="gpt-4.1")
```

サポートされているモデル:
- GPT-5シリーズ: `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-pro`
- GPT-4.1シリーズ: `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`
- GPT-4oシリーズ: `gpt-4o`, `gpt-4o-mini`
- O-シリーズ: `o1`, `o1-mini`, `o3`, `o3-mini`, `o4-mini`
- その他多数（詳細は `token_counter.py` 参照）

### 2. LangChain エージェントに設定

```python
from langchain_core.runnables import RunnableConfig

response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": user_input}]},
    config=RunnableConfig(
        callbacks=[token_counter]  # ここで設定
    )
)
```

## 推奨パターン: track_query() を使用

最もシンプルで推奨される使い方です。

```python
from appium_tools.token_counter import TiktokenCountCallback

# 初期化
token_counter = TiktokenCountCallback(model="gpt-4.1")

# クエリごとに追跡
with token_counter.track_query() as query:
    # LLM呼び出し
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=RunnableConfig(callbacks=[token_counter])
    )
    
    # このクエリのレポートを表示
    print(query.report())

# セッション終了時に全体のサマリーを表示
print(token_counter.format_session_summary())
```

### track_query() の利点

- ✅ インデックス管理が不要（自動）
- ✅ スコープが明確（`with` ブロック）
- ✅ エラーが少ない
- ✅ 読みやすいコード

## 完全な使用例（chat.py パターン）

```python
import asyncio
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from appium_tools.token_counter import TiktokenCountCallback

async def main():
    # 初期化
    token_counter = TiktokenCountCallback(model="gpt-4.1")
    agent = create_agent(model="gpt-4.1", tools=tools)
    
    # メインループ
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            break
        
        # クエリを追跡
        with token_counter.track_query() as query:
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=RunnableConfig(callbacks=[token_counter])
            )
            
            print(f"\nAssistant: {response['messages'][-1].content}\n")
            
            # このクエリのレポート
            report = query.report()
            if report:
                print(report)
    
    # ループ終了後、セッション全体のサマリー
    session_summary = token_counter.format_session_summary()
    if session_summary:
        print("\n" + session_summary + "\n")

if __name__ == '__main__':
    asyncio.run(main())
```

### 出力例

**クエリごと（ループ内）:**
```
======================================================================
📊 This Query LLM Calls:
======================================================================

🔹 Call #1 (1.23s)
   Model: gpt-4.1
   Tokens: 1500 input + 200 output = 1700 total
   💰 Cost: $0.004600

🔹 Call #2 (0.95s)
   Model: gpt-4.1
   Tokens: 1800 input + 150 output = 1950 total
   💾 Cache Hit: 500 tokens saved $0.000250
   💰 Cost: $0.004200

----------------------------------------------------------------------
📊 This Query Total: 2 calls, 3650 tokens, $0.008800
======================================================================
```

**セッション終了時:**
```
======================================================================
📈 SESSION SUMMARY:
======================================================================
Total LLM Calls: 6
Total Tokens: 10850 (9200 input + 1650 output)
💾 Total Cached: 1200 tokens
💰 Total Cost: $0.025400
📊 Average: 1808.3 tokens/call, $0.004233/call
======================================================================
```

## データ取得メソッド

### 履歴取得

```python
# 全履歴を取得
history = token_counter.get_invocation_history()
# [
#   {
#     "invocation_id": 1,
#     "timestamp": "2025-11-28T10:30:45.123456",
#     "elapsed_seconds": 1.23,
#     "model": "gpt-4.1",
#     "input_tokens": 1500,
#     "cached_tokens": 0,
#     "output_tokens": 200,
#     "total_tokens": 1700,
#     "input_cost_usd": 0.003000,
#     "output_cost_usd": 0.001600,
#     "cached_cost_usd": 0.0,
#     "total_cost_usd": 0.004600
#   },
#   ...
# ]

# 特定のIDで取得
inv = token_counter.get_invocation_by_id(2)

# 最新の呼び出しを取得
latest = token_counter.get_latest_invocation()
```

### サマリー取得

```python
summary = token_counter.get_invocations_summary()
# {
#   "total_invocations": 6,
#   "total_input_tokens": 9200,
#   "total_cached_tokens": 1200,
#   "total_output_tokens": 1650,
#   "total_tokens": 10850,
#   "total_cost_usd": 0.025400,
#   "average_tokens_per_invocation": 1808.33,
#   "average_cost_per_invocation": 0.004233
# }
```

### 後方互換性（従来のメソッド）

```python
# 累積カウンター（後方互換性のため残されています）
metrics = token_counter.get_metrics()
# {
#   "model": "gpt-4.1",
#   "input_tokens": 9200,
#   "cached_tokens": 1200,
#   "output_tokens": 1650,
#   "total_tokens": 10850,
#   "input_cost_usd": 0.018400,
#   "output_cost_usd": 0.013200,
#   "cached_cost_usd": 0.000600,
#   "total_cost_usd": 0.031400
# }
```

## フォーマット済み出力

### 詳細レポート

```python
# 全invocationの詳細
print(token_counter.format_invocation_details())

# サマリーのみ
print(token_counter.format_summary())

# 両方（詳細 + サマリー）
print(token_counter.format_report())

# サマリーのみ（詳細なし）
print(token_counter.format_report(show_details=False))
```

### カスタム幅

```python
# 表示幅を指定（デフォルト: 70文字）
print(token_counter.format_summary(width=80))
print(token_counter.format_session_summary(width=100))
```

## リセット

```python
# 全てのカウンターと履歴をクリア
token_counter.reset_counters()

# リセット後は invocation_id が 1 から再開
```

## 高度な使い方

### 手動でインデックス管理（非推奨）

`track_query()` を使わない場合:

```python
# 開始時点を記録
start_index = len(token_counter.get_invocation_history())

# LLM呼び出し
response = await agent.ainvoke(...)

# レポート表示
print(token_counter.format_loop_report(start_index))
```

**注意:** この方法は煩雑なので、`track_query()` の使用を推奨します。

### モデルの途中変更

```python
# モデルを変更しても、各invocationに正しいモデルとコストが記録される
token_counter.model = "gpt-4o-mini"
response1 = await agent.ainvoke(...)  # gpt-4o-mini として記録

token_counter.model = "gpt-4.1"
response2 = await agent.ainvoke(...)  # gpt-4.1 として記録

# 各invocationのmodelフィールドで確認可能
history = token_counter.get_invocation_history()
print(history[0]["model"])  # "gpt-4o-mini"
print(history[1]["model"])  # "gpt-4.1"
```

## ベストプラクティス

### ✅ 推奨

```python
# 1. track_query() を使う
with token_counter.track_query() as query:
    response = await agent.ainvoke(...)
    print(query.report())

# 2. セッション終了時にサマリー表示
print(token_counter.format_session_summary())

# 3. 長期間使用する場合は定期的にリセット
if iteration % 100 == 0:
    token_counter.reset_counters()
```

### ❌ 非推奨

```python
# 手動でインデックス管理（面倒でエラーが起きやすい）
start = len(token_counter.get_invocation_history())
response = await agent.ainvoke(...)
print(token_counter.format_loop_report(start))

# 累積カウンターのみ使用（詳細が失われる）
metrics = token_counter.get_metrics()
print(metrics["total_cost_usd"])
```

## トラブルシューティング

### キャッシュトークンが記録されない

OpenAI API が `prompt_tokens_details.cached_tokens` を返していることを確認してください。一部のモデルではキャッシュ機能が無効な場合があります。

### コストが正確でない

使用しているモデル名が正しいか確認してください。モデル名は `token_counter.py` の `PRICING` 辞書に含まれている必要があります。

### 履歴が蓄積されすぎる

長時間実行する場合は、定期的に `reset_counters()` を呼び出してください:

```python
# 100クエリごとにリセット
if query_count % 100 == 0:
    # サマリーを保存してからリセット
    final_summary = token_counter.get_invocations_summary()
    save_to_database(final_summary)
    token_counter.reset_counters()
```

## まとめ

- **基本**: `TiktokenCountCallback(model="...")` で初期化
- **推奨パターン**: `with token_counter.track_query() as query:`
- **クエリごと**: `query.report()` で詳細表示
- **セッション終了**: `token_counter.format_session_summary()` で合計表示
- **データ取得**: `get_invocation_history()`, `get_invocations_summary()`
- **リセット**: `reset_counters()` で履歴クリア

このパターンに従えば、シンプルかつ強力なトークン追跡が実現できます。
