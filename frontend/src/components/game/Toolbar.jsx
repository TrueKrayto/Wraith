import "../../styles/components/Toolbar.css";

function Toolbar() {
  return (
    <header className="game-toolbar">
      <div className="game-toolbar__brand">
        Wraith
      </div>

      <nav className="game-toolbar__controls">
        <button type="button">
          Game
        </button>

        <button type="button">
          Save
        </button>

        <button type="button">
          Load
        </button>

        <button type="button">
          Settings
        </button>
      </nav>
    </header>
  );
}


export default Toolbar;