import "../../styles/components/SceneCharacters.css";

function SceneCharacters({
  characters,
  playerId,
}) {
  const sceneCharacters = characters.filter(
    (character) => String(character.id) !== String(playerId)
  );

  return (
    <section className="scene-characters">
      <h2>Characters in Scene</h2>

      <div className="scene-characters__list">
        {sceneCharacters.length === 0 && (
          <p>No other characters present.</p>
        )}

        {sceneCharacters.map((character) => (
          <div
            key={character.id}
            className="scene-character"
          >
            <strong>{character.name}</strong>

            <span>{character.role}</span>

            <span>
              Level {character.level}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}


export default SceneCharacters;