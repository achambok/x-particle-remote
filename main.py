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
    messages = [
        HumanMessage(
            content="""
                Execute the mandatory 5-phase trading workflow:
                1. Run health checks (account status, trade frequency, existing positions)
                2. Perform technical analysis on all symbols
                3. Check for high-impact news events
                4. Validate any potential trade setup
                5. Make a final decision: EXECUTE or NO TRADE

                Remember: NO TRADE is better than a bad trade. Most runs should result in NO TRADE.
                """
        )
    ]
    print("Starting agent...")

    try:
        messages = agent.invoke({"messages": messages}, config={"recursion_limit": 100})
        last_message = messages["messages"][-1].content
        logger.info(last_message)
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
