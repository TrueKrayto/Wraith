import "../../styles/components/PlayerButtonBar.css";

function PlayerButtonBar() {
  return (
    <section className="player-button-bar">
      <button type="button">
        Character
      </button>

      <button type="button">
        Inventory
      </button>

      <button type="button">
        Abilities
      </button>

      <button type="button">
        Journal
      </button>

      <button type="button">
        Map
      </button>
    </section>
  );
}


export default PlayerButtonBar;