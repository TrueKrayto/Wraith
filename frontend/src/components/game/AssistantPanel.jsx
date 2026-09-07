import "../../styles/components/AssistantPanel.css";

function AssistantPanel() {
  return (
    <aside className="assistant-panel">
      <h2>Assistant</h2>

      <div className="assistant-panel__content">
        <p>
          Assistant tools and guidance will appear here.
        </p>
      </div>

      <div className="assistant-panel__input">
        <input
          type="text"
          placeholder="Ask the assistant..."
          disabled
        />

        <button
          type="button"
          disabled
        >
          Send
        </button>
      </div>
    </aside>
  );
}


export default AssistantPanel;