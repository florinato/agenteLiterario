import json
import sys
from subprocess import PIPE, run


def replace_in_file(path, diff):
    try:
        command = [
            "python",
            "-c",
            """
import json
from subprocess import run, PIPE

def execute_tool(tool_name, kwargs):
    tool_str = f'<{tool_name}>'
    for key, value in kwargs.items():
        tool_str += f'<{key}>{value}</{key}>'
    tool_str += f'</{tool_name}>'
    return tool_str

tool_data = execute_tool('replace_in_file', {'path': '{}', 'diff': '{}'})
print(tool_data)
""".format(path, diff)
        ]
        result = run(command, stdout=PIPE, stderr=PIPE, text=True, shell=False)

        if result.returncode == 0:
            print("Command executed successfully")
            print(result.stdout)
            return {"success": True, "message": result.stdout}
        else:
            print(f"Command failed with error: {result.stderr}")
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python replace_file.py <path> <diff>")
        sys.exit(1)

    path = sys.argv[1]
    diff = sys.argv[2]

    result = replace_in_file(path, diff)
    print(json.dumps(result))
