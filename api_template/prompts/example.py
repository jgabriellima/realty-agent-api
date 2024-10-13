from api_template.prompts.manager import prompt_manager

prompt = prompt_manager.get_prompt("rag_assistant")

compiled_prompt = prompt_manager.compile_prompt(
    "rag_assistant", action="elabore", topic="inteligência artificial"
)
print(compiled_prompt)
