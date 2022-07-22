import React from "react";
import "./style/main.scss";
import { CodeBlock, dracula } from "react-code-blocks";

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
    <div className="App">
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

    </div>
  );
}

export default App;
