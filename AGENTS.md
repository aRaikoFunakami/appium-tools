# AI Agents Context

このファイルは、AIエージェント（GitHub CopilotやCursorなど）がこのプロジェクトを理解し、効果的に支援するためのコンテキスト情報を提供します。

## プロジェクト概要

**appium-tools**は、LangChainと統合されたAppium自動化ツールキットです。GPT-4を使用して自然言語でAndroidデバイスを操作できます。

このパッケージは**他のプロジェクトでも再利用可能**で、Git経由でインストールできます。

### 主要な技術スタック

- **Python 3.13**: 最新のPython機能と型ヒントを使用
- **Appium Python Client 5.x**: Androidデバイスの自動化
- **LangChain 1.x**: AI エージェントフレームワーク
- **OpenAI GPT-4**: 自然言語処理
- **pytest**: テストフレームワーク
- **uv**: 高速なPythonパッケージマネージャー

### 他のプロジェクトでの使用方法

このツールキットは、他のプロジェクトから簡単にインストールして使用できます。

#### 通常のインストール（本番環境向け）

```bash
uv add git+https://github.com/aRaikoFunakami/appium-tools.git
```

#### 編集可能モードでインストール（開発向け）

```bash
uv add --editable git+https://github.com/aRaikoFunakami/appium-tools.git
```

#### 使用例

```python
from appium_tools import appium_driver, appium_tools
from appium_tools.token_counter import TiktokenCountCallback

# Appiumツールを取得
tools = appium_tools()

# LangChainエージェントで使用
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4o-mini",
    tools=tools,
    system_prompt="Androidデバイスを操作するエージェントです。"
)

# トークンカウンター（オプション）
token_counter = TiktokenCountCallback(model="gpt-4o-mini")
response = await agent.ainvoke(
    {"messages": [("user", "設定アプリを開いて")]},
    config={"callbacks": [token_counter]}
)

# コスト表示
metrics = token_counter.get_metrics()
print(f"💰 Cost: ${metrics['total_cost_usd']:.6f}")
```

### パッケージ管理と実行の原則

**重要:** このプロジェクトでは**uv**をパッケージマネージャーとして使用します。

#### ライブラリのインストール

新しい依存関係を追加する際は、必ず`uv add`を使用:

```bash
# 新しいライブラリを追加
uv add package-name

# 開発用依存関係を追加
uv add --dev package-name
```

❌ **使用禁止**: `pip install`は使わないでください（pyproject.tomlが更新されません）

#### スクリプトの実行

Pythonスクリプトやコマンドを実行する際は、必ず`uv run`を使用:

```bash
# Pythonスクリプト実行
uv run python chat.py

# pytestテスト実行
uv run pytest test_tools.py -v

# その他のコマンド
uv run python -m module_name
```

❌ **使用禁止**: `python`や`pytest`を直接実行しないでください（仮想環境の不一致が起きる可能性）

#### 理由

- `uv add`は自動的に`pyproject.toml`と`uv.lock`を更新
- `uv run`は常に正しい仮想環境でコマンドを実行
- チーム全体で依存関係のバージョンが一致
- 高速な依存関係解決とインストール

## アーキテクチャ

### ディレクトリ構造

```
appium-tools/
├── appium_tools/             # ツールモジュール（コア機能）
│   ├── __init__.py           # appium_tools()でツール一覧を返す
│   ├── session.py            # Appiumドライバーのライフサイクル管理
│   ├── interaction.py        # 要素操作ツール (click, tap, input)
│   ├── navigation.py         # ナビゲーションツール (screenshot, scroll)
│   ├── app_management.py     # アプリ管理ツール (activate, terminate)
│   ├── device_info.py        # デバイス情報ツール (info, orientation)
│   └── token_counter.py      # トークンカウンターとコスト計算
├── chat.py                    # LangChainエージェントのメインインターフェース
├── test_tools.py             # 全ツールのpytestテストスイート
└── pyproject.toml            # プロジェクト設定とdependencies
```

### 重要な設計パターン

#### 1. グローバルドライバーパターン

```python
# appium_tools/session.py
driver = None  # グローバル変数

@asynccontextmanager
async def appium_driver(options):
    global driver
    driver = webdriver.Remote("http://localhost:4723", options=options)
    yield driver
    driver.quit()
    driver = None
```

すべてのツールは `from .session import driver` でグローバルドライバーにアクセスします。

