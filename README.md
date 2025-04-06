# 🤖 Smart AI Agents: Making AI Work for You

Hey there! 👋 Welcome to my project where I've built a framework for creating intelligent AI agents that can actually get things done. Think of it as giving AI the ability to think, plan, and execute tasks just like a human would, but with the speed and accuracy of a computer.

## 🎯 What Can It Do?

Imagine having a smart assistant that can:
- Remember past conversations and learn from them
- Break down big tasks into smaller, manageable steps
- Make decisions based on how confident it is
- Run multiple tasks at the same time
- Learn and improve as it goes

## 🛠️ The Tools It Uses

I've built in several useful tools that the AI can use:
- A Python code executor (so it can write and run code)
- Web search capabilities (to find information online)
- Hacker News search (to stay updated with tech news)
- General web search tools
- Alternative search engines

## 🚀 Getting Started

Want to try it out? Here's how to get it running:

```bash
# First, get the code
git clone https://github.com/owaisasghar/llm-agents.git
cd llm-agents

# Set up your Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install what you need
pip install -r requirements.txt
```

## 📋 What You'll Need

- Python 3.8 or newer
- An OpenAI API key (for the AI brain)
- (Optional) A SerpAPI key if you want web search features

## 💡 Quick Example

Here's a simple example of how to use it:

```python
from llm_agents import AdvancedAgent, ChatLLM
from llm_agents.tools import PythonREPLTool, SerpAPITool

# Create your AI agent
agent = AdvancedAgent(
    llm=ChatLLM(),
    tools=[PythonREPLTool(), SerpAPITool()]
)

# Give it a task
result = await agent.run("Your task here")
```

## 🧠 Cool Features

### Memory That Makes Sense
The AI can remember past conversations and find relevant information when needed:
```python
relevant_memories = agent.memory.get_relevant_memory("your query", top_k=5)
```

### Smart Goal Management
It can break down big tasks and track progress:
```python
agent.set_goal("complex task")
print(f"Progress: {agent.current_goal.progress}")
```

### Tool Combinations
You can create custom workflows by combining different tools:
```python
tool_manager.define_tool_chain(
    "search_and_analyze",
    ["SerpAPITool", "PythonREPLTool"]
)
```

## 📊 Keeping Track

You can monitor how well the AI is doing:
```python
stats = agent.tool_stats
print(f"Success rate: {stats['PythonREPLTool']['success'] / stats['PythonREPLTool']['total']}")
```

## 🤝 Want to Help?

I'd love your help in making this project even better! Here's how you can contribute:

1. Fork the project
2. Create your feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source and free to use under the MIT License.

## 👋 About Me

Hi! I'm Awais Asghar, the creator of this project. I built this because I wanted to create something that makes AI more useful and accessible for everyone.

You can find me on:
- GitHub: [@owaisasghar](https://github.com/owaisasghar)
- Email: awaisasghar900@gmail.com
- LinkedIn: [Awais Asghar](https://www.linkedin.com/in/awais-asghar-9b9b27175/)

## 🙏 Special Thanks

This project wouldn't be possible without:
- The inspiration from [LangChain](https://github.com/hwchase17/langchain)
- [Sentence Transformers](https://github.com/UKPLab/sentence-transformers) for making semantic search possible
- [Pydantic](https://github.com/pydantic/pydantic) for keeping everything organized

Feel free to reach out if you have any questions or ideas! 😊
