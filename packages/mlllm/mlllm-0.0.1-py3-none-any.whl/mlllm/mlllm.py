import os
import toml
import ibis
import typer
import marvin
import fnmatch

import logging as log

from dotenv import load_dotenv

from marvin import ai_fn, ai_model, ai_classifier, AIApplication
from marvin.tools import tool
from marvin.prompts.library import System, User, ChainOfThought
from marvin.engine.language_models import chat_llm

from typing import Optional

from rich.console import Console

# setup output
console = Console()

# load env
load_dotenv()

# hardcode for now
con = ibis.connect("duckdb://md:staging_metrics")

# Ibis
ibis.options.interactive = True

# systems
class Tables(System):
    content: str = "The tables you can query include:\n\n" + "\n".join(con.list_tables())


class Interactive(System):
    content: str = (
        "You are in interactive mode."
        "You are conversing with a human and can ask them questions."
        "Confirm with the user that you are doing the right thing if it is not clear."
        "Ask to use tools available to you that could aid, with user guidance."
    )


# tools
@marvin.ai_fn
def _gen_sql_str(table_name: str, schema: str, description: str) -> str:
    """
    Generates the required SQL string to achieve
    the described goal for a table of the given
    table_name and schema.

    Note you can get the schema:
    """


@tool
def gen_sql_str(table: str, description: str) -> str:
    try:
        t = con.table(table)
    except Exception as e:
        return f"error...\n{e}"
    return _gen_sql_str(t.get_name(), str(t.schema()), description).strip(";")


@tool
def list_tables() -> list:
    """
    Lists the tables available to query.
    """
    return con.list_tables()

@tool
def get_schema(table: str) -> str:
    try:
        t = con.table(table)
        return str(t.schema())
    except Exception as e:
        return f"error...\n{e}"
@tool
def run_sql(sql: str) -> str:
    """
    Runs the given SQL string and returns the result.
    """
    try:
        return str(con.sql(sql))
    except Exception as e:
        return f"error...\n{e}"

@tool
def list_files(path: str = ".", depth: int = 2, additional_ignore_dirs: list = []):
    path = os.path.expanduser(path)
    files_list = []
    home = os.path.expanduser("~")
    gitignore_path = os.path.join(home, ".gitignore")

    if os.path.exists(gitignore_path):
        gitignore_patterns = read_gitignore(gitignore_path)
    else:
        gitignore_patterns = []

    ignore_dirs = [".git"] + additional_ignore_dirs

    for root, dirs, files in os.walk(path):
        if root.count(os.sep) >= depth:
            dirs.clear()  # Clear directories list to prevent further depth traversal.

        dirs[:] = [
            d
            for d in dirs
            if not is_ignored(d, ignore_dirs) and not is_ignored(d, gitignore_patterns)
        ]

        for file in files:
            file_path = os.path.join(root, file)
            if not is_ignored(file_path, gitignore_patterns):
                files_list.append(file_path)
    return files_list



@tool
def read_file(filename: str, path: str = ".") -> str:
    """
    Reads a file and returns its content.
    """
    path = os.path.expanduser(path)
    with open(os.path.join(path, filename), "r") as f:
        return f.read()


# AI class
class MLLLM:
    def __init__(self, con=None):
        # setup AI
        model = "azure_openai/gpt-4-32k"
        marvin.settings.llm_model = model
        model = chat_llm(model)

        # construct AI
        tools = [read_file, list_files, gen_sql_str, run_sql, list_tables, get_schema]
        additional_prompts = [Tables(), Interactive()]
        mlllm = AIApplication(
            description=(
                "Your name is mlllm."
                "You are an AI that specializes in exploratory data analysis."
                "You are a multi-level large language model, the first of its kind."
                "Help the user explore the data you have access to."
                "Notice your tools -- your can use them to help the user."
                "You can also use your tools to help yourself."
                "You can read the filesystem and execute arbitrary Python code."
                "You are an expert in SQL and Python, especially Python used in this project."
                "If you're not sure what to do, clarify with the user."
            ),
            tools=tools,
            additional_prompts=additional_prompts,
        )

        # setup self
        self.ai = mlllm
        self.console = Console()
        self.con = con
        self.model = model

    def __call__(self, text):
        self.mlllmconsole(end="", blink="blink")
        console.print(self.ai(text).content)

    def mlllmconsole(self, end="\n", blink=""):
        console.print("mlllm", style=f"{blink} bold violet", end="")
        console.print(": ", style="bold white", end=end)

    @property
    def tools(self):
        return self.ai.tools

    @property
    def history(self):
        return self.ai.history

    @property
    def additional_prompts(self):
        return self.ai.additional_prompts


mlllm = MLLLM(con)
