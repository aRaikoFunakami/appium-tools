import asyncio
import os
from appium.options.android import UiAutomator2Options
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver 
from tools import appium_driver, get_all_tools
from tools.token_counter import TiktokenCountCallback

LLM_MODEL="gpt-4.1"

async def main():
    # OpenAI API キーの確認
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return
    
    # Set up Appium options
    options = UiAutomator2Options()
    options.set_capability("platformName", "Android")
    options.set_capability("appium:automationName", "uiautomator2")
    options.set_capability("appium:deviceName", "Android")
    options.set_capability("appium:appPackage", "com.android.settings")
    options.set_capability("appium:appWaitActivity", "*")
    options.set_capability("appium:language", "en")
    options.set_capability("appium:locale", "US")
    options.set_capability("appium:newCommandTimeout", 300)  # 5分（300秒）に設定
    
    # トークンカウンターコールバックを作成
    token_counter = TiktokenCountCallback(model=LLM_MODEL)
    
    # エージェントの作成（LangChain v1 API）
    agent = create_agent(
        model=LLM_MODEL,
        tools=get_all_tools(),
        checkpointer=InMemorySaver(),
        system_prompt="""You are a helpful assistant that controls an Android device using Appium.
You can help users interact with the Android Settings app.

Available actions:
- Check driver status
- Find elements on the screen using XPath, ID, or accessibility ID
- Click on elements
- Get the XML page source of the current screen
- Take a screenshot and save it to a file
- Scroll within a scrollable element (like a list or scrollview)

When the user asks you to interact with the device, use the appropriate tools.
For finding elements, use XPath like '//*[@text="Battery"]' or '//*[@resource-id="com.android.settings:id/search"]'.
Always check the driver status first before attempting operations."""
    )
    
    print("=== Appium Chat Assistant ===")
    print("チャットを開始します。'quit' または 'exit' で終了します。\n")
    
    # Appium driver を起動
    async with appium_driver(options) as driver:
        print("Appium driver が起動しました。Android Settings アプリに接続しています...\n")
        
        while True:
            # セッションが有効かチェック
            try:
                _ = driver.session_id
            except Exception as session_error:
                print(f"\n⚠️  セッションが切れています: {session_error}")
                print("プログラムを再起動してください。\n")
                break

            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("チャットを終了します。")
                    break
                
                if not user_input:
                    continue
                
                # トークンカウンターをリセット(1チャットごとに)
                # 注: エージェントは複数回LLM呼び出しをするため、リセットは実行前に1回だけ
                token_counter.reset_counters()
                
                # エージェントを実行(LangChain v1 API)
                # callbacks は config の外に出す必要がある
                from langchain_core.runnables import RunnableConfig
                
                response = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config=RunnableConfig(
                        configurable={"thread_id": "1"},
                        callbacks=[token_counter]
                    )
                )
                
                print(f"\nAssistant: {response['messages'][-1].content}\n")
                
                # トークン使用量と費用を表示
                metrics = token_counter.get_metrics()
                print(f"\n💰 Cost: ${metrics['total_cost_usd']:.6f} USD | 📊 Total: {metrics['total_tokens']} tokens")
                print(f"   📥 Input: {metrics['input_tokens']} tokens (${metrics['input_cost_usd']:.6f})")
                if metrics['cached_tokens'] > 0:
                    print(f"   💾 Cached: {metrics['cached_tokens']} tokens (${metrics['cached_cost_usd']:.6f})")
                print(f"   📤 Output: {metrics['output_tokens']} tokens (${metrics['output_cost_usd']:.6f})\n")
                
                
            except KeyboardInterrupt:
                print("\n\nチャットを終了します。")
                break
            except Exception as e:
                print(f"\nError: {e}\n")


if __name__ == '__main__':
    asyncio.run(main())
