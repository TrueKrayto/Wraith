import { useEffect, useState } from "react";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/health`)
      .then((response) => response.json())
      .then((data) => setBackendStatus(data.status))
      .catch(() => setBackendStatus("error"));
  }, []);

  return (
    <div>
      <h1>Wraith</h1>
      <p>Backend status: {backendStatus}</p>
    </div>
  );
}

export default App;