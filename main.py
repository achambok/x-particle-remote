from agents.main_agent import agent
from langchain.messages import HumanMessage
import logging
import os

# Ensure logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configure root logger to WARNING to suppress third-party library logs
logging.basicConfig(
    filename=os.path.join(log_dir, "agent.log"),
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# Create custom logger for this application at INFO level
logger = logging.getLogger("x-particle")
logger.setLevel(logging.INFO)


def main():
    messages = [HumanMessage(content="Hello! Analyze and trade accordingly.")]
    logger.info("Starting agent...")

    try:
        messages = agent.invoke({"messages": messages}, config={"recursion_limit": 100})
        # logger.info(messages)
        last_message = messages["messages"][-1].content
        logger.info(last_message)
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