#### 2. LangChain @tool デコレータ

```python
from langchain.tools import tool

@tool
def tool_name(param: str) -> str:
    """Description visible to LLM.
    
    Args:
        param: Parameter description
        
    Returns:
        Success or error message (must be string)
    """
    from .session import driver
    if driver:
        try:
            # Implementation
            return "Success message"
        except Exception as e:
            return f"Failed: {e}"
    else:
        return "Driver is not initialized"
```

**重要:** LangChainツールは**必ず文字列を返す**必要があります。オブジェクトを返すとエラーになります。

#### 3. 動的ツール取得

```python
# appium_tools/__init__.py
def appium_tools():
    """全ツールのリストを返す"""
    return [
        get_driver_status,
        find_element,
        click_element,
        # ... all tools
    ]
```

`chat.py`では`appium_tools()`を呼び出すだけで、新しいツールが自動的に利用可能になります。

## コーディング規約

### ツール作成時の必須要件

1. **@toolデコレータを使用**
2. **docstringを必ず記述** (LLMが読みます)
3. **型ヒントを使用** (param: str, return: str)
4. **文字列を返す** (オブジェクト不可)
5. **エラーハンドリング** (try-except必須)
6. **driver存在チェック** (if driver:)
7. **ログ出力** (print()で操作内容を記録)

### テスト作成時の必須要件

1. **@pytest.mark.asyncio デコレータ**
2. **driver_session フィクスチャを使用**
3. **成功/失敗の両方を考慮**
4. **環境依存の処理にはpytest.skip()**
5. **await asyncio.sleep()で画面遷移を待つ**

例:

```python
@pytest.mark.asyncio
async def test_my_tool(driver_session):
    """Test my_tool."""
    result = my_tool.invoke({"param": "value"})
    
    # 環境依存のスキップ
    if "some_error" in result.lower():
        pytest.skip("Feature not available")
    
    # 検証
    assert "success" in result.lower()
    await asyncio.sleep(0.5)  # 画面遷移待ち
```

## 新機能追加のワークフロー

### 1. ツール作成

適切なモジュールにツールを追加:

- **要素操作** → `appium_tools/interaction.py`
- **ナビゲーション** → `appium_tools/navigation.py`
- **アプリ管理** → `appium_tools/app_management.py`
- **デバイス情報** → `appium_tools/device_info.py`
- **新カテゴリ** → 新しいファイルを作成

### 2. エクスポート追加

`appium_tools/__init__.py`を更新:

```python
from .module import new_tool

__all__ = [
    # ... existing
    "new_tool",
]

def appium_tools():
    return [
        # ... existing
        new_tool,
    ]
```

### 3. テスト作成 ⚠️ **必須**

`test_tools.py`にテストを追加:

```python
@pytest.mark.asyncio
async def test_new_tool(driver_session):
    """Test new_tool."""
    result = new_tool.invoke({"param": "test"})
    assert "expected" in result.lower()
```

### 4. テスト実行

```bash
uv run pytest test_tools.py::test_new_tool -v
```

**テストなしでコードをコミットしない!**

## パッケージ管理ルール

### 依存関係の追加

新しいライブラリが必要な場合:

```bash
# 通常の依存関係
uv add library-name

# 開発用依存関係（テストツールなど）
uv add --dev library-name

# 特定バージョン指定
uv add "library-name>=1.0.0"
```

### 実行コマンド

すべてのPython実行には`uv run`を使用:

```bash
# テスト実行
uv run pytest test_tools.py -v

# チャット実行
uv run python chat.py

# 個別テスト
uv run pytest test_tools.py::test_name -v -s
```

### 禁止事項

- ❌ `pip install` - pyproject.tomlが更新されない
- ❌ `python` 直接実行 - 仮想環境の不一致リスク
- ❌ `pytest` 直接実行 - 依存関係の不一致リスク

常に`uv add`と`uv run`を使用してください。

## よくある問題と解決策

### 問題: LangChainツールがエラー

**原因:** ツールがオブジェクトを返している

**解決策:** 必ず文字列を返す

```python
# ❌ 間違い
return element

# ✅ 正しい
return f"Found element: {element.text}"
```

### 問題: テストでドライバーが初期化されない

**原因:** フィクスチャの使い方が間違っている

**解決策:**

