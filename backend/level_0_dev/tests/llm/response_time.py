import time

from backend.level_4_systems.llm.clients import (
    get_llm_client,
    get_llm_model,
)


test = """
Design a fault-tolerant distributed backend for a real-time multiplayer simulation game supporting 100,000 concurrent players across multiple geographic regions. The system must maintain persistent player state, NPC state, faction state, inventories, combat events, and an advancing in-game calendar. Explain how you would divide responsibilities between API servers, simulation workers, databases, caches, message queues, and background jobs. Discuss how you would partition the workload, handle horizontal scaling, prevent race conditions when multiple services modify the same entity, and maintain acceptable latency when players in different regions interact with shared world objects.

Then analyze the consistency model in detail. Compare strong consistency, eventual consistency, optimistic concurrency control, distributed locking, event sourcing, and CQRS for this system, and explain where each technique would or would not be appropriate. Give a concrete example involving two players simultaneously attacking the same NPC while a background faction simulation also modifies that NPC's location. Trace the requests through the system step by step, including database transactions, queue messages, version checks, failure recovery, retries, idempotency, and what happens if one service crashes halfway through processing the event.

Finally, propose a complete production architecture and justify the major technical decisions. Include likely technologies, database schema considerations, caching strategy, queue topology, worker orchestration, observability, deployment strategy, disaster recovery, and security boundaries. Identify the most likely bottlenecks as the game grows from 100 concurrent users to 1,000, 10,000, and 100,000, and explain what architectural changes would become necessary at each stage. Where there are meaningful trade-offs, compare at least two viable approaches rather than simply selecting one, and explain how you would benchmark the finished architecture to determine whether it meets latency, throughput, consistency, and reliability requirements.
"""


def test_llm(prompt: str):
    client = get_llm_client()
    model = get_llm_model()

    print(f"Model: {model}")
    print("Sending request...\n")

    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    elapsed = time.perf_counter() - start

    content = response.choices[0].message.content
    finish_reason = response.choices[0].finish_reason

    print(content)

    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)

    print(f"Response time: {elapsed:.3f} seconds")
    print(f"Finish reason: {finish_reason}")

    if response.usage:
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Completion tokens: {completion_tokens}")
        print(f"Total tokens: {total_tokens}")

        if elapsed > 0:
            output_speed = completion_tokens / elapsed
            print(f"Output speed: {output_speed:.1f} tokens/sec")
    else:
        print("Token usage unavailable.")

    print("=" * 60)


if __name__ == "__main__":
    test_llm(test)