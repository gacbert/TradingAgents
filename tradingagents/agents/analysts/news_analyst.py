from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
import re


def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_global_news_openai, toolkit.get_google_news]
        else:
            tools = [
                toolkit.get_finnhub_news,
                toolkit.get_reddit_news,
                toolkit.get_google_news,
            ]

        system_message = (
            "You are a news researcher tasked with analyzing recent news and trends over the past week. Please write a comprehensive report of the current state of the world that is relevant for trading and macroeconomics. Look at news from EODHD, and finnhub to be comprehensive. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
            + """ Make sure to append a Makrdown table at the end of the report to organize key points in the report, organized and easy to read."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. We are looking at the company {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        # Use full message history for context
        full_messages = state["messages"]
        # Handle Gemini provider with manual invocation to specify contents
        if toolkit.config["llm_providers"].get("quick_think") == "gemini":
            prompt_val = prompt.format_prompt(messages=full_messages)
            # Combine all prompt messages into a single string for Gemini
            contents = "\n\n".join([msg.content for msg in prompt_val.messages])
            result = llm.invoke(contents=[contents])
        else:
            chain = prompt | llm.bind_tools(tools)
            result = chain.invoke({"messages": full_messages})

        # Clean news report: remove planning intro and duplicate lines
        raw = result.content
        # Skip intro paragraph(s) up to first blank line
        parts = re.split(r"\n\s*\n", raw, maxsplit=1)
        raw = parts[1] if len(parts) > 1 else parts[0]
        # Remove any parenthetical planning remarks
        raw = re.sub(r"\([^)]*(?:I will|I'll)[^)]*\)\s*", "", raw)
        # Remove any lines starting with planning phrases
        raw = re.sub(r"^(?:I will|I'll)[^\n]*\n+", "", raw, flags=re.IGNORECASE)
        # Remove duplicate consecutive lines
        lines = raw.splitlines()
        filtered = []
        prev = None
        for ln in lines:
            if ln != prev:
                filtered.append(ln)
            prev = ln
        raw = "\n".join(filtered)
        # Final cleanup: strip whitespace
        cleaned = raw.strip()
        return {
            "messages": [result],
            "news_report": cleaned,
        }

    return news_analyst_node
