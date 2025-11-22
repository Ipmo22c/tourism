"""
Main entry point for the Multi-Agent Tourism System
"""
from agents.tourism_agent import TourismAgent


def main():
    """Main function to run the tourism system"""
    print("=" * 60)
    print("Welcome to the Multi-Agent Tourism System!")
    print("=" * 60)
    print("\nEnter a place you want to visit and ask about weather or places to visit.")
    print("Examples:")
    print("  - 'I'm going to go to Bangalore, let's plan my trip.'")
    print("  - 'I'm going to go to Bangalore, what is the temperature there'")
    print("  - 'I'm going to go to Bangalore, what is the temperature there? And what are the places I can visit?'")
    print("\nType 'exit' or 'quit' to stop.\n")
    
    tourism_agent = TourismAgent()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nThank you for using the Tourism System. Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\nProcessing your query...")
            response = tourism_agent.process_query(user_input)
            print(f"\nAgent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nThank you for using the Tourism System. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again with a different query.")


if __name__ == "__main__":
    main()

