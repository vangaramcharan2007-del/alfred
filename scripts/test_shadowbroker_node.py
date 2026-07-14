import logging
from jarvisx.integrations.shadowbroker_node import ShadowBrokerNode

logging.basicConfig(level=logging.INFO)

def test_shadowbroker_nlp():
    print("--- Simulating Alfred NLP Command Routing for External Intel Node ---")
    node = ShadowBrokerNode()
    
    commands = [
        "Check ShadowBroker status",
        "Open ShadowBroker",
        "Restart ShadowBroker",
        "Shutdown ShadowBroker"
    ]
    
    for cmd in commands:
        print(f"\nUser: '{cmd}'")
        response = node.execute_nlp_intent(cmd)
        print(f"Alfred: {response}")

if __name__ == "__main__":
    test_shadowbroker_nlp()
