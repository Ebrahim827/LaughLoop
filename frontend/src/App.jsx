import { useState } from "react";
import Login from "./Login";
import Dashboard from "./Dashboard";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  return (
    <>
      {loggedIn ? (
        <Dashboard setLoggedIn={setLoggedIn} />
      ) : (
        <Login setLoggedIn={setLoggedIn} />
      )}
    </>
  );
}

export default App;