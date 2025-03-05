import os
import requests
import json
import time
from typing import Optional

class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str = None, max_retries: int = 3, timeout: int = 300):
        """初始化DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥，如果为None则尝试从环境变量获取
            max_retries: 最大重试次数
            timeout: 请求超时时间（秒）
        """
        # 优先从环境变量获取API key
        env_key = os.getenv('DEEPSEEK_API_KEY')
        print(f"从环境变量获取的API key: {'已设置' if env_key else '未设置'}")
        
        self.api_key = api_key or env_key
        self.max_retries = max_retries
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置。请通过环境变量 DEEPSEEK_API_KEY 或初始化参数设置API密钥。")
            
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_text(self, prompt: str) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            
        Returns:
            str: 生成的文本
        """
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                print(f"DeepSeek客户端开始生成文本，提示词长度: {len(prompt)}")
                print(f"当前尝试次数: {retry_count + 1}/{self.max_retries}")
                
                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一个专业的角色描述生成器，擅长根据八字和世界背景生成生动的角色描述。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.9,
                    "max_tokens": 4096
                }
                
                print(f"准备发送请求到 {self.api_url}")
                print(f"请求超时设置: {self.timeout}秒")
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout  # 使用实例变量的超时设置
                )
                
                print(f"收到响应，状态码: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"响应内容类型: {type(result)}")
                    print(f"响应内容结构: {list(result.keys())}")
                    
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0]["message"]["content"]
                        print(f"成功提取内容，长度: {len(content)}")
                        return content
                    else:
                        print(f"响应格式异常: {result}")
                        raise ValueError(f"API响应格式异常: {result}")
                else:
                    print(f"API请求失败: {response.status_code} - {response.text}")
                    raise ValueError(f"API请求失败: {response.status_code} - {response.text}")
            
            except requests.exceptions.Timeout as e:
                retry_count += 1
                last_error = e
                print(f"请求超时，正在重试 ({retry_count}/{self.max_retries})...")
                # 指数退避策略，每次重试等待时间增加
                time.sleep(2 ** retry_count)
                continue
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                last_error = e
                print(f"请求异常，正在重试 ({retry_count}/{self.max_retries}): {e}")
                time.sleep(2 ** retry_count)
                continue
                
            except Exception as e:
                print(f"生成文本时出错: {e}")
                print(f"错误类型: {type(e)}")
                print(f"错误详情: {e.__dict__ if hasattr(e, '__dict__') else '无详细信息'}")
                raise ValueError(f"生成文本时出错: {e}")
        
        # 如果所有重试都失败
        print(f"达到最大重试次数 ({self.max_retries})，请求失败")
        raise ValueError(f"在 {self.max_retries} 次尝试后生成文本失败: {last_error}")
    
    def analyze_text(self, text: str) -> dict:
        """分析文本
        
        Args:
            text: 要分析的文本
            
        Returns:
            dict: 分析结果
        """
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一个专业的文本分析器，擅长分析文本的情感、主题和关键信息。"},
                        {"role": "user", "content": f"请分析以下文本：\n\n{text}"}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return json.loads(result["choices"][0]["message"]["content"])
                else:
                    raise ValueError(f"API请求失败: {response.status_code} - {response.text}")
            
            except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                retry_count += 1
                last_error = e
                print(f"请求异常，正在重试 ({retry_count}/{self.max_retries}): {e}")
                time.sleep(2 ** retry_count)
                continue
                
            except Exception as e:
                raise ValueError(f"分析文本时出错: {e}")
        
        # 如果所有重试都失败
        raise ValueError(f"在 {self.max_retries} 次尝试后分析文本失败: {last_error}")
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """总结文本
        
        Args:
            text: 要总结的文本
            max_length: 最大长度
            
        Returns:
            str: 总结结果
        """
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一个专业的文本总结器，擅长提取文本的核心内容。"},
                        {"role": "user", "content": f"请总结以下文本（不超过{max_length}字）：\n\n{text}"}
                    ],
                    "temperature": 0.3,
                    "max_tokens": max_length
                }
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    raise ValueError(f"API请求失败: {response.status_code} - {response.text}")
            
            except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                retry_count += 1
                last_error = e
                print(f"请求异常，正在重试 ({retry_count}/{self.max_retries}): {e}")
                time.sleep(2 ** retry_count)
                continue
                
            except Exception as e:
                raise ValueError(f"总结文本时出错: {e}")
        
        # 如果所有重试都失败
        raise ValueError(f"在 {self.max_retries} 次尝试后总结文本失败: {last_error}")
    
    def translate_text(self, text: str, target_lang: str = "en") -> str:
        """翻译文本
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言
            
        Returns:
            str: 翻译结果
        """
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一个专业的翻译器，擅长准确传达文本的原意。"},
                        {"role": "user", "content": f"请将以下文本翻译成{target_lang}：\n\n{text}"}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    raise ValueError(f"API请求失败: {response.status_code} - {response.text}")
            
            except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                retry_count += 1
                last_error = e
                print(f"请求异常，正在重试 ({retry_count}/{self.max_retries}): {e}")
                time.sleep(2 ** retry_count)
                continue
                
            except Exception as e:
                raise ValueError(f"翻译文本时出错: {e}")
        
        # 如果所有重试都失败
        raise ValueError(f"在 {self.max_retries} 次尝试后翻译文本失败: {last_error}")
    
    def check_api_key(self) -> bool:
        """检查 API 密钥是否有效。
        
        Returns:
            bool: 密钥是否有效
        """
        try:
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": "测试"}
                ],
                "max_tokens": 1
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=data,
                timeout=10  # 检查API密钥使用较短的超时时间
            )
            
            return response.status_code == 200
        
        except:
            return False 