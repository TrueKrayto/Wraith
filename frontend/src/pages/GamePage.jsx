import { useEffect, useState } from "react";

import "../styles/pages/GamePage.css";

import Toolbar from "../components/game/Toolbar";
import CharacterPanel from "../components/game/CharacterPanel";
import SceneCharacters from "../components/game/SceneCharacters";
import MainPanel from "../components/game/MainPanel";
import PlayerButtonBar from "../components/game/PlayerButtonBar";
import InputPanel from "../components/game/InputPanel";
import AssistantPanel from "../components/game/AssistantPanel";


function GamePage() {
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
    <div className="game-page">
      <Toolbar />

      <CharacterPanel
        characters={characters}
        playerId={playerId}
        onPlayerChange={setPlayerId}
        resources={playerResources}
      />

      <div className="game-page__center">
        <SceneCharacters
          characters={characters}
          playerId={playerId}
        />

        <MainPanel
          gameLog={gameLog}
        />

        <PlayerButtonBar />

        <InputPanel
          actionText={actionText}
          onActionTextChange={setActionText}
          onSubmit={handleActionSubmit}
          isActing={isActing}
        />
      </div>

      <AssistantPanel />
    </div>
  );
}


export default GamePage;