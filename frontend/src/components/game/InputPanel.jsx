import "../../styles/components/InputPanel.css";

function InputPanel({
  actionText,
  onActionTextChange,
  onSubmit,
  isActing,
}) {
  return (
    <section className="input-panel">
      <form
        className="input-panel__form"
        onSubmit={onSubmit}
      >
        <textarea
          className="input-panel__textarea"
          value={actionText}
          onChange={(event) =>
            onActionTextChange(event.target.value)
          }
          placeholder="What do you do?"
          disabled={isActing}
        />

        <button
          className="input-panel__submit"
          type="submit"
          disabled={isActing}
        >
          {isActing ? "Resolving..." : "Act"}
        </button>
      </form>
    </section>
  );
}


export default InputPanel;