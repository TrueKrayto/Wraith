from backend.llm.client import get_llm_client, get_llm_model


def main():
    client = get_llm_client()
    model = get_llm_model()

    print(f"Using model: {model}")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "exit":
            break

        if not user_input:
            continue

        response = client.responses.create(
            model=model,
            input=user_input,
        )

        print("\nLLM:", response.output_text)


if __name__ == "__main__":
    main()