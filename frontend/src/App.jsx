import { useEffect, useState } from "react";


function App() {
  const [characters, setCharacters] = useState([]);
  const [playerId, setPlayerId] = useState("");

  const [playerResources, setPlayerResources] = useState([]);

  const [actionText, setActionText] = useState("");
  const [gameLog, setGameLog] = useState([]);

  const [isActing, setIsActing] = useState(false);


  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/characters`)
      .then((response) => response.json())
      .then((data) => {
        setCharacters(data);

        if (data.length > 0) {
          setPlayerId(String(data[0].id));
        }
      })
      .catch((error) => {
        console.error("Failed to load characters:", error);
      });
  }, []);


  useEffect(() => {
    loadPlayerResources();
  }, [playerId]);


  function loadPlayerResources() {
    if (!playerId) {
      return;
    }

    fetch(
      `${import.meta.env.VITE_API_URL}/characters/${playerId}/resources`
    )
      .then((response) => response.json())
      .then((data) => setPlayerResources(data))
      .catch((error) => {
        console.error("Failed to load player resources:", error);
      });
  }


  async function handleActionSubmit(event) {
    event.preventDefault();

    const trimmedAction = actionText.trim();

    if (!trimmedAction || !playerId || isActing) {
      return;
    }

    setActionText("");
    setIsActing(true);

    setGameLog((previousLog) => [
      ...previousLog,
      {
        type: "player",
        text: trimmedAction,
      },
    ]);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/play`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            actor_character_id: Number(playerId),
            action_text: trimmedAction,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Action failed."
        );
      }

      setGameLog((previousLog) => [
        ...previousLog,
        {
          type: "narration",
          text: data.narration,
          debug: data,
        },
      ]);

      loadPlayerResources();

    } catch (error) {
      setGameLog((previousLog) => [
        ...previousLog,
        {
          type: "error",
          text: error.message,
        },
      ]);

    } finally {
      setIsActing(false);
    }
  }


  return (
    <main>
      <h1>Wraith</h1>

      <section>
        <h2>Player</h2>

        <select
          value={playerId}
          onChange={(event) => setPlayerId(event.target.value)}
        >
          {characters.map((character) => (
            <option key={character.id} value={character.id}>
              {character.name} — Level {character.level}
            </option>
          ))}
        </select>

        <ResourceList resources={playerResources} />
      </section>

      <hr />

      <section>
        <h2>Game</h2>

        <div>
          {gameLog.length === 0 && (
            <p>No actions yet.</p>
          )}

          {gameLog.map((entry, index) => {
            if (entry.type === "player") {
              return (
                <p key={index}>
                  <strong>You:</strong> {entry.text}
                </p>
              );
            }

            if (entry.type === "error") {
              return (
                <p key={index}>
                  <strong>Error:</strong> {entry.text}
                </p>
              );
            }

            return (
              <div key={index}>
                <p>
                  <strong>Wraith:</strong> {entry.text}
                </p>

                <details>
                  <summary>Debug</summary>

                  <pre>
                    {JSON.stringify(entry.debug, null, 2)}
                  </pre>
                </details>
              </div>
            );
          })}
        </div>

        <form onSubmit={handleActionSubmit}>
          <textarea
            value={actionText}
            onChange={(event) => setActionText(event.target.value)}
            placeholder="What do you do?"
            rows={4}
            disabled={isActing}
          />

          <br />

          <button
            type="submit"
            disabled={isActing}
          >
            {isActing ? "Resolving..." : "Act"}
          </button>
        </form>
      </section>
    </main>
  );
}


function ResourceList({ resources }) {
  if (resources.length === 0) {
    return <p>No resources.</p>;
  }

  return (
    <ul>
      {resources.map((resource) => (
        <li key={resource.id}>
          {resource.name}: {resource.current} / {resource.maximum}
        </li>
      ))}
    </ul>
  );
}


export default App;