import datetime
import re
from typing import List, Dict, Tuple, Optional, Any
from pydantic import BaseModel, Field
from llm_agents.llm import ChatLLM
from llm_agents.tools.base import ToolInterface
from llm_agents.tools.python_repl import PythonREPLTool


FINAL_ANSWER_TOKEN = "Final Answer:"
OBSERVATION_TOKEN = "Observation:"
THOUGHT_TOKEN = "Thought:"
PROMPT_TEMPLATE = """Today is {today} and you can use tools to get new information. 
Here's some relevant previous experience:
{memory_context}

Answer the question as best as you can using the following tools: 

{tool_description}

Use the following format:

Question: the input question you must answer
Thought: comment on what you want to do next
Action: the action to take, exactly one element of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation repeats N times, use it until you are sure of the answer)
Thought: I now know the final answer
Final Answer: your final answer to the original input question

Begin!

Question: {question}
Thought: {previous_responses}
"""


class Memory(BaseModel):
    short_term: List[Dict[str, Any]] = Field(default_factory=list)
    long_term: List[Dict[str, Any]] = Field(default_factory=list)
    max_short_term: int = 10
    max_long_term: int = 100

    def add_short_term(self, thought: str, action: str, result: str):
        self.short_term.append({
            "thought": thought,
            "action": action,
            "result": result,
            "timestamp": datetime.datetime.now()
        })
        if len(self.short_term) > self.max_short_term:
            self.short_term.pop(0)

    def add_long_term(self, key: str, value: Any):
        self.long_term.append({
            "key": key,
            "value": value,
            "timestamp": datetime.datetime.now()
        })
        if len(self.long_term) > self.max_long_term:
            self.long_term.pop(0)

    def get_relevant_memory(self, query: str) -> List[Dict[str, Any]]:
        # Simple keyword matching for now - could be enhanced with embeddings
        relevant = []
        for item in self.long_term:
            if query.lower() in str(item["value"]).lower():
                relevant.append(item)
        return relevant


class EnhancedAgent(BaseModel):
    llm: ChatLLM
    tools: List[ToolInterface]
    memory: Memory = Field(default_factory=Memory)
    prompt_template: str = PROMPT_TEMPLATE
    max_loops: int = 15
    # The stop pattern is used, so the LLM does not hallucinate until the end
    stop_pattern: List[str] = [f'\n{OBSERVATION_TOKEN}', f'\n\t{OBSERVATION_TOKEN}']
    confidence_threshold: float = 0.7
    current_goal: Optional[str] = None
    sub_goals: List[str] = Field(default_factory=list)

    @property
    def tool_description(self) -> str:
        return "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])

    @property
    def tool_names(self) -> str:
        return ",".join([tool.name for tool in self.tools])

    @property
    def tool_by_names(self) -> Dict[str, ToolInterface]:
        return {tool.name: tool for tool in self.tools}

    def set_goal(self, goal: str):
        self.current_goal = goal
        self.sub_goals = self._decompose_goal(goal)

    def _decompose_goal(self, goal: str) -> List[str]:
        # Simple goal decomposition - could be enhanced with LLM
        return [goal]  # For now, just return the main goal

    async def run(self, question: str):
        if not self.current_goal:
            self.set_goal(question)
        
        previous_responses = []
        num_loops = 0
        prompt = self.prompt_template.format(
            today=datetime.date.today(),
            tool_description=self.tool_description,
            tool_names=self.tool_names,
            question=question,
            previous_responses='{previous_responses}',
            memory_context='\n'.join([f"Previous experience: {m['value']}" for m in self.memory.get_relevant_memory(question)])
        )
        print(prompt.format(previous_responses=''))
        while num_loops < self.max_loops:
            num_loops += 1
            curr_prompt = prompt.format(previous_responses='\n'.join(previous_responses))
            generated, tool, tool_input = await self.decide_next_action(curr_prompt)
            
            if tool == 'Final Answer':
                self.memory.add_long_term(question, tool_input)
                return tool_input

            if tool not in self.tool_by_names:
                raise ValueError(f"Unknown tool: {tool}")

            try:
                tool_result = await self.tool_by_names[tool].use(tool_input)
                self.memory.add_short_term(
                    thought=generated.split(THOUGHT_TOKEN)[-1].strip(),
                    action=f"{tool}: {tool_input}",
                    result=tool_result
                )
            except Exception as e:
                tool_result = f"Error executing tool: {str(e)}"
                generated += f"\nThought: I encountered an error. Let me try a different approach."

            generated += f"\n{OBSERVATION_TOKEN} {tool_result}\n{THOUGHT_TOKEN}"
            print(generated)
            previous_responses.append(generated)

    async def decide_next_action(self, prompt: str) -> str:
        generated = await self.llm.generate(prompt, stop=self.stop_pattern)
        tool, tool_input = self._parse(generated)
        return generated, tool, tool_input

    def _parse(self, generated: str) -> Tuple[str, str]:
        if FINAL_ANSWER_TOKEN in generated:
            return "Final Answer", generated.split(FINAL_ANSWER_TOKEN)[-1].strip()
        regex = r"Action: [\[]?(.*?)[\]]?[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, generated, re.DOTALL)
        if not match:
            raise ValueError(f"Output of LLM is not parsable for next tool use: `{generated}`")
        tool = match.group(1).strip()
        tool_input = match.group(2)
        return tool, tool_input.strip(" ").strip('"')


if __name__ == '__main__':
    agent = EnhancedAgent(llm=ChatLLM(), tools=[PythonREPLTool()])
    result = agent.run("Your question here")

    print(f"Final answer is {result}")
