"""
Token counting and cost calculation functionality using tiktoken
OpenAI APIのトークン数計算と費用計算機能
"""
from typing import Any, Dict, List, Optional, Tuple
from langchain_core.callbacks.base import BaseCallbackHandler


class OpenAIPricingCalculator:
    """OpenAI APIの料金計算クラス"""
    
    # OpenAI pricing (USD per 1K tokens) - 2025年11月24日時点の最新料金
    # https://platform.openai.com/docs/pricing
    PRICING = {
        # Latest GPT-5 series (最新モデル)
        "gpt-5.1": {
            "input": 0.00125,  # $1.25 / 1M tokens
            "cached": 0.000125,  # $0.125 / 1M tokens (10%)
            "output": 0.010,   # $10.00 / 1M tokens
        },
        "gpt-5": {
            "input": 0.00125,  # $1.25 / 1M tokens
            "cached": 0.000125,  # $0.125 / 1M tokens (10%)
            "output": 0.010,   # $10.00 / 1M tokens
        },
        "gpt-5-mini": {
            "input": 0.00025,  # $0.25 / 1M tokens
            "cached": 0.000025,  # $0.025 / 1M tokens (10%)
            "output": 0.002,   # $2.00 / 1M tokens
        },
        "gpt-5-nano": {
            "input": 0.00005,  # $0.05 / 1M tokens
            "cached": 0.000005,  # $0.005 / 1M tokens (10%)
            "output": 0.0004,  # $0.40 / 1M tokens
        },
        "gpt-5.1-chat-latest": {
            "input": 0.00125,  # $1.25 / 1M tokens
            "cached": 0.000125,  # $0.125 / 1M tokens (10%)
            "output": 0.010,   # $10.00 / 1M tokens
        },
        "gpt-5-chat-latest": {
            "input": 0.00125,  # $1.25 / 1M tokens
            "cached": 0.000125,  # $0.125 / 1M tokens (10%)
            "output": 0.010,   # $10.00 / 1M tokens
        },
        "gpt-5.1-codex": {
            "input": 0.00125,  # $1.25 / 1M tokens
            "cached": 0.000125,  # $0.125 / 1M tokens (10%)
            "output": 0.010,   # $10.00 / 1M tokens
        },
        "gpt-5-codex": {
            "input": 0.00125,  # $1.25 / 1M tokens
            "cached": 0.000125,  # $0.125 / 1M tokens (10%)
            "output": 0.010,   # $10.00 / 1M tokens
        },
        "gpt-5-pro": {
            "input": 0.015,    # $15.00 / 1M tokens
            "cached": 0.015,   # キャッシュなし
            "output": 0.120,   # $120.00 / 1M tokens
        },
        
        # GPT-4.1 series (新しいモデル)
        "gpt-4.1": {
            "input": 0.002,    # $2.00 / 1M tokens
            "cached": 0.0005,  # $0.50 / 1M tokens (25%)
            "output": 0.008,   # $8.00 / 1M tokens
        },
        "gpt-4.1-mini": {
            "input": 0.0004,   # $0.40 / 1M tokens
            "cached": 0.0001,  # $0.10 / 1M tokens (25%)
            "output": 0.0016,  # $1.60 / 1M tokens
        },
        "gpt-4.1-nano": {
            "input": 0.0001,   # $0.10 / 1M tokens
            "cached": 0.000025,  # $0.025 / 1M tokens (25%)
            "output": 0.0004,  # $0.40 / 1M tokens
        },
        
        # O-series models (推論モデル)
        "o1": {
            "input": 0.015,    # $15.00 / 1M tokens
            "cached": 0.0075,  # $7.50 / 1M tokens (50%)
            "output": 0.060,   # $60.00 / 1M tokens
        },
        "o1-pro": {
            "input": 0.150,    # $150.00 / 1M tokens
            "cached": 0.150,   # キャッシュなし
            "output": 0.600,   # $600.00 / 1M tokens
        },
        "o3": {
            "input": 0.002,    # $2.00 / 1M tokens
            "cached": 0.0005,  # $0.50 / 1M tokens (25%)
            "output": 0.008,   # $8.00 / 1M tokens
        },
        "o3-pro": {
            "input": 0.020,    # $20.00 / 1M tokens
            "cached": 0.020,   # キャッシュなし
            "output": 0.080,   # $80.00 / 1M tokens
        },
        "o3-deep-research": {
            "input": 0.010,    # $10.00 / 1M tokens
            "cached": 0.0025,  # $2.50 / 1M tokens (25%)
            "output": 0.040,   # $40.00 / 1M tokens
        },
        "o4-mini": {
            "input": 0.0011,   # $1.10 / 1M tokens
            "cached": 0.000275,  # $0.275 / 1M tokens (25%)
            "output": 0.0044,  # $4.40 / 1M tokens
        },
        "o4-mini-deep-research": {
            "input": 0.002,    # $2.00 / 1M tokens
            "cached": 0.0005,  # $0.50 / 1M tokens (25%)
            "output": 0.008,   # $8.00 / 1M tokens
        },
        "o3-mini": {
            "input": 0.0011,   # $1.10 / 1M tokens
            "cached": 0.00055,  # $0.55 / 1M tokens (50%)
            "output": 0.0044,  # $4.40 / 1M tokens
        },
        "o1-mini": {
            "input": 0.0011,   # $1.10 / 1M tokens
            "cached": 0.00055,  # $0.55 / 1M tokens (50%)
            "output": 0.0044,  # $4.40 / 1M tokens
        },
        
        # GPT-4o models (現行モデル)
        "gpt-4o": {
            "input": 0.0025,   # $2.50 / 1M tokens
            "cached": 0.00125,  # $1.25 / 1M tokens (50%)
            "output": 0.010,   # $10.00 / 1M tokens
        },
        "gpt-4o-mini": {
            "input": 0.000150, # $0.15 / 1M tokens
            "cached": 0.000075, # $0.075 / 1M tokens (50%)
            "output": 0.000600, # $0.60 / 1M tokens
        },
        "gpt-4o-2024-05-13": {
            "input": 0.005,    # $5.00 / 1M tokens
            "cached": 0.005,   # キャッシュなし
            "output": 0.015,   # $15.00 / 1M tokens
        },
        
        # Realtime models
        "gpt-realtime": {
            "input": 0.004,    # $4.00 / 1M tokens
            "cached": 0.0004,  # $0.40 / 1M tokens (10%)
            "output": 0.016,   # $16.00 / 1M tokens
        },
        "gpt-realtime-mini": {
            "input": 0.0006,   # $0.60 / 1M tokens
            "cached": 0.00006,  # $0.06 / 1M tokens (10%)
            "output": 0.0024,  # $2.40 / 1M tokens
        },
        
        # Legacy models for backward compatibility
        "gpt-4": {
            "input": 0.03,     # $30.00 / 1M tokens
            "cached": 0.03,    # キャッシュなし
            "output": 0.06,    # $60.00 / 1M tokens
        },
        "gpt-4-32k": {
            "input": 0.06,     # $60.00 / 1M tokens
            "cached": 0.06,    # キャッシュなし
            "output": 0.12,    # $120.00 / 1M tokens
        },
        "gpt-4-turbo": {
            "input": 0.01,     # $10.00 / 1M tokens
            "cached": 0.01,    # キャッシュなし
            "output": 0.03,    # $30.00 / 1M tokens
        },
        "gpt-3.5-turbo": {
            "input": 0.0005,   # $0.50 / 1M tokens
            "cached": 0.0005,  # キャッシュなし
            "output": 0.0015,  # $1.50 / 1M tokens
        },
        "gpt-3.5-turbo-16k": {
            "input": 0.003,    # $3.00 / 1M tokens
            "cached": 0.003,   # キャッシュなし
            "output": 0.004,   # $4.00 / 1M tokens
        },
        
        # Fallback for unknown models - use gpt-4.1-mini pricing (cost-effective)
        "default": {
            "input": 0.0004,
            "cached": 0.0001,
            "output": 0.0016,
        }
    }
    
    @classmethod
    def calculate_cost(cls, model_name: str, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """
        トークン数から費用を計算する
        
        Args:
            model_name: OpenAIモデル名
            input_tokens: 入力トークン数
            output_tokens: 出力トークン数
            
        Returns:
            Dict containing input_cost, output_cost, total_cost in USD
        """
        # モデル名を正規化（バージョン番号等を除去）
        normalized_model = cls._normalize_model_name(model_name)
        
        # 料金情報を取得（未知のモデルはdefaultを使用）
        pricing = cls.PRICING.get(normalized_model, cls.PRICING["default"])
        
        # 費用計算（1K tokens単位での料金なので、1000で割る）
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6)
        }
    
    @classmethod
    def _normalize_model_name(cls, model_name: str) -> str:
        """
        モデル名を正規化して料金表のキーと一致させる
        """
        model_lower = model_name.lower().strip()
        
        # Exact matches first
        if model_lower in cls.PRICING:
            return model_lower
        
        # Pattern matching for versioned models (最新モデルから順番にチェック)
        # GPT-5 series
        if "gpt-5-pro" in model_lower:
            return "gpt-5-pro"
        elif "gpt-5-nano" in model_lower:
            return "gpt-5-nano"
        elif "gpt-5-mini" in model_lower:
            return "gpt-5-mini"
        elif "gpt-5-chat-latest" in model_lower:
            return "gpt-5-chat-latest"
        elif "gpt-5-codex" in model_lower:
            return "gpt-5-codex"
        elif "gpt-5" in model_lower:
            return "gpt-5"
        
        # GPT-4.1 series
        elif "gpt-4.1-nano" in model_lower:
            return "gpt-4.1-nano"
        elif "gpt-4.1-mini" in model_lower:
            return "gpt-4.1-mini"
        elif "gpt-4.1" in model_lower:
            return "gpt-4.1"
        
        # O-series models
        elif "o4-mini-deep-research" in model_lower:
            return "o4-mini-deep-research"
        elif "o4-mini" in model_lower:
            return "o4-mini"
        elif "o3-deep-research" in model_lower:
            return "o3-deep-research"
        elif "o3-pro" in model_lower:
            return "o3-pro"
        elif "o3-mini" in model_lower:
            return "o3-mini"
        elif "o3" in model_lower:
            return "o3"
        elif "o1-pro" in model_lower:
            return "o1-pro"
        elif "o1-mini" in model_lower:
            return "o1-mini"
        elif "o1" in model_lower:
            return "o1"
        
        # GPT-4o series
        elif "gpt-4o-mini" in model_lower:
            return "gpt-4o-mini"
        elif "gpt-4o-2024-05-13" in model_lower:
            return "gpt-4o-2024-05-13"
        elif "gpt-4o" in model_lower:
            return "gpt-4o"
        
        # Realtime models
        elif "gpt-realtime-mini" in model_lower:
            return "gpt-realtime-mini"
        elif "gpt-realtime" in model_lower:
            return "gpt-realtime"
        
        # Legacy GPT-4 models
        elif "gpt-4-turbo" in model_lower:
            return "gpt-4-turbo"
        elif "gpt-4-32k" in model_lower:
            return "gpt-4-32k"
        elif "gpt-4" in model_lower:
            return "gpt-4"
        
        # GPT-3.5 models
        elif "gpt-3.5-turbo-16k" in model_lower:
            return "gpt-3.5-turbo-16k"
        elif "gpt-3.5-turbo" in model_lower:
            return "gpt-3.5-turbo"
        
        else:
            return "default"


