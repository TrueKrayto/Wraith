import "../../styles/components/CharacterPanel.css";

function CharacterPanel({
  characters,
  playerId,
  onPlayerChange,
  resources,
}) {
  const player = characters.find(
    (character) => String(character.id) === String(playerId)
  );

  return (
    <aside className="character-panel">
      <h2>Player</h2>

      <select
        value={playerId}
        onChange={(event) => onPlayerChange(event.target.value)}
      >
        {characters.map((character) => (
          <option
            key={character.id}
            value={character.id}
          >
            {character.name}
          </option>
        ))}
      </select>

      {player && (
        <div className="character-panel__identity">
          <h3>{player.name}</h3>
          <p>{player.role}</p>
          <p>Level {player.level}</p>
        </div>
      )}

      <div className="character-panel__resources">
        {resources.map((resource) => (
          <div
            key={resource.id}
            className={`resource resource--${resource.name}`}
          >
            <div className="resource__label">
              <span>{resource.name}</span>

              <span>
                {resource.current} / {resource.maximum}
              </span>
            </div>

            <div className="resource__track">
              <div
                className="resource__fill"
                style={{
                  width: `${
                    (resource.current / resource.maximum) * 100
                  }%`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}


export default CharacterPanel;