```python
# ❌ 間違い
@pytest.fixture  # ← asyncio用ではない
async def driver_session():
    ...

# ✅ 正しい
@pytest_asyncio.fixture  # ← これを使う
async def driver_session():
    ...
```

### 問題: adb_shell機能が無効

**原因:** Appiumサーバーのセキュリティ設定

**解決策:**

```bash
appium --allow-insecure=uiautomator2:adb_shell
```

### 問題: 要素が見つからない

**原因:** 画面遷移が完了していない

**解決策:** テストに待機時間を追加

```python
click_element.invoke({"by": "id", "value": "button"})
await asyncio.sleep(1)  # 画面遷移を待つ
```

## 重要な制約事項

### Appium関連

1. **UiAutomator2Options使用**: set_capability()で設定
2. **newCommandTimeout**: デフォルト300秒（5分）
3. **adb_shell**: デフォルトで無効（有効化が必要）

### LangChain関連

1. **LangChain v1 API**: create_agent()を使用
2. **ツールの戻り値**: 必ず文字列
3. **システムプロンプト**: tools操作方法を記述

### pytest関連

1. **pytest-asyncio**: 非同期テスト用
2. **@pytest_asyncio.fixture**: 非同期フィクスチャ用
3. **@pytest.mark.asyncio**: 非同期テスト用

## AI エージェント向けのヒント

### コードレビュー時のチェックポイント

- [ ] 新しいツールにdocstringがある
- [ ] 型ヒント（param: str, return: str）がある
- [ ] エラーハンドリング（try-except）がある
- [ ] ツールが文字列を返している
- [ ] appium_tools/__init__.pyにエクスポート追加されている
- [ ] appium_tools/__init__.pyのappium_tools()に追加されている
- [ ] **テストが作成されている** ← 最重要
- [ ] テストが@pytest.mark.asyncioを使用している
- [ ] テストがdriver_sessionフィクスチャを使用している
- [ ] **新しい依存関係は`uv add`で追加されている**
- [ ] **テスト実行に`uv run pytest`を使用している**

### 提案すべき改善

- ツールにログ出力（print）を追加
- エラーメッセージをより具体的に
- テストケースの追加（エッジケース）
- docstringの改善（使用例を追加）
- 型ヒントの追加

### 避けるべきパターン

- ❌ グローバルdriverを直接変更する（session.py以外で）
- ❌ ツールからオブジェクトを返す
- ❌ テストなしで新機能を追加
- ❌ 同期関数と非同期関数を混在させる
- ❌ ベアexcept（`except:`）を使う → `except Exception:`を使う
- ❌ `pip install`を使う → `uv add`を使う
- ❌ `python`や`pytest`を直接実行 → `uv run`を使う

## プロジェクトの進化

### 現在のツール数: 19

1. get_driver_status
2. find_element
3. click_element
4. double_tap
5. get_text
6. set_value
7. press_keycode
8. take_screenshot
9. get_page_source
10. scroll_element
11. scroll_to_element
12. get_current_app
13. activate_app
14. terminate_app
15. list_apps (adb_shell必要)
16. get_device_info (adb_shell必要)
17. is_locked
18. get_orientation
19. set_orientation

### 今後の拡張案

- iOS対応（XCUITestドライバー）
- スクリーンショット比較ツール
- OCRベースの要素検索
- ジェスチャ操作（ピンチ、ローテート）
- パフォーマンス測定ツール
- ビデオ録画機能

### 拡張時の注意

新しいツールを追加する際は:

1. 既存のツールパターンに従う
2. 必ずテストを作成する
3. README.mdを更新する
4. このAGENTS.mdも更新する

## 参考リンク

- [Appium Documentation](https://appium.io/docs/en/latest/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [UiAutomator2 Driver](https://github.com/appium/appium-uiautomator2-driver)

## バージョン情報

- **Python**: 3.13+
- **Appium**: 3.1.1+
- **LangChain**: 1.0.8+
- **pytest**: 9.0.1+

## まとめ

このプロジェクトは:

- 🎯 **テスト駆動開発（TDD）**: 新機能には必ずテストが必要
- 🔧 **モジュール設計**: 責務に応じてファイルを分割
- 🤖 **AI統合**: LangChainでGPT-4と連携
- 📦 **型安全**: 完全な型ヒント
- ⚡ **高速開発**: uvによる依存関係管理

AIエージェントとして支援する際は、これらの原則を守り、特に**テストの作成を忘れないよう**促してください。