class TiktokenCountCallback(BaseCallbackHandler):
    """
    LangChain callback to count tokens using tiktoken
    tiktoken を使用してトークン数を計算するLangChainコールバック
    """
    
    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        """
        Initialize the callback with the specified model
        
        Args:
            model: OpenAI model name for token encoding
        """
        self.model = model
        self.input_tokens = 0
        self.cached_tokens = 0  # キャッシュヒットしたトークン数
        self.output_tokens = 0
        self.pricing_calculator = OpenAIPricingCalculator()
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """LLM開始時に呼び出される（何もしない）"""
        pass
    
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """ストリーミング時に呼び出される（何もしない）"""
        pass
    
    def on_llm_end(self, response, **kwargs: Any) -> None:
        """
        Called when LLM completes - count tokens from actual API response
        LLM完了時に呼び出され、実際のAPIレスポンスからトークン数を取得
        """
        if not (hasattr(response, 'llm_output') and response.llm_output):
            raise ValueError("APIレスポンスにllm_outputが含まれていません")
        
        token_usage = response.llm_output.get('token_usage')
        if not token_usage:
            raise ValueError("APIレスポンスにtoken_usageが含まれていません")
        
        # OpenAI APIの実際の使用量を使用
        prompt_tokens = token_usage.get('prompt_tokens', 0)
        completion_tokens = token_usage.get('completion_tokens', 0)
        
        # キャッシュされたトークンを取得（50%割引適用）
        prompt_details = token_usage.get('prompt_tokens_details', {})
        cached_tokens = prompt_details.get('cached_tokens', 0)
        
        # 通常トークンとキャッシュトークンを分けて記録
        self.input_tokens += prompt_tokens
        self.cached_tokens = getattr(self, 'cached_tokens', 0) + cached_tokens
        self.output_tokens += completion_tokens
    
    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)"""
        return self.input_tokens + self.output_tokens
    
    def get_cost_breakdown(self) -> Dict[str, float]:
        """
        Calculate the cost breakdown for the tokens used
        使用されたトークンの費用内訳を計算（キャッシュ割引を考慮）
        """
        # モデル名を正規化
        normalized_model = self.pricing_calculator._normalize_model_name(self.model)
        pricing = self.pricing_calculator.PRICING.get(normalized_model, self.pricing_calculator.PRICING["default"])
        
        # 通常の入力トークン（キャッシュされていない部分）
        non_cached_tokens = self.input_tokens - self.cached_tokens
        
        # 費用計算
        # 通常の入力トークン: 通常料金
        non_cached_cost = (non_cached_tokens / 1000) * pricing["input"]
        # キャッシュヒットトークン: キャッシュ料金（モデルごとに異なる）
        cached_cost = (self.cached_tokens / 1000) * pricing["cached"]
        # 出力トークン: 通常料金
        output_cost = (self.output_tokens / 1000) * pricing["output"]
        
        input_cost = non_cached_cost + cached_cost
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "cached_cost": round(cached_cost, 6),
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics including tokens and costs
        トークン数と費用を含む総合的なメトリクスを取得
        """
        cost_breakdown = self.get_cost_breakdown()
        
        return {
            "model": self.model,
            "input_tokens": self.input_tokens,
            "cached_tokens": self.cached_tokens,  # キャッシュヒット数を追加
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "input_cost_usd": cost_breakdown["input_cost"],
            "output_cost_usd": cost_breakdown["output_cost"],
            "total_cost_usd": cost_breakdown["total_cost"],
            "cached_cost_usd": cost_breakdown["cached_cost"],  # キャッシュコストを追加
        }
    
    def reset_counters(self) -> None:
        """
        Reset all counters for reuse
        カウンターをリセットして再利用可能にする
        """
        self.input_tokens = 0
        self.cached_tokens = 0
        self.output_tokens = 0





# Convenience functions for cost calculation
# 費用計算のための便利関数

def calculate_openai_cost(model: str, input_tokens: int, output_tokens: int) -> Dict[str, float]:
    """
    Calculate OpenAI API cost for given token usage
    指定されたトークン使用量に対するOpenAI APIの費用を計算
    """
    return OpenAIPricingCalculator.calculate_cost(model, input_tokens, output_tokens)


