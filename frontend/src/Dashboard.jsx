import { useEffect, useState } from "react";
import axios from "axios";
import "./style.css";

function Dashboard() {

    const API = "/api";

    const [joke, setJoke] = useState(null);
    const [showAnswer, setShowAnswer] = useState(false);
    const [startTime, setStartTime] = useState(Date.now());
    const [explanation,setExplanation]=useState("");
    const [preferences,setPreferences]=useState([]);
    const [savedJokes, setSavedJokes] = useState([]);
    const [showSaved, setShowSaved] = useState(false);
    const [darkMode, setDarkMode] = useState(
    localStorage.getItem("theme") === "dark"
     );

    useEffect(() => {

    if (darkMode) {
        document.body.classList.add("dark");
        localStorage.setItem("theme", "dark");
    } else {
        document.body.classList.remove("dark");
        localStorage.setItem("theme", "light");
    }

}, [darkMode]); 

    useEffect(() => {
        loadRandomJoke();
        loadSavedCount();

    }, []);

    const loadSavedCount = async () => {

    try {

        const token = localStorage.getItem("token");

        const res = await axios.get(
            `${API}/interactions/saved`,
            {
                headers:{
                    Authorization:`Bearer ${token}`
                }
            }
        );

        setSavedJokes(res.data);

    }

    catch(err){
        console.log(err);
    }

};
    

    const loadRandomJoke = async () => {

        try{

            const token = localStorage.getItem("token");

            const res = await axios.get(
                `${API}/jokes/random`,
                {
                    headers:{
                        Authorization:`Bearer ${token}`
                    }
                }
            );

            setJoke(res.data);

            setStartTime(Date.now());
            setExplanation("");
            loadPreferences();
            setShowAnswer(false);

        }

            

        catch(err){

            console.log(err);

        }

    };

    const loadSavedJokes = async () => {
    try {
        const token = localStorage.getItem("token");

        const res = await axios.get(
            `${API}/interactions/saved`,
            {
                headers: { Authorization: `Bearer ${token}` }
            }
        );

        setSavedJokes(res.data);
        setShowSaved(true);

    } catch (err) {
        console.log(err);
    }
};

    const loadRecommendation = async () => {

    try{

        const token = localStorage.getItem("token");
        const userId = localStorage.getItem("user_id");

        const res = await axios.get(
            `${API}/recommendations/${userId}`,
            {
                headers:{
                    Authorization:`Bearer ${token}`
                }
            }
        );

        setJoke(res.data);

        setStartTime(Date.now());
        setExplanation("");
        setShowAnswer(false);

    }

    catch(err){

        console.log(err);

    }

};

    const saveInteraction = async (
rating,
liked,
disliked
) => {

try{

const token = localStorage.getItem("token");

await axios.post(

`${API}/interactions/`,

{
joke_id:joke.joke_id,
rating,
liked,
disliked,
time_spent: Math.floor((Date.now() - startTime) / 1000)
},

{
headers:{
Authorization:`Bearer ${token}`
}
}

);

alert("Saved!");

}

catch(err){

console.log(err);

}

};

const getExplanation=async()=>{

try{

const res=await axios.post(

`${API}/explain`,

{
question:joke.question,
answer:joke.answer
}

);

setExplanation(res.data.explanation);

}

catch(err){

console.log(err);

}

};

const loadPreferences = async () => {
    try {
        const token = localStorage.getItem("token");
        const userId = localStorage.getItem("user_id");

        const res = await axios.get(
            `${API}/preferences/${userId}`,
            {
                headers: { Authorization: `Bearer ${token}` }
            }
        );

        setPreferences(res.data);
    } catch (err) {
        console.log(err);
    }
};

const removeSaved = async (jokeId) => {

    const token = localStorage.getItem("token");

    await axios.delete(
        `${API}/interactions/saved/${jokeId}`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    setSavedJokes(
        savedJokes.filter(j => j.joke_id !== jokeId)
    );
};

    return (

        <div className="dashboard">

            <nav className="navbar">

                <h2>😂LaughLoop </h2>

                <div className="nav-right">


                    <div className="nav-user">

    <button
        className="theme-btn"
        onClick={() => setDarkMode(!darkMode)}
    >
        {darkMode ? "☀ Light" : "🌙 Dark"}
    </button>

    <span>{localStorage.getItem("username")}</span>

</div>

                    <button
                        className="logout-btn"
                        onClick={()=>{
                            localStorage.removeItem("token");
                            localStorage.removeItem("user_id");
                            window.location.reload();
                        }}
                    >
                        Logout
                    </button>

                </div>

            </nav>

            <div className="dashboard-container">

                <div className="joke-card">

                    <h1>🎲 Jokes </h1>

                   <div className="question-box">

    <h3> Question</h3>

    <p>{joke?.question}</p>

</div>

<div
    className={`answer-box ${showAnswer ? "show" : ""}`}
    onClick={() => setShowAnswer(!showAnswer)}
>

    {!showAnswer ? (

        <>
            <h3>🎁 Reveal Answer</h3>
            <p>Click to flip</p>
        </>

    ) : (

        <>
            <h3> Answer</h3>
            <p>{joke?.answer}</p>
        </>

    )}

    

</div>

<button
className="explain-btn"
onClick={getExplanation}
>
💡 Explain Joke
</button>

                    {
explanation &&

<div className="explanation">

{explanation}

</div>

}

                    <div className="actions">

<button
className="reaction-btn"
onClick={()=>saveInteraction(1,true,false)}
>
👍🏼
</button>

<button
className="reaction-btn"
onClick={()=>saveInteraction(1,false,true)}
>
👎🏿
</button>

</div>

                    

                </div>

                <div className="side-panel">

                    <div className="recommend-box">

                        <h2>
                            🔻 Recommended
                        </h2>

                        <button
                            className="next-btn"
                            onClick={loadRecommendation}
                        >
                            Next Joke
                        </button>

                    </div>

                    <div className="profile-box">

                       <h2>
    📊 Your Preferences
</h2>

{preferences.map((item,index)=>(

<div className="preference" key={index}>

<span>{item.category}</span>

<div className="bar">
<div
className="fill"
style={{
width:`${Math.min(item.count*10,100)}%`
}}
></div>
</div>
</div>
))}


<div className="recommend-box">
    <button className="next-btn" onClick={loadSavedJokes}>
    ❤️ Saved ({savedJokes.length})
</button>
</div>

                    </div>

                </div>

            </div>

            {showSaved && (
    <div className="modal-overlay" onClick={() => setShowSaved(false)}>
        <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h2>❤️ Your Saved Jokes</h2>
            <button className="close-btn" onClick={() => setShowSaved(false)}>✕</button>

            <div className="saved-list">
                {savedJokes.length === 0 ? (
                    <p>No saved jokes yet. Like some jokes first!</p>
                ) : (
                    savedJokes.map((j) => (
                        <div className="saved-joke-item" key={j.joke_id}>

    <p className="saved-question">
        ❓ {j.question}
    </p>

    <p className="saved-answer">
        😂 {j.answer}
    </p>

    <button
        className="remove-btn"
        onClick={() => removeSaved(j.joke_id)}
    >
        🗑 Remove
    </button>

</div>
                    ))
                )}
            </div>
        </div>
    </div>
)}

        </div>

    );

}

export default Dashboard;