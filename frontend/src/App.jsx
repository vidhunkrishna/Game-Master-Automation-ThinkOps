import { GameProvider } from "./context/GameContext";
import Dashboard from "./components/Dashboard";

function App() {
  return (
    <GameProvider>
      <Dashboard />
    </GameProvider>
  );
}

export default App;
