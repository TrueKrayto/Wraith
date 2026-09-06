import { useEffect, useState } from "react";

function App() {
  const [characters, setCharacters] = useState([]);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/characters`)
      .then((response) => response.json())
      .then((data) => setCharacters(data))
      .catch((error) => console.error("Failed to load characters:", error));
  }, []);

  return (
    <div>
      <h1>Wraith</h1>

      <h2>Characters</h2>

      {characters.map((character) => (
        <div key={character.id}>
          <p>
            ID: {character.id} | Name: {character.name} | Level:{" "}
            {character.level} | Role: {character.role}
          </p>
        </div>
      ))}
    </div>
  );
}

export default App;