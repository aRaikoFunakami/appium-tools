# Appium Tools

LangChain統合されたAppium自動化ツール集。GPT-4を使ってAndroidデバイスを自然言語で操作できます。

## 特徴

- 🤖 **LangChainエージェント統合**: GPT-4で自然言語によるデバイス操作
- 🛠️ **19種類のツール**: 要素操作、ナビゲーション、アプリ管理、デバイス情報取得
- ✅ **包括的なテスト**: pytestによる全ツールの自動テスト
- 🔧 **モジュール設計**: 簡単に新しいツールを追加可能
- 📦 **型安全**: Python 3.13対応、完全な型ヒント

## セットアップ

### 必要要件

- Python 3.13+
- Appium Server 3.x
- Android Emulator または実機
- OpenAI APIキー (チャット機能用)

### インストール

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd appium-tools
```

2. **依存関係のインストール (uv使用)**
```bash
uv sync
```

または pip の場合:
```bash
pip install -e .
```

3. **環境変数の設定**
```bash
cp .env.example .env
# .envファイルを編集してOPENAI_API_KEYを設定
```

### Appium Serverの起動

**基本起動:**
```bash
appium
```

**adb_shell機能を有効化 (list_apps, get_device_infoツール使用時):**
```bash
appium --allow-insecure=uiautomator2:adb_shell
```

### Androidデバイスの準備

エミュレーターまたは実機を起動し、Settings アプリがインストールされていることを確認してください。

## 使い方

### 1. チャット形式でデバイス操作 (chat.py)

GPT-4を使って自然言語でAndroidデバイスを操作:

```bash
uv run python chat.py
```

**使用例:**
```
You: Take a screenshot
Assistant: I've taken a screenshot successfully.

You: Find the Battery menu and click it
Assistant: I found the Battery menu and clicked it successfully.

You: Go back
Assistant: Successfully pressed the back button.
```

終了: `quit`, `exit`, または `q` を入力

### 2. ツールの直接テスト (test_tools.py)

新しいツールを追加した際は、必ずpytestでテストを作成・実行してください:

```bash
# 全ツールをテスト
uv run pytest test_tools.py -v

# 特定のツールのみテスト
uv run pytest test_tools.py::test_click_element -v

# 詳細出力付き
uv run pytest test_tools.py -v -s
```

**テスト実行時の注意:**
- Appiumサーバーが起動していること
- Androidデバイス/エミュレーターが起動していること
- Settings アプリがインストールされていること

## 利用可能なツール

### Session管理
- `get_driver_status` - ドライバーのステータス確認

### 要素操作 (interaction.py)
- `find_element` - 要素を検索
- `click_element` - 要素をクリック
- `double_tap` - 要素をダブルタップ
- `get_text` - 要素のテキストを取得
- `set_value` - テキストフィールドに値を設定
- `press_keycode` - Androidキーコードを送信

### ナビゲーション (navigation.py)
- `take_screenshot` - スクリーンショット取得
- `get_page_source` - ページのXMLソース取得
- `scroll_element` - 要素内をスクロール
- `scroll_to_element` - 要素が表示されるまでスクロール

### アプリ管理 (app_management.py)
- `get_current_app` - 現在のアプリ情報取得
- `activate_app` - アプリを起動
- `terminate_app` - アプリを終了
- `list_apps` - インストール済みアプリ一覧 *(要: adb_shell)*

### デバイス情報 (device_info.py)
- `get_device_info` - デバイス詳細情報取得 *(要: adb_shell)*
- `is_locked` - ロック状態確認
- `get_orientation` - 画面向き取得
- `set_orientation` - 画面向き設定

## 新しいツールの追加方法

新しいツールを追加する際の手順:

1. 適切なモジュール（`tools/interaction.py`など）にツールを作成
2. `tools/__init__.py`にエクスポートと`get_all_tools()`に追加
3. `test_tools.py`にテストを追加
4. `uv run pytest test_tools.py::test_new_tool -v` でテスト実行

**重要:** 新しいツールを追加したら、必ずテストを作成して動作確認してください。

詳細な実装方法は`AGENTS.md`を参照してください。

## プロジェクト構成

```
appium-tools/
├── tools/                      # ツールモジュール
│   ├── __init__.py            # エクスポートとget_all_tools()
│   ├── session.py             # ドライバー管理
│   ├── interaction.py         # 要素操作ツール
│   ├── navigation.py          # ナビゲーションツール
│   ├── app_management.py      # アプリ管理ツール
│   └── device_info.py         # デバイス情報ツール
├── chat.py                     # LangChainチャットインターフェース
├── test_tools.py              # pytestテストスイート
├── pyproject.toml             # プロジェクト設定
└── README.md                  # このファイル
```

## トラブルシューティング

### adb_shell機能が無効のエラー

```
Potentially insecure feature 'adb_shell' has not been enabled
```

**解決策:** Appiumサーバーを以下のコマンドで再起動:
```bash
appium --allow-insecure=uiautomator2:adb_shell
```

### セッションタイムアウト

デフォルトのタイムアウトは300秒です。`tools/session.py`で調整可能:
```python
options.set_capability("appium:newCommandTimeout", 600)  # 10分
```

### テストが失敗する

1. Appiumサーバーが起動しているか確認
2. デバイス/エミュレーターが起動しているか確認
3. Settings アプリがインストールされているか確認
4. `adb devices` でデバイスが認識されているか確認

## ライセンス

MIT

## 貢献

1. Fork the repository
2. Create your feature branch
3. **テストを追加** (`test_tools.py`)
4. テストが通ることを確認 (`uv run pytest test_tools.py -v`)
5. Commit your changes
6. Push to the branch
7. Create a Pull Request

**注意:** テストなしのPull Requestは受け付けられません。
