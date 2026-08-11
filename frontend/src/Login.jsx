import { useState } from "react";
import axios from "axios";
import "./style.css";

function Login({ setLoggedIn }) {
  const [loginMode, setLoginMode] = useState(true);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const API = "/api";

  const login = async (e) => {
  e.preventDefault();

  try {

    const res = await axios.post(
      `${API}/login`,
      {
        email: email,
        password: password,
      }
    );

    localStorage.setItem(
      "token",
      res.data.access_token
    );

    localStorage.setItem(
      "user_id",
      res.data.user_id
    );

    localStorage.setItem("username", res.data.username);

    setLoggedIn(true);

  } catch (err) {

    alert(
      err.response?.data?.detail || "Login failed."
    );

  }
};

  const signup = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      alert("Passwords don't match.");
      return;
    }

    try {
      await axios.post(`${API}/signup`, {
        username,
        email,
        password,
      });

      alert("Account created successfully!");

      setLoginMode(true);

      setUsername("");
      setEmail("");
      setPassword("");
      setConfirmPassword("");
    } catch (err) {
  console.log(err);
  alert(err.message);
}
  };

    return (
  <div className="login-page">

    <div className="card">

      <h2>
        {loginMode ? "Login to your Account" : "Create Account"}
      </h2>

    
      

      <form onSubmit={loginMode ? login : signup}>

        {!loginMode && (
          <div className="input-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e)=>setUsername(e.target.value)}
              required
            />
          </div>
        )}

        <div className="input-group">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e)=>setEmail(e.target.value)}
            required
          />
        </div>

        <div className="input-group">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
            required
          />
        </div>

        {!loginMode && (
          <div className="input-group">
            <label>Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e)=>setConfirmPassword(e.target.value)}
              required
            />
          </div>
        )}

        <button className="login-btn" type="submit">
          {loginMode ? "Login" : "Create Account"}
        </button>

      </form>

      <div className="bottom-text">
        {loginMode ? (
          <>
            New here?{" "}
            <span onClick={()=>setLoginMode(false)}>
              Sign Up
            </span>
          </>
        ) : (
          <>
            Already have an account?{" "}
            <span onClick={()=>setLoginMode(true)}>
              Login
            </span>
          </>
        )}
      </div>

    </div>

  </div>
);
}

export default Login;