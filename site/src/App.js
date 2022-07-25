import React from "react";
import "./style/main.scss";
import { CodeBlock, dracula } from "react-code-blocks";
import { BrowserRouter, Routes, Route, Link} from "react-router-dom"
import {useState, useCallback, useEffect} from "react";
import useWebSocket, { ReadyState } from 'react-use-websocket';

export const WebSocketDemo = () => {
    //Public API that will echo messages sent to it back to the client

    const [messageHistory, setMessageHistory] = useState([]);

    const {sendMessage, lastMessage, readyState} = useWebSocket(socketUrl);

    useEffect(() => {
        if (lastMessage !== null) {
            setMessageHistory((prev) => prev.concat(lastMessage));
        }
    }, [lastMessage, setMessageHistory]);

    const handleClickChangeSocketUrl = useCallback(
        () => setSocketUrl('wss://demos.kaazing.com/echo'),
        []
    );
    const handleClickSendMessage = useCallback(() => sendMessage('Hello'), []);
     const connectionStatus = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Open',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
    [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
  }[readyState];

  return (
    <div>
      <button onClick={handleClickChangeSocketUrl}>
        Click Me to change Socket Url
      </button>
      <button
        onClick={handleClickSendMessage}
        disabled={readyState !== ReadyState.OPEN}
      >
        Click Me to send 'Hello'
      </button>
      <span className="debug-color">The WebSocket is currently {connectionStatus}</span>
      {lastMessage ? <span>Last message: {lastMessage.data}</span> : null}
      <ul>
        {messageHistory.map((message, idx) => (
          <span key={idx}>{message ? message.data : null}</span>
        ))}
      </ul>
    </div>
  );
};



const Categories = () => {
    return(
        <div className="flex">
            <button>1</button>
            <button>2</button>
            <button>3</button>
        </div>
    )
}

const LandingPage = () =>{
    const [socketUrl, setSocketUrl] = useState('http://127.0.0.1:8000/');
    const connect_event = (event) =>{
        const itemId = document.getElementById("itemID")
        const token = document.getElementById("token")
        setSocketUrl("ws://localhost:8000/new_question/" + itemId.value + "/ws?token=" + token.value)
           useWebSoket(sokcetURL => {
                onMessage((mess) => {
                console.log(mess.data)
                const data_parsed = "idk"
                    })
           })
    }
    return (
        <div>
            <div className="inputs registration">
                <input type="text" className="input-base" id="itemID" placeholder="Username: "/>
                <input type="text" className="input-base" id="token" placeholder="Password"/>
                <button className="bb-buton small-height" onClick={(event) => connect_event(event)}>Connect</button>
            </div>
            <Link to="/categories"><button className="bb-buton start-button">Start game</button></Link>
            <h1 className="main-title center">Add custom questions </h1>
            <div className="inputs">
                <input type="text" className="input-base" id="newQuestionText" placeholder="New Question: "/>
                <input type="text" className="input-base" id="correctAnswer" placeholder='"Bug" or "feature":'/>
                <input type="text" className="input-base" id="newQuestionTitle" placeholder="Question title:"/>
                <input type="text" className="input-base" id="newQuestionExplanation" placeholder="Question explanation:"/>
                <button className="bb-buton small-height">Send</button>
            </div>

        </div>


    )
}

const Box = () =>{
    return (
         <div className="box">
                    <div className="code-snippet">
                    <MyCoolCodeBlock code={`class Dog:
                          #init creates certain parameters that allow you to define information quickly.
                          def __init__(self, name):
                            self.name = name

                          def get_name(self):
                        \treturn self.name

                        if __name__ == "__main__":
                          d = Dog(str(input("name your dog: "))
                          print(d.get_name())
                          `} language={"python"} showLineNumbers={true} startingLineNumber={1} theme={dracula} />
                </div>
                <div className="buttons">
                    <button className="bb-buton bug">
                        Bug
                </button>
                    <button className="bb-buton feature">
                        Features
                    </button>
                    <button className="bb-buton upload">
                        Upload my own question!
                    </button>
                </div>
          </div>

    )
}

function MyCoolCodeBlock({ code, language, showLineNumbers, startingLineNumber }) {
  return (<CodeBlock
    text={code}
    language={language}
    showLineNumbers={showLineNumbers}
    startingLineNumber={startingLineNumber}
    theme={dracula}
    codeBlock
  />);
}

function App() {
  return (
      <BrowserRouter>
          <div className="App">
              <h1 className="main-title">WebSocket Quiz - Bug, Feature or Tupilaqs</h1>
              <Routes>
                  <Route path="/categories/:category" element={<Box/>}/>
                  <Route path="/" element={<LandingPage/>}/>
                  <Route path="/categories" element={<Categories/>}/>
              </Routes>
    </div>
      </BrowserRouter>

  );
}

export default App;
