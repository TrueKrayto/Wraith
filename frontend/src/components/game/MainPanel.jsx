import "../../styles/components/MainPanel.css";

function MainPanel({
  gameLog,
}) {
  return (
    <section className="main-panel">
      <div className="main-panel__content">
        {gameLog.length === 0 && (
          <p className="main-panel__empty">
            No actions yet.
          </p>
        )}

        {gameLog.map((entry, index) => {
          if (entry.type === "player") {
            return (
              <div
                key={index}
                className="game-entry game-entry--player"
              >
                <strong>You</strong>

                <p>{entry.text}</p>
              </div>
            );
          }

          if (entry.type === "error") {
            return (
              <div
                key={index}
                className="game-entry game-entry--error"
              >
                <strong>Error</strong>

                <p>{entry.text}</p>
              </div>
            );
          }

          return (
            <div
              key={index}
              className="game-entry game-entry--narration"
            >
              <strong>Wraith</strong>

              <p>{entry.text}</p>

              {entry.debug && (
                <details className="game-entry__debug">
                  <summary>Debug</summary>

                  <pre>
                    {JSON.stringify(
                      entry.debug,
                      null,
                      2
                    )}
                  </pre>
                </details>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}


export default MainPanel;