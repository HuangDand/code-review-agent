import os
import ast
import dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Tongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 加载环境变量
dotenv.load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")

# ========== 自定义工具：代码静态分析工具 ==========
@tool
def code_static_analyzer(code: str) -> str:
    """
    对输入的Python代码做静态语法检查，统计代码行数、函数数量，检测语法错误。
    参数: code: 用户提交的Python代码字符串
    返回: 静态分析结果文本
    """
    result = []
    line_count = len(code.splitlines())
    result.append(f"【代码基础信息】总代码行数：{line_count}")

    try:
        tree = ast.parse(code)
        func_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        result.append(f"【语法校验】Python语法合法，无语法错误")
        result.append(f"【结构统计】函数数量：{func_count}，类数量：{class_count}")
    except SyntaxError as e:
        result.append(f"【语法校验❌】代码存在语法错误：第{e.lineno}行，{e.msg}")
    except Exception as e:
        result.append(f"【分析异常】{str(e)}")
    return "\n".join(result)

# 工具列表
tools = [code_static_analyzer]

# ========== LLM初始化：通义千问 ==========
llm = Tongyi(
    model="qwen-turbo",
    dashscope_api_key=api_key,
    temperature=0.1
)

# ========== Prompt模板（Agent系统提示词） ==========
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是专业代码审查Agent。
你的工作流程：
1. 拿到用户代码，先调用 code_static_analyzer 工具做静态代码分析。
2. 结合工具返回结果 + LLM推理，做完整代码审查。
审查维度：
- 潜在Bug、边界错误
- 代码规范、命名规范
- 性能问题、安全风险
- 可维护性、重构建议
输出格式：
1. 静态分析结果
2. 缺陷清单（问题+位置+风险等级）
3. 优化&重构建议
语言：中文，简洁清晰。"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 记忆组件，保存多轮对话
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# 创建Agent
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,  # 打开可以看到Agent思考过程
    handle_parsing_errors=True, # 错误处理，自动捕获解析异常
)

# ========== 命令行交互入口 ==========
def main():
    print("===== 代码审查Agent（命令行） =====")
    print("输入代码进行审查，输入 exit 退出程序\n")
    while True:
        user_input = input("\n请粘贴代码：")
        if user_input.strip().lower() == "exit":
            print("程序退出")
            break
        try:
            resp = agent_executor.invoke({"input": user_input})
            print("\n===== 代码审查报告 =====")
            print(resp["output"])
        except Exception as err:
            print(f"❌ 执行出错：{str(err)}")

if __name__ == "__main__":
    main()
