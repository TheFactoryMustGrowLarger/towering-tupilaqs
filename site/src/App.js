import React from "react";
import "./style/main.scss";
import { CodeBlock, dracula } from "react-code-blocks";
import { BrowserRouter, Routes, Route, Link} from "react-router-dom"

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
    return (
        <div>
            <Link to="/categories"><button className="bb-buton start-button">Start game</button></Link>
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
                        Upload my own question
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
