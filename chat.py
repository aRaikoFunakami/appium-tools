import asyncio
import os
from appium.options.android import UiAutomator2Options
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver 
from appium_tools import appium_driver, appium_tools
from appium_tools.token_counter import TiktokenCountCallback

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
        tools=appium_tools(),
        checkpointer=InMemorySaver(),
        system_prompt="""You are a helpful assistant that controls an Android device using Appium.
You can help users interact with the Android Settings app.

Available actions:
- Check driver status
- Find elements on the screen using XPath, ID, or accessibility ID
- Click on elements
- Input text using send_keys (simulates real typing, triggers input events)
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
                
                # クエリを追跡（自動的にこの処理の開始地点を記録）
                with token_counter.track_query() as query:
                    # エージェントを実行(LangChain v1 API)
                    from langchain_core.runnables import RunnableConfig
                    
                    response = await agent.ainvoke(
                        {"messages": [{"role": "user", "content": user_input}]},
                        config=RunnableConfig(
                            configurable={"thread_id": "1"},
                            callbacks=[token_counter]
                        )
                    )
                    
                    print(f"\nAssistant: {response['messages'][-1].content}\n")
                    
                    # このクエリのレポートを表示
                    report = query.report()
                    if report:
                        print(report)
                        print()  # 空行
                
                
            except KeyboardInterrupt:
                print("\n\nチャットを終了します。")
                break
            except Exception as e:
                print(f"\nError: {e}\n")
        
        # ループを抜けたら全体のサマリーを表示
        session_summary = token_counter.format_session_summary()
        if session_summary:
            print("\n" + session_summary + "\n")


if __name__ == '__main__':
    asyncio.run(main())
