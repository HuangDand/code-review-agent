# 代码审查Agent
> 基于LangChain + 通义千问大模型实现的代码审查智能Agent
## 项目简介
本Agent接收用户提交的Python代码，自动完成静态代码分析 + AI代码审查，自动查找bug、规范问题、给出重构建议。
实现标准Agent循环：输入 → 推理 → 调用工具 → 生成输出；支持多轮对话记忆。

## 技术栈
- Python 3.9+
- LangChain：Agent框架
- 通义千问Qwen：LLM大模型
- ast：Python内置抽象语法树（静态代码分析工具）

## 安装部署
1. 创建虚拟环境
```bash
python -m venv venv
# windows
venv\Scripts\activate
# mac/linux
source venv/bin/activate
