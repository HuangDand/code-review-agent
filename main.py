# -*- coding: utf-8 -*-
import os
import ast
import requests

DASHSCOPE_API_KEY = "sk-ws-H.PEDREIY.eL0M.MEYCIQD4iFFvEygwWf5vw-G2ZIQYns8Ep5fsfx1Rv4zs8w_P4QIhAJ6X26TtvJhvrDPtPLCKIpzyadmu2Dh7TG7zOel4_nVv"

def code_static_analyzer(code):
    result = []
    line_count = len(code.splitlines())
    result.append("Code lines: {}".format(line_count))
    try:
        tree = ast.parse(code)
        func_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        result.append("Syntax check: Pass")
        result.append("Function count: {}, Class count: {}".format(func_count, class_count))
    except SyntaxError as e:
        result.append("Syntax ERROR at line {}: {}".format(e.lineno, e.msg))
    except Exception as e:
        result.append("Analysis error: {}".format(str(e)))
    return "\n".join(result)


def call_qwen_api(api_key, prompt_text):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-turbo",
        "input": {
            "messages": [
                {"role": "user", "content": prompt_text}
            ]
        },
        "parameters": {"temperature": 0.1}
    }
    resp = requests.post(url, headers=headers, json=payload)
    print("API raw response:", resp.text)
    return resp.json()


def main():
    print("===== Code Review Agent (Qwen Dashscope) =====")
    print("Paste multi-line code, end input with <<END")
    print("Type exit to quit\n")

    while True:
        print("\nPaste your code, finish with <<END")
        lines = []
        while True:
            line = input()
            strip_line = line.strip()
            if strip_line == "<<END":
                break
            if strip_line.lower() == "exit":
                print("Program exit")
                return
            lines.append(line)
        user_code = "\n".join(lines)

        static_info = code_static_analyzer(user_code)
        prompt = """You are a professional code reviewer.
Use the static analysis result below to review the code.
Check for bugs, boundary error, code style, performance, security and maintainability.
Output format:
1. Static analysis result
2. Defect list (line number, description, risk level: High/Medium/Low)
3. Optimization suggestions

Static analysis result: {}
Code to review:
{}
""".format(static_info, user_code)

        try:
            data = call_qwen_api(DASHSCOPE_API_KEY, prompt)
            if "output" not in data:
                raise Exception(f"API error response: {data}")
            output_text = data["output"]["text"]

            with open("report.txt", "w", encoding="utf-8") as f:
                f.write("===== Review Report =====\n")
                f.write(output_text)
            print("SUCCESS: Report saved into report.txt")
            try:
                print("\n===== Review Report =====")
                print(output_text)
            except UnicodeEncodeError:
                print("\nWARNING: Cannot print report to console (encoding error). Please open report.txt.")
        except Exception as err:
            with open("error.txt", "w", encoding="utf-8") as f:
                f.write(str(err))
            print("ERROR: details saved to error.txt")


if __name__ == "__main__":
    main()
